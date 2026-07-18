"""pipeline/terminal/ingest_news.py — 09-trading-terminal Fase 5: real sector news ingestion.

Populates sector_news (migrations/0091) from REAL RSS feeds of Spain's automotive-sector trade
associations — verified live and read in full THIS session (curl'd, not assumed): ANFAC
(anfac.com/feed/), Faconauto (faconauto.com/feed/), GANVAM (ganvam.es/feed/). These are the
Spain-specific analogue of the carta's cited SMMT/KBA/DGT/ACEA pattern (carta §2.4) — the
official-adjacent source that replaces the demolished, fabricated `carNews()` (09-Fase0).

Zero LLM in this pipeline (§8 doctrine: "cero LLM en el camino crítico del dato" + "AI out of
critical path" per the project's memory mandate). symbol_keys classification is a DETERMINISTIC
keyword match against active market_symbol makes — a real LLM classifier is explicitly named as a
FUTURE enhancement in the carta (§8: "clasificación de noticias por tema/relevancia... batch,
offline, re-ejecutable"), not fabricated here as a call this session cannot verify actually runs.

Uses only the Python standard library (urllib, xml.etree, hashlib) — no new project dependency for
a straightforward RSS 2.0 fetch+parse (`requests` is present transitively but not a declared
project dependency; adding it for this alone would be scope creep the coding-style doctrine
(KISS/YAGNI) argues against).

Run:
    python -m pipeline.terminal.ingest_news          # fetch + ingest new items
    python -m pipeline.terminal.ingest_news --verify  # V5 re-verify existing items only
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import asyncpg

from pipeline.ids import ulid

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# Real RSS feeds — Spain automotive-sector trade associations, each verified reachable and
# well-formed RSS 2.0 THIS session (curl -sI / curl -s, both logged in the F5 execution notes).
FEEDS: tuple[tuple[str, str], ...] = (
    ("ANFAC", "https://anfac.com/feed/"),
    ("Faconauto", "https://www.faconauto.com/feed/"),
    ("GANVAM", "https://ganvam.es/feed/"),
)

HTTP_TIMEOUT_SECONDS = 15
USER_AGENT = "CardeepTerminalNewsBot/1.0 (+https://github.com/sublimine/cardeep)"

# V5 freshness — an item not re-verified within this window is NOT served by the API (terminal.py
# applies this at read time; this constant is mirrored there for documentation, not imported
# directly, since the router must not depend on a pipeline/ import for a plain integer).
V5_FRESHNESS_DAYS = 30


def _http_get(url: str) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            if resp.status != 200:
                return None
            return resp.read()
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def _parse_pubdate(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def _content_hash(title: str, description: str) -> str:
    return hashlib.sha256(f"{title}\n{description}".encode("utf-8")).hexdigest()


def _parse_feed(raw: bytes) -> list[dict[str, Any]]:
    """Parse a standard RSS 2.0 <channel><item> feed. Returns [] on malformed XML — never raises
    into the caller (a single bad feed must not abort ingestion of the other sources)."""
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return []
    items = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        pub_date = _parse_pubdate(item.findtext("pubDate"))
        if title and link:
            items.append({"title": title, "link": link, "description": description, "pub_date": pub_date})
    return items


def _match_symbol_keys(title: str, description: str, makes: list[str]) -> list[str]:
    """Deterministic keyword match: a make name appearing (word-boundary, case-insensitive) in
    the title/description tags this news item with every ACTIVE national symbol for that make.
    No LLM, no fuzzy scoring — see module docstring."""
    text = f"{title} {description}".lower()
    matched = []
    for make in makes:
        if re.search(rf"\b{re.escape(make.lower())}\b", text):
            matched.append(make)
    return matched


async def _active_makes(conn: asyncpg.Connection) -> list[str]:
    rows = await conn.fetch("SELECT DISTINCT make FROM market_symbol WHERE is_active")
    return [r["make"] for r in rows]


async def _symbol_keys_for_makes(conn: asyncpg.Connection, makes: list[str]) -> list[str]:
    if not makes:
        return []
    rows = await conn.fetch(
        "SELECT symbol_key FROM market_symbol WHERE make = ANY($1::text[]) AND is_active",
        makes,
    )
    return [r["symbol_key"] for r in rows]


async def ingest(conn: asyncpg.Connection) -> dict[str, Any]:
    makes = await _active_makes(conn)
    counts: dict[str, int] = {}
    total_new = 0

    for source_name, feed_url in FEEDS:
        raw = _http_get(feed_url)
        if raw is None:
            counts[source_name] = -1  # fetch failed — declared, not silently zero
            continue
        items = _parse_feed(raw)
        counts[source_name] = len(items)

        for it in items:
            existing = await conn.fetchval("SELECT 1 FROM sector_news WHERE source_url = $1", it["link"])
            if existing:
                continue
            matched_makes = _match_symbol_keys(it["title"], it["description"], makes)
            symbol_keys = await _symbol_keys_for_makes(conn, matched_makes)
            await conn.execute(
                """
                INSERT INTO sector_news
                    (news_ulid, source_name, source_url, title, published_at, fetched_at,
                     content_hash, symbol_keys)
                VALUES ($1, $2, $3, $4, $5, now(), $6, $7)
                ON CONFLICT (source_url) DO NOTHING
                """,
                ulid(), source_name, it["link"], it["title"], it["pub_date"],
                _content_hash(it["title"], it["description"]), symbol_keys,
            )
            total_new += 1

    return {"feeds_fetched": counts, "items_ingested": total_new}


# ---------------------------------------------------------------------------
# V5 — periodic re-verification: re-fetch each item's OWN permalink (not the feed listing,
# which only ever shows the last N items — an older article can still be alive at its own URL
# long after it scrolls off the feed) and confirm the title still appears in the live page.
# ---------------------------------------------------------------------------

def verify_item(source_url: str, title: str) -> bool:
    raw = _http_get(source_url)
    if raw is None:
        return False
    try:
        html = raw.decode("utf-8", errors="ignore")
    except Exception:
        return False
    # Loose but real check: the exact title string appears verbatim in the live page. WordPress
    # renders the post title in <title>/<h1> untouched, so this is a meaningful liveness+match
    # test, not a rubber stamp.
    return title in html


async def verify_all(conn: asyncpg.Connection) -> dict[str, Any]:
    rows = await conn.fetch("SELECT news_ulid, source_url, title FROM sector_news")
    n_verified = 0
    n_failed = 0
    for r in rows:
        ok_match = verify_item(r["source_url"], r["title"])
        if ok_match:
            await conn.execute("UPDATE sector_news SET verified_at = now() WHERE news_ulid = $1", r["news_ulid"])
            n_verified += 1
        else:
            n_failed += 1
    return {"n_checked": len(rows), "n_verified": n_verified, "n_failed_match_or_fetch": n_failed}


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="V5 re-verify existing items only, skip ingestion")
    args = parser.parse_args()

    conn = await asyncpg.connect(DSN, command_timeout=120)
    try:
        t0 = time.monotonic()
        if args.verify:
            summary = await verify_all(conn)
            print(f"verify: {summary}")
        else:
            summary = await ingest(conn)
            print(f"ingest: {summary}")
        print(f"elapsed_seconds={time.monotonic() - t0:.2f}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())

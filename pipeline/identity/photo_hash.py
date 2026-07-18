"""pipeline/identity/photo_hash.py — 04-arbitrage F6 (identidad-captura, background).

Executes P08-S3's core (plans/P08.md): "Backfill de photo_hash sobre la flota viva"
— populates ``vehicle.photo_hash`` (0/2,670,828 measured at F6 start,
02-history-reports-f0.md). This is the SAME column ``scripts/
cross_platform_dedup_watermark.py`` reads for the pHash cross-platform-match arm
(cannot run with zero hashes) and 02-history-reports' ``link_lifetimes.py`` found
0 real edges for the same root cause (plans/cardeep-omni/PROGRESO.md Bloque 1).
This module does NOT touch either downstream engine — only supplies the signal
(04-arbitrage mandate: "no reconstruye el motor de 02/dedup, solo entrega la señal").
The CLIP-embedding / pgvector-HNSW half of P08-S3 is explicitly OUT of this
module's scope (a separate, much larger [L]-effort item; 04-arbitrage F6 asks only
for photo_hash).

Reuses, does NOT reinvent:
  - ``pipeline/delta_photo.py::hash_image_bytes`` — the SAME DCT pHash (PIL+numpy+
    scipy, imagehash-compatible geometry) the live PHOTO_CHANGE delta path (P08-S1/
    S2, pipeline/delta.py) already uses. One perceptual-hash implementation project-
    wide, not a second divergent one (00-MASTER.md C-1's spirit applied to hashing).
  - ``pipeline/engine/governor.py`` — the per-HOST token-bucket rate governor every
    other egress path in this codebase routes through (the AS24-ban-scar doctrine:
    "no acciones irreversibles" applies directly to hammering someone else's CDN).
    Unknown hosts inherit the conservative STEALTH profile (0.7 req/s) — this module
    does NOT register a faster override for the CDN hosts photo_url points at
    (cdn.wallapop.com, images.milanuncios.com, ...) without measured evidence,
    exactly as the governor's own doctrine requires ("never raise without evidence").
    Declared consequence: hashing the full ~1.96M-photo corpus at the conservative
    default is a multi-day background job, not a single-session batch — this module
    is idempotent and safely re-run/resumed in bounded batches (``--limit``) for
    exactly that reason.

Population, NOT re-derivation: ``vehicle`` is CARDEEP's mutable current-state
table (ingest already UPDATEs price/last_seen in place; this is not the
INSERT-only append-log doctrine governing vehicle_event or the arbitrage_* run
tables) — a plain ``UPDATE vehicle SET photo_hash = $1 WHERE vehicle_ulid = $2``
is the correct, idiomatic write here.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import time
from dataclasses import dataclass

import aiohttp
import asyncpg

from pipeline.delta_photo import hash_image_bytes
from pipeline.engine.governor import RateGovernor, governor, host_of

FETCH_TIMEOUT_SECONDS: float = 10.0
DEFAULT_CONCURRENCY: int = 20
DEFAULT_BATCH_LIMIT: int = 2000
USER_AGENT: str = "Mozilla/5.0 (compatible; CardeepPhotoHash/1.0; +https://cardeep.local)"


@dataclass(frozen=True)
class HashOutcome:
    vehicle_ulid: str
    photo_hash: str | None
    error: str | None


async def fetch_and_hash(
    session: aiohttp.ClientSession,
    vehicle_ulid: str,
    photo_url: str,
    rate_governor: RateGovernor,
) -> HashOutcome:
    """Governed fetch (per-host token bucket — never hammer one CDN host) +
    perceptual hash via the shared ``pipeline.delta_photo.hash_image_bytes``.
    """
    host = host_of(photo_url)
    await rate_governor.acquire(host)
    try:
        async with session.get(
            photo_url,
            timeout=aiohttp.ClientTimeout(total=FETCH_TIMEOUT_SECONDS),
            headers={"User-Agent": USER_AGENT},
        ) as resp:
            if resp.status != 200:
                return HashOutcome(vehicle_ulid, None, f"http_{resp.status}")
            data = await resp.read()
    except Exception as exc:  # noqa: BLE001 - a single bad URL must never abort the batch
        return HashOutcome(vehicle_ulid, None, f"fetch_error:{type(exc).__name__}")

    try:
        result = hash_image_bytes(data)
    except Exception as exc:  # noqa: BLE001 - corrupt/non-image payload, same policy
        return HashOutcome(vehicle_ulid, None, f"decode_error:{type(exc).__name__}")

    return HashOutcome(vehicle_ulid, result.phash, None)


async def run_batch(
    conn: asyncpg.Connection,
    *,
    limit: int = DEFAULT_BATCH_LIMIT,
    concurrency: int = DEFAULT_CONCURRENCY,
    make_filter: list[str] | None = None,
    rate_governor: RateGovernor | None = None,
) -> dict[str, object]:
    """Hash up to *limit* vehicles with ``photo_hash IS NULL AND photo_url IS NOT NULL``.

    Idempotent (re-running only ever touches rows still missing a hash) and
    safely interruptible (each successful hash is written immediately via its
    own UPDATE, not batched into one end-of-run transaction).

    *make_filter* scopes the scan to specific makes — lets tests run against a
    synthetic slice instead of the full live photo_url population (which would
    otherwise perform real network fetches against production CDN images from
    inside a test). *rate_governor* defaults to the process-wide governor
    (``pipeline.engine.governor.governor()``); tests inject a fresh, isolated
    instance so per-host bucket state never bleeds between test cases.
    """
    t0 = time.monotonic()
    rate_governor = rate_governor if rate_governor is not None else governor()

    if make_filter:
        rows = await conn.fetch(
            "SELECT vehicle_ulid, photo_url FROM vehicle "
            "WHERE photo_hash IS NULL AND photo_url IS NOT NULL AND make = ANY($2::text[]) "
            "ORDER BY vehicle_ulid LIMIT $1",
            limit, list(make_filter),
        )
    else:
        rows = await conn.fetch(
            "SELECT vehicle_ulid, photo_url FROM vehicle "
            "WHERE photo_hash IS NULL AND photo_url IS NOT NULL "
            "ORDER BY vehicle_ulid LIMIT $1",
            limit,
        )
    if not rows:
        return {"attempted": 0, "hashed": 0, "failed": 0, "errors": {}, "elapsed_seconds": 0.0}

    sem = asyncio.Semaphore(concurrency)

    async def _bounded(row) -> HashOutcome:
        async with sem:
            return await fetch_and_hash(session, row["vehicle_ulid"], row["photo_url"], rate_governor)

    async with aiohttp.ClientSession() as session:
        outcomes = await asyncio.gather(*(_bounded(r) for r in rows))

    hashed = 0
    error_counts: dict[str, int] = {}
    for outcome in outcomes:
        if outcome.photo_hash is not None:
            await conn.execute(
                "UPDATE vehicle SET photo_hash = $1 WHERE vehicle_ulid = $2 AND photo_hash IS NULL",
                outcome.photo_hash, outcome.vehicle_ulid,
            )
            hashed += 1
        else:
            key = (outcome.error or "unknown").split(":")[0]
            error_counts[key] = error_counts.get(key, 0) + 1

    return {
        "attempted": len(rows),
        "hashed": hashed,
        "failed": len(rows) - hashed,
        "errors": error_counts,
        "elapsed_seconds": round(time.monotonic() - t0, 2),
    }


async def _main() -> None:
    parser = argparse.ArgumentParser(description="04-arbitrage F6 photo_hash population batch")
    parser.add_argument("--limit", type=int, default=DEFAULT_BATCH_LIMIT)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    args = parser.parse_args()

    dsn = os.environ.get("CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep")
    conn = await asyncpg.connect(dsn)
    try:
        result = await run_batch(conn, limit=args.limit, concurrency=args.concurrency)
        print(
            f"photo_hash batch: attempted={result['attempted']} hashed={result['hashed']} "
            f"failed={result['failed']} elapsed={result['elapsed_seconds']}s errors={result['errors']}"
        )
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(_main())

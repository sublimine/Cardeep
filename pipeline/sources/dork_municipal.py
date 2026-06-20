"""VECTOR 3 — Systematic dorking across the 8.132 INE municipalities.

For every municipality, fire automotive search templates and harvest the *own
domains* of dealers that no directory indexes — the "garaje de montaña con web
propia" of the mandate. Stratified by municipality, it also measures fine-grained
geographic coverage (which municipalities yield long-tail domains).

Coste cero, sin cuenta:
- Primary engine: a self-hosted/public **SearXNG** JSON endpoint (set
  CARDEEP_SEARXNG_URL, e.g. http://127.0.0.1:8888). Meta-search, no quota.
- Free fallback with no account at all: **DuckDuckGo HTML** endpoint, parsed for
  result domains. Used automatically when SearXNG is absent/unreachable, so the
  vector produces results out of the box.

Municipalities come from the live `geo_municipality` table (the authoritative INE
list of 8.132). Recipe-first: CARDEEP_DORK_LIMIT caps how many municipalities are
swept (verify-then-delete); unset = full national sweep. Marketplace and generic
domains are filtered so only candidate dealer-owned domains become entities; the
INE geo-resolver + identity collapse handle dedup downstream.
"""
from __future__ import annotations

import os
import re
import threading
import time
import urllib.parse

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# Search templates per municipality -> (query, cardeep kind). The municipality name is
# interpolated; kind is the prior the template implies (refined later by harvest/identity).
_TEMPLATES = (
    ("concesionario coches {m}", "concesionario_oficial"),
    ("compraventa coches ocasion {m}", "compraventa"),
    ("venta coches segunda mano {m}", "compraventa"),
    ("taller mecanico coches {m}", "garaje"),
    ("desguace {m}", "desguace"),
)

# Domains that are NOT a dealer's own site: marketplaces, directories, socials, infra.
# A hit on any of these is noise for V3 (other vectors census the marketplaces directly).
_BLOCK_SUBSTR = (
    "google.", "bing.", "duckduckgo.", "facebook.", "instagram.", "twitter.", "x.com",
    "youtube.", "linkedin.", "tiktok.", "wikipedia.", "wikimedia.", "maps.", "waze.",
    "wallapop.", "milanuncios.", "coches.net", "coches.com", "autocasion.", "autoscout24.",
    "ocasionplus.", "flexicar.", "clicars.", "motor.es", "vibbo.", "yamovil.",
    "paginasamarillas.", "paginas-amarillas.", "qdq.com", "einforma.", "axesor.",
    "infoempresa.", "empresia.", "cylex", "tuugo.", "yelp.", "tripadvisor.",
    "amazon.", "ebay.", "mercadolibre.", "booking.", "idealista.", "fotocasa.",
    "elmundo.", "elpais.", "abc.es", "lavanguardia.", "20minutos.", "europapress.",
    "boe.es", "dgt.es", "gob.es", "ine.es", "play.google", "apps.apple",
)


def _registrable_domain(url: str) -> str | None:
    try:
        netloc = urllib.parse.urlsplit(url if "://" in url else "http://" + url).netloc.lower()
    except Exception:  # noqa: BLE001
        return None
    netloc = netloc.split("@")[-1].split(":")[0]
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc or None


def _is_dealer_domain(domain: str | None) -> bool:
    if not domain or "." not in domain:
        return False
    return not any(b in domain for b in _BLOCK_SUBSTR)


def _run_async(coro):
    """Run an async coroutine in a private thread+loop (discover() already owns a loop)."""
    box: dict = {}

    def worker():
        import asyncio

        box["v"] = asyncio.new_event_loop().run_until_complete(coro)

    t = threading.Thread(target=worker)
    t.start()
    t.join()
    return box.get("v")


async def _load_municipalities(limit: int | None, names: list[str] | None) -> list[dict]:
    import asyncpg

    conn = await asyncpg.connect(DSN)
    try:
        if names:
            # Targeted recipe-first sweep (CARDEEP_DORK_MUNI): verify on real cities, then delete.
            return [dict(r) for r in await conn.fetch(
                "SELECT code, name, province_code, lat, lon FROM geo_municipality "
                "WHERE name = ANY($1::text[]) ORDER BY name", names)]
        # Deterministic order by code so a sampled run is reproducible. Full run when limit is None.
        q = "SELECT code, name, province_code, lat, lon FROM geo_municipality ORDER BY code"
        if limit:
            q += f" LIMIT {int(limit)}"
        return [dict(r) for r in await conn.fetch(q)]
    finally:
        await conn.close()


def _search_searxng(base: str, query: str, ua: str) -> list[str]:
    import requests

    r = requests.get(
        base.rstrip("/") + "/search",
        params={"q": query, "format": "json", "language": "es-ES", "safesearch": "0"},
        headers={"User-Agent": ua}, timeout=25,
    )
    r.raise_for_status()
    data = r.json()
    return [it.get("url") for it in data.get("results", []) if it.get("url")]


def _search_ddg(query: str, ua: str) -> list[str]:
    """Free, account-less fallback: DuckDuckGo HTML results (redirect links decoded)."""
    import requests

    r = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": query, "kl": "es-es"},
        headers={"User-Agent": ua}, timeout=25,
    )
    r.raise_for_status()
    urls: list[str] = []
    for href in re.findall(r'href="(/l/\?[^"]+)"', r.text):
        m = re.search(r"[?&]uddg=([^&]+)", href)
        if m:
            urls.append(urllib.parse.unquote(m.group(1)))
    # Some responses already carry absolute result links.
    urls += re.findall(r'href="(https?://[^"]+)"', r.text)
    return urls


class DorkMunicipalAdapter(SourceAdapter):
    """V3 — municipal search dorking for dealer-owned domains (SearXNG -> DDG)."""

    source_key = "dork_municipal"
    _UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/146.0 Safari/537.36"

    def __init__(self) -> None:
        self._rows: list[DiscoveredEntity] | None = None
        self._isolated: str | None = None
        self._engine: str | None = None

    def _pick_engine(self) -> str | None:
        base = os.environ.get("CARDEEP_SEARXNG_URL")
        if base:
            try:
                import requests

                requests.get(base, headers={"User-Agent": self._UA}, timeout=10)
                self._engine = "searxng"
                return base
            except Exception:  # noqa: BLE001 — instance down: fall back to DDG
                pass
        # No SearXNG: probe DDG reachability once.
        try:
            import requests

            requests.get("https://duckduckgo.com/", headers={"User-Agent": self._UA}, timeout=10)
            self._engine = "ddg"
            return None
        except Exception as e:  # noqa: BLE001
            self._isolated = f"no search engine reachable (SearXNG unset, DDG failed: {e!r})"
            return None

    def _query(self, base: str | None, q: str) -> list[str]:
        try:
            if self._engine == "searxng" and base:
                return _search_searxng(base, q, self._UA)
            return _search_ddg(q, self._UA)
        except Exception:  # noqa: BLE001 — one query failing must not kill the sweep
            return []

    def _build(self) -> list[DiscoveredEntity]:
        limit = os.environ.get("CARDEEP_DORK_LIMIT")
        names_env = os.environ.get("CARDEEP_DORK_MUNI")
        names = [n.strip() for n in names_env.split(",") if n.strip()] if names_env else None
        munis = _run_async(_load_municipalities(int(limit) if limit else None, names)) or []
        base = self._pick_engine()
        if self._isolated:
            return []
        delay = float(os.environ.get("CARDEEP_DORK_DELAY", "1.0"))
        max_hits = int(os.environ.get("CARDEEP_DORK_MAX_HITS_PER_QUERY", "8"))
        seen: set[str] = set()
        out: list[DiscoveredEntity] = []
        for mu in munis:
            name = mu["name"]
            for tmpl, kind in _TEMPLATES:
                q = tmpl.format(m=name)
                for url in self._query(base, q)[:max_hits]:
                    dom = _registrable_domain(url)
                    if not _is_dealer_domain(dom) or dom in seen:
                        continue
                    seen.add(dom)
                    out.append(DiscoveredEntity(
                        kind=kind,
                        source_key=self.source_key,
                        source_ref=f"{mu['code']}:{dom}",
                        trade_name=dom.split(".")[0],
                        legal_name=dom,
                        province_name=mu["province_code"],
                        municipality_name=name,
                        website=f"https://{dom}",
                        extra={"vector": 3, "engine": self._engine, "query": q,
                               "municipality_code": mu["code"]},
                    ))
                if delay:
                    time.sleep(delay)
        return out

    def _load(self) -> list[DiscoveredEntity]:
        if self._rows is None:
            self._rows = self._build()
        return self._rows

    def declared_count(self) -> int | None:
        # Search has no count oracle; the gate compares fetched vs DB-ingested.
        return None

    def fetch(self) -> list[DiscoveredEntity]:
        rows = self._load()
        if self._isolated:
            print(f"[dork_municipal] ISOLATED — {self._isolated}")
            return []
        print(f"[dork_municipal] engine={self._engine} domains={len(rows)}")
        return rows

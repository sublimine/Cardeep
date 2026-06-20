"""Páginas Amarillas adapter — long-tail brick-and-mortar POS census (§1.4).

Promotes the standalone ``scripts/discover_paginas_amarillas.py`` crawler into a first-class
``SourceAdapter`` on the canonical discovery pipeline (geo-resolution + immutable cdp +
VAM count gate), instead of a loose script with no single source of truth.

Every PA listing is a real brick-and-mortar point of sale — exactly the "garaje perdido en
la montaña" that no marketplace indexes. Identity uses the canonical key: the listing's REAL
website (bare host -> ``domain:{host}``) when present — a strong cross-source dedup signal —
otherwise normalized name + municipality + street. So a listing that matches a dealer already
known by domain/name collapses on ``ON CONFLICT (cdp_code)``; a genuinely new long-tail POS
mints a fresh cdp = the directory's real contribution.

The crawl logic (paginated PA search per province × auto rubro, schema.org microdata parse)
is REUSED verbatim from the script module — this adapter is the pipeline-contract wrapper,
not a second crawler.

Run via the canonical pipeline (full ES) or the resumable runner for incremental persistence:
  python -m pipeline.discover paginas_amarillas
  python -m scripts.census_paginas_amarillas_batched           # per-province, resumable
"""
from __future__ import annotations

import logging

from pipeline.sources.base import DiscoveredEntity, SourceAdapter
from scripts.discover_paginas_amarillas import (  # reuse the verified crawler (DRY)
    BASE,
    PROV_SLUG,
    RUBROS,
    fetch as pa_fetch,
    parse_page,
)

log = logging.getLogger(__name__)

SOURCE_KEY = "paginas_amarillas"
_PAGE_CAP = 60  # hard safety cap per (rubro, province); no ES auto rubro exceeds this


def _province_of(rec: dict) -> str | None:
    """Province from the LISTING'S OWN postcode (authoritative), NOT the crawl slug.

    Two PA province slugs (ceuta, melilla) silently fall back to the NATIONAL result list
    instead of filtering, so trusting the crawl ``prov_code`` mis-stamps thousands of real
    businesses (e.g. a Madrid shop) onto Ceuta/Melilla. The listing's postcode is the ground
    truth: ``postcode[:2]`` is the INE province. Fall back to the crawl code only when the
    listing carries no usable postcode (then geo resolution still has the locality to try)."""
    pc = rec.get("postcode")
    if pc and len(str(pc)) >= 2 and str(pc)[:2].isdigit():
        cc = str(pc)[:2]
        if "01" <= cc <= "52":
            return cc
    # No usable postcode: fall back to the listing's OWN region name (addressRegion, e.g.
    # 'Madrid'), which discover._upsert resolves via geo.province_code(name) — still the
    # listing's ground truth, NOT the crawl slug. Only if even that is absent do we trust the
    # crawl prov_code (safe for the 50 provinces whose slug actually filters).
    region = rec.get("region")
    if region:
        return region
    return rec.get("prov_code")


def record_to_entity(rec: dict) -> DiscoveredEntity:
    """Map a parsed PA listing to a DiscoveredEntity on the canonical identity.

    province from the listing's OWN postcode (see ``_province_of`` — the crawl slug is NOT
    trusted because ceuta/melilla fall back to national results); municipality from the
    listing locality; the REAL website (PA's own host already stripped by the crawler) drives
    the domain-based canonical key. source_ref is the stable PA detail URL when present.
    """
    return DiscoveredEntity(
        kind=rec.get("kind", "compraventa"),
        source_key=SOURCE_KEY,
        source_ref=rec.get("detail") or f"{rec.get('name')}|{rec.get('locality')}",
        legal_name=rec.get("name"),
        trade_name=rec.get("name"),
        province_name=_province_of(rec),
        municipality_name=rec.get("locality"),
        address=rec.get("address"),
        postcode=rec.get("postcode"),
        phone=rec.get("phone"),
        website=rec.get("website"),
        extra={"source_group": "directory", "vector": 3,
               "activity": rec.get("activity"), "rubro": rec.get("rubro"),
               "detail": rec.get("detail")},
    )


def crawl_province(prov_code: str) -> list[dict]:
    """Crawl every auto rubro for one province, returning distinct listing records
    (deduped within the province by detail URL / name|locality)."""
    slug = PROV_SLUG[prov_code]
    seen: dict[str, dict] = {}
    for rubro, kdefault in RUBROS.items():
        page = 1
        while page <= _PAGE_CAP:
            t = pa_fetch(BASE.format(rubro=rubro, prov=slug, page=page))
            if t is None:
                break
            recs = parse_page(t, kdefault)
            if not recs:
                break
            for r in recs:
                key = r["detail"] or f"{r['name']}|{r['locality']}"
                if key not in seen:
                    r["prov_code"] = prov_code
                    r["rubro"] = rubro
                    seen[key] = r
            page += 1
    return list(seen.values())


class PaginasAmarillasAdapter(SourceAdapter):
    """Long-tail directory census across the auto rubros, all 52 provinces (or a subset)."""

    source_key = SOURCE_KEY

    def __init__(self, provinces: list[str] | None = None) -> None:
        self._provinces = provinces or list(PROV_SLUG.keys())
        self._records: list[dict] | None = None
        self.excluded_count = 0

    def _crawl(self) -> list[dict]:
        if self._records is None:
            out: list[dict] = []
            for pc in self._provinces:
                recs = crawl_province(pc)
                out.extend(recs)
                log.info("paginas_amarillas: province %s -> %d listings (cum %d)",
                         pc, len(recs), len(out))
            self._records = out
        return self._records

    def declared_count(self) -> int | None:
        return len(self._crawl())

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        for rec in self._crawl():
            if not rec.get("name"):
                self.excluded_count += 1
                continue
            out.append(record_to_entity(rec))
        return out

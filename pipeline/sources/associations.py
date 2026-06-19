"""Association census SourceAdapters — AEDRA / ACEVAS / AECS.

These three official Spanish sector associations are an ORTHOGONAL census front
(legal_census / source_group='association'): the same dealer attested by an
association AND by OSM AND by a platform is what makes capture-recapture work
(07-COVERAGE-STRATEGY §3). Until now they only lived in the standalone
`scripts/associations/upsert_associations.py` path, OUTSIDE the canonical
`pipeline.discover` VAM count-quorum gate. This module brings them INTO the
canonical discover pipeline so `python -m pipeline.discover aecs` runs them with
the same geo-resolution, immutable cdp_code minting, and declared==fetched==DB
quorum every other census source gets.

Provenance (local, committed): docs/research/associations/{aedra,acevas,aecs}_members.json
parsed by scripts/associations/parse_*.py from the raw association directories.

Pure-stdlib by design (no asyncpg / curl_cffi import) so the parse layer is unit
-testable offline without a DB or network. Field mapping mirrors
`upsert_associations.load_records()` verbatim to avoid a second source-of-truth.
"""
from __future__ import annotations

import json
from pathlib import Path

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

# Repo root = .../cardeep ; this file is at pipeline/sources/associations.py
_ROOT = Path(__file__).resolve().parents[2]
_RES = _ROOT / "docs" / "research" / "associations"


def _to_float(v) -> float | None:
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


class AedraAdapter(SourceAdapter):
    """AEDRA — Asociacion Espanola del Desguace y Reciclaje del Automovil -> desguace."""

    source_key = "aedra"
    _FILE = "aedra_members.json"

    def _records(self) -> list[dict]:
        return json.loads((_RES / self._FILE).read_text(encoding="utf-8"))

    def declared_count(self) -> int | None:
        return len(self._records())

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        for m in self._records():
            slug = m.get("slug")
            out.append(DiscoveredEntity(
                kind="desguace",
                source_key=self.source_key,
                source_ref=f"https://aedra.org/asociados/{slug}/" if slug else None,
                legal_name=m.get("name"),
                trade_name=m.get("name"),
                province_name=m.get("province_slug"),  # usually null -> geo from address
                address=m.get("address_raw"),
                phone=m.get("phone"),
                website=m.get("website"),
                extra={"source_group": "association", "kind_source": "legal_census"},
            ))
        return out


class AcevasAdapter(SourceAdapter):
    """ACEVAS — VW/Audi/Skoda dealer association -> concesionario_oficial."""

    source_key = "acevas"
    _FILE = "acevas_members.json"
    _REF = "https://www.acevas.com/concesionarios/"

    def _records(self) -> list[dict]:
        return json.loads((_RES / self._FILE).read_text(encoding="utf-8"))

    def declared_count(self) -> int | None:
        return len(self._records())

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        for m in self._records():
            out.append(DiscoveredEntity(
                kind="concesionario_oficial",
                source_key=self.source_key,
                source_ref=self._REF,
                legal_name=m.get("name"),
                trade_name=m.get("name"),
                province_name=m.get("province"),
                municipality_name=None,
                address=m.get("address_raw"),
                postcode=m.get("zip"),
                lat=_to_float(m.get("lat")),
                lon=_to_float(m.get("lon")),
                phone=m.get("phone"),
                email=m.get("email"),
                website=m.get("website"),
                extra={"source_group": "association", "kind_source": "legal_census",
                       "brands": m.get("brands")},
            ))
        return out


class AecsAdapter(SourceAdapter):
    """AECS — Stellantis dealer association -> concesionario_oficial."""

    source_key = "aecs"
    _FILE = "aecs_members.json"
    _REF = "https://asociacionstellantis.com/directorio-asociados/"

    def _records(self) -> list[dict]:
        return json.loads((_RES / self._FILE).read_text(encoding="utf-8"))

    def declared_count(self) -> int | None:
        return len(self._records())

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        for m in self._records():
            out.append(DiscoveredEntity(
                kind="concesionario_oficial",
                source_key=self.source_key,
                source_ref=self._REF,
                legal_name=m.get("name"),
                trade_name=m.get("name"),
                province_name=m.get("province"),
                website=m.get("website"),
                extra={"source_group": "association", "kind_source": "legal_census"},
            ))
        return out

"""SourceAdapter contract — normalizes any F1 census source to DiscoveredEntity."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DiscoveredEntity:
    kind: str                         # concesionario_oficial|compraventa|garaje|desguace|plataforma|cadena
    source_key: str                   # e.g. 'dgt_cat'
    source_ref: str | None = None     # stable id/url within the source
    legal_name: str | None = None
    trade_name: str | None = None
    cif: str | None = None
    cnae: str | None = None
    province_name: str | None = None  # raw, resolved to INE code at ingest
    municipality_name: str | None = None
    address: str | None = None
    postcode: str | None = None
    lat: float | None = None
    lon: float | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    is_tier1: bool = False
    extra: dict = field(default_factory=dict)


class SourceAdapter:
    """Base contract. Implementations yield DiscoveredEntity and declare the count
    the source itself asserts (for the VAM quorum gate)."""

    source_key: str = "base"

    def declared_count(self) -> int | None:
        """The count the source claims (e.g. its own counter/total). None if unknown."""
        return None

    def fetch(self) -> list[DiscoveredEntity]:
        raise NotImplementedError

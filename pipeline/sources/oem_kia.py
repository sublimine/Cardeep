"""Kia España official dealer network adapter.

Open unauthenticated JSON API (verified live 2026-06-12: 242 dealers).
Province is derived from the Spanish postcode (first 2 digits == INE province
code); municipality from the dealerResidence field, resolved at ingest.
"""
from __future__ import annotations

import json
import urllib.request

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

_URL = "https://www.kia.com/api/bin/dealer?locale=es-es&program=dealerLocatorSearch"
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/137 Safari/537.36"


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (trusted vendor host)
        return json.loads(r.read().decode("utf-8"))


def _find_dealers(obj) -> list[dict]:
    """Robustly locate the list of dealer dicts regardless of wrapper shape."""
    if isinstance(obj, list) and obj and isinstance(obj[0], dict) and "dealerName" in obj[0]:
        return obj
    if isinstance(obj, list):
        for v in obj:
            r = _find_dealers(v)
            if r:
                return r
    if isinstance(obj, dict):
        for v in obj.values():
            r = _find_dealers(v)
            if r:
                return r
    return []


def _clean(v) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def _to_float(v) -> float | None:
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return None


class KiaOemAdapter(SourceAdapter):
    source_key = "oem_kia"

    def __init__(self) -> None:
        self._dealers: list[dict] | None = None
        self.excluded_count = 0  # out-of-scope (non-Spain) dealers dropped

    def _load(self) -> list[dict]:
        if self._dealers is None:
            self._dealers = _find_dealers(_get(_URL))
        return self._dealers

    @staticmethod
    def _spain_province(d: dict) -> str | None:
        """Spanish INE province from postcode (01-52), or None if out of scope (e.g. Andorra)."""
        pc = _clean(d.get("dealerPostcode")) or ""
        p = pc[:2]
        return p if (len(pc) >= 2 and p.isdigit() and "01" <= p <= "52") else None

    def declared_count(self) -> int | None:
        # in-scope (Spain) count — the real denominator for the VAM gate
        return sum(1 for d in self._load() if self._spain_province(d))

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        self.excluded_count = 0
        for d in self._load():
            province = self._spain_province(d)
            if not province:
                self.excluded_count += 1  # out of scope (non-Spain), excluded transparently
                continue
            postcode = _clean(d.get("dealerPostcode"))
            phone = _clean(d.get("dealerPhone1")) or _clean(d.get("dealerPhone")) or _clean(d.get("dealerPhone2"))
            out.append(DiscoveredEntity(
                kind="concesionario_oficial",
                source_key=self.source_key,
                source_ref=_clean(d.get("dealerSeq")) or _clean(d.get("dealerExternalid")),
                legal_name=_clean(d.get("dealerName")),
                trade_name=_clean(d.get("dealerName")),
                province_name=province,           # 2-digit code; resolver accepts digit form
                municipality_name=_clean(d.get("dealerResidence")),
                address=_clean(d.get("dealerAddress")),
                postcode=postcode,
                lat=_to_float(d.get("dealerLatitude")),
                lon=_to_float(d.get("dealerLongitude")),
                phone=phone,
                email=_clean(d.get("dealerEmail")),
                website=None,                     # websiteUrl points to kia.com, not the dealer's own domain
                extra={"brand": "Kia", "service_type": _clean(d.get("dealerServiceType"))},
            ))
        return out

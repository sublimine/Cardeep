"""Skoda España official dealer network adapter.

Open unauthenticated JSON API (verified live 2026-06-12: 215 dealers).
Each record carries a nested ``address`` object; province is derived from the
Spanish postcode (first 2 digits == INE province code) and the municipality
from the ``city`` field (formatted "Municipality, Province"), resolved at
ingest. The payload exposes no phone, email or own-domain website fields, so
those stay None rather than being fabricated.
"""
from __future__ import annotations

import json
import urllib.request

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

_URL = "https://www.skoda.es/apps/retailers/api/572/es-ES/DealersV2/GetDealers"
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/137 Safari/537.36"


def _get(url: str) -> list:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (trusted vendor host)
        return json.loads(r.read().decode("utf-8"))


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


def _norm_zip(v) -> str | None:
    """Normalize a Spanish postcode to 5 digits.

    Several records drop the leading zero of provinces 01-09 (e.g. '8205' for
    Barcelona, '5002' for Ávila), so a 4-digit value is left-padded before use.
    """
    digits = "".join(ch for ch in str(v or "") if ch.isdigit())
    if len(digits) == 4:
        digits = "0" + digits
    return digits if len(digits) == 5 else None


def _municipality(city: str | None) -> str | None:
    """Extract the municipality from a 'Municipality, Province' city string."""
    s = _clean(city)
    if s is None:
        return None
    return _clean(s.rsplit(",", 1)[0])


class OemSkodaAdapter(SourceAdapter):
    source_key = "oem_skoda"

    def __init__(self) -> None:
        self._dealers: list[dict] | None = None
        self.excluded_count = 0  # out-of-scope (non-Spain) dealers dropped

    def _load(self) -> list[dict]:
        if self._dealers is None:
            data = _get(_URL)
            self._dealers = data if isinstance(data, list) else []
        return self._dealers

    @staticmethod
    def _spain_province(d: dict) -> str | None:
        """Spanish INE province from postcode (01-52), or None if out of scope."""
        pc = _norm_zip((d.get("address") or {}).get("zip"))
        if pc is None:
            return None
        p = pc[:2]
        return p if ("01" <= p <= "52") else None

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
            a = d.get("address") or {}
            out.append(DiscoveredEntity(
                kind="concesionario_oficial",
                source_key=self.source_key,
                source_ref=_clean(d.get("globalId")) or _clean(d.get("markerId")),
                legal_name=_clean(d.get("name")),
                trade_name=_clean(d.get("name")),
                province_name=province,           # 2-digit code; resolver accepts digit form
                municipality_name=_municipality(a.get("city")),
                address=_clean(a.get("street")),
                postcode=_norm_zip(a.get("zip")),
                lat=_to_float(a.get("latitude")),
                lon=_to_float(a.get("longitude")),
                phone=None,                       # no phone field in the payload
                email=None,                       # no email field in the payload
                website=None,                     # no dealer-own website in the payload
                extra={"brand": "Skoda", "parent_code": _clean(d.get("parentCode"))},
            ))
        return out

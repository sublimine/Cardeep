"""BYD España official dealer network adapter.

Open unauthenticated JSON API (verified live 2026-06-12: 106 sales dealers, all ES).
Province is derived from the Spanish zipCode (first 2 digits == INE province code);
municipality is parsed from the trailing component of the address (which is always
formatted as '..., <municipality>, <province>, Spain'), resolved at ingest.
"""
from __future__ import annotations

import json
import urllib.request

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

_URL = "https://eu-site-api.byd.com/byd-api/eu/dealer/getFindDealer?country=ES&type=sales"
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


def _municipality(address: str | None) -> str | None:
    """Parse the municipality from a BYD address.

    The address is consistently '<street...>, <municipality>, <province>, Spain',
    so the municipality is the third-from-last comma component.
    """
    if not address:
        return None
    parts = [p.strip() for p in address.split(",") if p.strip()]
    if len(parts) >= 3 and parts[-1].lower() == "spain":
        return parts[-3] or None
    return None


class OemBydAdapter(SourceAdapter):
    source_key = "oem_byd"

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
        """Spanish INE province from zipCode (01-52), or None if out of scope."""
        pc = _clean(d.get("zipCode")) or ""
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
            address = _clean(d.get("address"))
            out.append(DiscoveredEntity(
                kind="concesionario_oficial",
                source_key=self.source_key,
                source_ref=_clean(d.get("organizationCode")),
                legal_name=_clean(d.get("organizationName")),
                trade_name=_clean(d.get("organizationName")),
                province_name=province,           # 2-digit code; resolver accepts digit form
                municipality_name=_municipality(address),
                address=address,
                postcode=_clean(d.get("zipCode")),
                lat=_to_float(d.get("lat")),
                lon=_to_float(d.get("lng")),
                phone=_clean(d.get("phoneNumber")),
                email=_clean(d.get("mail")),
                website=_clean(d.get("website")),
                extra={"brand": "BYD", "feature": _clean(d.get("feature")),
                       "status": _clean(d.get("statusTrans"))},
            ))
        return out

"""Hyundai España official dealer network adapter.

Hyundai España runs on the Hyundai WWN AEM platform. The dealer-locator
component posts to a JSON servlet (selector ``car-models``) with an empty body
to retrieve the full outlet list; the response carries a flat ``dealers`` array.
Verified live 2026-06-12: 175 Spanish dealers (POST, empty JSON body).

The vendor JSON ships postcodes with the leading zero stripped (e.g. "8720"
for Barcelona, "6200" for Badajoz). Postcodes are zero-padded to 5 digits before
deriving the Spanish province (first 2 digits == INE province code, 01-52);
municipality comes from the ``city`` field, resolved at ingest. After padding,
all 175 outlets fall inside the Spanish INE range and ``country`` is "Spain".
"""
from __future__ import annotations

import json
import urllib.request

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

_URL = ("https://www.hyundai.com/es/es/concesionarios/jcr:content/root/"
        "content_section_cont/dealer_locator.car-models.json")
_REFERER = "https://www.hyundai.com/es/es/concesionarios.html"
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/137 Safari/537.36"


def _post(url: str) -> dict:
    req = urllib.request.Request(
        url,
        data=b"{}",  # the locator servlet returns the full list for an empty filter
        method="POST",
        headers={
            "User-Agent": _UA,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Referer": _REFERER,
        },
    )
    with urllib.request.urlopen(req, timeout=40) as r:  # noqa: S310 (trusted vendor host)
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


def _norm_postcode(d: dict) -> str | None:
    """Spanish 5-digit postcode; vendor strips the leading zero, so zero-pad it."""
    pc = _clean(d.get("postalCode"))
    if pc and pc.isdigit() and len(pc) in (4, 5):
        return pc.zfill(5)
    return pc


class HyundaiOemAdapter(SourceAdapter):
    source_key = "oem_hyundai"

    def __init__(self) -> None:
        self._dealers: list[dict] | None = None
        self.excluded_count = 0  # out-of-scope (non-Spain) dealers dropped

    def _load(self) -> list[dict]:
        if self._dealers is None:
            payload = _post(_URL)
            self._dealers = payload.get("dealers") or []
        return self._dealers

    @staticmethod
    def _spain_province(d: dict) -> str | None:
        """Spanish INE province from postcode (01-52), or None if out of scope."""
        pc = _norm_postcode(d) or ""
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
            address = " ".join(
                p for p in (_clean(d.get("addressLine1")), _clean(d.get("addressLine2"))) if p
            ) or None
            phone = _clean(d.get("phone")) or _clean(d.get("salesTelephone")) or _clean(d.get("serviceTelephone"))
            out.append(DiscoveredEntity(
                kind="concesionario_oficial",
                source_key=self.source_key,
                source_ref=_clean(d.get("dealerId")) or _clean(d.get("id")),
                legal_name=_clean(d.get("fullDealerName")),
                trade_name=_clean(d.get("shortOutletName")) or _clean(d.get("fullDealerName")),
                province_name=province,           # 2-digit code; resolver accepts digit form
                municipality_name=_clean(d.get("city")),
                address=address,
                postcode=_norm_postcode(d),
                lat=_to_float(d.get("lat")),
                lon=_to_float(d.get("lng")),
                phone=phone,
                email=_clean(d.get("email")) or _clean(d.get("salesEmail")) or _clean(d.get("serviceEmail")),
                website=_clean(d.get("webSite")),
                extra={"brand": "Hyundai",
                       "outlet_type": _clean(d.get("outletType")),
                       "province_label": _clean(d.get("province"))},
            ))
        return out

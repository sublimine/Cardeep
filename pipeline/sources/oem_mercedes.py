"""Mercedes-Benz España official dealer network adapter.

The dealer-locator front-end (mercedes-benz.es/passengercars/mercedes-benz-cars/
dealer-locator.html) calls the OneWeb DMS-plus API with an apikey embedded in the
page bundle and sent as the `x-apikey` header. The `0001_DLp-ES` search profile
restricts the response to outletId/legalName/coordinates by default, but the API
accepts an `includeFields` whitelist that exposes the full address (zipCode, city,
street, region). We request those fields explicitly.

Province is derived from the Spanish postcode (first 2 digits == INE province
code); municipality comes from address.city, resolved at ingest. The API tags
every outlet as country "ES", but a few are Andorra (zipCode AD*) or Gibraltar
(zipCode GX*); the 01-52 postcode gate excludes them transparently.

Verified live 2026-06-12: page.totalElements = 245, 242 in-scope Spain dealers.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

# apikey extracted from the dealer-locator front-end bundle (sent as x-apikey).
_APIKEY = "ce7d9916-6a3d-407a-b086-fea4cbae05f6"
# Whitelist that unlocks the full address behind the 0001_DLp-ES search profile.
_FIELDS = (
    "legalName,outletId,"
    "address.coordinates.latitude,address.coordinates.longitude,"
    "address.zipCode,address.city,address.street,address.country,"
    "address.region.province,address.region.state"
)
_BASE = "https://api.oneweb.mercedes-benz.com/dms-plus/v3/api/dealers/market"
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/137 Safari/537.36"


def _url() -> str:
    q = urllib.parse.urlencode({
        "marketCode": "ES",
        "searchProfile": "0001_DLp-ES",
        "page": "1",
        "size": "250",
        "includeFields": _FIELDS,
    })
    return f"{_BASE}?{q}"


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={
        "User-Agent": _UA,
        "Accept": "application/json",
        "x-apikey": _APIKEY,
        "dlcorigin": "FE",
    })
    with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310 (trusted vendor host)
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


class OemMercedesAdapter(SourceAdapter):
    source_key = "oem_mercedes"

    def __init__(self) -> None:
        self._data: dict | None = None
        self.excluded_count = 0  # out-of-scope (Andorra/Gibraltar) dealers dropped

    def _load(self) -> dict:
        if self._data is None:
            self._data = _get(_url())
        return self._data

    def _dealers(self) -> list[dict]:
        d = self._load().get("dealers")
        return d if isinstance(d, list) else []

    @staticmethod
    def _spain_province(d: dict) -> str | None:
        """Spanish INE province from postcode (01-52), or None if out of scope.

        The API tags Andorra (AD*) and Gibraltar (GX*) outlets as country "ES";
        the digit-range gate is what actually excludes them.
        """
        pc = _clean(d.get("address", {}).get("zipCode")) or ""
        p = pc[:2]
        return p if (len(pc) >= 2 and p.isdigit() and "01" <= p <= "52") else None

    def declared_count(self) -> int | None:
        # in-scope (Spain) count — the real denominator for the VAM gate
        return sum(1 for d in self._dealers() if self._spain_province(d))

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        self.excluded_count = 0
        for d in self._dealers():
            province = self._spain_province(d)
            if not province:
                self.excluded_count += 1  # out of scope (Andorra/Gibraltar), excluded transparently
                continue
            addr = d.get("address", {})
            coords = addr.get("coordinates", {})
            name = _clean(d.get("legalName"))
            out.append(DiscoveredEntity(
                kind="concesionario_oficial",
                source_key=self.source_key,
                source_ref=_clean(d.get("outletId")),
                legal_name=name,
                trade_name=name,
                province_name=province,            # 2-digit code; resolver accepts digit form
                municipality_name=_clean(addr.get("city")),
                address=_clean(addr.get("street")),
                postcode=_clean(addr.get("zipCode")),
                lat=_to_float(coords.get("latitude")),
                lon=_to_float(coords.get("longitude")),
                phone=None,                        # not exposed by the dealer-locator profile
                email=None,                        # not exposed by the dealer-locator profile
                website=None,                      # not exposed by the dealer-locator profile
                extra={"brand": "Mercedes-Benz",
                       "region_province": _clean(addr.get("region", {}).get("province"))},
            ))
        return out

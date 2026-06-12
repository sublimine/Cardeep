"""Dacia España official dealer network adapter.

Public HTML directory (no auth). Each listing page embeds one schema.org
AutomotiveBusiness JSON-LD block per dealer (name, telephone, postal address,
geo). The directory is paginated via ?page=N; pages are drained until one
returns no business blocks (verified live 2026-06-12: pages 1-17 populated,
page 18 empty -> 483 unique dealers, of which 482 are in Spain).

Province is derived from the Spanish postcode (first 2 digits == INE province
code, 01-52); municipality from address.addressLocality. Entries whose postcode
is out of scope (e.g. Andorra, AD500 -- tagged addressCountry "ES" upstream but
not Spanish) are excluded transparently, mirroring the OEM Kia adapter.
"""
from __future__ import annotations

import json
import re
import urllib.request

from pipeline.sources.base import DiscoveredEntity, SourceAdapter

_BASE = "https://concesionario.dacia.es/?page={page}"
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/137 Safari/537.36"
_MAX_PAGES = 100  # hard stop; real pagination ends ~17, drained until empty

_LD_JSON = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S
)


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (trusted vendor host)
        return r.read().decode("utf-8", "replace")


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


def _page_businesses(html: str) -> list[dict]:
    """Extract every schema.org AutomotiveBusiness block from a listing page."""
    out: list[dict] = []
    for block in _LD_JSON.findall(html):
        try:
            d = json.loads(block)
        except (ValueError, TypeError):
            continue
        if isinstance(d, dict) and d.get("@type") == "AutomotiveBusiness":
            out.append(d)
    return out


class OemDaciaAdapter(SourceAdapter):
    source_key = "oem_dacia"

    def __init__(self) -> None:
        self._dealers: list[dict] | None = None
        self.excluded_count = 0  # out-of-scope (non-Spain) dealers dropped

    def _load(self) -> list[dict]:
        """Drain every directory page, deduplicating on name+postcode+street."""
        if self._dealers is None:
            seen: dict[tuple, dict] = {}
            prev_sig: tuple | None = None
            for page in range(1, _MAX_PAGES + 1):
                businesses = _page_businesses(_get(_BASE.format(page=page)))
                if not businesses:
                    break
                sig = tuple(sorted(
                    (b.get("name"), (b.get("address") or {}).get("postalCode"))
                    for b in businesses
                ))
                if sig == prev_sig:  # pagination wrapped / repeated -> done
                    break
                prev_sig = sig
                for b in businesses:
                    addr = b.get("address") or {}
                    key = (
                        _clean(b.get("name")),
                        _clean(addr.get("postalCode")),
                        _clean(addr.get("streetAddress")),
                    )
                    seen[key] = b
            self._dealers = list(seen.values())
        return self._dealers

    @staticmethod
    def _spain_province(d: dict) -> str | None:
        """Spanish INE province from postcode (01-52), or None if out of scope (e.g. Andorra)."""
        pc = _clean((d.get("address") or {}).get("postalCode")) or ""
        p = pc[:2]
        return p if (len(pc) >= 2 and p.isdigit() and "01" <= p <= "52") else None

    def declared_count(self) -> int | None:
        # in-scope (Spain) count -- the real denominator for the VAM gate
        return sum(1 for d in self._load() if self._spain_province(d))

    def fetch(self) -> list[DiscoveredEntity]:
        out: list[DiscoveredEntity] = []
        self.excluded_count = 0
        for d in self._load():
            province = self._spain_province(d)
            if not province:
                self.excluded_count += 1  # out of scope (non-Spain), excluded transparently
                continue
            addr = d.get("address") or {}
            geo = d.get("geo") or {}
            name = _clean(d.get("name"))
            postcode = _clean(addr.get("postalCode"))
            # @id is "dealer.undefined" upstream; build a stable ref from name+postcode
            source_ref = f"{name}|{postcode}" if name else None
            out.append(DiscoveredEntity(
                kind="concesionario_oficial",
                source_key=self.source_key,
                source_ref=source_ref,
                legal_name=name,
                trade_name=name,
                province_name=province,           # 2-digit code; resolver accepts digit form
                municipality_name=_clean(addr.get("addressLocality")),
                address=_clean(addr.get("streetAddress")),
                postcode=postcode,
                lat=_to_float(geo.get("latitude")),
                lon=_to_float(geo.get("longitude")),
                phone=_clean(d.get("telephone")),
                email=None,                       # not exposed in the directory JSON-LD
                website=None,                     # directory hosts dealer pages, not own domains
                extra={"brand": "Dacia"},
            ))
        return out

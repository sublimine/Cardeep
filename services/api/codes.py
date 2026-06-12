"""Immutable Cardeep entity code (cdp_code) generator.

Deterministic over the entity's canonical identity, so re-discovering the same
entity through a different source never mints a second code.

Canonical key priority: domain > CIF > normalized(name|municipality_code).
Format: CDP-ES-{province2}-{8 x Crockford-base32 of sha256(key)}.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # no I, L, O, U


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "", text.lower())
    return text


def _base32(digest: bytes, length: int = 8) -> str:
    num = int.from_bytes(digest, "big")
    out = []
    for _ in range(length):
        out.append(_CROCKFORD[num & 0x1F])
        num >>= 5
    return "".join(reversed(out))


def canonical_key(*, domain: str | None = None, cif: str | None = None,
                  name: str | None = None, municipality_code: str | None = None) -> str:
    if domain:
        d = domain.lower().strip()
        d = re.sub(r"^https?://", "", d)
        d = re.sub(r"^www\.", "", d).split("/")[0]
        return f"domain:{d}"
    if cif:
        return f"cif:{cif.upper().strip()}"
    if name and municipality_code:
        return f"name:{_normalize(name)}|{municipality_code}"
    raise ValueError("need domain, cif, or (name + municipality_code) to mint a cdp_code")


def cdp_code(*, province_code: str, domain: str | None = None, cif: str | None = None,
             name: str | None = None, municipality_code: str | None = None) -> str:
    key = canonical_key(domain=domain, cif=cif, name=name, municipality_code=municipality_code)
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{province_code}-{_base32(digest)}"

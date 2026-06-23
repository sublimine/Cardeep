"""Immutable Cardeep entity code (cdp_code) generator.

Deterministic over the entity's canonical identity, so re-discovering the same
entity through a different source never mints a second code.

Canonical key priority: particular(platform:sellerId) > domain > CIF >
normalized(name|municipality_code).
Format: CDP-{country2}-{province2}-{8 x Crockford-base32 of sha256(key)}.

Country-parametrization: every public coder accepts an optional ``country_code``
defaulting to :data:`DEFAULT_COUNTRY` (``"ES"``), so every existing call site and
every ES output is byte-identical. ``country_code`` ONLY enters the human-facing
prefix via :func:`mint_code`; it is deliberately kept OUT of :func:`canonical_key`'s
returned pre-image (the immutable dedup key), so threading it cannot re-key any
existing entity.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata

# The sole default tenant. Threaded through every coder so ES output never changes.
DEFAULT_COUNTRY = "ES"

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


def mint_code(*, province_code: str, digest: bytes,
              country_code: str = DEFAULT_COUNTRY) -> str:
    """Assemble the final ``cdp_code`` from its parts — the ONE home of the prefix literal.

    Every coder (this module plus the ~30 ``pipeline/platform`` mints) routes through here,
    so ``CDP-{country}-`` exists in exactly one place. With ``country_code`` defaulting to
    ``"ES"`` and ``_base32(digest)`` unchanged, the output is byte-identical to the historical
    ``f"CDP-ES-{province_code}-{_base32(digest)}"`` — verified by the golden tests.
    """
    return f"CDP-{country_code}-{province_code}-{_base32(digest)}"


def canonical_key(*, domain: str | None = None, cif: str | None = None,
                  name: str | None = None, municipality_code: str | None = None,
                  province_code: str | None = None, address: str | None = None,
                  particular_platform: str | None = None,
                  particular_seller_id: str | None = None,
                  country_code: str = DEFAULT_COUNTRY) -> str:
    # ``country_code`` is accepted for signature symmetry with the other coders, but is
    # DELIBERATELY NOT used here: this function returns the immutable dedup pre-image, and
    # mixing the country into it would change every sha256 hash and re-key all entities.
    # The country lives only in the human-facing prefix minted by mint_code().
    # A private individual seller. Identity is the platform's OWN stable seller id where
    # the source exposes one (milanuncios authorId, wallapop user_id) -> one entity per
    # real human, so a particular with N cars is a single multi-car seller. Where the
    # source anonymises privates (coches.net shares contractId='1', only a first name),
    # the caller passes the province code as the seller id -> one 'Particulares' bucket
    # per province. We never fabricate per-seller identity the source withholds.
    if particular_platform and particular_seller_id:
        plat = re.sub(r"[^a-z0-9]+", "", particular_platform.lower().strip())
        sid = str(particular_seller_id).strip()
        return f"particular:{plat}:{sid}"
    if domain:
        d = domain.lower().strip()
        d = re.sub(r"^https?://", "", d)
        d = re.sub(r"^www\.", "", d)
        d = d.split("?")[0].split("#")[0].rstrip("/")
        host, _, path = d.partition("/")
        # A BARE host (the dealer's own domain) is a strong cross-source dedup identity.
        # A path-bearing URL is almost always an OEM/aggregator portal page
        # ("hyundai.es/concesionarios/<slug>") shared by many branches — NOT an identity;
        # fall through to name+address so distinct physical branches stay distinct.
        if host and not path:
            return f"domain:{host}"
    if cif:
        return f"cif:{cif.upper().strip()}"
    # A physical point of sale without domain/cif is identified by name + location +
    # address (two sites of the same company in one town are distinct POS, not dupes).
    addr = f"|{_normalize(address)}" if address else ""
    if name and municipality_code:
        return f"name:{_normalize(name)}|{municipality_code}{addr}"
    if name and province_code:
        return f"name:{_normalize(name)}|p{province_code}{addr}"
    raise ValueError("need domain, cif, (name + municipality_code) or (name + province_code)")


def cdp_pair(*, province_code: str, domain: str | None = None, cif: str | None = None,
             name: str | None = None, municipality_code: str | None = None,
             address: str | None = None, particular_platform: str | None = None,
             particular_seller_id: str | None = None,
             country_code: str = DEFAULT_COUNTRY) -> tuple[str, str]:
    """Return ``(canonical_key, cdp_code)`` — the dedup pre-image key AND its hashed code.

    cdp_code() delegates here so callers that must persist ``entity.canonical_key`` (the audit
    pre-image: ``particular:wallapop:{id}`` / ``domain:ford.es`` / ``name:{norm}|{muni}``) get the key
    without re-deriving it (audit P2 B-canonical-key). The returned code is byte-identical to the
    historical cdp_code() output — verified by the golden test.
    """
    key = canonical_key(domain=domain, cif=cif, name=name, municipality_code=municipality_code,
                        province_code=province_code, address=address,
                        particular_platform=particular_platform,
                        particular_seller_id=particular_seller_id,
                        country_code=country_code)
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return key, mint_code(province_code=province_code, digest=digest, country_code=country_code)


def cdp_code(*, province_code: str, domain: str | None = None, cif: str | None = None,
             name: str | None = None, municipality_code: str | None = None,
             address: str | None = None, particular_platform: str | None = None,
             particular_seller_id: str | None = None,
             country_code: str = DEFAULT_COUNTRY) -> str:
    return cdp_pair(province_code=province_code, domain=domain, cif=cif, name=name,
                    municipality_code=municipality_code, address=address,
                    particular_platform=particular_platform,
                    particular_seller_id=particular_seller_id,
                    country_code=country_code)[1]

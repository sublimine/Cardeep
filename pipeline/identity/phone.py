"""Country-aware phone normalization dispatch (P2 country-#2 readiness).

``phone_es`` is the ES authority: it validates the Spanish numbering plan (national = 9 digits leading
6/7/8/9, strips +34/0034) and returns a bare 9-digit key — the immutable ES cross-source hard key. It
rejects every non-ES number (a +49 German line → ``None``), so a SECOND tenant loses the phone hard
key entirely (``resolve_entities`` / ``cross_source_dedup`` use it cross-source).

This module is the country-aware seam over it:
  * ``country_code == 'ES'`` (the default) → ``phone_es``, BYTE-IDENTICAL (the ES key never changes a
    bit; the golden ``test_phone_es`` / ``test_cross_source_phone`` pin it).
  * any other country → a generic E.164 key ``'+<calling_code><national digits>'`` so the phone is a
    usable cross-source key again AND two calling codes can NEVER collide (``+33…`` ≠ ``+34…``).
    ``cross_source_dedup`` already buckets by ``(key, muni, country)``, so this only ADDS phone edges
    WITHIN a country — it can never merge across borders.

DELIBERATE SCOPE — engineering vs OPS. This is the country-aware DISPATCH (the engineering seam). The
real per-country numbering PLAN — national trunk-prefix rules, exact national lengths, leading-digit
validation per region — is operational data and is NOT encoded here. The generic path canonicalizes to
a STABLE, collision-proof E.164 key; it does NOT validate national shape (that is ``phone_es``'s job
for ES, and a per-country plan or the battle-tested ``phonenumbers`` library for the rest — see
docs/generic-engine-bible/NEXT-LEVEL.md). ``phonenumbers`` is intentionally NOT a dependency (the
module ethos is the €0 pure-stdlib replacement for that install gate); a country is onboarded for
phone keys by adding its ITU calling code below (or by wiring ``phonenumbers`` behind this surface).

Public surface (mirrors phone_es, plus the ``country_code`` dimension):
  phone_match_key(raw, country_code='ES') -> the cross-source index key, or None.
  normalize_e164(raw, country_code='ES')  -> canonical E.164 '+<cc><national>', or None.
"""
from __future__ import annotations

from pipeline.identity.phone_es import normalize_es_phone as _es_e164
from pipeline.identity.phone_es import phone_match_key as _es_match_key
from pipeline.paths import DEFAULT_COUNTRY  # 'ES'

# ITU-T E.164 country calling codes for the generic dispatch. This is NOT a numbering plan (no national
# lengths / leading-digit rules) — only the prefix needed to form a collision-proof E.164 key for a
# national-format number. OPS owns the real per-country validation; extend this map (or adopt
# ``phonenumbers``) to onboard a country's phone keys.
_CALLING_CODE: dict[str, str] = {
    "ES": "34", "PT": "351", "FR": "33", "IT": "39", "DE": "49", "GB": "44",
    "IE": "353", "NL": "31", "BE": "32", "LU": "352", "AT": "43", "CH": "41",
    "PL": "48", "MX": "52", "AR": "54", "BR": "55", "US": "1", "JP": "81",
}


def _generic_e164(raw: str | None, country_code: str) -> str | None:
    """A stable, collision-proof E.164 key for a non-ES number, or None.

    International input (leading ``+`` or ``00<cc>``) is canonicalized to ``'+<digits>'`` directly. A
    national-format input is prefixed with the country's ITU calling code. This deliberately does NOT
    strip national trunk prefixes or validate length — it produces a DETERMINISTIC key, not a validated
    number (per-country validation is OPS / ``phonenumbers``). An unknown country in national format
    yields None (no reliable E.164 prefix until OPS onboards it)."""
    if not raw or not isinstance(raw, str):
        return None
    s = raw.strip()
    digits = "".join(c for c in s if c.isdigit())
    if not digits:
        return None
    if s.startswith("+"):
        return "+" + digits
    if digits.startswith("00"):
        return "+" + digits[2:]
    cc = _CALLING_CODE.get(country_code)
    if cc is None:
        return None
    if not digits.startswith(cc):
        digits = cc + digits
    return "+" + digits


def phone_match_key(raw: str | None, country_code: str = DEFAULT_COUNTRY) -> str | None:
    """Cross-source phone hard key for ``raw`` in ``country_code``.

    ES (the default) → ``phone_es`` (byte-identical 9-digit national). Non-ES → a generic E.164 key.
    """
    if country_code == DEFAULT_COUNTRY:
        return _es_match_key(raw)
    return _generic_e164(raw, country_code)


def normalize_e164(raw: str | None, country_code: str = DEFAULT_COUNTRY) -> str | None:
    """Canonical E.164 for ``raw``. ES → ``phone_es`` ``'+34…'`` (byte-identical). Non-ES → generic."""
    if country_code == DEFAULT_COUNTRY:
        return _es_e164(raw)
    return _generic_e164(raw, country_code)

"""Spanish phone-number normalization (E.164) — pure stdlib, zero dependencies.

P06 CAPA-0 (deterministic-first hard keys): a phone is only an identity-grade cross-source hard key
when it is a real Spanish number. The Spanish numbering plan fixes the national number at 9 digits
beginning with 6 or 7 (mobile) or 8 or 9 (geographic / landline / special); there is no trunk 0. The
two legacy ``_normalize_phone`` copies (resolve_entities, cross_source_dedup) just take the last 9
digits of whatever they are handed, so an extension or a malformed length yields a key that can
FALSE-merge two distinct dealers. This authority validates the shape, so the produced key is either a
genuine Spanish national number or None — never a fragile substring.

The €0 replacement for python-stdnum/phonenumbers (an install gate): the rule is short and fully
deterministic, so it is verified exhaustively offline (see tests/test_phone_es).

Public surface:
  phone_match_key(raw)   -> the 9-digit national number iff valid, else None (cross-source index key).
  normalize_es_phone(raw)-> canonical E.164 "+34XXXXXXXXX" iff valid, else None.
"""
from __future__ import annotations

_VALID_LEADING = frozenset("6789")  # mobile (6/7) + geographic/landline/special (8/9)


def _national(raw: str | None) -> str | None:
    """Reduce any well-formed Spanish phone rendering to its 9-digit national number, else None."""
    if not raw or not isinstance(raw, str):
        return None
    digits = "".join(c for c in raw if c.isdigit())
    if not digits:
        return None
    # Strip the international prefix (+34 / 0034) to reach the national part. A national number is
    # never 11 digits and never starts with 34, so these strips can't corrupt a bare national number.
    if digits.startswith("0034"):
        digits = digits[4:]
    elif len(digits) == 11 and digits.startswith("34"):
        digits = digits[2:]
    if len(digits) == 9 and digits[0] in _VALID_LEADING:
        return digits
    return None


def phone_match_key(raw: str | None) -> str | None:
    """The 9-digit national number iff ``raw`` is a valid Spanish phone, else None."""
    return _national(raw)


def normalize_es_phone(raw: str | None) -> str | None:
    """Canonical E.164 (``+34XXXXXXXXX``) iff ``raw`` is a valid Spanish phone, else None."""
    national = _national(raw)
    return f"+34{national}" if national else None

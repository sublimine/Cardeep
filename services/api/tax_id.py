"""Spanish tax-ID (NIF / NIE / CIF) checksum validation — pure stdlib, zero dependencies.

P06 CAPA-0 (deterministic-first hard keys): a tax ID is only an identity-grade hard key if it passes
its OFFICIAL checksum. ``canonical_key`` (codes.py) keys an entity off a bare ``cif`` with no
validation, so a corrupt CIF mints identity off garbage and risks inflating the dealer denominator.
This is the €0 replacement for python-stdnum (es.nif/es.cif, an install gate): the BOE algorithms are
short and fully deterministic, so they are verified exhaustively offline (see tests/test_spanish_tax_id).

Public surface:
  is_valid_nif / is_valid_nie / is_valid_cif — per-family checksum validation.
  is_valid_tax_id — accepts any of the three families.
  canonical_tax_id — normalize (strip separators, uppercase) and return the ID iff valid, else None
                     (the "certified hard key", ready for the resolver; None means "do not key off this").
"""
from __future__ import annotations

import re

# DNI/NIF control letter, indexed by (8-digit number) % 23. Excludes I, O, U, Ñ by construction.
_NIF_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"
# NIE leading letter -> numeric prefix substituted before the mod-23 step.
_NIE_PREFIX = {"X": "0", "Y": "1", "Z": "2"}
# CIF control may be a letter (J,A..I indexed by the check digit) for certain org types.
_CIF_CONTROL_LETTERS = "JABCDEFGHI"
# Valid CIF organisation-type leading letters (BOE). X/Y/Z are NIE, never CIF.
_CIF_ORG_DIGIT = frozenset("ABEH")   # control MUST be the digit
_CIF_ORG_LETTER = frozenset("KPQS")  # control MUST be the letter
_CIF_ORG_EITHER = frozenset("CDFGJLMNRUVW")  # control may be digit OR letter
_CIF_ORG_ALL = _CIF_ORG_DIGIT | _CIF_ORG_LETTER | _CIF_ORG_EITHER


def _clean(raw: str | None) -> str:
    """Uppercase and strip everything that is not A-Z/0-9 (spaces, dots, hyphens)."""
    if not raw:
        return ""
    return re.sub(r"[^A-Z0-9]", "", raw.upper())


def is_valid_nif(raw: str | None) -> bool:
    s = _clean(raw)
    if not re.fullmatch(r"\d{8}[A-Z]", s):
        return False
    return s[8] == _NIF_LETTERS[int(s[:8]) % 23]


def is_valid_nie(raw: str | None) -> bool:
    s = _clean(raw)
    if not re.fullmatch(r"[XYZ]\d{7}[A-Z]", s):
        return False
    number = _NIE_PREFIX[s[0]] + s[1:8]
    return s[8] == _NIF_LETTERS[int(number) % 23]


def _cif_check_digit(seven: str) -> int:
    """Luhn-like control over the 7 middle digits: odd positions (1-based) doubled with digit-sum,
    even positions added straight; control = (10 - total % 10) % 10."""
    total = 0
    for i, ch in enumerate(seven):
        d = int(ch)
        if i % 2 == 0:  # 1-based odd position -> double and sum the product's digits
            d *= 2
            d = d // 10 + d % 10
        total += d
    return (10 - total % 10) % 10


def is_valid_cif(raw: str | None) -> bool:
    s = _clean(raw)
    if not re.fullmatch(r"[A-Z]\d{7}[0-9A-Z]", s):
        return False
    org = s[0]
    if org not in _CIF_ORG_ALL:
        return False
    check = _cif_check_digit(s[1:8])
    control = s[8]
    digit_form = str(check)
    letter_form = _CIF_CONTROL_LETTERS[check]
    if org in _CIF_ORG_DIGIT:
        return control == digit_form
    if org in _CIF_ORG_LETTER:
        return control == letter_form
    return control == digit_form or control == letter_form


def is_valid_tax_id(raw: str | None) -> bool:
    return is_valid_nif(raw) or is_valid_nie(raw) or is_valid_cif(raw)


def canonical_tax_id(raw: str | None) -> str | None:
    """Normalized tax ID iff it passes its checksum, else None. The CAPA-0 certified hard key:
    a None return means "not identity-grade — do not key an entity off this value"."""
    s = _clean(raw)
    return s if is_valid_tax_id(s) else None

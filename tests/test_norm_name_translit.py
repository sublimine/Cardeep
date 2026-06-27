"""
tests/test_norm_name_translit.py

GOLDEN -- OPEN-C / gap (C) closure (project 360-A, task F2): the dealer-name
normaliser must TRANSLITERATE non-Latin scripts instead of erasing them, while
staying byte-identical for Spanish / Latin names.

RED (pre-fix legacy fold = NFKD + str.encode('ascii', 'ignore')):
    norm('Athina'[Greek])        -> None         (dead identity signal)
    norm('Athina Motors'[Greek]) -> 'motors'     (over-merge: only the incidental
                                                  Latin token survives, so every
                                                  distinct Greek "... Motors" dealer
                                                  collapses onto the same key)
    norm('Avto Servis'[Cyrillic])-> None
GREEN (post-fix anyascii, applied per-character):
    norm('Athina'[Greek])        -> 'athina'
    norm('Athina Motors'[Greek]) -> 'athinamotors'
    norm('Avto Servis'[Cyrillic])-> 'avtoservis'

ES BYTE-IDENTITY is the hard gate. The fix transliterates ONLY the letters the
legacy fold DROPPED; every character the legacy fold turned into ASCII is kept
exactly (per-character survivor invariant), so no Spanish dealer key changes.

Pure unit -- no DB, no network. The non-Latin literals are built from code points
so this source file's exotic-script content stays explicit.
"""
from __future__ import annotations

import re
import unicodedata

import pytest

from pipeline.identity import cluster_dealers as cd
from pipeline.identity import cross_source_dedup as csd
from pipeline.identity.name_normalize import normalize_name

# --- Non-Latin fixtures (code points -> ASCII-explicit source) --------------
_GREEK = "".join(chr(c) for c in (0x391, 0x3B8, 0x3AE, 0x3BD, 0x3B1))            # 'Αθήνα'
_GREEK_MOTORS = _GREEK + " Motors"
_GREEK_PATRA = "".join(chr(c) for c in (0x3A0, 0x3AC, 0x3C4, 0x3C1, 0x3B1))      # 'Πάτρα'
_GREEK_PATRA_MOTORS = _GREEK_PATRA + " Motors"
_CYRILLIC = "".join(chr(c) for c in (0x410, 0x432, 0x442, 0x43E))               # 'Авто'
_CYRILLIC_SERVICE = "".join(
    chr(c) for c in (0x410, 0x432, 0x442, 0x43E, 0x20, 0x421, 0x435, 0x440, 0x432, 0x438, 0x441)
)  # 'Авто Сервис'


# --- Byte-identity oracle: a frozen copy of the LEGACY algorithm -------------
_RE_NON_ALNUM = re.compile(r"[^a-z0-9]")
_LEGAL = ("sociedadlimitadaunipersonal", "sociedadanonima", "sociedadlimitada",
          "scoop", "scp", "slu", "sau", "sll", "sl", "sa")
_RE_LEGAL = re.compile(r"(" + "|".join(re.escape(s) for s in _LEGAL) + r")$")


def _legacy_normalize_name(name):
    """The pre-fix normaliser, kept verbatim as the ES byte-identity oracle."""
    if name is None or not isinstance(name, str) or not name.strip():
        return None
    clean = _RE_NON_ALNUM.sub(
        "", unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii").lower())
    if not clean:
        return None
    m = _RE_LEGAL.search(clean)
    if m and len(clean[: m.start()]) >= 3:
        clean = clean[: m.start()]
    return clean


def _legacy_fold(ch: str) -> str:
    return unicodedata.normalize("NFKD", ch).encode("ascii", "ignore").decode("ascii")


# ===========================================================================
# GREEN -- non-Latin scripts now yield a live identity key
# ===========================================================================
@pytest.mark.unit
def test_greek_name_transliterated_not_erased():
    """RED: legacy -> None. GREEN: a usable transliterated key."""
    assert _legacy_normalize_name(_GREEK) is None          # documents the RED
    assert normalize_name(_GREEK) == "athina"


@pytest.mark.unit
def test_cyrillic_name_transliterated_not_erased():
    assert _legacy_normalize_name(_CYRILLIC) is None        # documents the RED
    assert normalize_name(_CYRILLIC) == "avto"
    assert normalize_name(_CYRILLIC_SERVICE) == "avtoservis"


@pytest.mark.unit
def test_mixed_script_no_longer_collapses_to_latin_residue():
    """The over-merge fix: legacy mapped every 'X Motors' Greek name onto 'motors';
    the transliterator keeps the distinguishing Greek token, so two different Greek
    dealerships no longer share one name key."""
    assert _legacy_normalize_name(_GREEK_MOTORS) == "motors"        # documents the RED
    assert normalize_name(_GREEK_MOTORS) == "athinamotors"
    assert normalize_name(_GREEK_PATRA_MOTORS) == "patramotors"
    assert normalize_name(_GREEK_MOTORS) != normalize_name(_GREEK_PATRA_MOTORS)


@pytest.mark.unit
def test_both_identity_modules_share_the_canonical_normalizer():
    """cluster_dealers and cross_source_dedup must resolve to the SAME function
    (single source of truth) so the two clustering passes can never drift."""
    assert cd._normalize_name is normalize_name
    assert csd._normalize_name is normalize_name
    assert cd._normalize_name(_GREEK) == "athina"
    assert csd._normalize_name(_GREEK) == "athina"


# ===========================================================================
# ES BYTE-IDENTITY -- the hard gate
# ===========================================================================
@pytest.mark.unit
def test_es_real_names_byte_identical_to_legacy():
    """Real Spanish dealer-name shapes must normalise EXACTLY as before the fix."""
    es_names = [
        "José Motors", "Talleres Peña", "AUTOMOCIÓN del Oeste, S.L.",
        "Garaje Ibáñez", "Vehículos Núñez S.A.", "Citroën Centro",
        "Müller Automóviles", "Comercial L·L", "Autos Sánchez & Hijos",
        "Peña-Vega 2000", "MÁLAGA Wagen", "Niño & Cía., S.L.U.",
        "O'Donnell Motors", "Crta. N-340 km 5", "talleres garcia",
    ]
    for nm in es_names:
        assert normalize_name(nm) == _legacy_normalize_name(nm), nm


@pytest.mark.unit
def test_es_repertoire_folds_exactly_like_legacy():
    """Every character Spanish actually uses (incl. acentos, n-tilde, dieresis, the
    Catalan c-cedilla and middle dot) folds byte-identically to the legacy normaliser."""
    es_repertoire = (
        "abcdefghijklmnopqrstuvwxyz0123456789"
        "áéíóúüñç"      # á é í ó ú ü ñ ç
        "ÁÉÍÓÚÜÑÇ"      # Á É Í Ó Ú Ü Ñ Ç
        "·"                                                 # Catalan middle dot
    )
    assert normalize_name(es_repertoire) == _legacy_normalize_name(es_repertoire)
    for ch in es_repertoire:
        probe = "auto" + ch + "centro"
        assert normalize_name(probe) == _legacy_normalize_name(probe), repr(ch)


@pytest.mark.unit
def test_per_character_survivor_invariant():
    """The formal byte-identity guarantee: for EVERY codepoint whose legacy fold is
    non-empty (a 'survivor'), the new normaliser yields the identical result. Only
    codepoints the legacy fold DROPPED may gain a transliteration. Swept across Latin,
    Latin-Extended, Greek, Cyrillic, Hebrew and Arabic blocks."""
    violations = []
    for cp in range(0x0, 0x3000):
        ch = chr(cp)
        if _legacy_fold(ch):  # survivor -> must be preserved exactly
            probe = "z" + ch + "z"
            if normalize_name(probe) != _legacy_normalize_name(probe):
                violations.append(hex(cp))
    assert not violations, f"survivor byte-identity divergences: {violations[:20]}"


@pytest.mark.unit
def test_empty_missing_and_symbol_only_unchanged():
    """None / blank / symbol-only / suffix-only inputs behave exactly as legacy."""
    for x in (None, "", "   ", "###", "&&&", "S.L.", "- . -"):
        assert normalize_name(x) == _legacy_normalize_name(x), repr(x)


@pytest.mark.unit
def test_legal_suffix_strip_preserved():
    """FIX-B legal-suffix stripping is unchanged by the transliteration swap."""
    assert normalize_name("Automocion del Oeste, S.A.") == "automociondeloeste"
    assert normalize_name("Automocion del Oeste") == "automociondeloeste"

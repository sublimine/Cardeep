"""Country-proof (red-team R2 #6): the G1 province segment must accept 2-to-8 char codes.

geo_province.code was widened to VARCHAR(8) (migration 0059) for FR DOM '971' (3 digits),
German Kreis (up to 5) and NUTS-3 'ITI43', and migration 0062's evict-ledger CHECK accepts
[0-9A-Z]{2,8}. The G1 identity gate (pipeline/complete.py + its set-based SQL mirror
scripts/populate_completion.py) had generalised the ^CDP-ES- prefix but kept a FIXED
[0-9A-Z]{2} province segment, so a second-country dealer with a >2-char province got a
schema-valid cdp_code (the mint emits it, 0062 accepts it) that G1 nonetheless marked
invalid_province_code forever. These goldens lock the segment to {2,8} in lockstep across
both mirrors and pin ES byte-identical.
"""
import re

from pipeline.complete import _CDP_CODE_RE, _NON_ES_PROVINCE_RE
from scripts.populate_completion import _CDP_CODE_PATTERN, _NON_ES_PROVINCE_PATTERN

_CDP_PAT = re.compile(_CDP_CODE_PATTERN)
_PROV_PAT = re.compile(_NON_ES_PROVINCE_PATTERN)


def test_cdp_accepts_es_2char_province_byte_identical():
    # ES unchanged: 2-digit province still matches in both mirrors.
    assert _CDP_CODE_RE.match("CDP-ES-28-AB23CDEF")
    assert _CDP_PAT.match("CDP-ES-28-AB23CDEF")


def test_cdp_accepts_country2_3char_province():
    # The exact red-team repro: 3-char provinces the mint legitimately emits (was None).
    for code in ("CDP-DE-091-AB23CDEF", "CDP-FR-2A2-AB23CDEF", "CDP-IT-ITI-AB23CDEF"):
        assert _CDP_CODE_RE.match(code), code
        assert _CDP_PAT.match(code), code


def test_cdp_accepts_up_to_8char_province():
    assert _CDP_CODE_RE.match("CDP-DE-ABCDEFGH-AB23CDEF")  # 8-char province
    assert _CDP_PAT.match("CDP-DE-ABCDEFGH-AB23CDEF")


def test_cdp_still_rejects_1char_and_9char_province():
    for bad in ("CDP-ES-2-AB23CDEF", "CDP-DE-ABCDEFGHI-AB23CDEF"):  # 1 and 9 chars
        assert _CDP_CODE_RE.match(bad) is None, bad
        assert _CDP_PAT.match(bad) is None, bad


def test_cdp_still_rejects_crockford_and_case_violations():
    for bad in ("CDP-ES-28-AB23CDEI", "CDP-ES-28-ab23cdef"):  # I excluded; lowercase invalid
        assert _CDP_CODE_RE.match(bad) is None, bad
        assert _CDP_PAT.match(bad) is None, bad


def test_non_es_province_accepts_2_to_8_alphanumeric():
    for ok in ("28", "2A", "RM", "091", "ITI43", "ABCDEFGH"):
        assert _NON_ES_PROVINCE_RE.match(ok), ok
        assert _PROV_PAT.match(ok), ok


def test_non_es_province_rejects_1char_and_9char():
    for bad in ("2", "ABCDEFGHI"):
        assert _NON_ES_PROVINCE_RE.match(bad) is None, bad
        assert _PROV_PAT.match(bad) is None, bad


def test_complete_and_populate_patterns_are_in_lockstep():
    # Anti-drift: the two mirrors must stay byte-identical so one never country-blinds again.
    assert _CDP_CODE_RE.pattern == _CDP_CODE_PATTERN
    assert _NON_ES_PROVINCE_RE.pattern == _NON_ES_PROVINCE_PATTERN

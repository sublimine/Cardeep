"""T1.1 (logic, no PG) — the vam_verified gating RULE as a pure, testable single-source-of-truth.

`vam_verified=TRUE` on a cluster_run is what makes it SERVED. The escéptico's #1 finding: today that
flag is a manual boolean with NO check, so a human can serve a run that never passed quorum. The rule
that SHOULD gate it: only a TRUSTWORTHY verdict with quorum_n>=2 (the same quorum the Inquisition/VAM
require). This function is the EXACT predicate the DB trigger (blueprint 01-T1.1) mirrors — so the
rule is verified HERE, in memory, without PG; the trigger SQL just implements this tested spec.
"""
from __future__ import annotations

import pytest

from pipeline.identity.vam_gate import vam_verified_allowed

pytestmark = pytest.mark.unit


def test_trustworthy_with_quorum_is_allowed():
    assert vam_verified_allowed("TRUSTWORTHY", 2) is True
    assert vam_verified_allowed("TRUSTWORTHY", 5) is True


def test_trustworthy_without_quorum_is_blocked():
    assert vam_verified_allowed("TRUSTWORTHY", 1) is False
    assert vam_verified_allowed("TRUSTWORTHY", 0) is False
    assert vam_verified_allowed("TRUSTWORTHY", None) is False


def test_non_trustworthy_is_blocked_regardless_of_quorum():
    for v in ("REFUTED", "UNVERIFIED", "QUARANTINED", None, ""):
        assert vam_verified_allowed(v, 5) is False


def test_grandfathered_zero_quorum_trustworthy_is_blocked():
    # the ~989 grandfathered TRUSTWORTHY/quorum_n=0 rows (0026/0036) must NOT pass the real gate.
    assert vam_verified_allowed("TRUSTWORTHY", 0) is False

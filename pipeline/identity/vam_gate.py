"""The single rule that gates SERVING: a cluster_run may be marked ``vam_verified=TRUE`` only with a
TRUSTWORTHY verdict of ``quorum_n>=2``.

Today `vam_verified` is a MANUAL boolean with no DB check (the adversarial review's #1 finding), so a
human can serve a run that never passed quorum. The DB trigger (blueprint
plans/road-to-13/01-T1.1-vam-verified-blueprint.md) will enforce this EXACT predicate; keeping it
here as a pure function makes the rule testable WITHOUT PG and gives the trigger a single-source-of-
truth spec to implement. Mirrors verification_verdict's chk_trustworthy_needs_quorum (mig 0026) and
the gestion_item RESOLVED proof (mig 0036).
"""
from __future__ import annotations


def vam_verified_allowed(verdict: str | None, quorum_n: int | None) -> bool:
    """True iff a cluster_run may be served (``vam_verified=TRUE``): verdict is TRUSTWORTHY AND
    ``quorum_n>=2``. Grandfathered TRUSTWORTHY/quorum_n=0 rows are correctly rejected (they are not
    a real quorum)."""
    return verdict == "TRUSTWORTHY" and (quorum_n or 0) >= 2

"""T1.1 (DB) — the vam_verified trigger (mig 0070) enforces the serving gate AT THE DATABASE.

A canonical_dedup_run may be vam_verified=TRUE (= served) only with a TRUSTWORTHY verification_verdict
of quorum_n>=2. Mirrors the pure spec pipeline.identity.vam_gate.vam_verified_allowed. This is the
mechanical proof of the adversarial review's #1 finding: a direct INSERT that tries to serve a run
without a real quorum is REJECTED BY THE DB, not by human discipline.

@integration: refuses :5433 (production); skips if the dry-run PG is unreachable.
"""
from __future__ import annotations

import os

import psycopg2
import pytest

pytestmark = pytest.mark.integration

_DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep")


def _conn():
    if "5433" in _DSN:
        pytest.skip("refusing :5433 (production); use the :5434 dry-run")
    try:
        return psycopg2.connect(_DSN, connect_timeout=3)
    except Exception:
        pytest.skip(f"dry-run PG not reachable at {_DSN}")


def _setup(cur):
    """Fresh fixtures inside the current (rolled-back) transaction.

    quorum_n/family_n/origin_n are GENERATED columns (cdp_modal_cluster / cdp_distinct_families /
    cdp_distinct_origins), so we drive them via independent_values + verifier_paths. The 'good' verdict
    has 2 agreeing values across 2 families/2 origins (real quorum, passes chk_trustworthy_needs_quorum);
    the 'bad' verdict is UNVERIFIED (a non-TRUSTWORTHY proof the trigger must reject)."""
    cur.execute("INSERT INTO entity_cluster_run (cluster_run_id, resolver, scope, vam_verified) "
                "VALUES ('ecr-r13','test','test',FALSE) ON CONFLICT DO NOTHING")
    cur.execute(
        "INSERT INTO verification_verdict "
        "(subject_type,subject_key,claim,verdict,independent_values,verifier_paths,"
        " claim_kind,tolerance,method_version) "
        "VALUES ('t','k-good','c','TRUSTWORTHY','[100,100]'::jsonb,"
        "'[{\"family\":\"db\",\"origin\":\"o1\"},{\"family\":\"http\",\"origin\":\"o2\"}]'::jsonb,"
        "'count',0,'v1') RETURNING id")
    good = cur.fetchone()[0]
    cur.execute(
        "INSERT INTO verification_verdict "
        "(subject_type,subject_key,claim,verdict,independent_values,verifier_paths,"
        " claim_kind,tolerance,method_version) "
        "VALUES ('t','k-bad','c','UNVERIFIED','[100]'::jsonb,'[]'::jsonb,'count',0,'v1') RETURNING id")
    not_trustworthy = cur.fetchone()[0]
    return good, not_trustworthy


def _insert_run(cur, run_id, vam_verified, verdict_id):
    cur.execute(
        "INSERT INTO canonical_dedup_run "
        "(run_id,resolver,source_cluster_run,vam_verified,vam_verdict_id) "
        "VALUES (%s,'test','ecr-r13',%s,%s)", (run_id, vam_verified, verdict_id))


def test_vam_verified_true_requires_trustworthy_quorum_verdict():
    conn = _conn()
    try:
        conn.autocommit = False
        # 1) vam_verified=TRUE WITHOUT a verdict -> rejected by the DB
        cur = conn.cursor()
        _setup(cur)
        with pytest.raises(psycopg2.Error):
            _insert_run(cur, "r13-noproof", True, None)
        conn.rollback()
        # 2) vam_verified=TRUE with a NON-TRUSTWORTHY verdict -> rejected
        cur = conn.cursor()
        _, not_trustworthy = _setup(cur)
        with pytest.raises(psycopg2.Error):
            _insert_run(cur, "r13-untrustworthy", True, not_trustworthy)
        conn.rollback()
        # 3) vam_verified=TRUE with TRUSTWORTHY quorum_n>=2 -> ALLOWED
        cur = conn.cursor()
        good, _ = _setup(cur)
        _insert_run(cur, "r13-ok", True, good)        # must not raise
        # 4) vam_verified=FALSE -> always allowed (no proof needed)
        _insert_run(cur, "r13-false", False, None)    # must not raise
        conn.rollback()
    finally:
        conn.close()

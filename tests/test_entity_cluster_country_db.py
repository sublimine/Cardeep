"""T1.2 (DB) — the entity_cluster country-proof trigger (mig 0071) is the 3rd, MECHANICAL belt.

A direct INSERT of a cluster row whose member and canonical entities are in different countries is
REJECTED BY THE DATABASE — turning v_country_proof_violations from a passive detector view into an
impossibility by construction. @integration: refuses :5433; skips if the dry-run PG is unreachable.
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
    cur.execute("INSERT INTO entity_cluster_run (cluster_run_id,resolver,scope,vam_verified) "
                "VALUES ('ecr-71','test','test',FALSE) ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO entity (entity_ulid,cdp_code,kind,is_tier1,status,kind_source,"
                "attest_count,country_code) VALUES "
                "('01ARZ3NDEKTSV4RRFFQ69G5FAV','CDP-ES-28-AAAAAAAA','compraventa',false,'active','manual',1,'ES') "
                "ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO entity (entity_ulid,cdp_code,kind,is_tier1,status,kind_source,"
                "attest_count,country_code) VALUES "
                "('01BX5ZZKBKACTAV9WEVGEMMVRZ','CDP-PT-11-BBBBBBBB','compraventa',false,'active','manual',1,'PT') "
                "ON CONFLICT DO NOTHING")


def _cluster(cur, member, canonical):
    cur.execute("INSERT INTO entity_cluster (cluster_run_id,entity_ulid,canonical_ulid,cluster_size) "
                "VALUES ('ecr-71',%s,%s,2)", (member, canonical))


def test_entity_cluster_cannot_span_countries():
    conn = _conn()
    try:
        conn.autocommit = False
        cur = conn.cursor()
        _setup(cur)
        # member ES, canonical PT -> cross-country -> rejected by the DB
        with pytest.raises(psycopg2.Error):
            _cluster(cur, "01ARZ3NDEKTSV4RRFFQ69G5FAV", "01BX5ZZKBKACTAV9WEVGEMMVRZ")
        conn.rollback()
        cur = conn.cursor()
        _setup(cur)
        _cluster(cur, "01ARZ3NDEKTSV4RRFFQ69G5FAV", "01ARZ3NDEKTSV4RRFFQ69G5FAV")   # same country -> allowed (must not raise)
        conn.rollback()
    finally:
        conn.close()

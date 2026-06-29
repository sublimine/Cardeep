"""T1.2-ext (DB) — the vehicle_cluster country-proof trigger (mig 0072) protects the SECOND served axis.

A direct INSERT fusing two vehicles whose dealers are in different countries (country via vehicle ->
entity) is REJECTED BY THE DATABASE, closing the asymmetry with entity_cluster (0071). @integration:
refuses :5433; skips if the dry-run PG is unreachable.
"""
from __future__ import annotations

import os

import psycopg2
import pytest

pytestmark = pytest.mark.integration

_DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep")

# unique ULIDs/cdp_codes for THIS test (the :5434 dry-run carries residual rows from the T2.1
# re-cluster fixture; reusing shared ULIDs would silently bind to the wrong country via ON CONFLICT).
_E_ES = "01VC72E5AAAAAAAAAAAAAAAAAA"
_E_PT = "01VC72P7AAAAAAAAAAAAAAAAAA"
_V_ES = "01VC72VEAAAAAAAAAAAAAAAAAA"
_V_PT = "01VC72VPAAAAAAAAAAAAAAAAAA"


def _conn():
    if "5433" in _DSN:
        pytest.skip("refusing :5433 (production); use the :5434 dry-run")
    try:
        return psycopg2.connect(_DSN, connect_timeout=3)
    except Exception:
        pytest.skip(f"dry-run PG not reachable at {_DSN}")


def _setup(cur):
    cur.execute("INSERT INTO vehicle_cluster_run (cluster_run_id,resolver,scope,vam_verified) "
                "VALUES ('vcr-72','test','test',FALSE) ON CONFLICT DO NOTHING")
    for ulid, cdp, country in ((_E_ES, "CDP-ES-28-VC72ESEE", "ES"), (_E_PT, "CDP-PT-11-VC72PTPP", "PT")):
        cur.execute("INSERT INTO entity (entity_ulid,cdp_code,kind,is_tier1,status,kind_source,"
                    "attest_count,country_code) VALUES (%s,%s,'compraventa',false,'active','manual',1,%s) "
                    "ON CONFLICT DO NOTHING", (ulid, cdp, country))
    for v_ulid, e_ulid in ((_V_ES, _E_ES), (_V_PT, _E_PT)):
        cur.execute("INSERT INTO vehicle (vehicle_ulid,entity_ulid,deep_link,currency,status) "
                    "VALUES (%s,%s,'http://x','EUR','available') ON CONFLICT DO NOTHING", (v_ulid, e_ulid))


def _cluster(cur, member, canonical):
    cur.execute("INSERT INTO vehicle_cluster (cluster_run_id,vehicle_ulid,canonical_vehicle_ulid,"
                "cluster_size) VALUES ('vcr-72',%s,%s,2)", (member, canonical))


def test_vehicle_cluster_cannot_span_countries():
    conn = _conn()
    try:
        conn.autocommit = False
        cur = conn.cursor()
        _setup(cur)
        with pytest.raises(psycopg2.Error):       # vehicles whose dealers are ES vs PT -> rejected
            _cluster(cur, _V_ES, _V_PT)
        conn.rollback()
        cur = conn.cursor()
        _setup(cur)
        _cluster(cur, _V_ES, _V_ES)               # same country -> allowed (must not raise)
        conn.rollback()
    finally:
        conn.close()

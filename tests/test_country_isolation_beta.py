"""
tests/test_country_isolation_beta.py

GOLDEN -- cross-border ENTITY-RESOLUTION (beta) false-merge isolation
(generic-engine vector #4).

``pipeline/identity/resolve_entities.py`` is the beta resolver: it derives the
"same professional dealer" across channels using an INVENTORY FINGERPRINT --
Jaccard similarity on the set of ``canonical_vehicle_ulid`` (from the B7
vehicle-cluster run ``vehicle-identity-det-v1``). When two P-stratum entities
share >= ``JACCARD_THETA`` (0.30) of their used-car canonicals, beta declares
them the same physical dealer and merges them.

Before the country-proof fix this fingerprint merge was COUNTRY-BLIND
(``resolve_entities.py:690-691,756-757``): ``_build_edges`` accepted the merge on
``fp_ok`` alone, with no country in the block-key or the adjudication. A shared
canonical set can arise across borders -- a Signal-A photo cross-merge upstream
(vector #2) makes one ES dealer and one DE dealer point at the SAME
``canonical_vehicle_ulid`` set -- so beta fused an ES and a DE dealer into one
served identity. ``entity`` carries ``country_code`` (``migrations/0052``); the
fingerprint key did not.

WHAT IS ASSERTED
----------------
  fingerprint : ES + DE sharing >= 30% canonicals  -> MUST NOT merge
  fingerprint : two ES sharing >= 30% canonicals   -> MUST     merge  (no-reg)
  guard       : a hand-built cross-country cluster -> MUST raise pre-write
  guard       : a single-country census            -> MUST pass silently

The fingerprint tests drive the REAL build core (``_load_p_entities`` ->
``_load_fingerprints`` -> ``_build_edges`` -> ``_build_resolution_table``), the
exact path ``main()`` persists, so a regression in the shipped resolver -- not a
test fixture -- trips the guard.

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). It HARD-REFUSES
:5433 (live production) two ways -- by DSN string and by asserting the target
census (entity AND vehicle) is empty before seeding. Every test seeds inside a
transaction and ROLLS BACK, leaving the dry-run byte-identical (entity stays 0).
"""
from __future__ import annotations

import os

import psycopg2
import psycopg2.extras
import pytest

from pipeline.identity import resolve_entities as rez

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Crockford base32 (no I, L, O, U) -- the alphabet entity_ulid_shape accepts:
#   CHECK (entity_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$')
# vehicle_ulid has no shape CHECK, but we reuse the same generator for uniformity.
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Connection + isolation guard (same surface as the other country goldens)
# ---------------------------------------------------------------------------
def _target_dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


def _db_reachable(dsn: str) -> bool:
    try:
        psycopg2.connect(dsn, connect_timeout=3).close()
        return True
    except Exception:
        return False


@pytest.fixture
def dry_conn():
    """A transactional connection to the dry-run DB, rolled back on teardown.

    Triple isolation guard against the live census:
      1. refuse any DSN pointing at :5433;
      2. skip if the DB is unreachable;
      3. refuse to seed unless BOTH ``entity`` and ``vehicle`` are EMPTY (the
         dry-run holds 0/0; production holds ~452k entities) -- so a mis-pointed
         DSN can never mutate real data.
    """
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip(
            "refusing to run the beta-isolation golden against :5433 "
            "(live production); point CARDEEP_DSN at the :5434 dry-run")
    if not _db_reachable(dsn):
        pytest.skip(f"dry-run cardeep-pg not reachable at {dsn}")

    conn = psycopg2.connect(dsn)
    conn.autocommit = False
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM entity")
        n_entities = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM vehicle")
        n_vehicles = cur.fetchone()[0]
    if n_entities != 0 or n_vehicles != 0:
        conn.close()
        pytest.skip(
            f"target DB has {n_entities} entities / {n_vehicles} vehicles -- not "
            "the empty dry-run; refusing to seed/cluster against a populated census")
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


# ---------------------------------------------------------------------------
# Seeding helpers (FK + CHECK respecting)
# ---------------------------------------------------------------------------
def _ulid(tag: str) -> str:
    """Deterministic 26-char Crockford ULID from a safe tag (entity_ulid_shape)."""
    safe = "".join(c for c in tag.upper() if c in _CROCKFORD)
    return (safe + "0" * 26)[:26]


def _seed_geo(cur, country: str, province: str = "28", muni: str = "28079") -> None:
    """Seed (country, province) then (country, muni) -- order satisfies the
    composite FK geo_municipality(country_code, province_code) -> geo_province,
    the muni CHECK left(code,2)=province_code (ES) and the composite PKs (0053)."""
    cur.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
        (province, f"prov-{country}-{province}", "13", f"ccaa-{country}", country),
    )
    cur.execute(
        "INSERT INTO geo_municipality "
        "(code, name, province_code, comarca_id, country_code) "
        "VALUES (%s, %s, %s, NULL, %s) ON CONFLICT DO NOTHING",
        (muni, f"muni-{country}-{muni}", province, country),
    )


def _seed_entity(
    cur,
    *,
    ulid_tag: str,
    cdp: str,
    name: str,
    country: str,
    province: str = "28",
    muni: str = "28079",
) -> str:
    """Insert one P-stratum dealer (kind='compraventa', status='active') and return
    its entity_ulid. The trade_name is deliberately a non-municipality string so the
    INE city-guard does not pre-empt the country guard (the merge under test is the
    FINGERPRINT path, not name). org_id is left NULL (no chain guard interference)."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " province_code, municipality_code, country_code, status) "
        "VALUES (%s, %s, 'compraventa', %s, %s, %s, %s, %s, 'active')",
        (ulid, cdp, name, name, province, muni, country),
    )
    return ulid


def _seed_vehicle(cur, *, ulid_tag: str, entity_ulid: str, km: int) -> str:
    """Insert one in-scope vehicle (km>0 so it survives the new-car fingerprint
    guard cv.km>0) and return its vehicle_ulid. vehicle has no country_code
    (migrations/0003); the country is reached via entity."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, km, status) "
        "VALUES (%s, %s, %s, %s, 'available')",
        (ulid, entity_ulid, f"https://x.example/v/{ulid}", km),
    )
    return ulid


def _seed_vcluster_run(cur, run_id: str) -> None:
    """Create the B7 vehicle-cluster run that resolve_entities reads fingerprints
    from. run_id MUST equal rez.VEHICLE_CLUSTER_RUN; vam_verified is irrelevant
    (the fingerprint loader filters by cluster_run_id directly, not the view)."""
    cur.execute(
        "INSERT INTO vehicle_cluster_run (cluster_run_id, resolver, scope, vam_verified) "
        "VALUES (%s, 'union-find-deterministic', 'test', FALSE) "
        "ON CONFLICT DO NOTHING",
        (run_id,),
    )


def _seed_vcluster(cur, run_id: str, vehicle_ulid: str, canonical_ulid: str) -> None:
    """Assign a vehicle to a canonical in the B7 run -- the row that puts a
    canonical_vehicle_ulid into an entity's inventory fingerprint."""
    cur.execute(
        "INSERT INTO vehicle_cluster "
        "(cluster_run_id, vehicle_ulid, canonical_vehicle_ulid, match_signal) "
        "VALUES (%s, %s, %s, 'photo_url')",
        (run_id, vehicle_ulid, canonical_ulid),
    )


def _seed_shared_fingerprint(cur, ent_a: str, ent_b: str, tag: str, n: int = 4) -> None:
    """Make ent_a and ent_b share a Jaccard=1.0 inventory fingerprint.

    For each of n canonicals: ent_a owns a vehicle that is its OWN canonical
    (km>0), and ent_b owns a vehicle that points at ent_a's canonical. This is
    exactly the upstream-Signal-A-cross-merge shape: both entities end up with the
    SAME canonical set, so beta's fingerprint Jaccard = 1.0 >= 0.30."""
    run = rez.VEHICLE_CLUSTER_RUN
    _seed_vcluster_run(cur, run)
    for i in range(n):
        va = _seed_vehicle(cur, ulid_tag=f"VA{i}{tag}", entity_ulid=ent_a, km=40000 + i)
        vb = _seed_vehicle(cur, ulid_tag=f"VB{i}{tag}", entity_ulid=ent_b, km=40000 + i)
        _seed_vcluster(cur, run, va, va)   # ent_a vehicle is its own canonical
        _seed_vcluster(cur, run, vb, va)   # ent_b vehicle points at ent_a's canonical


def _run_build(conn) -> dict[str, str]:
    """Run the REAL beta resolver core over the rows seeded in this transaction;
    return ``{entity_ulid: resolved_dealer_ulid}``. Same connection => it sees the
    uncommitted seed. No write to entity_resolution: we assert on the in-memory
    assignment, the exact thing main() persists."""
    entities = rez._load_p_entities(conn)
    entity_ulids = [e["entity_ulid"] for e in entities]
    all_ulids = set(entity_ulids)
    org_map = {e["entity_ulid"]: e.get("org_id") for e in entities}
    fingerprints = rez._load_fingerprints(conn, entity_ulids)
    ine = rez._load_ine_municipalities(conn)
    b1_edges = rez._load_b1_edges(conn, all_ulids)
    edges = rez._build_edges(entities, fingerprints, ine_municipalities=ine)
    rows, _rej = rez._build_resolution_table(
        entities, edges, b1_edges=b1_edges, org_map=org_map, ine_municipalities=ine)
    return {r["entity_ulid"]: r["resolved_dealer_ulid"] for r in rows}


# ===========================================================================
# FINGERPRINT -- Jaccard on canonical_vehicle_ulid (the dominant beta key)
# ===========================================================================
def test_fingerprint_cross_country_do_not_merge(dry_conn):
    """ES + DE sharing a Jaccard=1.0 inventory fingerprint MUST land in distinct
    resolved dealers. The fingerprint key is country-blind today: a shared canonical
    set fuses them across borders."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        es = _seed_entity(
            cur, ulid_tag="ESBETA", cdp="CDP-ES-28-BETA0001",
            name="autohaus nord", country="ES")
        de = _seed_entity(
            cur, ulid_tag="DEBETA", cdp="CDP-DE-28-BETA0002",
            name="autohaus sud", country="DE")
        _seed_shared_fingerprint(cur, es, de, tag="X")

    canon = _run_build(dry_conn)

    assert canon[es] != canon[de], (
        "CROSS-BORDER FALSE-MERGE (beta): ES and DE dealers sharing a Jaccard=1.0 "
        f"inventory fingerprint collapsed into one resolved dealer (canonical={canon[es]!r}). "
        "The fingerprint block-key/adjudication is country-blind.")


def test_fingerprint_same_country_merge(dry_conn):
    """No-regression: two ES dealers sharing a Jaccard=1.0 fingerprint MUST still
    merge (the whole point of beta -- cross-source same-dealer dedup)."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        a = _seed_entity(
            cur, ulid_tag="ESBETAA", cdp="CDP-ES-28-BETAA001",
            name="autohaus nord", country="ES")
        b = _seed_entity(
            cur, ulid_tag="ESBETAB", cdp="CDP-ES-28-BETAB002",
            name="autohaus sud", country="ES")
        _seed_shared_fingerprint(cur, a, b, tag="Y")

    canon = _run_build(dry_conn)

    assert canon[a] == canon[b], (
        "ES REGRESSION (beta): two ES dealers sharing a Jaccard=1.0 inventory "
        "fingerprint did NOT merge -- the country fix broke same-country fingerprint "
        "resolution.")


# ---------------------------------------------------------------------------
# Pre-write BLOCKING guard (mechanical enforcement) -- pure Python, no DB.
# Hardening path (b) of the invariant: an inquisitor hand-builds a cross-country
# cluster and the guard MUST refuse it before any write/serve. Mirrors
# cluster_vehicles._assert_no_cross_country_clusters for the beta layer.
# ---------------------------------------------------------------------------
def test_blocking_guard_raises_on_cross_country_cluster():
    """A resolved dealer whose members span >1 country_code MUST abort pre-write."""
    rows = [
        {"entity_ulid": "A", "resolved_dealer_ulid": "A"},
        {"entity_ulid": "B", "resolved_dealer_ulid": "A"},
    ]
    entity_by_ulid = {
        "A": {"entity_ulid": "A", "country_code": "ES"},
        "B": {"entity_ulid": "B", "country_code": "DE"},
    }
    with pytest.raises(RuntimeError, match="COUNTRY-PROOF VIOLATION"):
        rez._assert_no_cross_country_clusters(rows, entity_by_ulid)


def test_blocking_guard_silent_on_single_country_clusters():
    """A single-country census MUST pass the guard untouched (ES no-regression)."""
    rows = [
        {"entity_ulid": "A", "resolved_dealer_ulid": "A"},
        {"entity_ulid": "B", "resolved_dealer_ulid": "A"},
        {"entity_ulid": "C", "resolved_dealer_ulid": "C"},
    ]
    entity_by_ulid = {
        "A": {"entity_ulid": "A", "country_code": "ES"},
        "B": {"entity_ulid": "B", "country_code": "ES"},
        "C": {"entity_ulid": "C", "country_code": "ES"},
    }
    # Must not raise.
    rez._assert_no_cross_country_clusters(rows, entity_by_ulid)

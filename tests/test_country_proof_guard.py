"""
tests/test_country_proof_guard.py

GOLDEN -- the SERVED-LAYER country-proof guard (generic-engine vector #4, guard).

``migrations/0057_country_proof_guard.sql`` adds the diagnostic view
``v_country_proof_violations``: the SQL "mechanical belt" of the COUNTRY-PROOF
invariant (``docs/generic-engine-bible/COUNTRY-PROOF-INVARIANT.md`` §1 Guard). It
returns any SERVED cluster -- dealer (``v_dealer_resolved``) OR vehicle
(``v_canonical_vehicle``) -- whose members span more than one ``country_code``.
Empty == the invariant holds in what is served; >0 rows == a cross-border
false-merge is being served.

WHAT IS ASSERTED
----------------
  detect (vehicle) : a FORCED cross-country vehicle cluster  -> view returns it
  detect (dealer)  : a FORCED cross-country dealer  cluster  -> view returns it
  clean  (both)    : a normal census run through the FIXED resolvers (vectors
                     #1-#4) -- including cross-border collision vectors that the
                     country-blind code WOULD have merged -- leaves the view EMPTY
                     while still producing real same-country clusters.

The "detect" tests bypass the resolvers and write a cross-country cluster straight
into the served tables (the inquisitor hand-build, hardening path (c)): they prove
the guard SEES a violation. The "clean" test drives the REAL build cores
(cluster_dealers, cluster_vehicles) and persists their output, proving the FIXED
pipeline serves zero violations on a mixed-country census.

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

from pipeline.identity import cluster_dealers as cd
from pipeline.identity import cluster_vehicles as cv

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Crockford base32 (no I, L, O, U) -- the alphabet entity_ulid_shape accepts:
#   CHECK (entity_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$')
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
            "refusing to run the country-proof-guard golden against :5433 "
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
    country: str,
    name: str = "concesionario test",
    province: str = "28",
    muni: str = "28079",
) -> str:
    """Insert one in-scope dealer (kind='compraventa', status='active') and return
    its entity_ulid. The entity is the sole carrier of country_code for both the
    dealer guard (via cdp_code) and the vehicle guard (via vehicle.entity_ulid)."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " province_code, municipality_code, country_code, status) "
        "VALUES (%s, %s, 'compraventa', %s, %s, %s, %s, %s, 'active')",
        (ulid, cdp, name, name, province, muni, country),
    )
    return ulid


def _seed_vehicle(
    cur,
    *,
    ulid_tag: str,
    entity_ulid: str,
    deep_link: str,
    photo_url: str,
    title: str,
    make: str = "seat",
    model: str = "leon",
    year: int = 2020,
    km: int = 45000,
    price: float = 15000,
) -> str:
    """Insert one in-scope vehicle (status defaults 'available', km>0) and return
    its vehicle_ulid. photo_url drives Signal A; distinct titles keep Signal B's
    title-guard off so Signal A is the sole cross-entity merge driver."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO vehicle "
        "(vehicle_ulid, entity_ulid, deep_link, make, model, year, km, price, "
        " title, photo_url, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'available')",
        (ulid, entity_ulid, deep_link, make, model, year, km, price, title, photo_url),
    )
    return ulid


def _seed_vam_vehicle_run(cur, run_id: str) -> None:
    """A vehicle-cluster run gated vam_verified=TRUE so v_canonical_vehicle serves it."""
    cur.execute(
        "INSERT INTO vehicle_cluster_run (cluster_run_id, resolver, scope, vam_verified) "
        "VALUES (%s, 'union-find-deterministic', 'test', TRUE)",
        (run_id,),
    )


def _seed_vam_entity_run(cur, run_id: str) -> None:
    """An entity-cluster run gated vam_verified=TRUE so v_canonical serves it."""
    cur.execute(
        "INSERT INTO entity_cluster_run (cluster_run_id, resolver, scope, vam_verified) "
        "VALUES (%s, 'deterministic', 'test', TRUE)",
        (run_id,),
    )


def _seed_vcluster(cur, run_id: str, vehicle_ulid: str, canonical_ulid: str) -> None:
    cur.execute(
        "INSERT INTO vehicle_cluster "
        "(cluster_run_id, vehicle_ulid, canonical_vehicle_ulid, match_signal) "
        "VALUES (%s, %s, %s, 'photo_url')",
        (run_id, vehicle_ulid, canonical_ulid),
    )


def _seed_ecluster(cur, run_id: str, entity_ulid: str, canonical_ulid: str) -> None:
    cur.execute(
        "INSERT INTO entity_cluster "
        "(cluster_run_id, entity_ulid, canonical_ulid) VALUES (%s, %s, %s)",
        (run_id, entity_ulid, canonical_ulid),
    )


# ---------------------------------------------------------------------------
# Real build drivers (FIXED resolvers, in-memory) + persistence to served tables
# ---------------------------------------------------------------------------
def _run_dealer_build(conn) -> dict[str, str]:
    """Run the REAL (fixed) cluster_dealers core; return {entity_ulid: canonical_ulid}."""
    entities = cd._load_entities(conn)
    det_edges = cd._build_deterministic_edges(entities)
    fuzzy_edges, _m, _e = cd._load_fuzzy_sql_edges(conn, entities)
    rows = cd._build_cluster_table(entities, list(set(det_edges + fuzzy_edges)))
    return {r["entity_ulid"]: r["canonical_ulid"] for r in rows}


def _run_vehicle_build(conn) -> dict[str, str]:
    """Run the REAL (fixed) cluster_vehicles core; return {vehicle_ulid: canonical}."""
    vehicles = cv._load_vehicles(conn)
    edges, edge_signal_map = cv._build_edges(vehicles)
    rows = cv._build_cluster_table(vehicles, edges, edge_signal_map)
    return {r["vehicle_ulid"]: r["canonical_vehicle_ulid"] for r in rows}


def _persist_entity_clusters(cur, run_id: str, mapping: dict[str, str]) -> None:
    """Persist a dealer build into the served entity_cluster (vam_verified)."""
    _seed_vam_entity_run(cur, run_id)
    for entity_ulid, canonical in mapping.items():
        _seed_ecluster(cur, run_id, entity_ulid, canonical)


def _persist_vehicle_clusters(cur, run_id: str, mapping: dict[str, str]) -> None:
    """Persist a vehicle build into the served vehicle_cluster (vam_verified)."""
    _seed_vam_vehicle_run(cur, run_id)
    for vehicle_ulid, canonical in mapping.items():
        _seed_vcluster(cur, run_id, vehicle_ulid, canonical)


def _violations(conn, layer: str | None = None) -> list[dict]:
    """Query v_country_proof_violations (optionally a single layer) in this txn."""
    sql = "SELECT layer, cluster_key, n_countries, countries FROM v_country_proof_violations"
    params: tuple = ()
    if layer is not None:
        sql += " WHERE layer = %s"
        params = (layer,)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return cur.fetchall()


# ===========================================================================
# DETECT -- the guard SEES a forced cross-country served cluster
# ===========================================================================
def test_guard_detects_forced_cross_country_vehicle(dry_conn):
    """A vehicle_cluster (vam_verified) whose canonical groups an ES and a DE
    vehicle MUST surface in v_country_proof_violations as layer='vehicle'."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        es_ent = _seed_entity(cur, ulid_tag="GVDES", cdp="CDP-ES-28-GVD0001", country="ES")
        de_ent = _seed_entity(cur, ulid_tag="GVDDE", cdp="CDP-DE-28-GVD0002", country="DE")
        ves = _seed_vehicle(
            cur, ulid_tag="VESGVD", entity_ulid=es_ent, deep_link="https://es/v1",
            photo_url="https://cdn/x.jpg", title="seat leon es")
        vde = _seed_vehicle(
            cur, ulid_tag="VDEGVD", entity_ulid=de_ent, deep_link="https://de/v1",
            photo_url="https://cdn/y.jpg", title="seat leon de")
        # FORCED cross-country canonical (bypasses the resolver): vde -> ves.
        run = "test-guard-vehicle-forced"
        _seed_vam_vehicle_run(cur, run)
        # 0072's trg_vehicle_cluster_country now FORBIDS this cross-country write at
        # write time; disable it ONLY for the forced injection -- THIS test asserts the
        # DETECTION view (v_country_proof_violations) sees the violation, not the write-guard.
        cur.execute("ALTER TABLE vehicle_cluster DISABLE TRIGGER trg_vehicle_cluster_country")
        try:
            _seed_vcluster(cur, run, ves, ves)
            _seed_vcluster(cur, run, vde, ves)
        finally:
            cur.execute("ALTER TABLE vehicle_cluster ENABLE TRIGGER trg_vehicle_cluster_country")

    rows = _violations(dry_conn, layer="vehicle")

    assert len(rows) == 1, (
        f"guard did NOT detect the forced cross-country VEHICLE cluster: {rows}")
    assert rows[0]["n_countries"] == 2, rows[0]
    assert sorted(c.strip() for c in rows[0]["countries"]) == ["DE", "ES"], rows[0]


def test_guard_detects_forced_cross_country_dealer(dry_conn):
    """An entity_cluster (vam_verified) resolving a DE dealer onto an ES canonical
    MUST surface in v_country_proof_violations as layer='dealer'."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        es_ent = _seed_entity(cur, ulid_tag="GDDES", cdp="CDP-ES-28-GDD0001", country="ES")
        de_ent = _seed_entity(cur, ulid_tag="GDDDE", cdp="CDP-DE-28-GDD0002", country="DE")
        # FORCED cross-country canonical: de_ent resolves to es_ent.
        run = "test-guard-dealer-forced"
        _seed_vam_entity_run(cur, run)
        # 0071's trg_entity_cluster_country now FORBIDS this cross-country write at
        # write time; disable it ONLY for the forced injection -- THIS test asserts the
        # DETECTION view sees the violation, not the write-guard.
        cur.execute("ALTER TABLE entity_cluster DISABLE TRIGGER trg_entity_cluster_country")
        try:
            _seed_ecluster(cur, run, es_ent, es_ent)
            _seed_ecluster(cur, run, de_ent, es_ent)
        finally:
            cur.execute("ALTER TABLE entity_cluster ENABLE TRIGGER trg_entity_cluster_country")

    rows = _violations(dry_conn, layer="dealer")

    assert len(rows) == 1, (
        f"guard did NOT detect the forced cross-country DEALER cluster: {rows}")
    assert rows[0]["n_countries"] == 2, rows[0]
    assert rows[0]["cluster_key"] == "CDP-ES-28-GDD0001", rows[0]


# ===========================================================================
# CLEAN -- the FIXED pipeline serves ZERO violations on a mixed-country census
# ===========================================================================
def test_guard_empty_on_fixed_pipeline_normal_census(dry_conn):
    """A normal census carrying the exact cross-border collision vectors (dealer
    same name+muni, vehicle shared photo) run through the FIXED resolvers must
    leave v_country_proof_violations EMPTY -- while still producing real
    same-country clusters (so the empty result is meaningful, not vacuous)."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        # Dealers: two ES + one DE, all identical (name, muni). FIXED cluster_dealers
        # merges the two ES, keeps DE apart.
        es1 = _seed_entity(cur, ulid_tag="CLES1", cdp="CDP-ES-28-CLN0001",
                           name="talleres garcia", country="ES")
        es2 = _seed_entity(cur, ulid_tag="CLES2", cdp="CDP-ES-28-CLN0002",
                           name="talleres garcia", country="ES")
        de1 = _seed_entity(cur, ulid_tag="CLDE1", cdp="CDP-DE-28-CLN0003",
                           name="talleres garcia", country="DE")
        # Vehicles: one per dealer, ALL sharing one photo_url (Signal A vector).
        # FIXED cluster_vehicles merges the two ES vehicles, keeps the DE one apart.
        shared_photo = "https://cdn.oemfeed.example/auction/lot/clean777.jpg"
        ves1 = _seed_vehicle(cur, ulid_tag="VCLES1", entity_ulid=es1,
                             deep_link="https://es/cl1", photo_url=shared_photo,
                             title="seat leon a")
        ves2 = _seed_vehicle(cur, ulid_tag="VCLES2", entity_ulid=es2,
                             deep_link="https://es/cl2", photo_url=shared_photo,
                             title="seat leon b")
        vde1 = _seed_vehicle(cur, ulid_tag="VCLDE1", entity_ulid=de1,
                             deep_link="https://de/cl1", photo_url=shared_photo,
                             title="seat leon c")

    # Drive the REAL fixed resolvers in-memory, then persist into the served tables.
    dealer_map = _run_dealer_build(dry_conn)
    vehicle_map = _run_vehicle_build(dry_conn)

    # Sanity: the fixed resolvers did NOT cross the border (precondition of "clean").
    assert dealer_map[es1] != dealer_map[de1], "fixed dealer build crossed ES/DE!"
    assert vehicle_map[ves1] != vehicle_map[vde1], "fixed vehicle build crossed ES/DE!"
    # And DID merge the same-country pairs (the clusters are real, not singletons).
    assert dealer_map[es1] == dealer_map[es2], "fixed dealer build lost ES merge"
    assert vehicle_map[ves1] == vehicle_map[ves2], "fixed vehicle build lost ES merge"

    with dry_conn.cursor() as cur:
        _persist_entity_clusters(cur, "test-clean-dealer-run", dealer_map)
        _persist_vehicle_clusters(cur, "test-clean-vehicle-run", vehicle_map)

    rows = _violations(dry_conn)

    assert rows == [], (
        "COUNTRY-PROOF VIOLATION in served census: the fixed pipeline produced "
        f"cross-border served cluster(s) {rows} -- v_country_proof_violations must "
        "be empty for a single-country-per-cluster census.")

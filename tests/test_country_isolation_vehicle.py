"""
tests/test_country_isolation_vehicle.py

GOLDEN -- cross-border VEHICLE false-merge isolation (generic-engine vector #2).

``pipeline/identity/cluster_vehicles.py`` builds physical-car identity clusters
from two signals, BOTH country-blind before the country-proof fix:

  * Signal A (photo_url): a normalized ``photo_url`` is indexed by URL ALONE and
    is declared "sufficient alone" -- two listings sharing one photo collapse
    into one physical car with NO corroboration. A wholesale/auction/OEM-CDN feed
    that reuses the same photo across borders therefore fuses an ES car and a DE
    car into ONE canonical_vehicle_ulid.
  * Signal B (firma): block-key ``(make, model, year, km, province_code)`` carries
    NO country_code. A 2nd country reuses the same numeric ``province_code`` space
    (``migrations/0053`` -- DE province ``'28'`` deliberately coexists with ES
    Madrid ``'28'``), so an ES VW Golf and a DE VW Golf with equal firma, price
    within +-2%, and identical title collapse into one physical car.

The vehicle row has NO country_code (``migrations/0003``); the country of a
vehicle is reached by JOIN ``vehicle.entity_ulid -> entity.country_code``
(``migrations/0052``). This is the binding regression guard for the VEHICLE layer
of the COUNTRY-PROOF invariant (``docs/generic-engine-bible/COUNTRY-PROOF-INVARIANT.md``):

  * Signal A, cross-country, shared photo_url   -> MUST NOT merge
  * Signal A, same-country,  shared photo_url   -> MUST     merge (ES no-regression)
  * Signal B, cross-country, equal firma+title  -> MUST NOT merge
  * Signal B, same-country,  equal firma+title  -> MUST     merge (ES no-regression)

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). It HARD-REFUSES
:5433 (live production) two ways -- by DSN string and by asserting the target
census (entity AND vehicle) is empty before seeding. Every test seeds inside a
transaction and ROLLS BACK, leaving the dry-run byte-identical.
"""
from __future__ import annotations

import os

import psycopg2
import psycopg2.extras
import pytest

from pipeline.identity import cluster_vehicles as cv

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Crockford base32 (no I, L, O, U) -- the alphabet entity_ulid_shape accepts:
#   CHECK (entity_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$')
# vehicle_ulid has no shape CHECK, but we reuse the same generator for uniformity.
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Connection + isolation guard
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
            "refusing to run the vehicle-isolation golden against :5433 "
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
    """Insert one dealer entity and return its entity_ulid. The entity is the SOLE
    carrier of country_code for its vehicles (vehicle has none); the resolver reaches
    it via JOIN vehicle.entity_ulid -> entity.country_code."""
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
    make: str,
    model: str,
    year: int,
    km: int,
    price: float,
    title: str,
    photo_url: str,
) -> str:
    """Insert one in-scope vehicle (status defaults 'available') and return its
    vehicle_ulid. km>0 so the new-car (km=0/NULL) guard never disables a signal."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO vehicle "
        "(vehicle_ulid, entity_ulid, deep_link, make, model, year, km, price, "
        " title, photo_url, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'available')",
        (ulid, entity_ulid, deep_link, make, model, year, km, price, title, photo_url),
    )
    return ulid


def _run_build(conn) -> dict[str, str]:
    """Run the REAL cluster_vehicles edge build + union-find over the rows seeded
    in this transaction; return ``{vehicle_ulid: canonical_vehicle_ulid}``. Same
    connection => it sees the uncommitted seed. No write to vehicle_cluster: we
    assert on the in-memory assignment, the exact thing main() persists."""
    vehicles = cv._load_vehicles(conn)
    edges, edge_signal_map = cv._build_edges(vehicles)
    rows = cv._build_cluster_table(vehicles, edges, edge_signal_map)
    return {r["vehicle_ulid"]: r["canonical_vehicle_ulid"] for r in rows}


# ---------------------------------------------------------------------------
# SIGNAL A -- shared normalized photo_url ("sufficient alone")
# Pair shares ONE photo_url but has DIFFERENT titles, so Signal B's title guard
# is off and Signal A is the SOLE merge driver.
# ---------------------------------------------------------------------------
_PHOTO_A_CROSS = "https://cdn.oemfeed.example/auction/lot/shareda1b2c3.jpg"
_PHOTO_A_SAME = "https://cdn.oemfeed.example/auction/lot/sharedx9y8z7.jpg"


def test_signal_a_photo_cross_country_do_not_merge(dry_conn):
    """ES + DE listings sharing one photo_url MUST land in distinct clusters.
    Signal A is country-blind today: a shared photo fuses them across borders."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        es_ent = _seed_entity(cur, ulid_tag="ENTAESPHOTO", cdp="CDP-ES-28-VEHA001", country="ES")
        de_ent = _seed_entity(cur, ulid_tag="ENTADEPHOTO", cdp="CDP-DE-28-VEHA002", country="DE")
        es = _seed_vehicle(
            cur, ulid_tag="VEHAESPHOTO", entity_ulid=es_ent,
            deep_link="https://es.plat/a-es", make="seat", model="leon",
            year=2020, km=45000, price=15000, title="seat leon madrid",
            photo_url=_PHOTO_A_CROSS)
        de = _seed_vehicle(
            cur, ulid_tag="VEHADEPHOTO", entity_ulid=de_ent,
            deep_link="https://de.plat/a-de", make="seat", model="leon",
            year=2020, km=45000, price=15000, title="seat leon munchen",
            photo_url=_PHOTO_A_CROSS)

    canon = _run_build(dry_conn)

    assert canon[es] != canon[de], (
        "CROSS-BORDER FALSE-MERGE (Signal A): ES and DE vehicles sharing one "
        f"normalized photo_url collapsed into one cluster (canonical={canon[es]!r}). "
        "photo_url is indexed country-blind and is 'sufficient alone'.")


def test_signal_a_photo_same_country_merge(dry_conn):
    """No-regression: two ES listings sharing one photo_url MUST still merge."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        a_ent = _seed_entity(cur, ulid_tag="ENTAES1PH", cdp="CDP-ES-28-VEHA101", country="ES")
        b_ent = _seed_entity(cur, ulid_tag="ENTAES2PH", cdp="CDP-ES-28-VEHA102", country="ES")
        a = _seed_vehicle(
            cur, ulid_tag="VEHAES1PH", entity_ulid=a_ent,
            deep_link="https://es.plat/a1", make="seat", model="leon",
            year=2020, km=45000, price=15000, title="seat leon oferta",
            photo_url=_PHOTO_A_SAME)
        b = _seed_vehicle(
            cur, ulid_tag="VEHAES2PH", entity_ulid=b_ent,
            deep_link="https://es.plat/a2", make="seat", model="leon",
            year=2020, km=45000, price=15000, title="seat leon ocasion",
            photo_url=_PHOTO_A_SAME)

    canon = _run_build(dry_conn)

    assert canon[a] == canon[b], (
        "ES REGRESSION (Signal A): two ES vehicles sharing one photo_url did NOT "
        "merge -- the country fix broke same-country photo clustering.")


# ---------------------------------------------------------------------------
# SIGNAL B -- firma (make, model, year, km) + price +-2% + same title, cross-entity
# Pair has DISTINCT photo_urls so Signal A is off and Signal B is the SOLE driver.
# ---------------------------------------------------------------------------
def test_signal_b_firma_cross_country_do_not_merge(dry_conn):
    """ES + DE listings with equal firma + title + price +-2% MUST NOT merge.
    Signal B block-key carries province_code but NOT country_code, and DE reuses
    the ES '28' province space (migrations/0053)."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        es_ent = _seed_entity(cur, ulid_tag="ENTBESFIRMA", cdp="CDP-ES-28-VEHB001", country="ES")
        de_ent = _seed_entity(cur, ulid_tag="ENTBDEFIRMA", cdp="CDP-DE-28-VEHB002", country="DE")
        es = _seed_vehicle(
            cur, ulid_tag="VEHBESFIRMA", entity_ulid=es_ent,
            deep_link="https://es.plat/b-es", make="volkswagen", model="golf",
            year=2019, km=60000, price=18000, title="volkswagen golf 2019 gti",
            photo_url="https://img.plata.example/es/aaa111.jpg")
        de = _seed_vehicle(
            cur, ulid_tag="VEHBDEFIRMA", entity_ulid=de_ent,
            deep_link="https://de.plat/b-de", make="volkswagen", model="golf",
            year=2019, km=60000, price=18200, title="volkswagen golf 2019 gti",
            photo_url="https://img.platb.example/de/bbb222.jpg")

    canon = _run_build(dry_conn)

    assert canon[es] != canon[de], (
        "CROSS-BORDER FALSE-MERGE (Signal B): ES and DE vehicles with equal firma "
        f"(make/model/year/km), title and price +-2% collapsed (canonical={canon[es]!r}). "
        "The firma block-key is country-blind and DE reuses ES province '28'.")


def test_signal_b_firma_same_country_merge(dry_conn):
    """No-regression: two ES cross-entity listings with equal firma + title +
    price +-2% MUST still merge."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        a_ent = _seed_entity(cur, ulid_tag="ENTBES1FI", cdp="CDP-ES-28-VEHB101", country="ES")
        b_ent = _seed_entity(cur, ulid_tag="ENTBES2FI", cdp="CDP-ES-28-VEHB102", country="ES")
        a = _seed_vehicle(
            cur, ulid_tag="VEHBES1FI", entity_ulid=a_ent,
            deep_link="https://es.plat/b1", make="volkswagen", model="golf",
            year=2019, km=60000, price=18000, title="volkswagen golf 2019 gti",
            photo_url="https://img.platc.example/es/ccc333.jpg")
        b = _seed_vehicle(
            cur, ulid_tag="VEHBES2FI", entity_ulid=b_ent,
            deep_link="https://es.plat/b2", make="volkswagen", model="golf",
            year=2019, km=60000, price=18100, title="volkswagen golf 2019 gti",
            photo_url="https://img.platd.example/es/ddd444.jpg")

    canon = _run_build(dry_conn)

    assert canon[a] == canon[b], (
        "ES REGRESSION (Signal B): two ES cross-entity vehicles with equal firma, "
        "title and price +-2% did NOT merge -- the country fix broke same-country firma.")


# ---------------------------------------------------------------------------
# Pre-write BLOCKING guard (mechanical enforcement) -- pure Python, no DB.
# Hardening path (b) of the invariant: an inquisitor hand-builds a cross-country
# cluster and the guard MUST refuse it before any write/serve.
# ---------------------------------------------------------------------------
def test_blocking_guard_raises_on_cross_country_cluster():
    """A cluster whose members span >1 country_code MUST abort the run pre-write."""
    rows = [
        {"vehicle_ulid": "A", "canonical_vehicle_ulid": "A"},
        {"vehicle_ulid": "B", "canonical_vehicle_ulid": "A"},
    ]
    vehicle_by_ulid = {
        "A": {"vehicle_ulid": "A", "country_code": "ES"},
        "B": {"vehicle_ulid": "B", "country_code": "DE"},
    }
    with pytest.raises(RuntimeError, match="COUNTRY-PROOF VIOLATION"):
        cv._assert_no_cross_country_clusters(rows, vehicle_by_ulid)


def test_blocking_guard_silent_on_single_country_clusters():
    """A single-country census MUST pass the guard untouched (ES no-regression)."""
    rows = [
        {"vehicle_ulid": "A", "canonical_vehicle_ulid": "A"},
        {"vehicle_ulid": "B", "canonical_vehicle_ulid": "A"},
        {"vehicle_ulid": "C", "canonical_vehicle_ulid": "C"},
    ]
    vehicle_by_ulid = {
        "A": {"vehicle_ulid": "A", "country_code": "ES"},
        "B": {"vehicle_ulid": "B", "country_code": "ES"},
        "C": {"vehicle_ulid": "C", "country_code": "ES"},
    }
    # Must not raise.
    cv._assert_no_cross_country_clusters(rows, vehicle_by_ulid)

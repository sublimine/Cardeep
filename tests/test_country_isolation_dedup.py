"""
tests/test_country_isolation_dedup.py

GOLDEN -- cross-border identity false-merge isolation (generic-engine vector #3).

This file is the binding regression guard for the two IDENTITY-DEDUP layers of the
COUNTRY-PROOF invariant (``docs/generic-engine-bible/COUNTRY-PROOF-INVARIANT.md``)
that feed the SERVED surfaces:

  * ``scripts/build_canonical_dedup.py`` -- Layer-2 of the served dealer view
    ``v_dealer_resolved``. It fuses canonicals that share a ``vehicle.deep_link``
    (a listing URL). Before the country-proof fix the deep_link group was
    country-blind: an ES canonical and a DE canonical sharing one listing URL
    collapsed into a single super-canonical -> served as one cross-border dealer.

  * ``pipeline/identity/cross_source_dedup.py`` -- writes ``entity_cluster`` (the
    cross-source overlay). Before the fix every block-key was ``(value, muni)``
    with no country, so an ES entity and a DE entity sharing a phone / website /
    normalized-name in the same numeric ``municipality_code`` merged. The
    collision is REAL, not hypothetical: a second country reuses the same numeric
    ``municipality_code`` space (``migrations/0053`` -- DE province ``'28'``
    deliberately coexists with ES Madrid ``'28'``).

WHAT IS ASSERTED
----------------
  deep_link  : ES + DE sharing one deep_link               -> MUST NOT merge
  deep_link  : two ES sharing one deep_link                -> MUST     merge  (no-reg)
  phone      : ES + DE sharing phone+muni (cross-source)   -> MUST NOT merge
  phone      : two ES sharing phone+muni                   -> MUST     merge  (no-reg)
  website    : ES + DE sharing website+muni                -> MUST NOT merge
  website    : two ES sharing website+muni                 -> MUST     merge  (no-reg)
  name       : ES + DE sharing name+muni                   -> MUST NOT merge
  name       : two ES sharing name+muni                    -> MUST     merge  (no-reg)

Every test drives the REAL build code (the module-level merge core the scripts run,
not a copy) so a regression in the shipped pipeline -- not just in a test fixture --
trips the guard.

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). It HARD-REFUSES
:5433 (live production) two ways -- by DSN string and by asserting the target
census is empty before seeding. Every test seeds inside a transaction and ROLLS
BACK, leaving the dry-run byte-identical (``entity`` stays 0).
"""
from __future__ import annotations

import os

import psycopg2
import psycopg2.extras
import pytest

from scripts import build_canonical_dedup as bcd
from pipeline.identity import cross_source_dedup as csd

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Crockford base32 (no I, L, O, U) -- the alphabet entity_ulid_shape accepts:
#   CHECK (entity_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$')
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Connection + isolation guard (same surface as test_country_isolation_dealer.py)
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
      3. refuse to seed unless the target ``entity`` table is EMPTY (the dry-run
         is entity=0; production holds ~452k) -- so a mis-pointed DSN can never
         mutate real data.
    """
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip(
            "refusing to run the dedup-isolation golden against :5433 "
            "(live production); point CARDEEP_DSN at the :5434 dry-run")
    if not _db_reachable(dsn):
        pytest.skip(f"dry-run cardeep-pg not reachable at {dsn}")

    conn = psycopg2.connect(dsn)
    conn.autocommit = False
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM entity")
        n_entities = cur.fetchone()[0]
    if n_entities != 0:
        conn.close()
        pytest.skip(
            f"target DB has {n_entities} entities -- not the empty dry-run; "
            "refusing to seed/cluster against a populated census")
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
    kind: str = "compraventa",
    phone: str | None = None,
    website: str | None = None,
    province: str = "28",
    muni: str = "28079",
) -> str:
    """Insert one in-scope dealer entity and return its entity_ulid.

    ``kind='compraventa'`` keeps the row inside both SCOPE filters (the deep_link
    build excludes only kind='particular'; cross_source scopes to dealer kinds).
    ``phone`` / ``website`` are the optional cross-source block-key signals."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " province_code, municipality_code, country_code, status, phone, website) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active', %s, %s)",
        (ulid, cdp, kind, name, name, province, muni, country, phone, website),
    )
    return ulid


def _seed_source(cur, entity_ulid: str, source_key: str) -> None:
    """Attach a source to an entity. cross_source_dedup INNER-JOINs entity_source
    and needs orthogonal source groups (a GEO source vs a DIGITAL source) to even
    consider a pair, so every cross-source fixture seeds one of each."""
    cur.execute(
        "INSERT INTO entity_source (entity_ulid, source_key) VALUES (%s, %s)",
        (entity_ulid, source_key),
    )


def _seed_vehicle(cur, *, ulid_tag: str, entity_ulid: str, deep_link: str) -> None:
    """Insert one available vehicle carrying ``deep_link`` (the listing URL that
    the canonical-dedup graph fuses on). status defaults to 'available'."""
    cur.execute(
        "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link) "
        "VALUES (%s, %s, %s)",
        (_ulid(ulid_tag), entity_ulid, deep_link),
    )


# ---------------------------------------------------------------------------
# REAL build drivers
# ---------------------------------------------------------------------------
def _run_deeplink_graph(conn) -> dict[str, list[str]]:
    """Run the REAL deep_link load + merge-graph core over the seeded transaction.

    Same connection => it sees the uncommitted seed. Returns merge_components
    (union-find root -> [member canonical cdp_codes]); a pair appears together iff
    build_canonical_dedup would fuse them into one super-canonical."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(bcd._DEEPLINK_CANON_SQL)
        rows = cur.fetchall()
    merge_components, _pair_ev, _used, _excl = bcd._build_deeplink_merge_graph(rows)
    return merge_components


def _deeplink_merged(merge_components: dict[str, list[str]], a: str, b: str) -> bool:
    """True iff canonicals a and b land in the SAME super-canonical component."""
    return any(a in members and b in members for members in merge_components.values())


def _run_cross_source(conn) -> dict[str, str]:
    """Run the REAL cross_source edge build + union-find over the seeded rows;
    return ``{entity_ulid: canonical_ulid}`` -- the exact assignment main() persists
    to entity_cluster. Two entities merged iff they share a canonical_ulid."""
    entities = csd._load_entities(conn, None)
    match_pairs = csd._build_cross_source_edges(entities)
    rows = csd._build_cluster_table(entities, match_pairs)
    return {r["entity_ulid"]: r["canonical_ulid"] for r in rows}


# ===========================================================================
# LAYER 1 -- build_canonical_dedup.py (deep_link super-canonical, served Layer-2)
# ===========================================================================
def test_deeplink_cross_country_do_not_merge(dry_conn):
    """ES + DE canonicals sharing ONE deep_link MUST stay in distinct components."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        es = _seed_entity(cur, ulid_tag="ESDLA", cdp="CDP-ES-28-DLINK001",
                          name="talleres garcia", country="ES")
        de = _seed_entity(cur, ulid_tag="DEDLB", cdp="CDP-DE-28-DLINK002",
                          name="talleres garcia", country="DE")
        # The SAME listing URL attributed to both countries (the false-merge vector).
        _seed_vehicle(cur, ulid_tag="VESDL1", entity_ulid=es,
                      deep_link="https://x.example/listing/777")
        _seed_vehicle(cur, ulid_tag="VDEDL1", entity_ulid=de,
                      deep_link="https://x.example/listing/777")

    mc = _run_deeplink_graph(dry_conn)

    assert not _deeplink_merged(mc, "CDP-ES-28-DLINK001", "CDP-DE-28-DLINK002"), (
        "CROSS-BORDER FALSE-MERGE: ES and DE canonicals sharing one deep_link "
        "collapsed into a single super-canonical (Layer-2 of v_dealer_resolved). "
        "The deep_link group is country-blind.")


def test_deeplink_same_country_merge(dry_conn):
    """No-regression: two ES canonicals sharing one deep_link MUST still merge."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        a = _seed_entity(cur, ulid_tag="ESDLC", cdp="CDP-ES-28-DLINKC01",
                         name="talleres garcia", country="ES")
        b = _seed_entity(cur, ulid_tag="ESDLD", cdp="CDP-ES-28-DLINKC02",
                         name="talleres garcia", country="ES")
        _seed_vehicle(cur, ulid_tag="VESDLC", entity_ulid=a,
                      deep_link="https://x.example/listing/888")
        _seed_vehicle(cur, ulid_tag="VESDLD", entity_ulid=b,
                      deep_link="https://x.example/listing/888")

    mc = _run_deeplink_graph(dry_conn)

    assert _deeplink_merged(mc, "CDP-ES-28-DLINKC01", "CDP-ES-28-DLINKC02"), (
        "ES REGRESSION: two ES canonicals sharing one deep_link did NOT merge -- "
        "the country fix broke same-country deep_link deduplication.")


# ===========================================================================
# LAYER 2 -- cross_source_dedup.py (entity_cluster overlay)
# Each signal (phone / website / name) is exercised in isolation: the cross
# fixtures share ONLY that one block-key value, distinct on the others.
# ===========================================================================

# --- Signal: phone (9-digit national) + municipality -----------------------
def test_cross_source_phone_cross_country_do_not_merge(dry_conn):
    """ES(osm) + DE(as24) sharing phone+muni MUST NOT merge (cross-source)."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        es = _seed_entity(cur, ulid_tag="ESPH", cdp="CDP-ES-28-PHONE001",
                          name="autos norte", country="ES", phone="600111222")
        de = _seed_entity(cur, ulid_tag="DEPH", cdp="CDP-DE-28-PHONE002",
                          name="autos sur", country="DE", phone="600111222")
        _seed_source(cur, es, "osm")
        _seed_source(cur, de, "as24")

    canon = _run_cross_source(dry_conn)

    assert canon[es] != canon[de], (
        "CROSS-BORDER FALSE-MERGE: ES and DE entities sharing a phone in the same "
        "numeric municipality_code merged. The phone block-key is country-blind.")


def test_cross_source_phone_same_country_merge(dry_conn):
    """No-regression: two ES entities sharing phone+muni MUST still merge."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        a = _seed_entity(cur, ulid_tag="ESPHA", cdp="CDP-ES-28-PHONEA01",
                         name="autos norte", country="ES", phone="600111222")
        b = _seed_entity(cur, ulid_tag="ESPHB", cdp="CDP-ES-28-PHONEB02",
                         name="autos sur", country="ES", phone="600111222")
        _seed_source(cur, a, "osm")
        _seed_source(cur, b, "as24")

    canon = _run_cross_source(dry_conn)

    assert canon[a] == canon[b], (
        "ES REGRESSION: two ES entities sharing phone+muni did NOT merge -- the "
        "country fix broke same-country cross-source phone clustering.")


# --- Signal: website host + municipality ------------------------------------
def test_cross_source_website_cross_country_do_not_merge(dry_conn):
    """ES(osm) + DE(as24) sharing website+muni MUST NOT merge (cross-source)."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        es = _seed_entity(cur, ulid_tag="ESWB", cdp="CDP-ES-28-WEB00001",
                          name="alfa motors", country="ES", website="https://ejemplo.es/")
        de = _seed_entity(cur, ulid_tag="DEWB", cdp="CDP-DE-28-WEB00002",
                          name="beta cars", country="DE", website="https://ejemplo.es/")
        _seed_source(cur, es, "osm")
        _seed_source(cur, de, "as24")

    canon = _run_cross_source(dry_conn)

    assert canon[es] != canon[de], (
        "CROSS-BORDER FALSE-MERGE: ES and DE entities sharing a website host in "
        "the same municipality merged. The website block-key is country-blind.")


def test_cross_source_website_same_country_merge(dry_conn):
    """No-regression: two ES entities sharing website+muni MUST still merge."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        a = _seed_entity(cur, ulid_tag="ESWBA", cdp="CDP-ES-28-WEBA0001",
                         name="alfa motors", country="ES", website="https://ejemplo.es/")
        b = _seed_entity(cur, ulid_tag="ESWBB", cdp="CDP-ES-28-WEBB0002",
                         name="beta cars", country="ES", website="https://ejemplo.es/")
        _seed_source(cur, a, "osm")
        _seed_source(cur, b, "as24")

    canon = _run_cross_source(dry_conn)

    assert canon[a] == canon[b], (
        "ES REGRESSION: two ES entities sharing website+muni did NOT merge -- the "
        "country fix broke same-country cross-source website clustering.")


# --- Signal: exact normalized name + municipality ---------------------------
def test_cross_source_name_cross_country_do_not_merge(dry_conn):
    """ES(osm) + DE(as24) sharing name+muni (name-only) MUST NOT merge."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        es = _seed_entity(cur, ulid_tag="ESNM", cdp="CDP-ES-28-NAME0001",
                          name="talleres lopez", country="ES")
        de = _seed_entity(cur, ulid_tag="DENM", cdp="CDP-DE-28-NAME0002",
                          name="talleres lopez", country="DE")
        _seed_source(cur, es, "osm")
        _seed_source(cur, de, "as24")

    canon = _run_cross_source(dry_conn)

    assert canon[es] != canon[de], (
        "CROSS-BORDER FALSE-MERGE: ES and DE entities sharing a normalized name in "
        "the same municipality merged. The name block-key is country-blind.")


def test_cross_source_name_same_country_merge(dry_conn):
    """No-regression: two ES entities sharing name+muni MUST still merge."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        a = _seed_entity(cur, ulid_tag="ESNMA", cdp="CDP-ES-28-NAMEA001",
                         name="talleres lopez", country="ES")
        b = _seed_entity(cur, ulid_tag="ESNMB", cdp="CDP-ES-28-NAMEB002",
                         name="talleres lopez", country="ES")
        _seed_source(cur, a, "osm")
        _seed_source(cur, b, "as24")

    canon = _run_cross_source(dry_conn)

    assert canon[a] == canon[b], (
        "ES REGRESSION: two ES entities sharing name+muni did NOT merge -- the "
        "country fix broke same-country cross-source name clustering.")

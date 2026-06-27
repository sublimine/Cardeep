"""
tests/test_country_isolation_dealer.py

GOLDEN -- cross-border dealer false-merge isolation (generic-engine vector #1).

``pipeline/identity/cluster_dealers.py`` builds dealer identity clusters by
block-key. Before the country-proof fix EVERY block-key was country-blind:

  * edges 1-3 (Python):  ``(norm_name | phone | website_host, municipality_code)``
  * edge   4  (SQL fuzzy): self-join on ``a.muni_code = b.muni_code`` only,
                           ``levenshtein(norm_name) <= 2``

So a Spanish dealer and a German dealer that share a normalised name and a
``municipality_code`` collapse into ONE union-find component and are served as a
single dealer. The collision is REAL, not hypothetical: a second country reuses
the same numeric ``municipality_code`` space (``migrations/0053`` -- DE province
``'28'`` deliberately coexists with ES Madrid ``'28'``).

This file is the binding regression guard for the DEALER layer of the
COUNTRY-PROOF invariant (``docs/generic-engine-bible/COUNTRY-PROOF-INVARIANT.md``):

  * cross-country, identical ``(name, muni)``  -> MUST NOT merge   (edge 1)
  * cross-country, fuzzy    ``(name, muni)``  -> MUST NOT merge   (edge 4)
  * same-country,  identical ``(name, muni)``  -> MUST     merge   (ES no-regression)
  * same-country,  fuzzy    ``(name, muni)``  -> MUST     merge   (ES no-regression)

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). It HARD-REFUSES
:5433 (live production, ~452k entities) two ways -- by DSN string and by asserting
the target census is empty before seeding. Every test seeds inside a transaction
and ROLLS BACK, leaving the dry-run byte-identical (``entity`` stays 0).
"""
from __future__ import annotations

import os

import psycopg2
import psycopg2.extras
import pytest

from pipeline.identity import cluster_dealers as cd

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Crockford base32 (no I, L, O, U) -- the alphabet entity_ulid_shape accepts:
#   CHECK (entity_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$')
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
      3. refuse to seed unless the target ``entity`` table is EMPTY (the dry-run
         is entity=0; production holds ~452k) -- so a mis-pointed DSN can never
         mutate real data.
    """
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip(
            "refusing to run the dealer-isolation golden against :5433 "
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
    province: str = "28",
    muni: str = "28079",
) -> str:
    """Insert one in-scope dealer (kind='compraventa', status='active') and return
    its entity_ulid. trade_name is the load-bearing field (it drives every name
    block-key); legal_name mirrors it for fidelity."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " province_code, municipality_code, country_code, status) "
        "VALUES (%s, %s, 'compraventa', %s, %s, %s, %s, %s, 'active')",
        (ulid, cdp, name, name, province, muni, country),
    )
    return ulid


def _run_build(conn) -> dict[str, str]:
    """Run the REAL cluster_dealers edge build (edges 1-3 + edge-4 fuzzy SQL +
    union-find) over the rows seeded in this transaction; return
    ``{entity_ulid: canonical_ulid}``. Same connection => it sees the uncommitted
    seed. No write to entity_cluster: we assert on the in-memory assignment, the
    exact thing main() persists."""
    entities = cd._load_entities(conn)
    det_edges = cd._build_deterministic_edges(entities)
    fuzzy_edges, _munis_skipped, _ents_skipped = cd._load_fuzzy_sql_edges(conn, entities)
    all_edges = list(set(det_edges + fuzzy_edges))
    rows = cd._build_cluster_table(entities, all_edges)
    return {r["entity_ulid"]: r["canonical_ulid"] for r in rows}


# ---------------------------------------------------------------------------
# EDGE 1 -- exact (norm_name, municipality_code)
# ---------------------------------------------------------------------------
def test_exact_name_muni_cross_country_do_not_merge(dry_conn):
    """ES + DE sharing identical (norm_name, muni) MUST land in distinct clusters."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        es = _seed_entity(
            cur, ulid_tag="ESEXACT", cdp="CDP-ES-28-TESTAAAA",
            name="talleres garcia", country="ES")
        de = _seed_entity(
            cur, ulid_tag="DEEXACT", cdp="CDP-DE-28-TESTBBBB",
            name="talleres garcia", country="DE")

    canon = _run_build(dry_conn)

    assert canon[es] != canon[de], (
        "CROSS-BORDER FALSE-MERGE: ES and DE dealers with identical "
        "(norm_name, municipality_code) collapsed into one cluster "
        f"(canonical={canon[es]!r}). Edge-1 block-key is country-blind.")


def test_exact_name_muni_same_country_merge(dry_conn):
    """No-regression: two ES dealers sharing (norm_name, muni) MUST still merge."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        a = _seed_entity(
            cur, ulid_tag="ESONEAA", cdp="CDP-ES-28-TESTC001",
            name="talleres garcia", country="ES")
        b = _seed_entity(
            cur, ulid_tag="ESTWOBB", cdp="CDP-ES-28-TESTC002",
            name="talleres garcia", country="ES")

    canon = _run_build(dry_conn)

    assert canon[a] == canon[b], (
        "ES REGRESSION: two ES dealers with identical (norm_name, muni) did NOT "
        "merge -- the country fix broke same-country edge-1 clustering.")


# ---------------------------------------------------------------------------
# EDGE 4 -- fuzzy levenshtein(norm_name) <= 2, same muni
# ---------------------------------------------------------------------------
def test_fuzzy_name_cross_country_do_not_merge(dry_conn):
    """ES + DE fuzzy names (levenshtein=1) in one muni MUST NOT merge (edge 4)."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        es = _seed_entity(
            cur, ulid_tag="ESFUZZY", cdp="CDP-ES-28-TESTD001",
            name="talleres garcia", country="ES")
        de = _seed_entity(
            cur, ulid_tag="DEFUZZY", cdp="CDP-DE-28-TESTD002",
            name="talleres garcic", country="DE")  # levenshtein('...garcia','...garcic')=1

    canon = _run_build(dry_conn)

    assert canon[es] != canon[de], (
        "CROSS-BORDER FUZZY FALSE-MERGE: ES 'talleres garcia' and DE "
        "'talleres garcic' (levenshtein=1) merged via the muni-only fuzzy "
        "self-join. Edge-4 is country-blind.")


def test_fuzzy_name_same_country_merge(dry_conn):
    """No-regression: two ES fuzzy names (levenshtein=1) in one muni MUST merge."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        a = _seed_entity(
            cur, ulid_tag="ESFZAA", cdp="CDP-ES-28-TESTE001",
            name="talleres garcia", country="ES")
        b = _seed_entity(
            cur, ulid_tag="ESFZBB", cdp="CDP-ES-28-TESTE002",
            name="talleres garcic", country="ES")  # levenshtein=1

    canon = _run_build(dry_conn)

    assert canon[a] == canon[b], (
        "ES REGRESSION: two ES dealers with fuzzy names (levenshtein=1) in the "
        "same muni did NOT merge -- the country fix broke same-country edge-4.")

"""
tests/test_country_isolation_overlay_dedup.py

GOLDEN -- cross-border identity false-merge isolation for the TWO residual/particular
canonical_dedup OVERLAYS that the sibling dedup golden (test_country_isolation_dedup.py)
does NOT cover. This is the gap a red-team caught: a SERVED, silent cross-country
false-merge the build passed over.

  * scripts/build_residual_namemuni_dedup.py -- the residual name+municipality straggler
    overlay. It writes a canonical_dedup_run vam_verified=TRUE that v_dealer_resolved /
    v_servable_dealer SERVE. Before the fix the straggler group key was (normalized_name,
    municipality_code) with NO country, so two dealers sharing a name in the SAME numeric
    municipality_code but in ES and DE fused into ONE served super-canonical.

  * scripts/build_particular_dedup.py -- the particular canonical_key overlay. Before the
    fix it grouped particulares by canonical_key ALONE; two particulares in different
    countries sharing a canonical_key would fuse (latent today, the same defect).

The collision is REAL, not hypothetical: a second country reuses the same numeric
municipality_code / province space (migrations/0053 -- DE province '28' deliberately
coexists with ES Madrid '28').

WHAT IS ASSERTED
----------------
  residual   : ES + DE sharing name+muni                  -> MUST NOT fuse (served super differs)
  residual   : two ES sharing name+muni                   -> MUST     fuse  (no-reg)
  residual   : ES pair AND DE pair, same name+muni        -> each fuses WITHIN its country,
                                                             ES super != DE super (no crossing)
  particular : ES + DE sharing canonical_key              -> MUST NOT fuse
  particular : two ES sharing canonical_key (prov-split)  -> MUST     fuse  (no-reg)
  guard      : a cross-country fused component             -> MUST raise pre-write (both overlays)
  guard      : a single-country component                  -> MUST pass silently (both overlays)

Each DB test drives the REAL module-level grouping SQL + merge core the scripts run
(_RESIDUAL_GROUP_SQL / compute_residual_overlay and _PARTICULAR_GROUP_SQL /
compute_particular_overlay) -- NOT a copy -- so a regression in the shipped pipeline,
not just in a test fixture, trips the guard. This mirrors how test_country_isolation_dedup.py
drives build_canonical_dedup._build_deeplink_merge_graph.

ISOLATION (inviolable): the DB tests run ONLY against the dry-run DB (:5434). They
HARD-REFUSE :5433 (live production) two ways -- by DSN string and by asserting the target
census (entity) is EMPTY before seeding. Every test seeds inside a transaction and ROLLS
BACK, leaving the dry-run byte-identical (entity stays 0).
"""
from __future__ import annotations

import os

import psycopg2
import psycopg2.extras
import pytest

from scripts import build_residual_namemuni_dedup as brn
from scripts import build_particular_dedup as bpd

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Crockford base32 (no I, L, O, U) -- the alphabet entity_ulid_shape accepts:
#   CHECK (entity_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$')
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Connection + isolation guard (same surface as test_country_isolation_dedup.py)
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
            "refusing to run the overlay-dedup golden against :5433 "
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
            "refusing to seed/dedup against a populated census")
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
    """Seed (country, province) then (country, muni). A second country reusing the
    same numeric code is an ON CONFLICT no-op -- exactly the deliberate 0053
    dup-code coexistence the overlay must not pool across."""
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


def _seed_dealer(cur, *, ulid_tag: str, cdp: str, name: str, country: str,
                 province: str = "28", muni: str = "28079") -> str:
    """One in-scope dealer (kind='compraventa', status='active') sharing
    (normalized_name, municipality_code) with its peer -- the residual straggler
    block-key. Each resolves to its own cdp_code (no B1 cluster seeded), so a group
    forms iff >1 distinct resolved code shares the key."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " province_code, municipality_code, country_code, status) "
        "VALUES (%s, %s, 'compraventa', %s, %s, %s, %s, %s, 'active')",
        (ulid, cdp, name, name, province, muni, country),
    )
    return ulid


def _seed_particular(cur, *, ulid_tag: str, cdp: str, canonical_key: str, country: str) -> str:
    """One private seller (kind='particular') carrying a canonical_key
    ('particular:{platform}:{seller_id}'). Province/muni are left NULL (the
    particular overlay groups by canonical_key, not geo)."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, canonical_key, country_code, status) "
        "VALUES (%s, %s, 'particular', %s, %s, 'active')",
        (ulid, cdp, canonical_key, country),
    )
    return ulid


# ---------------------------------------------------------------------------
# REAL build drivers (module-level SQL + merge core, not a copy)
# ---------------------------------------------------------------------------
def _run_residual_overlay(conn) -> dict[str, str]:
    """Run the REAL residual group SQL + merge core over the seeded transaction;
    return {member_cdp_code: super_canonical_cdp_code}. A code absent from the map
    is its own super-canonical (singleton -> served as itself)."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(brn._RESIDUAL_GROUP_SQL)
        grp_rows = cur.fetchall()
    res = brn.compute_residual_overlay(grp_rows, base_rows=[], avail={})
    return {row[0]: row[1] for row in res["out"]}


def _residual_super(out_map: dict[str, str], cdp: str) -> str:
    return out_map.get(cdp, cdp)


def _run_particular_overlay(conn) -> dict[str, str]:
    """Run the REAL particular group SQL + case core over the seeded transaction;
    return {member_cdp_code: super_canonical_cdp_code}. A code absent is its own
    super-canonical."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(bpd._PARTICULAR_GROUP_SQL)
        grp_rows = cur.fetchall()
    new_pairs, *_ = bpd.compute_particular_overlay(grp_rows, mapped={}, avail={})
    return {c: sc for (c, _u, sc, _su, _is_rep, _key, _size) in new_pairs}


def _particular_super(pair_map: dict[str, str], cdp: str) -> str:
    return pair_map.get(cdp, cdp)


# ===========================================================================
# RESIDUAL overlay (build_residual_namemuni_dedup -> served vam_verified=TRUE)
# ===========================================================================
def test_residual_namemuni_cross_country_do_not_merge(dry_conn):
    """ES + DE dealers sharing name+muni MUST NOT fuse into one served super-canonical."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        _seed_dealer(cur, ulid_tag="RESNMES", cdp="CDP-ES-28-RESNM001",
                     name="talleres delta", country="ES")
        _seed_dealer(cur, ulid_tag="RESNMDE", cdp="CDP-DE-28-RESNM002",
                     name="talleres delta", country="DE")

    out_map = _run_residual_overlay(dry_conn)

    assert _residual_super(out_map, "CDP-ES-28-RESNM001") != _residual_super(out_map, "CDP-DE-28-RESNM002"), (
        "CROSS-BORDER FALSE-MERGE: ES and DE dealers sharing a normalized name in the same "
        "numeric municipality_code fused into ONE served super-canonical (residual overlay -> "
        "v_dealer_resolved). The straggler group key is country-blind.")


def test_residual_namemuni_same_country_merge(dry_conn):
    """No-regression: two ES dealers sharing name+muni MUST still fuse to one super-canonical."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_dealer(cur, ulid_tag="RESNMA", cdp="CDP-ES-28-RESNMA01",
                     name="talleres delta", country="ES")
        _seed_dealer(cur, ulid_tag="RESNMB", cdp="CDP-ES-28-RESNMB02",
                     name="talleres delta", country="ES")

    out_map = _run_residual_overlay(dry_conn)

    assert _residual_super(out_map, "CDP-ES-28-RESNMA01") == _residual_super(out_map, "CDP-ES-28-RESNMB02"), (
        "ES REGRESSION: two ES dealers sharing name+muni did NOT fuse -- the country fix broke "
        "same-country residual straggler collapse.")


def test_residual_per_country_groups_fuse_independently(dry_conn):
    """ES has 2 same-name+muni stragglers AND DE has 2 -- SAME normalized name, SAME numeric
    muni '28079'. Each country's pair MUST fuse WITHIN itself, and the ES super MUST stay
    distinct from the DE super (the (name,muni,country) key fuses per-country, never across)."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        _seed_dealer(cur, ulid_tag="PCES1", cdp="CDP-ES-28-PCES001", name="motor zeta", country="ES")
        _seed_dealer(cur, ulid_tag="PCES2", cdp="CDP-ES-28-PCES002", name="motor zeta", country="ES")
        _seed_dealer(cur, ulid_tag="PCDE1", cdp="CDP-DE-28-PCDE001", name="motor zeta", country="DE")
        _seed_dealer(cur, ulid_tag="PCDE2", cdp="CDP-DE-28-PCDE002", name="motor zeta", country="DE")

    out_map = _run_residual_overlay(dry_conn)
    es_super = _residual_super(out_map, "CDP-ES-28-PCES001")
    de_super = _residual_super(out_map, "CDP-DE-28-PCDE001")

    assert es_super == _residual_super(out_map, "CDP-ES-28-PCES002"), (
        "ES REGRESSION: the two ES stragglers did NOT fuse within country.")
    assert de_super == _residual_super(out_map, "CDP-DE-28-PCDE002"), (
        "DE REGRESSION: the two DE stragglers did NOT fuse within country.")
    assert es_super != de_super, (
        "CROSS-BORDER FALSE-MERGE: the ES pair and the DE pair (same name+muni) collapsed into "
        "the SAME super-canonical -- the residual group key crossed the border.")


# ===========================================================================
# PARTICULAR overlay (build_particular_dedup -> canonical_key merges)
# ===========================================================================
def test_particular_canonkey_cross_country_do_not_merge(dry_conn):
    """ES + DE particulares sharing a canonical_key MUST NOT fuse (latent vector, same defect)."""
    with dry_conn.cursor() as cur:
        _seed_particular(cur, ulid_tag="PARTES", cdp="CDP-ES-28-PARTC001",
                         canonical_key="particular:wallapop:7777", country="ES")
        _seed_particular(cur, ulid_tag="PARTDE", cdp="CDP-DE-28-PARTC002",
                         canonical_key="particular:wallapop:7777", country="DE")

    pair_map = _run_particular_overlay(dry_conn)

    assert _particular_super(pair_map, "CDP-ES-28-PARTC001") != _particular_super(pair_map, "CDP-DE-28-PARTC002"), (
        "CROSS-BORDER FALSE-MERGE: ES and DE particulares sharing a canonical_key fused into one "
        "super-canonical. The particular group key is country-blind.")


def test_particular_canonkey_same_country_merge(dry_conn):
    """No-regression: two ES particulares sharing a canonical_key (province-split) MUST still fuse."""
    with dry_conn.cursor() as cur:
        _seed_particular(cur, ulid_tag="PARTA", cdp="CDP-ES-28-PARTA001",
                         canonical_key="particular:wallapop:8888", country="ES")
        _seed_particular(cur, ulid_tag="PARTB", cdp="CDP-ES-41-PARTB002",
                         canonical_key="particular:wallapop:8888", country="ES")

    pair_map = _run_particular_overlay(dry_conn)

    assert _particular_super(pair_map, "CDP-ES-28-PARTA001") == _particular_super(pair_map, "CDP-ES-41-PARTB002"), (
        "ES REGRESSION: two ES particulares sharing a canonical_key (province-split) did NOT fuse -- "
        "the country fix broke same-country particular dedup.")


# ===========================================================================
# Pre-write BLOCKING guards (pure, no DB). Hardening path: an inquisitor
# hand-builds a cross-country component and the guard MUST refuse it pre-write;
# a single-country one passes silently. Mirrors
# cluster_vehicles._assert_no_cross_country_clusters.
# ===========================================================================
def test_residual_guard_raises_on_cross_country_component():
    """A residual super-canonical whose members span >1 country_code MUST abort pre-write."""
    out = [("CDP-ES-28-A", "CDP-DE-28-B", 2, False),
           ("CDP-DE-28-B", "CDP-DE-28-B", 2, True)]
    code_country = {"CDP-ES-28-A": "ES", "CDP-DE-28-B": "DE"}
    with pytest.raises(RuntimeError, match="COUNTRY-PROOF VIOLATION"):
        brn._assert_no_cross_country_residual(out, code_country)


def test_residual_guard_silent_on_single_country_component():
    """A single-country residual super-canonical must NOT raise."""
    out = [("CDP-ES-28-A", "CDP-ES-28-B", 2, False),
           ("CDP-ES-28-B", "CDP-ES-28-B", 2, True)]
    code_country = {"CDP-ES-28-A": "ES", "CDP-ES-28-B": "ES"}
    brn._assert_no_cross_country_residual(out, code_country)  # must not raise


def test_particular_guard_raises_on_cross_country_pair():
    """A particular merge pair fusing >1 country_code MUST abort pre-write."""
    new_pairs = [("CDP-ES-28-A", "uA", "CDP-DE-28-B", "uB", False, "particular:p:1", 2)]
    code_country = {"CDP-ES-28-A": "ES", "CDP-DE-28-B": "DE"}
    with pytest.raises(RuntimeError, match="COUNTRY-PROOF VIOLATION"):
        bpd._assert_no_cross_country_particular(new_pairs, code_country)


def test_particular_guard_silent_on_single_country_pair():
    """A single-country particular merge pair must NOT raise."""
    new_pairs = [("CDP-ES-28-A", "uA", "CDP-ES-28-B", "uB", False, "particular:p:1", 2)]
    code_country = {"CDP-ES-28-A": "ES", "CDP-ES-28-B": "ES"}
    bpd._assert_no_cross_country_particular(new_pairs, code_country)  # must not raise

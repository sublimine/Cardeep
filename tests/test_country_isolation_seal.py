"""
tests/test_country_isolation_seal.py

GOLDEN -- the SEAL / EXHAUSTIVENESS certificate layer country-scope (generic-engine
vector #5, the LAST country-blind SERVED surface after the dealer census, 0058).

Two certificate surfaces are pinned here:

  (a) v_province_seal (migrations 0042+0043) -- the per-province SU-SEAL the
      ``/geo/seal`` endpoint serves. Before migration 0060 it grouped by
      ``province_code`` ALONE, so a second tenant reusing the same numeric province
      code space (``migrations/0053`` -- DE province ``'28'`` deliberately coexists
      with ES Madrid ``'28'``) POOLED both countries' dealers into ONE numerator: a
      Spanish seal silently counted German dealers. Its bases (``entity`` 0052,
      ``denominator_estimate`` 0053) already carry ``country_code``, so the fix
      PROPAGATES country into the grouping + join; no value is invented.

  (b) v_exhaustiveness_seal (migration 0048) -- the national MSE coverage CERTIFICATE
      the ``/geo/exhaustiveness`` endpoint serves. Its base ``exhaustiveness_estimate``
      had NO country dimension at all, and the view's ``latest`` CTE picked the single
      globally-newest ``build_run_id`` -- so a newer second-country build would EVICT
      the ES certificate entirely. Migration 0060 adds ``country_code`` to the base
      (DEFAULT 'ES') and makes ``latest`` per-country.

WHAT IS ASSERTED
----------------
  structural : both certificate views project a ``country_code`` column (RED before 0060).
  venta      : with ES + DE venta dealers sharing province '28', the seal scoped to
               country='ES' counts ONLY the ES dealer (numerator==1), never the pooled 2.
  desguace   : same isolation for the DESGUACE discovery seal.
  exhaustive : with ES + DE certificates (DE build strictly NEWER), country='ES' still
               returns the ES national + province rows and NEVER a DE row -- proving both
               the country filter AND the per-country ``latest`` (the old global latest
               would have hidden ES behind the newer DE build).
  no-regress : with ONLY ES seeded, the historical country-blind query and the new
               country='ES' query return the IDENTICAL rows -- ES is byte-identical.

ISOLATION (inviolable): the DB tests run ONLY against the dry-run DB (:5434). They
HARD-REFUSE :5433 (live production) two ways -- by DSN string and by asserting the
target census (``entity``) is EMPTY before seeding. Every test seeds inside a
transaction and ROLLS BACK, leaving the dry-run byte-identical (``entity`` stays 0).
"""
from __future__ import annotations

import os

import psycopg2
import pytest

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Crockford base32 (no I, L, O, U) -- the alphabet entity_ulid_shape accepts:
#   CHECK (entity_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$')
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


# ===========================================================================
# Dry-run plumbing (mirrors test_country_isolation_serving.py exactly)
# ===========================================================================
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
      3. refuse to seed unless the target ``entity`` table is EMPTY (the dry-run is
         entity=0; production holds ~452k) -- so a mis-pointed DSN can never mutate
         real data.
    """
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip(
            "refusing to run the seal-isolation golden against :5433 "
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
            "refusing to seed against a populated census")
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


# ---------------------------------------------------------------------------
# Seeding helpers (FK + CHECK respecting) -- same surface as the other goldens
# ---------------------------------------------------------------------------
def _ulid(tag: str) -> str:
    safe = "".join(c for c in tag.upper() if c in _CROCKFORD)
    return (safe + "0" * 26)[:26]


def _seed_geo(cur, country: str, province: str = "28", muni: str = "28079") -> None:
    """Province + municipality. The geo PK is single-column ``code`` (0052 kept it),
    so a second country reusing code '28' is an ON CONFLICT no-op -- exactly the
    deliberate 0053 dup-code coexistence the seal must not pool across."""
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


def _seed_venta_dealer(cur, *, ulid_tag: str, cdp: str, country: str,
                       province: str = "28", muni: str = "28079") -> str:
    """One in-scope VENTA point: kind='compraventa', status='active', WITH one
    available vehicle (the v_province_seal venta numerator requires EXISTS a
    vehicle with status='available')."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " province_code, municipality_code, country_code, status) "
        "VALUES (%s, %s, 'compraventa', %s, %s, %s, %s, %s, 'active')",
        (ulid, cdp, f"venta {country}", f"venta {country}", province, muni, country),
    )
    cur.execute(
        "INSERT INTO vehicle "
        "(vehicle_ulid, entity_ulid, deep_link, currency, status, first_seen, last_seen) "
        "VALUES (%s, %s, %s, 'EUR', 'available', now(), now())",
        (_ulid("VEH" + ulid_tag), ulid, f"https://x/{cdp}"),
    )
    return ulid


def _seed_denominator(cur, *, country: str, province: str = "28", point_est: float = 10.0) -> None:
    """A VENTA registral ceiling for (province, country). denominator_estimate has
    country_code since 0053; chk_ci_order needs ci_low<=point_est<=ci_high."""
    cur.execute(
        "INSERT INTO denominator_estimate "
        "(segment, province_code, method, point_est, ci_low, ci_high, country_code) "
        "VALUES ('venta', %s, 'registral_ceiling', %s, %s, %s, %s)",
        (province, point_est, point_est, point_est, country),
    )


def _seed_desguace(cur, *, ulid_tag: str, cdp: str, country: str,
                   province: str = "28", muni: str = "28079") -> str:
    """One DESGUACE found via the DGT census (entity_source.source_key='dgt_cat'),
    so it contributes to BOTH the desguace numerator and denominator."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " province_code, municipality_code, country_code, status) "
        "VALUES (%s, %s, 'desguace', %s, %s, %s, %s, %s, 'active')",
        (ulid, cdp, f"desg {country}", f"desg {country}", province, muni, country),
    )
    cur.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, seen_at, first_seen) "
        "VALUES (%s, 'dgt_cat', now(), now())",
        (ulid,),
    )
    return ulid


def _seed_exhaustiveness(cur, *, build: str, country: str, created_at_sql: str) -> None:
    """A two-row certificate for one tenant: the grand-national headline (province
    AND segment NULL) + one per-province stratum. exhaustiveness_estimate carries
    country_code since 0060."""
    # national headline
    cur.execute(
        "INSERT INTO exhaustiveness_estimate "
        "(build_run_id, province_code, segment, k_lists, n_obs, n_hat, ci_low, ci_high, "
        " coverage_point, coverage_lower, method, confidence, seal_threshold, sealed, "
        " country_code, created_at) "
        f"VALUES (%s, NULL, NULL, 4, 100, 120, 110, 130, 0.83, 0.77, 'stratified_sum', "
        f"'high', 0.95, false, %s, {created_at_sql})",
        (build, country),
    )
    # one province stratum
    cur.execute(
        "INSERT INTO exhaustiveness_estimate "
        "(build_run_id, province_code, segment, k_lists, n_obs, n_hat, ci_low, ci_high, "
        " coverage_point, coverage_lower, method, confidence, seal_threshold, sealed, "
        " country_code, created_at) "
        f"VALUES (%s, '28', 'compraventa', 3, 50, 60, 55, 65, 0.83, 0.77, 'chao2', "
        f"'high', 0.95, false, %s, {created_at_sql})",
        (build, country),
    )


def _fetch(conn, sql: str, params: tuple) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


# ===========================================================================
# Structural: the certificate views carry a country dimension at all
# ===========================================================================
@pytest.mark.integration
def test_seal_views_carry_country_dimension(dry_conn):
    """v_province_seal AND v_exhaustiveness_seal MUST expose a country_code column --
    without it no seal can be scoped to a tenant. RED before migration 0060."""
    with dry_conn.cursor() as cur:
        for view in ("v_province_seal", "v_exhaustiveness_seal"):
            cur.execute(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name = %s AND column_name = 'country_code'",
                (view,),
            )
            assert cur.fetchone() is not None, (
                f"CERTIFICATE VIEW '{view}' has no country_code dimension -- the seal "
                "cannot be scoped by tenant (apply migration 0060).")


# ===========================================================================
# Behaviour: VENTA seal scoped to ES counts ONLY the ES dealer (never pooled)
# ===========================================================================
@pytest.mark.integration
def test_province_seal_venta_scoped_to_es_excludes_de(dry_conn):
    """ES + DE venta dealers sharing province '28': the venta seal scoped to
    country='ES' has numerator==1 (the ES dealer alone). RED before 0060 -- the view
    grouped by province_code only, pooling BOTH dealers into numerator==2, and had no
    country_code to filter on."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        _seed_venta_dealer(cur, ulid_tag="VES", cdp="CDP-ES-28-SEALES1", country="ES")
        _seed_venta_dealer(cur, ulid_tag="VDE", cdp="CDP-DE-28-SEALDE2", country="DE")
        _seed_denominator(cur, country="ES")
        _seed_denominator(cur, country="DE")

    es = _fetch(
        dry_conn,
        "SELECT numerator FROM v_province_seal "
        "WHERE province_code = %s AND segment = 'venta' AND country_code = %s",
        ("28", "ES"),
    )
    assert es == [(1,)], (
        f"SEAL POOLING: v_province_seal venta scoped to country='ES' returned "
        f"numerator {es} (expected [(1,)] -- ONLY the ES dealer). A value of 2 means "
        "the German dealer was pooled into the Spanish seal.")

    de = _fetch(
        dry_conn,
        "SELECT numerator FROM v_province_seal "
        "WHERE province_code = %s AND segment = 'venta' AND country_code = %s",
        ("28", "DE"),
    )
    assert de == [(1,)], (
        f"v_province_seal venta scoped to country='DE' returned {de} (expected [(1,)]).")


# ===========================================================================
# Behaviour: DESGUACE discovery seal scoped to ES counts ONLY the ES desguace
# ===========================================================================
@pytest.mark.integration
def test_province_seal_desguace_scoped_to_es_excludes_de(dry_conn):
    """ES + DE desguaces sharing province '28': the desguace discovery seal scoped to
    country='ES' has numerator==1 and denominator==1 (the ES desguace alone). RED
    before 0060 (pooled to numerator==2, no country_code)."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        _seed_desguace(cur, ulid_tag="DES", cdp="CDP-ES-28-DESGES1", country="ES")
        _seed_desguace(cur, ulid_tag="DDE", cdp="CDP-DE-28-DESGDE2", country="DE")

    es = _fetch(
        dry_conn,
        "SELECT numerator, denominator FROM v_province_seal "
        "WHERE province_code = %s AND segment = 'desguace' AND country_code = %s",
        ("28", "ES"),
    )
    assert es == [(1, 1)], (
        f"SEAL POOLING: v_province_seal desguace scoped to country='ES' returned "
        f"{es} (expected [(1, 1)] -- ONLY the ES desguace). A numerator of 2 means the "
        "German desguace was pooled into the Spanish discovery seal.")


# ===========================================================================
# Behaviour: EXHAUSTIVENESS certificate scoped to ES never serves a DE row,
# and survives a strictly-newer DE build (per-country `latest`)
# ===========================================================================
@pytest.mark.integration
def test_exhaustiveness_seal_scoped_to_es_excludes_de_and_survives_newer_de_build(dry_conn):
    """ES + DE certificates, DE build STRICTLY NEWER. The exact endpoint query scoped to
    country='ES' must return the ES national + province rows and NEVER a DE row. RED
    before 0060: exhaustiveness_estimate had no country_code (seeding DE was impossible)
    and the global `latest` CTE would have surfaced ONLY the newer DE build."""
    with dry_conn.cursor() as cur:
        # ES certificate is OLDER; DE certificate is NEWER -- the old global-latest CTE
        # would pick DE and evict ES entirely.
        _seed_exhaustiveness(cur, build="BUILD-ES-OLD", country="ES",
                             created_at_sql="now() - interval '2 hours'")
        _seed_exhaustiveness(cur, build="BUILD-DE-NEW", country="DE",
                             created_at_sql="now()")

    # The EXACT SQL /geo/exhaustiveness runs, plus the new country predicate.
    rows = _fetch(
        dry_conn,
        "SELECT province_code, segment, build_run_id, country_code "
        "FROM v_exhaustiveness_seal WHERE country_code = %s "
        "ORDER BY segment NULLS FIRST, province_code NULLS FIRST",
        ("ES",),
    )
    countries = {r[3] for r in rows}
    builds = {r[2] for r in rows}
    assert countries == {"ES"}, (
        f"EXHAUSTIVENESS LEAK: country='ES' served rows from {countries} "
        f"(builds {builds}); a German certificate row reached the Spanish scope.")
    assert builds == {"BUILD-ES-OLD"}, (
        f"per-country `latest` broken: ES scope served builds {builds} "
        "(expected only BUILD-ES-OLD; the newer DE build must NOT evict ES).")
    # The grand-national headline (province + segment NULL) survives for ES.
    assert any(r[0] is None and r[1] is None for r in rows), (
        "ES grand-national certificate row (province+segment NULL) vanished -- the "
        "newer DE build evicted it (global `latest` regression).")


# ===========================================================================
# No-regression: with ONLY ES, the historical country-blind seal == the ES scope
# (byte-identical for the sole tenant)
# ===========================================================================
@pytest.mark.integration
def test_province_seal_es_byte_identical(dry_conn):
    """With ONLY ES seeded, the historical country-blind venta query and the new
    country='ES' query return the IDENTICAL (denominator, numerator, coverage_pct,
    verdict). The country dimension must not perturb the sole tenant's seal."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_venta_dealer(cur, ulid_tag="REGES", cdp="CDP-ES-28-REGES01", country="ES")
        _seed_denominator(cur, country="ES")

    blind = _fetch(
        dry_conn,
        "SELECT denominator, numerator, coverage_pct, verdict FROM v_province_seal "
        "WHERE province_code = %s AND segment = 'venta'",
        ("28",),
    )
    scoped = _fetch(
        dry_conn,
        "SELECT denominator, numerator, coverage_pct, verdict FROM v_province_seal "
        "WHERE province_code = %s AND segment = 'venta' AND country_code = %s",
        ("28", "ES"),
    )
    assert blind == scoped and len(scoped) == 1, (
        f"ES REGRESSION: country-blind seal {blind} != ES-scoped seal {scoped}; the "
        "country dimension changed the sole tenant's figures (must be byte-identical).")

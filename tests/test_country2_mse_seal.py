"""
tests/test_country2_mse_seal.py

GOLDEN -- the EXHAUSTIVENESS *capture matrix* + MSE seal country-scope (the P1
country-#2 closer; the UPSTREAM twin of tests/test_exhaustiveness_country.py, which
pinned the PERSIST/READ-back side after b36224a country-aware-ed seal._persist).

THE GAP THIS PINS (items #7/#8/#9 of the P1 recon):
  ``pipeline/exhaustiveness/capture.py`` builds and reads ``discovery_capture`` keyed by
  (province_code, segment) ALONE -- COUNTRY-BLIND. The province code space COLLIDES across
  tenants BY DESIGN (migrations/0053 puts DE province '28' next to ES Madrid '28'), so a
  second-tenant build that reads the matrix country-blind POOLS the German and Spanish '28'
  captures into ONE stratum: the MSE estimate and the seal denominator are then computed over
  a MIXTURE of two countries. ``seal.compute`` already STAMPS the run country on every
  persisted row (b36224a) but READS the matrix country-blind (``capture.read_patterns`` had no
  country seam) and triangulates with ``load_external_census()`` country-blind -- so the DE
  seal would certify ES+DE pooled capture against the ES census.

WHAT IS ASSERTED
----------------
  collision  : with ES + DE captures materialised in the SAME build under province '28'
               (the deliberate 0053 dup-code), the matrix physically holds both tenants' rows.
  de-isolate : capture.build(country='DE') + read_patterns(country='DE') + seal.compute(
               country='DE') see ONLY the 74 German units -- never the 40 Spanish ones. The
               '28'/'compraventa' stratum n_obs is 74 (the DE denominator), NOT 114 (pooled).
               RED before the fix: capture.build/read_patterns have no country seam -- the
               engine cannot name a tenant at the capture layer, so a DE run would pool.
  es-byteid  : the no-country (default) path on a sole ES tenant is byte-identical -- the
               country-scoped read equals the country-blind read field-for-field (n_obs 74),
               every persisted row falls to 'ES'. Regression lock.

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). It HARD-REFUSES :5433 (live
production) two ways -- by DSN string and by asserting the live census (``entity``) is EMPTY
before seeding. capture.build / seal.compute open their OWN connections, so seeds are COMMITTED
(not a rolled-back txn); the fixture therefore scrubs every ``GOLDEN-C2MSE-%`` build and every
``C2MSE``-prefixed entity it created on entry AND exit, and removes the (ES,'28')/(DE,'28') geo
rows it added -- leaving the protected ``entity`` census byte-identical at 0.
"""
from __future__ import annotations

import os

import psycopg2
import pytest

from pipeline.exhaustiveness import capture, seal

pytestmark = pytest.mark.integration

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Every artefact this golden creates shares these prefixes, so cleanup is a single
# LIKE scrub that can never reach a real build / a real entity.
_BUILD_PREFIX = "GOLDEN-C2MSE-"
_ULID_PREFIX = "C2MSE"  # all Crockford-base32 (C,2,M,S,E) -> entity_ulid_shape-safe

# The 3 orthogonal MSE buckets the synthetic dealers populate (bit order), with the live
# source_key that maps to each (pipeline/exhaustiveness/lists.py::_EXACT).
_BUCKETS3 = ("GEO", "CENSUS", "DGT")
_SOURCE_KEY = {"GEO": "osm", "CENSUS": "autocasion_census", "DGT": "dgt_cat"}

# 2 Crockford chars per country, embedded in the ulid/cdp so the two tenants never collide.
_COUNTRY_TAG = {"ES": "E5", "DE": "DE"}

# A dense 3-list overlap -> 74 distinct units in one stratum (mirrors the sibling golden).
_DENSE = {
    (1, 1, 1): 20, (1, 1, 0): 10, (1, 0, 1): 10, (0, 1, 1): 10,
    (1, 0, 0): 8, (0, 1, 0): 8, (0, 0, 1): 8,
}  # sum == 74


# ===========================================================================
# Dry-run plumbing + COMMIT-and-scrub isolation (build/compute use own conns)
# ===========================================================================
def _target_dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


def _db_reachable(dsn: str) -> bool:
    try:
        psycopg2.connect(dsn, connect_timeout=3).close()
        return True
    except Exception:
        return False


def _scrub(cur, pre_list_keys: list[str]) -> None:
    """Delete everything this golden created (FK child -> parent order), leaving the
    protected ``entity`` census + reference geo byte-identical."""
    cur.execute("DELETE FROM exhaustiveness_estimate WHERE build_run_id LIKE %s",
                (_BUILD_PREFIX + "%",))
    cur.execute("DELETE FROM discovery_capture WHERE build_run_id LIKE %s",
                (_BUILD_PREFIX + "%",))
    cur.execute("DELETE FROM entity_source WHERE entity_ulid LIKE %s", (_ULID_PREFIX + "%",))
    cur.execute("DELETE FROM entity WHERE entity_ulid LIKE %s", (_ULID_PREFIX + "%",))
    cur.execute("DELETE FROM geo_municipality WHERE code = '28079' AND country_code IN ('ES','DE')")
    cur.execute("DELETE FROM geo_province WHERE code = '28' AND country_code IN ('ES','DE')")
    # discovery_list keys build() ADDED (not pre-existing) and now orphaned by the scrub above.
    cur.execute(
        "DELETE FROM discovery_list dl WHERE dl.list_key <> ALL(%s) "
        "AND NOT EXISTS (SELECT 1 FROM discovery_capture dc WHERE dc.list_key = dl.list_key)",
        (pre_list_keys,),
    )


@pytest.fixture
def dryrun():
    """Yield (dsn, autocommit conn) on the dry-run DB; scrub on entry + exit.

    Isolation guard against the live census: refuse :5433, skip if unreachable, and
    refuse to seed unless the live ``entity`` table is EMPTY (dry-run is 0; production
    holds ~452k) -- a mis-pointed DSN can never mutate real data.
    """
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip("refusing to run the country-2 MSE golden against :5433 (live "
                    "production); point CARDEEP_DSN at the :5434 dry-run")
    if not _db_reachable(dsn):
        pytest.skip(f"dry-run cardeep-pg not reachable at {dsn}")

    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM entity")
        if cur.fetchone()[0] != 0:
            conn.close()
            pytest.skip("target DB has a populated entity census -- not the empty dry-run; "
                        "refusing to seed against real data")
        cur.execute("SELECT list_key FROM discovery_list")
        pre_list_keys = [r[0] for r in cur.fetchall()]
        _scrub(cur, pre_list_keys)  # pre-clean any residue from a crashed prior run
    try:
        yield dsn, conn
    finally:
        with conn.cursor() as cur:
            _scrub(cur, pre_list_keys)
        conn.close()


# ---------------------------------------------------------------------------
# Seeding helpers (FK + CHECK respecting) -- entity-driven, exercising the REAL
# capture._fetch_raw -> v_dealer_resolved -> entity_source spine.
# ---------------------------------------------------------------------------
def _ulid(country: str, idx: int) -> str:
    """26-char Crockford-base32 entity_ulid (matches entity_ulid_shape), unique per
    (country, idx), all under the _ULID_PREFIX scrub prefix."""
    body = f"{_ULID_PREFIX}{_COUNTRY_TAG[country]}{idx:019d}"
    assert len(body) == 26, body
    return body


def _cdp(country: str, idx: int) -> str:
    """CDP-<CC>-28-<8 Crockford>, unique per (country, idx)."""
    return f"CDP-{country}-28-{_COUNTRY_TAG[country]}{idx:06d}"


def _seed_geo(cur, country: str) -> None:
    """Province '28' + municipality '28079' for one tenant. The (country_code, code)
    FK target: ES Madrid '28' and DE '28' coexist as DISTINCT rows -- exactly the
    deliberate 0053 dup-code collision the capture matrix must not pool across."""
    cur.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES ('28', %s, '13', %s, %s) ON CONFLICT DO NOTHING",
        (f"prov-{country}-28", f"ccaa-{country}", country),
    )
    cur.execute(
        "INSERT INTO geo_municipality (code, name, province_code, comarca_id, country_code) "
        "VALUES ('28079', %s, '28', NULL, %s) ON CONFLICT DO NOTHING",
        (f"muni-{country}-28079", country),
    )


def _seed_country_units(cur, *, country: str, patterns: dict[tuple[int, ...], int]) -> int:
    """Materialise a capture-recapture matrix AS ENTITIES: each pattern{bit-tuple: count}
    becomes ``count`` distinct compraventa entities in province '28', each with one
    entity_source row per list whose bit is 1. v_dealer_resolved maps a standalone entity
    to itself, so each entity is one capture unit. Returns n_obs (distinct units seeded)."""
    _seed_geo(cur, country)
    n_obs = 0
    idx = 0
    ents: list[tuple] = []
    srcs: list[tuple] = []
    for pat, cnt in patterns.items():
        for _ in range(cnt):
            ulid = _ulid(country, idx)
            cdp = _cdp(country, idx)
            ents.append((ulid, cdp, f"d{country}{idx}", f"d{country}{idx}", country))
            for bit, bucket in zip(pat, _BUCKETS3):
                if bit:
                    srcs.append((ulid, _SOURCE_KEY[bucket]))
            n_obs += 1
            idx += 1
    cur.executemany(
        "INSERT INTO entity (entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " province_code, municipality_code, country_code, status) "
        "VALUES (%s, %s, 'compraventa', %s, %s, '28', '28079', %s, 'active')",
        ents,
    )
    cur.executemany(
        "INSERT INTO entity_source (entity_ulid, source_key, seen_at, first_seen) "
        "VALUES (%s, %s, now(), now())",
        srcs,
    )
    return n_obs


def _fetch(dsn: str, sql: str, params: tuple) -> list[tuple]:
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def _stratum_units(patterns: dict, prov: str, seg: str) -> int:
    """Sum the per-pattern frequencies for one (prov, seg) stratum of read_patterns()."""
    return sum(patterns.get((prov, seg), {}).values())


# ===========================================================================
# CORE: a DE build/seal over the '28' collision sees ONLY the German units
# ===========================================================================
def test_de_build_and_seal_excludes_es_province_collision(dryrun):
    """ES (40) + DE (74) compraventa units share province '28'. Building the capture matrix
    for BOTH tenants into one build_run_id, then reading/sealing for country='DE', must yield
    the 74 German units alone -- never the pooled 114. RED before the fix: capture.build has no
    country_code seam (TypeError), so the engine cannot isolate a tenant at the capture layer
    and a DE run would pool the Spanish '28' rows."""
    dsn, conn = dryrun
    build = _BUILD_PREFIX + "COLLIDE-28"
    with conn.cursor() as cur:
        n_es = _seed_country_units(cur, country="ES", patterns={(1, 1, 0): 40})
        n_de = _seed_country_units(cur, country="DE", patterns=_DENSE)
    assert (n_es, n_de) == (40, 74)

    # Materialise BOTH tenants' captures under ONE build (the collision): ES first, then DE
    # appended (replace=False) so the matrix physically holds Spanish AND German '28' rows.
    capture.build(build, dsn=dsn, country_code="ES")
    capture.build(build, dsn=dsn, country_code="DE", replace=False)

    # The collision is real: discovery_capture holds both tenants' units under province '28'.
    by_country = dict(_fetch(
        dsn,
        "SELECT country_code, COUNT(DISTINCT resolved_ulid) FROM discovery_capture "
        "WHERE build_run_id = %s GROUP BY country_code",
        (build,),
    ))
    by_country = {k.strip(): v for k, v in by_country.items()}
    assert by_country == {"ES": 40, "DE": 74}, (
        f"capture matrix did not materialise the ES+DE '28' collision: {by_country}")

    # read_patterns scoped to each tenant isolates that tenant's '28'/'compraventa' stratum.
    de_pat, _ = capture.read_patterns(build, dsn=dsn, country_code="DE")
    es_pat, _ = capture.read_patterns(build, dsn=dsn, country_code="ES")
    assert _stratum_units(de_pat, "28", "compraventa") == 74, (
        "CAPTURE POOLING: read_patterns(country='DE') '28'/'compraventa' n_obs "
        f"{_stratum_units(de_pat, '28', 'compraventa')} (expected 74 -- the German units "
        "alone). 114 means the 40 Spanish units pooled into the German stratum.")
    assert _stratum_units(es_pat, "28", "compraventa") == 40, (
        f"read_patterns(country='ES') leaked: {_stratum_units(es_pat, '28', 'compraventa')}")

    # The DE seal certifies the German denominator only, stamped 'DE' on every persisted row.
    seal.compute(build, dsn=dsn, country_code="DE", external_census={})
    rows = _fetch(
        dsn,
        "SELECT province_code, segment, n_obs, country_code "
        "FROM exhaustiveness_estimate WHERE build_run_id = %s",
        (build,),
    )
    assert rows, "seal.compute persisted no rows for the DE build"
    assert {r[3].strip() for r in rows} == {"DE"}, (
        f"SEAL POOLING: DE build wrote country_code(s) {{r[3]}} (expected only 'DE'): {rows}")
    stratum = [r for r in rows if r[0] == "28" and r[1] == "compraventa"]
    assert stratum and stratum[0][2] == 74, (
        f"SEAL POOLING: '28'/'compraventa' stratum n_obs={stratum and stratum[0][2]} "
        "(expected 74 -- the German denominator). 114 means ES pooled into the DE seal.")
    assert any(r[0] is None and r[1] is None for r in rows), (
        "the DE national roll-up row (province + segment NULL) was not persisted")


# ===========================================================================
# REGRESSION: the sole-ES default path is byte-identical (country-blind == ES)
# ===========================================================================
def test_es_default_path_is_byte_identical(dryrun):
    """With ONLY ES seeded, the no-country (default) build/read/seal path equals the
    country-blind path field-for-field: the same 74 units, every persisted row 'ES'. The
    country dimension must not perturb today's sole tenant."""
    dsn, conn = dryrun
    build = _BUILD_PREFIX + "ES-BYTEID"
    with conn.cursor() as cur:
        n_es = _seed_country_units(cur, country="ES", patterns=_DENSE)
    assert n_es == 74

    capture.build(build, dsn=dsn)  # default country_code='ES'

    # Byte-identical: the country-blind count (no filter) equals the ES-scoped read -- only
    # ES exists, so the country dimension changes nothing.
    blind = _fetch(
        dsn,
        "SELECT COUNT(DISTINCT resolved_ulid) FROM discovery_capture WHERE build_run_id = %s",
        (build,),
    )[0][0]
    es_pat, _ = capture.read_patterns(build, dsn=dsn)  # default country_code='ES'
    assert blind == 74 and _stratum_units(es_pat, "28", "compraventa") == 74, (
        f"ES REGRESSION: country-blind capture {blind} != ES-scoped 74 "
        f"({_stratum_units(es_pat, '28', 'compraventa')}); the country dimension perturbed "
        "the sole tenant's capture matrix.")

    seal.compute(build, dsn=dsn, external_census={})  # default country_code='ES'
    rows = _fetch(
        dsn,
        "SELECT n_obs, country_code FROM exhaustiveness_estimate "
        "WHERE build_run_id = %s AND province_code = '28' AND segment = 'compraventa'",
        (build,),
    )
    assert rows and rows[0][0] == 74 and rows[0][1].strip() == "ES", (
        f"ES REGRESSION: default seal wrote {rows} (expected n_obs=74, country 'ES').")
    countries = {r[0].strip() for r in _fetch(
        dsn, "SELECT country_code FROM exhaustiveness_estimate WHERE build_run_id = %s",
        (build,))}
    assert countries == {"ES"}, f"BYTE-IDENTICAL BREAK: default build wrote {countries}"

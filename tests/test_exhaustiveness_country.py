"""
tests/test_exhaustiveness_country.py

GOLDEN -- the EXHAUSTIVENESS *pipeline* country-scope (generic-engine vector #5,
the WRITE/READ side, the twin of tests/test_country_isolation_seal.py which pins
the *served* VIEW side).

360-B / migration 0060 country-scoped the SERVED surface: ``exhaustiveness_estimate``
got a ``country_code`` column (DEFAULT 'ES'), ``v_exhaustiveness_seal`` projects it
with a PER-COUNTRY ``latest`` build, and ``/geo/exhaustiveness`` filters by it. But
the PIPELINE that COMPUTES the certificate stayed country-blind:

  (a) ``pipeline/exhaustiveness/seal.py::_persist`` -- its two INSERTs OMIT
      ``country_code``, so EVERY persisted row (per-stratum AND the national roll-up)
      silently falls to the column DEFAULT 'ES'. A second-tenant build (country='DE')
      would therefore WRITE its German coverage under 'ES' -- the served view would
      then leak DE rows into the ES scope and serve NOTHING under 'DE'.

  (b) ``pipeline/exhaustiveness/report.py::coverage_report`` -- it neither SELECTs nor
      FILTERs ``country_code``. With two tenants present it pools both: the single
      ``national`` slot (province + segment NULL) is overwritten by whichever country's
      national row sorts first, and ``strata`` mixes both countries' provinces.

WHY "country of the run", not "province -> country": the province code space COLLIDES
across tenants by design (``migrations/0053`` puts DE province '28' next to ES Madrid
'28') and ``geo_province``'s PK is the single column ``code`` (0052), so a province ->
country lookup is NOT a function -- it cannot separate ES '28' from DE '28'. The capture
matrix (``discovery_capture``, 0048) carries no country column either. The only sound
source is the COUNTRY OF THE BUILD RUN, exactly as migration 0060's own comment mandates:
"pipeline/exhaustiveness/seal.py's INSERT omits the column ... a per-country build sets
it explicitly when a 2nd tenant exists."

WHAT IS ASSERTED
----------------
  compute(DE)  : the REAL seal.compute(build, country_code='DE') stamps EVERY persisted
                 row (strata + national) with 'DE', never the DEFAULT 'ES'. RED today:
                 seal.compute has no country_code seam -- the engine cannot name a tenant.
  compute(ES)  : the no-arg / default path still writes 'ES' (byte-identical to the
                 historical DEFAULT). Regression lock.
  report scope : coverage_report(country_code=X) returns ONLY country X's national +
                 strata; the two tenants never pool. RED today (no country_code seam).
  report default: coverage_report() (the historical signature) defaults to ES and, with a
                 NEWER bigger DE build also present, returns the ES national + ES strata
                 ONLY -- never the German rows. PURE-ASSERTION RED today (it pools / mislabels).
  byte-identical: with ONLY ES seeded, coverage_report() equals the historical
                 country-blind view query field-for-field. Regression lock.

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). It HARD-REFUSES :5433
(live production) two ways -- by DSN string and by asserting the live census (``entity``)
is EMPTY before seeding. seal.compute / coverage_report open their OWN connections, so the
seeds are COMMITTED (not a rolled-back txn); the fixture therefore touches ONLY the three
pipeline-owned tables (discovery_list / discovery_capture / exhaustiveness_estimate),
scrubbing every ``GOLDEN-CC-%`` build it created on the way in AND out -- the protected
census table ``entity`` is never written, staying byte-identical at 0.
"""
from __future__ import annotations

import os

import psycopg2
import pytest

from pipeline.exhaustiveness import report, seal

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Every build id this golden creates shares this prefix, so cleanup is a single
# LIKE scrub that can never reach a real build.
_BUILD_PREFIX = "GOLDEN-CC-"

# The 3 orthogonal MSE lists the synthetic capture matrix populates (bit order).
_BUCKETS3 = ("GEO", "CENSUS", "DGT")

pytestmark = pytest.mark.integration


# ===========================================================================
# Dry-run plumbing + COMMIT-and-scrub isolation (compute/report use own conns)
# ===========================================================================
def _target_dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


def _db_reachable(dsn: str) -> bool:
    try:
        psycopg2.connect(dsn, connect_timeout=3).close()
        return True
    except Exception:
        return False


def _scrub(cur, added_list_keys: set[str]) -> None:
    """Delete everything this golden created (FK child -> parent order)."""
    cur.execute(
        "DELETE FROM exhaustiveness_estimate WHERE build_run_id LIKE %s",
        (_BUILD_PREFIX + "%",),
    )
    cur.execute(
        "DELETE FROM discovery_capture WHERE build_run_id LIKE %s",
        (_BUILD_PREFIX + "%",),
    )
    if added_list_keys:
        cur.execute(
            "DELETE FROM discovery_list WHERE list_key = ANY(%s)",
            (list(added_list_keys),),
        )


@pytest.fixture
def dryrun():
    """Yield (dsn, autocommit conn) on the dry-run DB; scrub GOLDEN-CC-% on entry+exit.

    Isolation guard against the live census:
      1. refuse any DSN pointing at :5433;
      2. skip if the DB is unreachable;
      3. refuse to seed unless the live ``entity`` table is EMPTY (dry-run is 0;
         production holds ~452k) -- a mis-pointed DSN can never mutate real data.
    Cleanup deletes only discovery_list keys this golden ADDED (keys already present
    before the test are preserved), keeping the three pipeline tables byte-identical.
    """
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip(
            "refusing to run the exhaustiveness-pipeline country golden against "
            ":5433 (live production); point CARDEEP_DSN at the :5434 dry-run")
    if not _db_reachable(dsn):
        pytest.skip(f"dry-run cardeep-pg not reachable at {dsn}")

    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM entity")
        if cur.fetchone()[0] != 0:
            conn.close()
            pytest.skip(
                "target DB has a populated entity census -- not the empty dry-run; "
                "refusing to seed against real data")
        cur.execute("SELECT list_key FROM discovery_list")
        pre_keys = {r[0] for r in cur.fetchall()}
        # list keys this golden will add (only the ones not already present)
        added_keys = {k for k in _BUCKETS3 if k not in pre_keys}
        _scrub(cur, added_keys)  # pre-clean any residue from a crashed prior run
    try:
        yield dsn, conn
    finally:
        with conn.cursor() as cur:
            _scrub(cur, added_keys)
        conn.close()


# ---------------------------------------------------------------------------
# Seeding helpers
# ---------------------------------------------------------------------------
def _seed_lists(cur) -> None:
    """Ensure the orthogonal MSE lists referenced by discovery_capture exist."""
    for key in _BUCKETS3:
        cur.execute(
            "INSERT INTO discovery_list (list_key, orthogonality_class, description) "
            "VALUES (%s, %s, %s) ON CONFLICT (list_key) DO NOTHING",
            (key, f"class_{key}", f"golden synthetic list {key}"),
        )


def _seed_capture(cur, *, build: str, patterns: dict[tuple[int, ...], int],
                  province: str = "28", segment: str = "compraventa") -> int:
    """Materialise a capture-recapture matrix: each pattern{bit-tuple: count} becomes
    ``count`` distinct resolved_ulids, each captured in the lists whose bit is 1.

    Returns n_obs (distinct resolved units) so the test can pin the national figure.
    """
    n_obs = 0
    for pat, cnt in patterns.items():
        for i in range(cnt):
            ru = f"{build}::u{''.join(map(str, pat))}::{i}"
            n_obs += 1
            for bit, bucket in zip(pat, _BUCKETS3):
                if bit:
                    cur.execute(
                        "INSERT INTO discovery_capture "
                        "(resolved_ulid, list_key, province_code, segment, build_run_id) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (ru, bucket, province, segment, build),
                    )
    return n_obs


def _seed_estimate_rows(cur, *, build: str, country: str, n_obs_national: int,
                        created_at_sql: str, province: str = "28",
                        segment: str = "compraventa") -> None:
    """Seed a 2-row certificate (national headline + one province stratum) DIRECTLY,
    mirroring tests/test_country_isolation_seal.py::_seed_exhaustiveness but with a
    caller-chosen national n_obs so a cross-country leak is detectable by value."""
    cur.execute(
        "INSERT INTO exhaustiveness_estimate "
        "(build_run_id, province_code, segment, k_lists, n_obs, n_hat, ci_low, ci_high, "
        " coverage_point, coverage_lower, method, confidence, seal_threshold, sealed, "
        " country_code, created_at) "
        f"VALUES (%s, NULL, NULL, 4, %s, %s, %s, %s, 0.83, 0.77, 'stratified_sum', "
        f"'high', 0.95, false, %s, {created_at_sql})",
        (build, n_obs_national, n_obs_national + 20, n_obs_national + 10,
         n_obs_national + 30, country),
    )
    cur.execute(
        "INSERT INTO exhaustiveness_estimate "
        "(build_run_id, province_code, segment, k_lists, n_obs, n_hat, ci_low, ci_high, "
        " coverage_point, coverage_lower, method, confidence, seal_threshold, sealed, "
        " country_code, created_at) "
        f"VALUES (%s, %s, %s, 3, 50, 60, 55, 65, 0.83, 0.77, 'chao2', "
        f"'high', 0.95, false, %s, {created_at_sql})",
        (build, province, segment, country),
    )


def _fetch(dsn: str, sql: str, params: tuple) -> list[tuple]:
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


# A dense 3-list overlap -> an identified stratum (n_obs = 74).
_DENSE = {
    (1, 1, 1): 20, (1, 1, 0): 10, (1, 0, 1): 10, (0, 1, 1): 10,
    (1, 0, 0): 8, (0, 1, 0): 8, (0, 0, 1): 8,
}


# ===========================================================================
# compute(): _persist stamps the RUN country on every row (the core bug)
# ===========================================================================
def test_compute_persist_stamps_run_country_de(dryrun):
    """seal.compute(build, country_code='DE') must write 'DE' on EVERY persisted row
    -- the per-stratum rows AND the national roll-up. RED today: seal.compute has no
    country_code seam, so the rows fall to the column DEFAULT 'ES' (a German build
    persisted as Spanish)."""
    dsn, conn = dryrun
    build = _BUILD_PREFIX + "COMPUTE-DE"
    with conn.cursor() as cur:
        _seed_lists(cur)
        _seed_capture(cur, build=build, patterns=_DENSE)

    seal.compute(build, dsn=dsn, country_code="DE", external_census={})

    rows = _fetch(
        dsn,
        "SELECT province_code, segment, country_code "
        "FROM exhaustiveness_estimate WHERE build_run_id = %s",
        (build,),
    )
    assert rows, "seal.compute persisted no exhaustiveness_estimate rows for the DE build"
    countries = {r[2].strip() for r in rows}
    assert countries == {"DE"}, (
        f"COUNTRY-BLIND PERSIST: the DE build wrote country_code(s) {countries} "
        "(expected only 'DE'). 'ES' means _persist omitted country_code and the row "
        "fell to the DEFAULT -- German coverage silently filed as Spanish.")
    assert any(r[0] is None and r[1] is None for r in rows), (
        "the national roll-up row (province + segment NULL) was not persisted")


def test_compute_persist_default_country_is_es_byte_identical(dryrun):
    """The historical no-country call path must still write 'ES' (byte-identical to the
    pre-fix DEFAULT). Locks the sole-tenant invariant: a build that names no country, or
    names 'ES', is indistinguishable from today's output."""
    dsn, conn = dryrun
    build = _BUILD_PREFIX + "COMPUTE-ES"
    with conn.cursor() as cur:
        _seed_lists(cur)
        _seed_capture(cur, build=build, patterns=_DENSE)

    # No country_code kwarg -> must default to 'ES' exactly like the DB column DEFAULT.
    seal.compute(build, dsn=dsn, external_census={})

    rows = _fetch(
        dsn,
        "SELECT country_code FROM exhaustiveness_estimate WHERE build_run_id = %s",
        (build,),
    )
    assert rows, "seal.compute persisted no rows for the ES build"
    countries = {r[0].strip() for r in rows}
    assert countries == {"ES"}, (
        f"BYTE-IDENTICAL BREAK: the default (no-country) build wrote {countries} "
        "(expected only 'ES'); the sole-tenant path must equal the historical DEFAULT.")


# ===========================================================================
# report(): coverage_report is scoped to one tenant, never pooled
# ===========================================================================
def test_coverage_report_scoped_by_country(dryrun):
    """coverage_report(country_code=X) returns ONLY country X's national + strata.
    Two tenants seeded (ES older, DE newer + bigger); each scope sees only its own
    figures. RED today: coverage_report has no country_code seam (and pools both)."""
    dsn, conn = dryrun
    es_build = _BUILD_PREFIX + "REP-ES"
    de_build = _BUILD_PREFIX + "REP-DE"
    with conn.cursor() as cur:
        _seed_estimate_rows(cur, build=es_build, country="ES", n_obs_national=100,
                            created_at_sql="now() - interval '2 hours'")
        _seed_estimate_rows(cur, build=de_build, country="DE", n_obs_national=200,
                            created_at_sql="now()")

    rep_es = report.coverage_report(dsn=dsn, country_code="ES")
    rep_de = report.coverage_report(dsn=dsn, country_code="DE")

    assert rep_es["national"] is not None and rep_de["national"] is not None
    assert rep_es["national"]["country_code"].strip() == "ES"
    assert rep_de["national"]["country_code"].strip() == "DE"
    assert rep_es["national"]["n_obs"] == 100, (
        f"ES scope national n_obs={rep_es['national']['n_obs']} (expected 100 -- the ES "
        "build); a different value means the DE certificate leaked into the ES scope.")
    assert rep_de["national"]["n_obs"] == 200, rep_de["national"]
    assert all(s["country_code"].strip() == "ES" for s in rep_es["strata"]), (
        f"ES report strata leaked a foreign country: {rep_es['strata']}")
    assert all(s["country_code"].strip() == "DE" for s in rep_de["strata"]), (
        f"DE report strata leaked a foreign country: {rep_de['strata']}")


def test_coverage_report_default_is_es_and_excludes_newer_de(dryrun):
    """coverage_report() (the historical signature, no kwarg) must default to ES and,
    with a NEWER bigger DE certificate also present, return the ES national + ES strata
    ONLY. PURE-ASSERTION RED today: country-blind, it pools both -- the national slot is
    overwritten by the bigger DE row and the strata list carries the German province."""
    dsn, conn = dryrun
    es_build = _BUILD_PREFIX + "DEF-ES"
    de_build = _BUILD_PREFIX + "DEF-DE"
    with conn.cursor() as cur:
        _seed_estimate_rows(cur, build=es_build, country="ES", n_obs_national=100,
                            created_at_sql="now() - interval '2 hours'")
        _seed_estimate_rows(cur, build=de_build, country="DE", n_obs_national=200,
                            created_at_sql="now()")

    rep = report.coverage_report(dsn=dsn)  # historical call -> must mean country='ES'

    assert rep["national"] is not None, "default report lost the national headline"
    assert rep["national"].get("country_code", "").strip() == "ES", (
        f"DEFAULT-SCOPE LEAK: coverage_report() national country_code="
        f"{rep['national'].get('country_code')!r} (expected 'ES'). A missing/foreign "
        "value means the report is country-blind and pooled the German certificate.")
    assert rep["national"]["n_obs"] == 100, (
        f"DEFAULT-SCOPE LEAK: coverage_report() national n_obs={rep['national']['n_obs']} "
        "(expected 100 -- the ES build). 200 means the bigger NEWER German national "
        "overwrote the Spanish headline.")
    assert rep["n_strata"] == 1, (
        f"DEFAULT-SCOPE LEAK: coverage_report() returned {rep['n_strata']} strata "
        "(expected 1 -- ES only). 2 means the German province '28' was pooled in.")
    assert all(s.get("country_code", "").strip() == "ES" for s in rep["strata"]), (
        f"DEFAULT-SCOPE LEAK: default report strata carried a foreign country: "
        f"{rep['strata']}")


def test_coverage_report_es_byte_identical_vs_country_blind(dryrun):
    """With ONLY ES seeded, coverage_report() returns exactly what the historical
    country-blind view query returns, field-for-field. The country dimension must not
    perturb the sole tenant's report. Regression lock (passes pre- and post-fix)."""
    dsn, conn = dryrun
    es_build = _BUILD_PREFIX + "BI-ES"
    with conn.cursor() as cur:
        _seed_estimate_rows(cur, build=es_build, country="ES", n_obs_national=100,
                            created_at_sql="now()")

    rep = report.coverage_report(dsn=dsn)

    # The historical country-blind projection (the pre-0060 reader's exact columns).
    blind = _fetch(
        dsn,
        "SELECT province_code, segment, k_lists, n_obs, n_hat, ci_low, ci_high, "
        "coverage_point, coverage_lower, method, confidence, seal_threshold, sealed "
        "FROM v_exhaustiveness_seal "
        "ORDER BY (province_code IS NULL) DESC, n_obs DESC",
        (),
    )
    cols = [
        "province_code", "segment", "k_lists", "n_obs", "n_hat", "ci_low",
        "ci_high", "coverage_point", "coverage_lower", "method", "confidence",
        "seal_threshold", "sealed",
    ]
    blind_rows = [dict(zip(cols, r)) for r in blind]
    blind_national = next(
        (d for d in blind_rows if d["province_code"] is None and d["segment"] is None),
        None,
    )
    blind_strata = [
        d for d in blind_rows
        if not (d["province_code"] is None and d["segment"] is None)
    ]

    # Compare only the historical fields (the report additively gained country_code).
    def _proj(d: dict) -> dict:
        return {k: d[k] for k in cols}

    assert blind_national is not None and rep["national"] is not None
    assert _proj(rep["national"]) == blind_national, (
        "ES REGRESSION: country-scoped report national != country-blind national "
        f"({_proj(rep['national'])} != {blind_national})")
    assert [_proj(s) for s in rep["strata"]] == blind_strata, (
        "ES REGRESSION: country-scoped report strata != country-blind strata")
    assert rep["n_strata"] == len(blind_strata)

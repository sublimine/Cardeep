"""
tests/test_analytic_province_width.py

GOLDEN -- ANALYTIC province_code WIDTH (schema-genericity follow-up, migration 0061).

Project 360-A/F1 widened the GEO backbone province family CHAR(2) -> VARCHAR(8)
(migration 0059, tests/test_geo_width_multicountry.py). Two ANALYTIC stratum-dimension
columns were OUTSIDE that geo-FK scope and stayed CHAR(2), so they would reject a
non-ES province whose code exceeds 2 chars (e.g. France's overseas department '971'
Guadeloupe):

  discovery_capture.province_code        (migrations/0048_discovery_capture.sql:39)
                                         -- capture-recapture stratum dimension 1
  exhaustiveness_estimate.province_code  (migrations/0048_discovery_capture.sql:58)
                                         -- per-stratum MSE estimate key (NULL => national)

Neither carries a geo FK or CHECK (they are free-text stratum labels, NOT geo_province
referrers), so they were invisible to the 0059 geo-FK widening. Migration 0061 widens
both to VARCHAR(8) -- additive and ES byte-identical (every ES province code is exactly
2 chars, so the CHAR(2)->VARCHAR(8) cast is 1:1 with no padding to strip).

This golden is RED before 0061 (the 3-char INSERTs raise psycopg2.DataError 'value too
long for type character(2)'; the column-type assertion sees 'character'; the ES padding
guard sees bpchar's trailing-space-insensitive equality) and GREEN after it (FR DOM '971'
ENTERS both analytic tables and the ES 2-char code round-trips byte-identical under the
new varchar exact equality).

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). HARD-REFUSES :5433
(live production) by DSN string AND asserts the census (entity/vehicle) is empty before
seeding. Every test seeds inside a transaction and ROLLS BACK -- the dry-run stays
byte-identical (entity/vehicle stay 0; the analytic tables keep whatever they had).
"""
from __future__ import annotations

import os

import psycopg2
import pytest

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"


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
    """Transactional connection to the dry-run DB, rolled back on teardown.

    Triple isolation guard against the live census (identical to the 360-A / geo-width
    goldens):
      1. refuse any DSN pointing at :5433;
      2. skip if the DB is unreachable;
      3. refuse to seed unless BOTH ``entity`` and ``vehicle`` are EMPTY.
    """
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip(
            "refusing to run the analytic-width golden against :5433 (live production); "
            "point CARDEEP_DSN at the :5434 dry-run")
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
            f"target DB has {n_entities} entities / {n_vehicles} vehicles -- not the "
            "empty dry-run; refusing to seed against a populated census")
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


def _seed_discovery_list(cur, list_key: str) -> None:
    """A discovery_list row to satisfy discovery_capture.list_key's FK (the ONLY FK on
    discovery_capture). Rolled back with the rest, so ON CONFLICT keeps it re-runnable."""
    cur.execute(
        "INSERT INTO discovery_list (list_key, orthogonality_class, description) "
        "VALUES (%s, %s, %s) ON CONFLICT (list_key) DO NOTHING",
        (list_key, "GEO", f"golden list {list_key}"),
    )


def _seed_capture(cur, *, resolved_ulid: str, list_key: str, province: str,
                  segment: str, build_run_id: str) -> None:
    cur.execute(
        "INSERT INTO discovery_capture "
        "(resolved_ulid, list_key, province_code, segment, build_run_id) "
        "VALUES (%s, %s, %s, %s, %s)",
        (resolved_ulid, list_key, province, segment, build_run_id),
    )


def _seed_estimate(cur, *, build_run_id: str, province: str, segment: str) -> None:
    """A minimal exhaustiveness_estimate row: every NOT NULL column populated so the ONLY
    thing that can fail the INSERT is province_code's width (country_code defaults to 'ES')."""
    cur.execute(
        "INSERT INTO exhaustiveness_estimate "
        "(build_run_id, province_code, segment, k_lists, n_obs, n_hat, ci_low, ci_high, "
        " coverage_point, coverage_lower, method, confidence, seal_threshold, sealed) "
        "VALUES (%s, %s, %s, 3, 10, 12.0, 11.0, 13.0, 0.83, 0.77, 'chao', 'high', 0.9, false)",
        (build_run_id, province, segment),
    )


# ===========================================================================
# discovery_capture: FR DOM 3-digit province now fits (was CHAR(2) 'value too long')
# ===========================================================================
@pytest.mark.integration
def test_discovery_capture_province_971_enters(dry_conn):
    """CLOSE the gap: France's overseas department '971' (Guadeloupe, 3 digits) MUST seed
    into discovery_capture. RED pre-0061 (CHAR(2) 'value too long for type character(2)')."""
    with dry_conn.cursor() as cur:
        _seed_discovery_list(cur, "GEOW")
        _seed_capture(cur, resolved_ulid="ULID-FR-DOM-971", list_key="GEOW",
                      province="971", segment="compraventa", build_run_id="run-fr-971")
        cur.execute(
            "SELECT province_code, length(province_code) FROM discovery_capture "
            "WHERE build_run_id='run-fr-971' AND province_code='971'")
        row = cur.fetchone()
    assert row is not None, (
        "FR DOM province '971' did not store in discovery_capture (CHAR(2) gap still open)")
    assert row == ("971", 3), (
        f"discovery_capture.province_code stored {row[0]!r} (len {row[1]}); expected '971' (3)")


# ===========================================================================
# exhaustiveness_estimate: FR DOM 3-digit province now fits (was CHAR(2) too long)
# ===========================================================================
@pytest.mark.integration
def test_exhaustiveness_estimate_province_971_enters(dry_conn):
    """CLOSE the gap: '971' (3 digits) MUST seed into exhaustiveness_estimate's stratum key.
    RED pre-0061 (CHAR(2) 'value too long for type character(2)')."""
    with dry_conn.cursor() as cur:
        _seed_estimate(cur, build_run_id="run-fr-971", province="971", segment="compraventa")
        cur.execute(
            "SELECT province_code, length(province_code) FROM exhaustiveness_estimate "
            "WHERE build_run_id='run-fr-971' AND province_code='971'")
        row = cur.fetchone()
    assert row is not None, (
        "FR DOM province '971' did not store in exhaustiveness_estimate (CHAR(2) gap still open)")
    assert row == ("971", 3), (
        f"exhaustiveness_estimate.province_code stored {row[0]!r} (len {row[1]}); expected '971' (3)")


# ===========================================================================
# Full DDL surface: both analytic stratum columns are VARCHAR(8) after 0061.
# ===========================================================================
@pytest.mark.integration
def test_analytic_province_columns_widened(dry_conn):
    """Both analytic province_code columns are VARCHAR(8) after 0061. RED pre-0061
    (data_type='character', max_length 2)."""
    expected = {
        ("discovery_capture", "province_code"): ("character varying", 8),
        ("exhaustiveness_estimate", "province_code"): ("character varying", 8),
    }
    with dry_conn.cursor() as cur:
        cur.execute(
            "SELECT table_name, column_name, data_type, character_maximum_length "
            "FROM information_schema.columns "
            "WHERE (table_name, column_name) IN "
            "(('discovery_capture','province_code'),"
            " ('exhaustiveness_estimate','province_code'))")
        got = {(r[0], r[1]): (r[2], r[3]) for r in cur.fetchall()}
    assert got == expected, (
        f"analytic province_code columns not widened as expected.\n got={got}\n exp={expected}")


# ===========================================================================
# ES byte-identity (STEP 4): a CHAR->VARCHAR widening must NOT change ES semantics.
# An exact-width ES code carries NO trailing-space padding and compares identically.
# ===========================================================================
@pytest.mark.integration
def test_es_exact_width_province_byte_identical(dry_conn):
    """ES province '28' (2 chars) must round-trip byte-identical in BOTH analytic tables
    after the widening: exact length 2, NO trailing-space padding, exact equality. This is
    the CHAR(2)->VARCHAR(8) regression STEP 4 guards -- VARCHAR never pads, and an exact-width
    ES value had no padding under CHAR either, so the stored bytes are identical. RED pre-0061
    on the padding assertion only (bpchar '28' = '28 ' is TRUE; varchar makes it FALSE)."""
    with dry_conn.cursor() as cur:
        _seed_discovery_list(cur, "GEOE")
        _seed_capture(cur, resolved_ulid="ULID-ES-28", list_key="GEOE",
                      province="28", segment="compraventa", build_run_id="run-es-28")
        cur.execute(
            "SELECT province_code, length(province_code), province_code='28', province_code='28 ' "
            "FROM discovery_capture WHERE build_run_id='run-es-28'")
        c_code, c_len, c_eq, c_padded = cur.fetchone()
        _seed_estimate(cur, build_run_id="run-es-28", province="28", segment="compraventa")
        cur.execute(
            "SELECT province_code, length(province_code), province_code='28', province_code='28 ' "
            "FROM exhaustiveness_estimate WHERE build_run_id='run-es-28'")
        e_code, e_len, e_eq, e_padded = cur.fetchone()
    assert (c_code, c_len, c_eq) == ("28", 2, True), (
        f"ES discovery_capture province '28' not byte-identical: {c_code!r} len {c_len}")
    assert c_padded is False, (
        "ES discovery_capture '28' must NOT equal padded '28 ' (varchar, no CHAR padding)")
    assert (e_code, e_len, e_eq) == ("28", 2, True), (
        f"ES exhaustiveness_estimate province '28' not byte-identical: {e_code!r} len {e_len}")
    assert e_padded is False, (
        "ES exhaustiveness_estimate '28' must NOT equal padded '28 ' (varchar, no CHAR padding)")

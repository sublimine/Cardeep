"""
tests/test_geo_width_multicountry.py

GOLDEN -- geo code WIDTH, multi-country (Project F1, closes 360-A OPEN-A + OPEN-B).

Project 360-A (test_country_isolation_multicountry.py) proved the country-scope but
LOCKED two width gaps as explicit, regression-tracked guards because widening the geo
backbone was out of that test's surgical scope:

  (A) geo_province.code CHAR(2) cannot store France's 3-digit overseas department codes
      (DOM '971' Guadeloupe .. '976' Mayotte) -> PostgreSQL 'value too long'.
  (B) geo_municipality.code CHAR(5) cannot store Italy's 6-digit ISTAT comune codes
      (Roma '058091', Milano '015146')        -> PostgreSQL 'value too long'.

Migration 0059_geo_code_width.sql closes both by widening the geo identity AND every
FK-referrer column from the ES-sized CHAR(2)/CHAR(5) to VARCHAR(8)/VARCHAR(16), keeping
the composite PK (country_code, code), all 6 composite FKs, and the two ES-guarded CHECKs.

This golden is RED before 0059 (the wide INSERTs raise psycopg2.DataError 'value too
long'; the column-type assertion sees 'character') and GREEN after it (the real FR DOM
and IT ISTAT codes ENTER, every FK-referrer accepts the wide code, and the FK chain still
resolves). It also pins ES exact-width byte-identity: a 2-char province / 5-char muni must
round-trip with NO trailing-space padding (the CHAR->VARCHAR risk STEP 4 guards against).

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). HARD-REFUSES :5433
(live production) by DSN string AND by asserting the target census is empty before
seeding. Every test seeds inside a transaction and ROLLS BACK -- the dry-run stays
byte-identical (entity/vehicle stay 0).
"""
from __future__ import annotations

import os

import psycopg2
import pytest

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Crockford base32 (no I, L, O, U) -- the alphabet entity_ulid_shape accepts.
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


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

    Triple isolation guard against the live census (identical to the 360-A goldens):
      1. refuse any DSN pointing at :5433;
      2. skip if the DB is unreachable;
      3. refuse to seed unless BOTH ``entity`` and ``vehicle`` are EMPTY.
    """
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip(
            "refusing to run the geo-width golden against :5433 (live production); "
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


def _ulid(tag: str) -> str:
    """Deterministic 26-char Crockford ULID from a safe tag (entity_ulid_shape)."""
    safe = "".join(c for c in tag.upper() if c in _CROCKFORD)
    return (safe + "0" * 26)[:26]


def _seed_province(cur, country: str, code: str) -> None:
    cur.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES (%s, %s, %s, %s, %s)",
        (code, f"prov-{country}-{code}", "97", f"reg-{country}", country),
    )


def _seed_municipality(cur, country: str, code: str, province: str) -> None:
    cur.execute(
        "INSERT INTO geo_municipality "
        "(code, name, province_code, comarca_id, country_code) "
        "VALUES (%s, %s, %s, NULL, %s)",
        (code, f"muni-{country}-{code}", province, country),
    )


def _seed_entity(cur, *, ulid_tag: str, cdp: str, country: str,
                 province: str, muni: str | None) -> str:
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " province_code, municipality_code, country_code, status) "
        "VALUES (%s, %s, 'compraventa', %s, %s, %s, %s, %s, 'active')",
        (ulid, cdp, f"dealer {country}", f"dealer {country}", province, muni, country),
    )
    return ulid


# ===========================================================================
# OPEN-A: FR DOM 3-digit province now fits (was CHAR(2) 'value too long')
# ===========================================================================
@pytest.mark.integration
def test_fr_dom_province_971_enters(dry_conn):
    """CLOSE gap (A): France's overseas department '971' (Guadeloupe, 3 digits) MUST seed
    into geo_province under country='FR'. RED pre-0059 (CHAR(2) 'value too long')."""
    with dry_conn.cursor() as cur:
        _seed_province(cur, "FR", "971")
        cur.execute(
            "SELECT code, length(code) FROM geo_province "
            "WHERE country_code='FR' AND code='971'")
        row = cur.fetchone()
    assert row is not None, "FR DOM province '971' did not store (gap A still open)"
    assert row[0] == "971" and row[1] == 3, (
        f"FR DOM province stored as {row[0]!r} (len {row[1]}); expected '971' (3)")


# ===========================================================================
# OPEN-B: IT ISTAT 6-digit comune now fits (was CHAR(5) 'value too long')
# ===========================================================================
@pytest.mark.integration
def test_it_istat_comune_058091_enters(dry_conn):
    """CLOSE gap (B): Italy's ISTAT comune '058091' (Roma, 6 digits) MUST seed into
    geo_municipality under country='IT' (province 'RM'). RED pre-0059 (CHAR(5) too long).
    The muni prefix CHECK is country-guarded to ES, so left('058091',2)='05' != 'RM' is OK."""
    with dry_conn.cursor() as cur:
        _seed_province(cur, "IT", "RM")
        _seed_municipality(cur, "IT", "058091", "RM")
        cur.execute(
            "SELECT code, length(code) FROM geo_municipality "
            "WHERE country_code='IT' AND code='058091'")
        row = cur.fetchone()
    assert row is not None, "IT ISTAT comune '058091' did not store (gap B still open)"
    assert row[0] == "058091" and row[1] == 6, (
        f"IT ISTAT comune stored as {row[0]!r} (len {row[1]}); expected '058091' (6)")


# ===========================================================================
# FK chain holds with wide codes (province family): entity + geo_municipality
# referrers accept >2-char province; composite FKs resolve.
# ===========================================================================
@pytest.mark.integration
def test_fk_chain_resolves_wide_province_fr_dom(dry_conn):
    """The whole province FK chain must resolve with a 3-char code: geo_province(FR,'971')
    <- geo_municipality(FR,'97101', province '971') <- entity(FR, province '971',
    muni '97101'). Proves geo_municipality.province_code AND entity.province_code widened
    and that geo_municipality_province_code_fkey / entity_province_code_fkey still resolve."""
    with dry_conn.cursor() as cur:
        _seed_province(cur, "FR", "971")
        _seed_municipality(cur, "FR", "97101", "971")  # FK (FR,'971') -> geo_province
        ent = _seed_entity(cur, ulid_tag="FRDOM1", cdp="CDP-FR-971-FRDOM001",
                           country="FR", province="971", muni="97101")
        cur.execute(
            "SELECT province_code, municipality_code FROM entity WHERE entity_ulid=%s",
            (ent,))
        row = cur.fetchone()
    assert row == ("971", "97101"), (
        f"entity stored ({row[0]!r},{row[1]!r}); expected ('971','97101') -- the wide "
        "province FK chain did not resolve")


# ===========================================================================
# FK chain holds with wide codes (municipality family): entity referrer accepts
# 6-char muni; entity_municipality_code_fkey resolves to the ISTAT comune.
# ===========================================================================
@pytest.mark.integration
def test_fk_chain_resolves_wide_municipality_it_istat(dry_conn):
    """entity.municipality_code must accept the 6-digit ISTAT comune and its composite FK
    must resolve: geo_province(IT,'RM') <- geo_municipality(IT,'058091') <- entity(IT,
    province 'RM', muni '058091'). chk_entity_muni_province is ES-guarded, so the IT row
    (left('058091',2)='05' != 'RM') is accepted."""
    with dry_conn.cursor() as cur:
        _seed_province(cur, "IT", "RM")
        _seed_municipality(cur, "IT", "058091", "RM")
        ent = _seed_entity(cur, ulid_tag="ITRM1", cdp="CDP-IT-RM-ITRM0001",
                           country="IT", province="RM", muni="058091")
        cur.execute(
            "SELECT municipality_code, length(municipality_code) FROM entity "
            "WHERE entity_ulid=%s", (ent,))
        row = cur.fetchone()
    assert row == ("058091", 6), (
        f"entity.municipality_code stored {row[0]!r} (len {row[1]}); expected '058091' (6)")


# ===========================================================================
# Full DDL surface: every FK-referrer column is widened to the same VARCHAR type.
# Covers the referrers not exercised by a functional INSERT above
# (geo_comarca.province_code, denominator_estimate.province_code, organization.hq_province_code).
# ===========================================================================
@pytest.mark.integration
def test_all_geo_code_columns_widened(dry_conn):
    """Every column in the geo FK chain is VARCHAR after 0059: the province family at
    width 8, the municipality family at width 16. RED pre-0059 (data_type='character')."""
    expected = {
        ("geo_province", "code"): ("character varying", 8),
        ("geo_comarca", "province_code"): ("character varying", 8),
        ("geo_municipality", "province_code"): ("character varying", 8),
        ("entity", "province_code"): ("character varying", 8),
        ("denominator_estimate", "province_code"): ("character varying", 8),
        ("organization", "hq_province_code"): ("character varying", 8),
        ("geo_municipality", "code"): ("character varying", 16),
        ("entity", "municipality_code"): ("character varying", 16),
    }
    with dry_conn.cursor() as cur:
        cur.execute(
            "SELECT table_name, column_name, data_type, character_maximum_length "
            "FROM information_schema.columns "
            "WHERE (table_name, column_name) IN "
            "(('geo_province','code'),('geo_comarca','province_code'),"
            " ('geo_municipality','code'),('geo_municipality','province_code'),"
            " ('entity','province_code'),('entity','municipality_code'),"
            " ('denominator_estimate','province_code'),('organization','hq_province_code'))")
        got = {(r[0], r[1]): (r[2], r[3]) for r in cur.fetchall()}
    assert got == expected, (
        f"geo code columns not all widened as expected.\n got={got}\n exp={expected}")


# ===========================================================================
# ES byte-identity (STEP 4): a CHAR->VARCHAR widening must NOT change ES semantics.
# An exact-width ES code carries NO trailing-space padding and compares identically.
# ===========================================================================
@pytest.mark.integration
def test_es_exact_width_codes_byte_identical(dry_conn):
    """ES province '28' (2 chars) and muni '28079' (5 chars) must round-trip byte-identical
    after the widening: exact length, NO trailing-space padding, exact equality. This is the
    CHAR(n)->VARCHAR(n) regression STEP 4 guards -- VARCHAR never pads, and an exact-width ES
    value had no padding under CHAR either, so the stored bytes are identical."""
    with dry_conn.cursor() as cur:
        _seed_province(cur, "ES", "28")
        _seed_municipality(cur, "ES", "28079", "28")
        cur.execute(
            "SELECT code, length(code), code='28', code='28 ' "
            "FROM geo_province WHERE country_code='ES' AND code='28'")
        p_code, p_len, p_eq, p_padded = cur.fetchone()
        cur.execute(
            "SELECT code, length(code), code='28079' "
            "FROM geo_municipality WHERE country_code='ES' AND code='28079'")
        m_code, m_len, m_eq = cur.fetchone()
    assert (p_code, p_len, p_eq) == ("28", 2, True), (
        f"ES province '28' not byte-identical: {p_code!r} len {p_len}")
    assert p_padded is False, "ES province '28' must NOT equal padded '28 ' (no CHAR padding)"
    assert (m_code, m_len, m_eq) == ("28079", 5, True), (
        f"ES muni '28079' not byte-identical: {m_code!r} len {m_len}")

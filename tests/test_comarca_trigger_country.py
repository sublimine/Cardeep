"""Country-proof (red-team R2 #7): entity_set_comarca() trigger must scope by country.

migration 0018's trigger resolved entity.comarca_id with `WHERE m.code = NEW.municipality_code`
alone. geo_municipality's PK is (country_code, code) and migration 0053 lets ES INE and FR/DE
codes (both 5-digit) collide, so a non-ES entity whose municipality_code matched a Spanish INE
inherited a Spanish comarca_id (comarca is an ES-specific INE layer). Migration 0063 adds
`AND m.country_code = NEW.country_code`. ES behaviour is byte-identical (every ES entity already
matched its own ES row); a non-ES entity now gets its own country's comarca (or NULL).
"""
import os

import psycopg2
import pytest

_DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
pytestmark = pytest.mark.skipif("5433" in _DSN, reason="needs the :5434 dry-run; refuses live :5433")

_CROCK = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # Crockford base32 (no I/L/O/U)


def _ulid(tag: str) -> str:
    base = "".join(c for c in tag.upper() if c in _CROCK)
    return (base + "0" * 26)[:26]


@pytest.fixture
def conn():
    c = psycopg2.connect(_DSN)
    try:
        yield c
    finally:
        c.rollback()
        c.close()


def _seed_province(cur, country, province):
    cur.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES (%s,%s,'13',%s,%s) ON CONFLICT DO NOTHING",
        (province, f"prov-{country}-{province}", f"ccaa-{country}", country))


def _seed_comarca(cur, country, province, name):
    cur.execute(
        "INSERT INTO geo_comarca (province_code, name, country_code) VALUES (%s,%s,%s) RETURNING id",
        (province, name, country))
    return cur.fetchone()[0]


def _seed_muni(cur, country, province, muni, comarca_id):
    cur.execute(
        "INSERT INTO geo_municipality (code, name, province_code, comarca_id, country_code) "
        "VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
        (muni, f"muni-{country}-{muni}", province, comarca_id, country))


def _insert_entity_get_comarca(cur, tag, cdp, country, province, muni):
    cur.execute(
        "INSERT INTO entity (entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " province_code, municipality_code, country_code, status) "
        "VALUES (%s,%s,'compraventa',%s,%s,%s,%s,%s,'active')",
        (_ulid(tag), cdp, f"dealer {country}", f"dealer {country}", province, muni, country))
    cur.execute("SELECT comarca_id FROM entity WHERE entity_ulid = %s", (_ulid(tag),))
    return cur.fetchone()[0]


def test_comarca_trigger_is_country_scoped(conn):
    """ES and DE municipalities reuse code '28079' (0053 dup-code), each with its OWN comarca.
    A DE entity in '28079' must inherit the DE comarca, never the Spanish one. (The ES municipality
    is inserted first: the country-blind trigger's unqualified `WHERE code=...` seq-scans and
    returns it first — the leak the fix closes.)"""
    with conn.cursor() as cur:
        _seed_province(cur, "ES", "28")
        _seed_province(cur, "DE", "28")
        es_comarca = _seed_comarca(cur, "ES", "28", "Comarca ES Madrid")
        de_comarca = _seed_comarca(cur, "DE", "28", "Landkreis DE")
        _seed_muni(cur, "ES", "28", "28079", es_comarca)   # inserted FIRST
        _seed_muni(cur, "DE", "28", "28079", de_comarca)

        es_got = _insert_entity_get_comarca(cur, "CMKES1", "CDP-ES-28-CMKAAAA1", "ES", "28", "28079")
        de_got = _insert_entity_get_comarca(cur, "CMKDE2", "CDP-DE-28-CMKBBBB2", "DE", "28", "28079")

        assert es_got == es_comarca, f"ES entity must inherit its ES comarca (got {es_got!r}, want {es_comarca!r})"
        assert de_got == de_comarca, (
            f"CROSS-COUNTRY COMARCA LEAK: DE entity in muni '28079' got comarca {de_got!r}; "
            f"must be its own DE comarca {de_comarca!r}, never the Spanish {es_comarca!r}.")
        conn.rollback()

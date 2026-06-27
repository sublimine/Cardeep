"""Country-proof (exhaustive sweep): backfill_comarca.py must scope its comarca writes to ES.

Comarca is the ES-only INE comarca-agraria layer. The one-off backfill resolved geo by
municipality_code ALONE (`UPDATE geo_municipality ... WHERE code`, and `UPDATE entity ... JOIN
geo_municipality ON code`), so a non-ES municipality/entity sharing a 5-digit code (0053
dup-code coexistence) inherited a Spanish comarca — `comarca_id` FK is simple (`→ geo_comarca(id)`,
NOT composite) so there is no fail-closed backstop. The live path (`entity_set_comarca` trigger)
was fixed in 0063; this golden locks the backfill twin. The cross-entity propagation is the worst
leak, and it is DETERMINISTIC: the `m.comarca_id IS NOT NULL` filter drops the non-ES (NULL-comarca)
row, leaving only the ES municipality to join — so a DE entity reliably inherits the ES comarca
under the blind query, and reliably gets NULL under the country-scoped one.
"""
import os
import pathlib

import psycopg2
import pytest

_DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
pytestmark = pytest.mark.skipif("5433" in _DSN, reason="needs the :5434 dry-run; refuses live :5433")

_CROCK = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _ulid(tag: str) -> str:
    base = "".join(c for c in tag.upper() if c in _CROCK)
    return (base + "0" * 26)[:26]


_BLIND_SQL = """
    UPDATE entity e SET comarca_id = m.comarca_id
      FROM geo_municipality m
     WHERE e.municipality_code = m.code AND m.comarca_id IS NOT NULL"""

# The exact statement backfill_comarca.py runs after the fix (kept in lockstep with the script).
_SCOPED_SQL = """
    UPDATE entity e SET comarca_id = m.comarca_id
      FROM geo_municipality m
     WHERE e.municipality_code = m.code
       AND m.country_code = e.country_code
       AND m.comarca_id IS NOT NULL"""


@pytest.fixture
def conn():
    c = psycopg2.connect(_DSN)
    try:
        yield c
    finally:
        c.rollback()
        c.close()


def _seed(cur):
    for cc in ("ES", "DE"):
        cur.execute("INSERT INTO geo_province (code,name,ccaa_code,ccaa_name,country_code) "
                    "VALUES ('28',%s,'13',%s,%s) ON CONFLICT DO NOTHING", (f"p-{cc}", f"c-{cc}", cc))
    cur.execute("INSERT INTO geo_comarca (province_code,name,country_code) VALUES ('28','Comarca ES','ES') RETURNING id")
    es_comarca = cur.fetchone()[0]
    cur.execute("INSERT INTO geo_municipality (code,name,province_code,comarca_id,country_code) "
                "VALUES ('28079','m-ES','28',%s,'ES') ON CONFLICT DO NOTHING", (es_comarca,))
    cur.execute("INSERT INTO geo_municipality (code,name,province_code,comarca_id,country_code) "
                "VALUES ('28079','m-DE','28',NULL,'DE') ON CONFLICT DO NOTHING")
    for cc, cdp in (("ES", "CDP-ES-28-CMKBF001"), ("DE", "CDP-DE-28-CMKBF002")):
        cur.execute("INSERT INTO entity (entity_ulid,cdp_code,kind,trade_name,legal_name,"
                    "province_code,municipality_code,country_code,status) "
                    "VALUES (%s,%s,'compraventa',%s,%s,'28','28079',%s,'active')",
                    (_ulid("CMKBF" + cc), cdp, f"d-{cc}", f"d-{cc}", cc))
    cur.execute("UPDATE entity SET comarca_id = NULL")  # isolate the backfill query from the 0063 trigger
    return es_comarca


def test_blind_propagation_leaks_cross_country(conn):
    """Documents the bug the fix closes: the country-blind JOIN leaks the ES comarca to the DE entity."""
    with conn.cursor() as cur:
        es_comarca = _seed(cur)
        cur.execute(_BLIND_SQL)
        cur.execute("SELECT comarca_id FROM entity WHERE country_code = 'DE'")
        assert cur.fetchone()[0] == es_comarca, "expected the blind query to leak (regression oracle)"
        conn.rollback()


def test_scoped_propagation_is_country_clean(conn):
    """The fixed (country-scoped) JOIN: ES entity keeps its ES comarca, DE entity gets NULL."""
    with conn.cursor() as cur:
        es_comarca = _seed(cur)
        cur.execute(_SCOPED_SQL)
        cur.execute("SELECT country_code, comarca_id FROM entity ORDER BY country_code")
        got = dict(cur.fetchall())
        assert got["ES"] == es_comarca, f"ES entity must keep its ES comarca (got {got['ES']!r})"
        assert got["DE"] is None, f"COMARCA LEAK: DE entity got {got['DE']!r}, must be NULL"
        conn.rollback()


def test_backfill_script_source_is_country_scoped():
    """Anti-drift: the backfill's three geo writes must stay country-scoped."""
    src = pathlib.Path(__file__).resolve().parent.parent.joinpath(
        "scripts", "backfill_comarca.py").read_text(encoding="utf-8")
    assert "WHERE code = $1 AND country_code = 'ES'" in src, "geo_municipality UPDATE lost its country scope"
    assert "m.country_code = e.country_code" in src, "entity-propagation JOIN lost its country scope"
    assert "WHERE country_code = 'ES'" in src, "db_codes fetch lost its country scope"

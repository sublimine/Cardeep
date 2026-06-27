"""
tests/test_country_isolation_multicountry.py

GOLDEN -- ADVERSARIAL MULTI-COUNTRY country-proof (Project 360-A).

The ES<->DE goldens (test_country_isolation_{dealer,vehicle,dedup,beta,serving}.py)
prove the country-scope with a SYNTHETIC second tenant: DE deliberately reuses ES's
numeric province '28' / muni '28079'. That synthetic choice MASKS every assumption
that ES province codes are 2 DIGITS in 01-52: '28' satisfies the Spanish grid by
coincidence. This file stresses the engine with the REAL administrative grammars of
four genuine second countries and hunts the ES-baked assumptions the '28' shortcut hid:

  * FR  -- Corsica departments '2A'/'2B' (NON-numeric), Paris '75' (a real metropolitan
           department OUTSIDE the ES 01-52 grid), overseas DOM '971' (3 digits). Real
           code reuse: department '28' is Madrid (ES) AND Eure-et-Loir (FR).
  * IT  -- 2-letter provinces ('RM' Roma); cadastral comune 'H501' where
           left(code,2)='H5' != province 'RM' (breaks the ES INE <prov2><muni3> shape);
           ISTAT comune '058091' (6 digits).
  * PT  -- distrito '11' Lisboa + concelho '1106' (INE-shaped, fits the ES schema cleanly).
  * GR  -- a Greek-script dealer name (norm_name stress, non-latin alphabet).

It drives the REAL builds and asserts the invariant for each real grammar:
  cross-country identical (name | photo | deep_link | phone) -> MUST NOT merge
  same-country  identical                                    -> MUST     merge (no-reg)

TWO ES-baked served-identity gates this file CAUGHT and that are FIXED in the same
commit (both in pipeline/complete.py, vector #5's surface; the '28' synthetic masked
them because '28' is itself a valid ES province):
  (1) _CDP_CODE_RE province segment was [0-9]{2} -> it REJECTED the valid Corsican
      ('CDP-FR-2A-...') / Italian ('CDP-IT-RM-...') cdp_codes the mint legitimately
      emits. Now [0-9A-Z]{2} (ES 01-52 still matches byte-identically).
  (2) check_g1 validated province against the ES 01-52 grid for EVERY tenant (the gate
      query did not even fetch country_code) -> France (Paris '75', Corsica '2A') and
      Italy ('RM') wrongly FAILED identity. Now country-scoped: ES keeps 01-52
      byte-identical; a non-ES tenant validates the generic 2-char geo_province.code shape.

THREE genericity gaps CAUGHT and DOCUMENTED (not fixed here -- each is a large
geo-backbone migration or a transliteration swap, outside this test's surgical scope;
locked below as guards so the limit is EXPLICIT and regression-tracked, never silent):
  (A) geo_province.code CHAR(2) cannot store FR DOM '971'   -> "value too long".
  (B) geo_municipality.code CHAR(5) cannot store IT '058091' -> "value too long".
  (C) norm_name (NFKD + ascii-fold) erases non-latin scripts: a pure Greek/Cyrillic
      name normalizes to None -> the name identity signal is DEAD for those tenants.

ISOLATION (inviolable): the DB tests run ONLY against the dry-run DB (:5434). They
HARD-REFUSE :5433 (live production) two ways -- by DSN string and by asserting the
target census is empty before seeding. Every DB test seeds inside a transaction and
ROLLS BACK, leaving the dry-run byte-identical (entity stays 0). The regex / norm /
G1-mock tests are pure unit (no DB).
"""
from __future__ import annotations

import os
from unittest.mock import AsyncMock

import psycopg2
import psycopg2.extras
import pytest

from pipeline.identity import cluster_dealers as cd
from pipeline.identity import cluster_vehicles as cv
from pipeline.identity import cross_source_dedup as csd
from scripts import build_canonical_dedup as bcd
from pipeline.complete import (
    check_g1,
    _CDP_CODE_RE,
    _PROVINCE_RE,
    _NON_ES_PROVINCE_RE,
)

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Crockford base32 (no I, L, O, U) -- the alphabet entity_ulid_shape accepts:
#   CHECK (entity_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$')
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


# ===========================================================================
# Connection + isolation guard (identical surface to the other country goldens)
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
      3. refuse to seed unless BOTH ``entity`` and ``vehicle`` are EMPTY (the dry-run
         holds 0/0; production holds ~452k entities) -- so a mis-pointed DSN can never
         mutate real data.
    """
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip(
            "refusing to run the multicountry-isolation golden against :5433 "
            "(live production); point CARDEEP_DSN at the :5434 dry-run")
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
            "empty dry-run; refusing to seed/cluster against a populated census")
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


# ===========================================================================
# Seeding helpers (FK + CHECK respecting) -- generalized to any real grammar
# ===========================================================================
def _ulid(tag: str) -> str:
    """Deterministic 26-char Crockford ULID from a safe tag (entity_ulid_shape)."""
    safe = "".join(c for c in tag.upper() if c in _CROCKFORD)
    return (safe + "0" * 26)[:26]


def _seed_geo(cur, country: str, province: str, muni: str) -> None:
    """Seed (country, province) then (country, muni). Order satisfies the composite FK
    geo_municipality(country_code, province_code) -> geo_province and the composite PKs
    (0053). The muni CHECK left(code,2)=province_code is country-guarded to ES (0053),
    so a non-ES non-prefix muni (e.g. IT 'H501' under province 'RM') is accepted."""
    cur.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
        (province, f"prov-{country}-{province}", "13", f"reg-{country}", country),
    )
    cur.execute(
        "INSERT INTO geo_municipality "
        "(code, name, province_code, comarca_id, country_code) "
        "VALUES (%s, %s, %s, NULL, %s) ON CONFLICT DO NOTHING",
        (muni, f"muni-{country}-{muni}", province, country),
    )


def _seed_entity(cur, *, ulid_tag: str, cdp: str, name: str, country: str,
                 province: str, muni: str, kind: str = "compraventa",
                 phone: str | None = None, website: str | None = None) -> str:
    """Insert one in-scope dealer (status='active') and return its entity_ulid."""
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
    cur.execute(
        "INSERT INTO entity_source (entity_ulid, source_key) VALUES (%s, %s)",
        (entity_ulid, source_key),
    )


def _seed_vehicle(cur, *, ulid_tag: str, entity_ulid: str, deep_link: str,
                  make: str = "seat", model: str = "leon", year: int = 2020,
                  km: int = 45000, price: float = 15000.0, title: str = "vehiculo",
                  photo_url: str | None = None) -> str:
    """Insert one in-scope vehicle (status defaults 'available', km>0 so the new-car
    guard never disables a signal) and return its vehicle_ulid."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO vehicle "
        "(vehicle_ulid, entity_ulid, deep_link, make, model, year, km, price, "
        " title, photo_url, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'available')",
        (ulid, entity_ulid, deep_link, make, model, year, km, price, title, photo_url),
    )
    return ulid


# --- REAL build drivers (the exact cores main() persists) -------------------
def _run_dealers(conn) -> dict[str, str]:
    entities = cd._load_entities(conn)
    det_edges = cd._build_deterministic_edges(entities)
    fuzzy_edges, _ms, _es = cd._load_fuzzy_sql_edges(conn, entities)
    rows = cd._build_cluster_table(entities, list(set(det_edges + fuzzy_edges)))
    return {r["entity_ulid"]: r["canonical_ulid"] for r in rows}


def _run_vehicles(conn) -> dict[str, str]:
    vehicles = cv._load_vehicles(conn)
    edges, edge_signal_map = cv._build_edges(vehicles)
    rows = cv._build_cluster_table(vehicles, edges, edge_signal_map)
    return {r["vehicle_ulid"]: r["canonical_vehicle_ulid"] for r in rows}


def _run_cross_source(conn) -> dict[str, str]:
    entities = csd._load_entities(conn, None)
    match_pairs = csd._build_cross_source_edges(entities)
    rows = csd._build_cluster_table(entities, match_pairs)
    return {r["entity_ulid"]: r["canonical_ulid"] for r in rows}


def _run_deeplink(conn) -> dict[str, list[str]]:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(bcd._DEEPLINK_CANON_SQL)
        rows = cur.fetchall()
    merge_components, _pe, _u, _x = bcd._build_deeplink_merge_graph(rows)
    return merge_components


def _deeplink_merged(mc: dict[str, list[str]], a: str, b: str) -> bool:
    return any(a in members and b in members for members in mc.values())


# Shared collision payloads.
_PHOTO = "https://cdn.oemfeed.example/auction/lot/multicountry777.jpg"


# ===========================================================================
# FR -- France: metropolitan (numeric, INE-shaped) + Corsica (non-numeric) + DOM width
# Real reuse: department '28' is Madrid (ES) AND Eure-et-Loir (FR). muni '28079' is a
# valid 5-digit code in both the Spanish INE and the French INSEE grammars.
# ===========================================================================
@pytest.mark.integration
def test_fr_metropolitan_dealer_name_muni_cross_country_do_not_merge(dry_conn):
    """ES (Madrid 28/28079) + FR (Eure-et-Loir 28/28079) sharing one (norm_name, muni)
    MUST land in distinct dealer clusters. Same numeric code, different country."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES", "28", "28079")
        _seed_geo(cur, "FR", "28", "28079")
        es = _seed_entity(cur, ulid_tag="FRMETES1", cdp="CDP-ES-28-FRMET001",
                          name="automoviles europa", country="ES",
                          province="28", muni="28079")
        fr = _seed_entity(cur, ulid_tag="FRMETFR2", cdp="CDP-FR-28-FRMET002",
                          name="automoviles europa", country="FR",
                          province="28", muni="28079")

    canon = _run_dealers(dry_conn)

    assert canon[es] != canon[fr], (
        "CROSS-BORDER FALSE-MERGE: ES Madrid and FR Eure-et-Loir dealers with identical "
        f"(norm_name, muni '28079') collapsed into one cluster (canonical={canon[es]!r}). "
        "Department '28' is reused across ES/FR.")


@pytest.mark.integration
def test_fr_metropolitan_dealer_same_country_merge(dry_conn):
    """No-regression: two FR dealers sharing (norm_name, muni) MUST still merge."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "FR", "28", "28079")
        a = _seed_entity(cur, ulid_tag="FRSAMEA1", cdp="CDP-FR-28-FRSAM001",
                         name="automoviles europa", country="FR",
                         province="28", muni="28079")
        b = _seed_entity(cur, ulid_tag="FRSAMEB2", cdp="CDP-FR-28-FRSAM002",
                         name="automoviles europa", country="FR",
                         province="28", muni="28079")

    canon = _run_dealers(dry_conn)

    assert canon[a] == canon[b], (
        "FR REGRESSION: two FR dealers with identical (norm_name, muni) did NOT merge -- "
        "the country scope broke same-country clustering for a real second tenant.")


@pytest.mark.integration
def test_fr_corsica_nonnumeric_province_accepted(dry_conn):
    """The ES 'province is 2 DIGITS 01-52' assumption must NOT break the geo backbone:
    France's Corsica departments are '2A'/'2B'. geo_province.code is CHAR(2) and the
    INE prefix CHECK is country-guarded to ES (0053), so '2A' + commune '2A004' (Ajaccio)
    seed cleanly under country='FR'."""
    with dry_conn.cursor() as cur:
        # No exception == accepted. (left('2A004',2)='2A'=province; also CHECK relaxed for FR.)
        _seed_geo(cur, "FR", "2A", "2A004")
        cur.execute(
            "SELECT count(*) FROM geo_municipality "
            "WHERE country_code='FR' AND code='2A004' AND province_code='2A'")
        assert cur.fetchone()[0] == 1, "Corsica commune '2A004' (province '2A') not stored"


@pytest.mark.integration
def test_fr_overseas_dom_province_exceeds_char2_DOCUMENTED_LIMIT(dry_conn):
    """DOCUMENTED GAP (A): geo_province.code CHAR(2) cannot store France's 3-digit
    overseas department codes (DOM '971' Guadeloupe .. '976' Mayotte). The INSERT is
    rejected by PostgreSQL with 'value too long for type character(2)'. Metropolitan FR
    (01-95) + Corsica (2A/2B) fit; the DOM/TOM tail does NOT. Fixing it is a geo-backbone
    width migration (CHAR(2)->wider) touching the composite PK + 6 FKs -- out of this
    test's surgical scope; locked here so the limit is explicit and regression-tracked."""
    with dry_conn.cursor() as cur:
        with pytest.raises(psycopg2.DataError) as excinfo:
            cur.execute(
                "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
                "VALUES ('971', 'Guadeloupe', '97', 'DOM', 'FR')")
        assert "too long" in str(excinfo.value), (
            "expected a CHAR(2) width rejection for FR DOM province '971'")


# ===========================================================================
# IT -- Italy: 2-letter provinces, non-prefix cadastral comune, 6-digit ISTAT width
# ===========================================================================
@pytest.mark.integration
def test_it_photo_signal_a_cross_country_do_not_merge(dry_conn):
    """IT (Roma 'RM'/'H501') + ES (Madrid 28/28079) listings sharing ONE photo_url MUST
    NOT merge. Drives the REAL cluster_vehicles Signal-A build with a genuine Italian
    grammar entity (alpha province 'RM', cadastral comune 'H501' where left(2)='H5'!=RM).
    Different titles so Signal-A (photo) is the sole merge driver."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES", "28", "28079")
        _seed_geo(cur, "IT", "RM", "H501")
        es_ent = _seed_entity(cur, ulid_tag="ITPHES1", cdp="CDP-ES-28-ITPH001",
                              name="concesionario es", country="ES",
                              province="28", muni="28079")
        it_ent = _seed_entity(cur, ulid_tag="ITPHIT2", cdp="CDP-IT-RM-ITPH002",
                              name="concessionaria it", country="IT",
                              province="RM", muni="H501")
        es = _seed_vehicle(cur, ulid_tag="ITPHVES1", entity_ulid=es_ent,
                           deep_link="https://es.plat/it-a", title="seat leon madrid",
                           photo_url=_PHOTO)
        it = _seed_vehicle(cur, ulid_tag="ITPHVIT2", entity_ulid=it_ent,
                           deep_link="https://it.plat/it-b", title="seat leon roma",
                           photo_url=_PHOTO)

    canon = _run_vehicles(dry_conn)

    assert canon[es] != canon[it], (
        "CROSS-BORDER FALSE-MERGE (Signal A): ES and IT vehicles sharing one photo_url "
        f"collapsed (canonical={canon[es]!r}) despite the Italian-grammar entity.")


@pytest.mark.integration
def test_it_photo_signal_a_same_country_merge(dry_conn):
    """No-regression: two IT listings (real IT grammar) sharing one photo_url MUST merge."""
    same_photo = "https://cdn.oemfeed.example/auction/lot/itsame999.jpg"
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "IT", "RM", "H501")
        a_ent = _seed_entity(cur, ulid_tag="ITSMA1", cdp="CDP-IT-RM-ITSM001",
                             name="concessionaria a", country="IT",
                             province="RM", muni="H501")
        b_ent = _seed_entity(cur, ulid_tag="ITSMB2", cdp="CDP-IT-RM-ITSM002",
                             name="concessionaria b", country="IT",
                             province="RM", muni="H501")
        a = _seed_vehicle(cur, ulid_tag="ITSMVA1", entity_ulid=a_ent,
                          deep_link="https://it.plat/s-a", title="seat leon offerta",
                          photo_url=same_photo)
        b = _seed_vehicle(cur, ulid_tag="ITSMVB2", entity_ulid=b_ent,
                          deep_link="https://it.plat/s-b", title="seat leon occasione",
                          photo_url=same_photo)

    canon = _run_vehicles(dry_conn)

    assert canon[a] == canon[b], (
        "IT REGRESSION (Signal A): two IT vehicles sharing one photo_url did NOT merge.")


@pytest.mark.integration
def test_it_cadastral_comune_non_prefix_accepted(dry_conn):
    """The ES 'left(muni,2)=province' INE shape is country-guarded to ES (0053): an
    Italian cadastral comune 'H501' (Roma) under province 'RM' -- where left('H501',2)='H5'
    != 'RM' -- MUST seed cleanly under country='IT'. This is the empirical proof the
    relaxation generalizes (an ES row with the same mismatch would still be rejected)."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "IT", "RM", "H501")
        cur.execute(
            "SELECT count(*) FROM geo_municipality "
            "WHERE country_code='IT' AND code='H501' AND province_code='RM'")
        assert cur.fetchone()[0] == 1, "IT cadastral comune 'H501' not stored under 'RM'"


@pytest.mark.integration
def test_it_istat_comune_exceeds_char5_DOCUMENTED_LIMIT(dry_conn):
    """DOCUMENTED GAP (B): geo_municipality.code CHAR(5) cannot store Italy's 6-digit
    ISTAT comune codes (Roma '058091', Milano '015146'). The INSERT is rejected with
    'value too long for type character(5)'. A <=5-char scheme (cadastral Belfiore 'H501')
    is the only representable option, which is a data-modeling compromise. Widening CHAR(5)
    is a geo-backbone migration -- out of this test's scope; locked here as the explicit limit."""
    with dry_conn.cursor() as cur:
        cur.execute(
            "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
            "VALUES ('RM', 'Roma', '12', 'Lazio', 'IT')")
        with pytest.raises(psycopg2.DataError) as excinfo:
            cur.execute(
                "INSERT INTO geo_municipality (code, name, province_code, comarca_id, country_code) "
                "VALUES ('058091', 'Roma', 'RM', NULL, 'IT')")
        assert "too long" in str(excinfo.value), (
            "expected a CHAR(5) width rejection for IT ISTAT comune '058091'")


# ===========================================================================
# PT -- Portugal: distrito '11' Lisboa + concelho '1106' (INE-shaped, fits the ES schema)
# Drives the REAL deep_link super-canonical build (vector #3, served Layer-2).
# ===========================================================================
@pytest.mark.integration
def test_pt_deeplink_cross_country_do_not_merge(dry_conn):
    """ES + PT canonicals sharing ONE deep_link MUST stay in distinct super-canonicals.
    Portugal's distrito/concelho grammar is INE-shaped and fits the ES schema cleanly."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES", "28", "28079")
        _seed_geo(cur, "PT", "11", "1106")
        es = _seed_entity(cur, ulid_tag="PTDLES1", cdp="CDP-ES-28-PTDL001",
                          name="stand auto", country="ES", province="28", muni="28079")
        pt = _seed_entity(cur, ulid_tag="PTDLPT2", cdp="CDP-PT-11-PTDL002",
                          name="stand auto", country="PT", province="11", muni="1106")
        _seed_vehicle(cur, ulid_tag="PTDLVES1", entity_ulid=es,
                      deep_link="https://x.example/listing/pt555")
        _seed_vehicle(cur, ulid_tag="PTDLVPT2", entity_ulid=pt,
                      deep_link="https://x.example/listing/pt555")

    mc = _run_deeplink(dry_conn)

    assert not _deeplink_merged(mc, "CDP-ES-28-PTDL001", "CDP-PT-11-PTDL002"), (
        "CROSS-BORDER FALSE-MERGE: ES and PT canonicals sharing one deep_link collapsed "
        "into a single super-canonical (Layer-2 of v_dealer_resolved).")


@pytest.mark.integration
def test_pt_deeplink_same_country_merge(dry_conn):
    """No-regression: two PT canonicals sharing one deep_link MUST still merge."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "PT", "11", "1106")
        a = _seed_entity(cur, ulid_tag="PTSMA1", cdp="CDP-PT-11-PTSM001",
                         name="stand auto", country="PT", province="11", muni="1106")
        b = _seed_entity(cur, ulid_tag="PTSMB2", cdp="CDP-PT-11-PTSM002",
                         name="stand auto", country="PT", province="11", muni="1106")
        _seed_vehicle(cur, ulid_tag="PTSMVA1", entity_ulid=a,
                      deep_link="https://x.example/listing/pt888")
        _seed_vehicle(cur, ulid_tag="PTSMVB2", entity_ulid=b,
                      deep_link="https://x.example/listing/pt888")

    mc = _run_deeplink(dry_conn)

    assert _deeplink_merged(mc, "CDP-PT-11-PTSM001", "CDP-PT-11-PTSM002"), (
        "PT REGRESSION: two PT canonicals sharing one deep_link did NOT merge.")


@pytest.mark.integration
def test_pt_ine_grammar_accepted(dry_conn):
    """Portugal's distrito '11' (Lisboa) + concelho '1106' is INE-shaped -- it even
    satisfies the ES prefix CHECK (left('1106',2)='11'='11') -- and seeds cleanly."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "PT", "11", "1106")
        cur.execute(
            "SELECT count(*) FROM geo_municipality "
            "WHERE country_code='PT' AND code='1106' AND province_code='11'")
        assert cur.fetchone()[0] == 1, "PT concelho '1106' (distrito '11') not stored"


# ===========================================================================
# GR -- Greece: non-latin (Greek-script) dealer name -- norm_name stress
# Uses the REAL, verified ES grid (28/28079) under two tenants (ES + GR) so no Greek
# admin code is invented; the VERIFIED quirk under test is the non-latin NAME.
# ===========================================================================
# Greek-script literals built from code points so the source file stays ASCII-safe.
_GREEK_NAME = "".join(chr(c) for c in (0x391, 0x3B8, 0x3AE, 0x3BD, 0x3B1))  # 'Αθήνα'
_CYRILLIC_NAME = "".join(chr(c) for c in (0x410, 0x432, 0x442, 0x43E))     # 'Авто'


@pytest.mark.unit
def test_nonlatin_name_normalizes_to_none_DOCUMENTED_LIMIT():
    """DOCUMENTED GAP (C): the shared name normalizer (NFKD + encode('ascii','ignore'))
    DROPS every non-ASCII codepoint, so a pure Greek or Cyrillic dealer name normalizes
    to None. The name-based identity signal is therefore DEAD for non-latin-script tenants
    (no name block-key is emitted; cluster_dealers.py:458 / cross_source_dedup gate on
    `if nn:`). Fixing it means swapping the ascii-fold for a transliterator across 3+
    modules and re-proving ES byte-identity -- out of this test's scope; locked here so
    the degradation is explicit. Country ISOLATION still holds via script-agnostic signals
    (photo / deep_link / phone) -- see test_greek_tenant_deeplink_cross_country_do_not_merge."""
    assert cd._normalize_name(_GREEK_NAME) is None, (
        "expected the Greek-script name to normalize to None (ascii-fold erases it)")
    assert cd._normalize_name(_CYRILLIC_NAME) is None, (
        "expected the Cyrillic-script name to normalize to None (ascii-fold erases it)")
    assert csd._normalize_name(_GREEK_NAME) is None, (
        "cross_source_dedup normalizer must agree: Greek-script name -> None")
    # ES control: a latin name still normalizes (no regression to the ES path).
    assert cd._normalize_name("talleres garcia") == "talleresgarcia"


@pytest.mark.integration
def test_greek_tenant_deeplink_cross_country_do_not_merge(dry_conn):
    """A Greek-script tenant flows through the REAL deep_link build without crashing AND
    stays country-isolated: a GR dealer (Greek trade_name) and an ES dealer sharing one
    deep_link MUST NOT merge. Country scope is script-agnostic (keys on country_code, not
    on the unusable non-latin name)."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES", "28", "28079")
        _seed_geo(cur, "GR", "28", "28079")  # real ES grid reused under the GR tenant
        es = _seed_entity(cur, ulid_tag="GRDLES1", cdp="CDP-ES-28-GRDL001",
                          name="talleres atenea", country="ES", province="28", muni="28079")
        gr = _seed_entity(cur, ulid_tag="GRDLGR2", cdp="CDP-GR-28-GRDL002",
                          name=_GREEK_NAME, country="GR", province="28", muni="28079")
        _seed_vehicle(cur, ulid_tag="GRDLVES1", entity_ulid=es,
                      deep_link="https://x.example/listing/gr333")
        _seed_vehicle(cur, ulid_tag="GRDLVGR2", entity_ulid=gr,
                      deep_link="https://x.example/listing/gr333")

    mc = _run_deeplink(dry_conn)

    assert not _deeplink_merged(mc, "CDP-ES-28-GRDL001", "CDP-GR-28-GRDL002"), (
        "CROSS-BORDER FALSE-MERGE: ES and GR canonicals sharing one deep_link collapsed.")


# ===========================================================================
# Cross-source (vector #3, entity_cluster overlay) with a real IT grammar -- phone signal
# ===========================================================================
@pytest.mark.integration
def test_it_cross_source_phone_cross_country_do_not_merge(dry_conn):
    """IT(osm) + ES(as24) sharing a phone in the (numerically reused) muni space MUST NOT
    merge cross-source, even with the Italian-grammar IT entity (province 'RM')."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES", "28", "28079")
        _seed_geo(cur, "IT", "RM", "H501")
        es = _seed_entity(cur, ulid_tag="ITXPES1", cdp="CDP-ES-28-ITXP001",
                          name="autos centro", country="ES", province="28", muni="28079",
                          phone="600111222")
        it = _seed_entity(cur, ulid_tag="ITXPIT2", cdp="CDP-IT-RM-ITXP002",
                          name="auto centro", country="IT", province="RM", muni="H501",
                          phone="600111222")
        _seed_source(cur, es, "osm")
        _seed_source(cur, it, "as24")

    canon = _run_cross_source(dry_conn)

    assert canon[es] != canon[it], (
        "CROSS-BORDER FALSE-MERGE (cross-source phone): ES and IT entities merged.")


# ===========================================================================
# MINT VALIDATION (vector #5) -- lock fix (1): _CDP_CODE_RE accepts alpha provinces
# ===========================================================================
@pytest.mark.unit
def test_mint_regex_accepts_alpha_province_real_codes():
    """The G1 cdp validator MUST accept the alphanumeric-province codes the mint emits
    for real countries: France Corsica ('2A'/'2B') and Italy ('RM'). RED before the fix
    (province segment was [0-9]{2})."""
    assert _CDP_CODE_RE.match("CDP-FR-2A-ABCD1234"), (
        "MINT BLIND: valid French-Corsica cdp 'CDP-FR-2A-ABCD1234' rejected by G1.")
    assert _CDP_CODE_RE.match("CDP-FR-2B-9ABCDEFG"), (
        "MINT BLIND: valid French-Corsica cdp 'CDP-FR-2B-9ABCDEFG' rejected by G1.")
    assert _CDP_CODE_RE.match("CDP-IT-RM-ABCD1234"), (
        "MINT BLIND: valid Italian cdp 'CDP-IT-RM-ABCD1234' rejected by G1.")


@pytest.mark.unit
def test_mint_regex_es_byte_identical_and_still_rejects_malformed():
    """ES output stays byte-identical and every documented malformed shape stays rejected
    after widening the province charset to [0-9A-Z]{2} (no regression to the chain golden)."""
    assert _CDP_CODE_RE.match("CDP-ES-28-ABCD1234")
    assert _CDP_CODE_RE.match("CDP-ES-01-00000000")
    assert _CDP_CODE_RE.match("CDP-ES-52-ZZZZZZZZ")
    assert not _CDP_CODE_RE.match("CDP-E-28-ABCD1234"), "1-char country must reject"
    assert not _CDP_CODE_RE.match("CDP-ESP-28-ABCD1234"), "3-char country must reject"
    assert not _CDP_CODE_RE.match("CDP-de-28-ABCD1234"), "lowercase country must reject"
    assert not _CDP_CODE_RE.match("CDP-DE-28-ABCDILOU"), "non-Crockford tail must reject"
    assert not _CDP_CODE_RE.match("CDP-DE-2-ABCD1234"), "1-char province must reject"
    assert not _CDP_CODE_RE.match("XDP-DE-28-ABCD1234"), "wrong prefix must reject"


# ===========================================================================
# G1 GATE (vector #5) -- lock fix (2): province validity is country-scoped
# Pure async-mock (mirrors tests/test_complete.py::TestCheckG1); no DB.
# ===========================================================================
def _g1_conn(row: dict) -> AsyncMock:
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=row)
    return conn


@pytest.mark.unit
@pytest.mark.asyncio
async def test_g1_accepts_non_es_provinces_outside_01_52():
    """A non-ES tenant whose province is outside the Spanish 01-52 grid MUST pass G1:
    France Paris '75' / Corsica '2A', Italy 'RM'. RED before the fix (check_g1 applied the
    ES 01-52 regex to every tenant and did not even fetch country_code)."""
    for cdp, prov, country in [
        ("CDP-FR-75-ABCD1234", "75", "FR"),   # Paris -- a real metropolitan dept > 52
        ("CDP-FR-2A-ABCD1234", "2A", "FR"),   # Corsica -- non-numeric
        ("CDP-IT-RM-ABCD1234", "RM", "IT"),   # Roma -- 2-letter
    ]:
        conn = _g1_conn({"cdp_code": cdp, "province_code": prov,
                         "kind": "compraventa", "country_code": country})
        passed, reason = await check_g1(conn, cdp)
        assert passed is True, (
            f"G1 wrongly rejected a valid {country} dealer (province {prov!r}): {reason}")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_g1_es_province_path_byte_identical():
    """ES verdicts are unchanged: a valid ES province passes, an out-of-grid ES province
    ('99') fails, and an ES row with no country_code (partial mock) defaults to the strict
    ES path -- byte-identical to the pre-fix gate."""
    ok = _g1_conn({"cdp_code": "CDP-ES-28-ABCD1234", "province_code": "28",
                   "kind": "compraventa", "country_code": "ES"})
    passed, reason = await check_g1(ok, "CDP-ES-28-ABCD1234")
    assert passed is True and reason == "ok"

    bad = _g1_conn({"cdp_code": "CDP-ES-99-ABCD1234", "province_code": "99",
                    "kind": "compraventa", "country_code": "ES"})
    passed, reason = await check_g1(bad, "CDP-ES-99-ABCD1234")
    assert passed is False and "invalid_province_code" in reason

    # Partial mock without country_code -> defaults to ES (strict) -> '99' still fails.
    legacy = _g1_conn({"cdp_code": "CDP-ES-99-ABCD1234", "province_code": "99"})
    passed, reason = await check_g1(legacy, "CDP-ES-99-ABCD1234")
    assert passed is False and "invalid_province_code" in reason


@pytest.mark.unit
def test_province_regexes_partition_es_vs_real_grammars():
    """Direct proof of the two province validators: the ES grid rejects FR/IT real codes
    while the generic non-ES shape accepts them (and both reject a 1-char province)."""
    for real in ("75", "2A", "2B", "RM"):
        if real != "75":  # '75' is two digits so the *shape* matches; the ES *range* is the point
            assert not _PROVINCE_RE.match(real), f"ES grid must reject {real!r}"
        assert _NON_ES_PROVINCE_RE.match(real), f"non-ES shape must accept {real!r}"
    assert not _PROVINCE_RE.match("75"), "ES grid must reject Paris '75' (out of 01-52)"
    assert not _NON_ES_PROVINCE_RE.match("2"), "non-ES shape must reject a 1-char province"


# ===========================================================================
# SERVING (vector #5) -- multi-tenant scope over real grammars (incl. alpha province IT)
# ===========================================================================
@pytest.mark.integration
def test_serving_view_scopes_each_real_tenant(dry_conn):
    """v_servable_dealer scoped to country=X returns ONLY X's dealer, across four real
    grammars seeded together (ES Madrid, FR Eure-et-Loir, IT Roma 'RM', PT Lisboa). Proves
    the served census isolates each tenant even when provinces/munis collide or are
    non-numeric ('RM')."""
    rows = {
        "ES": ("CDP-ES-28-SRVES01", "28", "28079"),
        "FR": ("CDP-FR-28-SRVFR02", "28", "28079"),
        "IT": ("CDP-IT-RM-SRVIT03", "RM", "H501"),
        "PT": ("CDP-PT-11-SRVPT04", "11", "1106"),
    }
    with dry_conn.cursor() as cur:
        for country, (cdp, prov, muni) in rows.items():
            _seed_geo(cur, country, prov, muni)
            _seed_entity(cur, ulid_tag=f"SRV{country}9", cdp=cdp,
                         name=f"dealer {country}", country=country,
                         province=prov, muni=muni)

    for country, (cdp, _prov, _muni) in rows.items():
        with dry_conn.cursor() as cur:
            cur.execute(
                "SELECT cdp_code FROM v_servable_dealer WHERE country_code = %s", (country,))
            served = {r[0] for r in cur.fetchall()}
        others = {c for k, (c, _p, _m) in rows.items() if k != country}
        assert cdp in served, (
            f"v_servable_dealer scoped to country={country!r} did NOT serve its own dealer "
            f"{cdp}: {sorted(served)}")
        assert not (served & others), (
            f"SERVING LEAK: country={country!r} served foreign tenants {sorted(served & others)}")

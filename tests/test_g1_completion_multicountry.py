"""
tests/test_g1_completion_multicountry.py

GOLDEN -- country-proof of the SET-BASED G1 identity gate (Red-team vector #5, SQL mirror).

pipeline/complete.py already country-scoped the per-dealer G1 validator (commit 052fa8f:
province validated against the ES 01-52 grid only for ES, generic 2-char geo_province.code
shape for a non-ES tenant, cdp_code accepting CDP-{CC}-{PP}- for any ISO tenant). But the
SET-BASED mirror in scripts/populate_completion.py -- the one that actually WRITES
entity_completion.g1_identity for every served dealer -- kept the ES-baked shapes:

  * _CDP_CODE_PATTERN = ^CDP-ES-([0-9]{2})-...  -> hard-codes the 'ES' country segment AND a
    numeric-only [0-9]{2} province segment. A second country's cdp_code (CDP-FR-2A-...,
    CDP-DE-09-...) is wrongly rejected -> g1_identity=FALSE.
  * the g1_check CTE validated province_code against the ES 01-52 grid for EVERY tenant
    (it never looked at country_code) -> France (Corsica '2A', Paris '75') and Italy ('RM')
    wrongly FAILED identity.

This golden seeds a real ES dealer (province '28', grid-valid) and real second-country dealers
(FR Corsica '2A' -- non-numeric, outside 01-52; FR Paris '75' -- numeric but outside 01-52),
runs the REAL set-based populate computation (TRUNCATE + _POPULATE_SQL, exactly as
scripts/populate_completion.main() steps 1-2), and reads entity_completion.g1_identity.

  RED today : the FR dealers get g1_identity=FALSE (country-blind ES patterns).
  GREEN     : after the fix mirrors complete.py, the FR dealers get g1_identity=TRUE, while
              every ES verdict (grid-valid -> TRUE, out-of-grid '75' -> FALSE) stays
              BYTE-IDENTICAL, and a genuinely malformed non-ES province still FAILS (the fix
              generalises the shape, it does NOT loosen validation to "anything").

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). HARD-REFUSES :5433 (live
production) by DSN string AND by asserting the census is empty before seeding. Every DB test
seeds inside a transaction and ROLLS BACK, leaving the dry-run byte-identical (entity stays 0).
"""
from __future__ import annotations

import os
import re

import psycopg2
import psycopg2.extras
import pytest

from scripts.populate_completion import (
    _POPULATE_SQL,
    _CDP_CODE_PATTERN,
    _PROVINCE_PATTERN,
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
            "refusing to run the G1-completion golden against :5433 "
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
    so a non-ES non-prefix muni is accepted under a second country."""
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
                 province: str, muni: str, kind: str = "compraventa") -> str:
    """Insert one in-scope dealer (status='active', kind<>particular) and return its ulid."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " province_code, municipality_code, country_code, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active')",
        (ulid, cdp, kind, name, name, province, muni, country),
    )
    return ulid


def _seed_vehicle(cur, *, ulid_tag: str, entity_ulid: str, deep_link: str) -> str:
    """Insert one in-scope vehicle (status='available') so the entity enters
    served_dealers (kind<>particular AND >=1 available vehicle)."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO vehicle "
        "(vehicle_ulid, entity_ulid, deep_link, make, model, year, km, price, "
        " title, status) "
        "VALUES (%s, %s, %s, 'seat', 'leon', 2020, 45000, 15000.0, 'vehiculo', 'available')",
        (ulid, entity_ulid, deep_link),
    )
    return ulid


def _run_populate_g1(conn) -> dict[str, bool]:
    """Run the REAL set-based populate exactly as scripts/populate_completion.main()
    steps 1-2 (TRUNCATE entity_completion + _POPULATE_SQL) inside the test txn, then
    return {cdp_code: g1_identity}. The fixture rolls the whole thing back."""
    with conn.cursor() as cur:
        cur.execute("TRUNCATE entity_completion")
        cur.execute(_POPULATE_SQL)
        cur.execute("SELECT cdp_code, g1_identity FROM entity_completion")
        return {r[0]: r[1] for r in cur.fetchall()}


# cdp_code suffixes: 8 Crockford chars (no I/L/O/U).
_CDP_ES = "CDP-ES-28-ESMADRD1"
_CDP_FR_CORSICA = "CDP-FR-2A-FRCRSCA1"
_CDP_FR_PARIS = "CDP-FR-75-FRPARS75"
_CDP_FR_MALFORMED = "CDP-FR-99-FRBADPRV"   # well-formed code; entity province is malformed
_CDP_ES_OUTGRID = "CDP-ES-75-ESGRD75X"


# ===========================================================================
# DB goldens -- the REAL set-based g1_identity computation
# ===========================================================================
@pytest.mark.integration
def test_es_dealer_g1_identity_true(dry_conn):
    """Control: an ES dealer with a grid-valid province (Madrid '28') and a CDP-ES-28-*
    code gets g1_identity=TRUE. This path must stay byte-identical across the fix."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES", "28", "28079")
        e = _seed_entity(cur, ulid_tag="G1ESMAD", cdp=_CDP_ES,
                         name="automoviles madrid", country="ES",
                         province="28", muni="28079")
        _seed_vehicle(cur, ulid_tag="G1ESMADV", entity_ulid=e,
                      deep_link="https://es.example/v/1")

    g1 = _run_populate_g1(dry_conn)

    assert g1.get(_CDP_ES) is True, (
        f"ES grid-valid dealer should pass G1, got {g1.get(_CDP_ES)!r}")


@pytest.mark.integration
def test_fr_corsica_g1_identity_true_not_false_by_country(dry_conn):
    """THE HEART. FR Corsica dealer: province '2A' (non-numeric, outside the ES 01-52 grid)
    and code CDP-FR-2A-*. Both the ES-baked sub-checks reject it today:
      - _CDP_CODE_PATTERN ^CDP-ES-([0-9]{2})- rejects 'FR' and the alphanumeric '2A' segment;
      - the g1_check CTE validates '2A' against the ES 01-52 grid (fails).
    => RED today: g1_identity=FALSE. GREEN after the country-scope mirror: TRUE."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "FR", "2A", "2A004")
        e = _seed_entity(cur, ulid_tag="G1FRCOR", cdp=_CDP_FR_CORSICA,
                         name="automobiles corse", country="FR",
                         province="2A", muni="2A004")
        _seed_vehicle(cur, ulid_tag="G1FRCORV", entity_ulid=e,
                      deep_link="https://fr.example/v/1")

    g1 = _run_populate_g1(dry_conn)

    assert g1.get(_CDP_FR_CORSICA) is True, (
        "COUNTRY-BLIND G1: FR Corsica dealer (province '2A', code CDP-FR-2A-*) got "
        f"g1_identity={g1.get(_CDP_FR_CORSICA)!r}; the set-based gate still bakes the ES "
        "01-52 grid + ^CDP-ES- shape instead of country-scoping like pipeline/complete.py.")


@pytest.mark.integration
def test_fr_paris_outside_es_grid_g1_identity_true(dry_conn):
    """FR Paris dealer: province '75' is numeric (matches [0-9]{2}) but OUTSIDE the ES
    01-52 grid, and the code is CDP-FR-75-*. The grid check fails it today even though the
    shape is numeric -> isolates the country-blind GRID assumption. RED today: FALSE."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "FR", "75", "75056")
        e = _seed_entity(cur, ulid_tag="G1FRPAR", cdp=_CDP_FR_PARIS,
                         name="automobiles paris", country="FR",
                         province="75", muni="75056")
        _seed_vehicle(cur, ulid_tag="G1FRPARV", entity_ulid=e,
                      deep_link="https://fr.example/v/2")

    g1 = _run_populate_g1(dry_conn)

    assert g1.get(_CDP_FR_PARIS) is True, (
        "COUNTRY-BLIND G1: FR Paris dealer (province '75', outside ES 01-52) got "
        f"g1_identity={g1.get(_CDP_FR_PARIS)!r}; the grid must be country-scoped to ES.")


@pytest.mark.integration
def test_es_and_second_country_isolated_in_one_populate(dry_conn):
    """ES + FR seeded together, one populate run: the ES dealer stays TRUE and the FR dealer
    is no longer collateral-damaged to FALSE. Proves the fix is per-row country-scoped."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES", "28", "28079")
        _seed_geo(cur, "FR", "2A", "2A004")
        es = _seed_entity(cur, ulid_tag="G1MIXES", cdp=_CDP_ES,
                          name="automoviles madrid", country="ES",
                          province="28", muni="28079")
        fr = _seed_entity(cur, ulid_tag="G1MIXFR", cdp=_CDP_FR_CORSICA,
                          name="automobiles corse", country="FR",
                          province="2A", muni="2A004")
        _seed_vehicle(cur, ulid_tag="G1MIXESV", entity_ulid=es,
                      deep_link="https://es.example/v/9")
        _seed_vehicle(cur, ulid_tag="G1MIXFRV", entity_ulid=fr,
                      deep_link="https://fr.example/v/9")

    g1 = _run_populate_g1(dry_conn)

    assert g1.get(_CDP_ES) is True, f"ES regressed to {g1.get(_CDP_ES)!r}"
    assert g1.get(_CDP_FR_CORSICA) is True, (
        f"FR collateral-damaged to {g1.get(_CDP_FR_CORSICA)!r} in a mixed populate")


@pytest.mark.integration
def test_non_es_malformed_province_still_false(dry_conn):
    """The fix GENERALISES the shape, it does NOT disable validation. A non-ES dealer whose
    province_code is a malformed 3-char value ('2AB') must STILL fail G1 (the generic non-ES
    shape is exactly 2 alphanumeric chars, mirroring geo_province.code / complete.py's
    _NON_ES_PROVINCE_RE). Invariant: FALSE today AND after the fix."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "FR", "2AB", "2AB01")
        e = _seed_entity(cur, ulid_tag="G1FRBAD", cdp=_CDP_FR_MALFORMED,
                         name="automobiles malforme", country="FR",
                         province="2AB", muni="2AB01")
        _seed_vehicle(cur, ulid_tag="G1FRBADV", entity_ulid=e,
                      deep_link="https://fr.example/v/3")

    g1 = _run_populate_g1(dry_conn)

    assert g1.get(_CDP_FR_MALFORMED) is False, (
        "NON-ES VALIDATION LOOSENED: a malformed 3-char province '2AB' passed G1 "
        f"(got {g1.get(_CDP_FR_MALFORMED)!r}); the non-ES shape must stay exactly 2 chars.")


@pytest.mark.integration
def test_es_outside_grid_still_false_byte_identical(dry_conn):
    """ES byte-identity guard: an ES dealer with province '75' (outside the 01-52 grid) must
    STILL fail G1 after the fix -- the ES path is untouched, the country-scope only adds a
    SEPARATE non-ES branch. Invariant: FALSE today AND after the fix."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES", "75", "75001")
        e = _seed_entity(cur, ulid_tag="G1ESGRD", cdp=_CDP_ES_OUTGRID,
                         name="automoviles fuera", country="ES",
                         province="75", muni="75001")
        _seed_vehicle(cur, ulid_tag="G1ESGRDV", entity_ulid=e,
                      deep_link="https://es.example/v/4")

    g1 = _run_populate_g1(dry_conn)

    assert g1.get(_CDP_ES_OUTGRID) is False, (
        "ES GRID REGRESSED: province '75' (outside 01-52) passed G1 "
        f"(got {g1.get(_CDP_ES_OUTGRID)!r}); the ES path must stay byte-identical.")


# ===========================================================================
# Unit goldens -- the patterns themselves (no DB, never skipped)
# ===========================================================================
@pytest.mark.unit
def test_cdp_pattern_accepts_second_country_codes():
    """_CDP_CODE_PATTERN must accept a second country's cdp_code (CDP-FR-2A-*, CDP-DE-09-*)
    and KEEP accepting the historical ES code byte-identically. RED today (^CDP-ES-([0-9]{2})-)."""
    rx = re.compile(_CDP_CODE_PATTERN)
    # ES historical -- must stay valid (byte-identical).
    assert rx.match("CDP-ES-28-ESMADRD1"), "ES code regressed"
    # Second-country codes -- must now pass.
    assert rx.match("CDP-FR-2A-FRCRSCA1"), "FR Corsica code wrongly rejected (country-blind)"
    assert rx.match("CDP-DE-09-DEABCD12"), "DE code wrongly rejected (country-blind)"
    assert rx.match("CDP-IT-RM-RMVENT23"), "IT 2-letter province code wrongly rejected"
    # Malformed shapes must STILL be rejected (the fix generalises, not loosens).
    assert not rx.match("CDP-FR-2AB-FRBADPR1"), "3-char province segment must be rejected"
    assert not rx.match("CDP-F-28-ESMADRD1"), "1-char country segment must be rejected"
    assert not rx.match("CDP-ES-28-ESMADRDI"), "Crockford 'I' in suffix must be rejected"


@pytest.mark.unit
def test_es_province_pattern_unchanged():
    """Invariant: the ES grid pattern (_PROVINCE_PATTERN) is NOT touched by the fix -- it
    still accepts exactly 01-52 and rejects '00'/'53'/non-numeric. This locks ES byte-identity."""
    rx = re.compile(_PROVINCE_PATTERN)
    assert rx.match("01") and rx.match("28") and rx.match("52"), "ES grid lower/mid/upper bound"
    assert not rx.match("00"), "'00' is not a valid ES province"
    assert not rx.match("53"), "'53' is above the ES 01-52 grid"
    assert not rx.match("2A"), "non-numeric must not match the ES grid"


@pytest.mark.unit
def test_non_es_province_pattern_exists_and_is_generic_2char():
    """After the fix, populate_completion exposes _NON_ES_PROVINCE_PATTERN mirroring
    complete.py's _NON_ES_PROVINCE_RE: exactly 2 alphanumeric chars. RED today via hasattr
    (the constant does not exist yet) -- a clean assertion failure, not a collection error."""
    from scripts import populate_completion as pc
    assert hasattr(pc, "_NON_ES_PROVINCE_PATTERN"), (
        "fix not applied: _NON_ES_PROVINCE_PATTERN missing from populate_completion")
    rx = re.compile(pc._NON_ES_PROVINCE_PATTERN)
    assert rx.match("2A") and rx.match("75") and rx.match("RM"), "generic 2-char shape"
    assert not rx.match("2AB"), "3 chars must be rejected (geo_province.code is 2 chars here)"
    assert not rx.match("7"), "1 char must be rejected"

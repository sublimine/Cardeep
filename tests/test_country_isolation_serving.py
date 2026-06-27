"""
tests/test_country_isolation_serving.py

GOLDEN -- the SERVING layer country-scope (generic-engine vector #5, LAST of the
served layer).

Two country-blind surfaces are pinned here:

  (a) MINT VALIDATION -- ``pipeline/complete.py::_CDP_CODE_RE`` is the regex the G1
      identity gate uses to accept a minted ``cdp_code``. Before the country-proof
      fix it was hardcoded ``^CDP-ES-`` so a perfectly valid ``CDP-DE-28-XXXXXXXX``
      (the mint itself is already country-parametrized in ``services/api/codes.py``)
      was REJECTED by the gate -- the served identity check was blind to any tenant
      but ES.

  (b) SERVED CENSUS QUERIES -- the public dealer surface is the view
      ``v_servable_dealer`` (migration 0056: "the single source of truth ... stats.py,
      geo.py and the seal will all read from here") and its base ``servable_entity``.
      Before the fix NEITHER carried a ``country_code`` dimension, so a query for the
      Spanish census could not exclude a German dealer that reuses the same numeric
      ``province_code`` / ``municipality_code`` space (``migrations/0053`` -- DE
      province ``'28'`` deliberately coexists with ES Madrid ``'28'``). Asking for
      ``country='ES'`` would serve DE rows.

WHAT IS ASSERTED
----------------
  (a) regex  : ``CDP-DE-...`` and ``CDP-FR-...`` ACCEPTED; ``CDP-ES-...`` byte-identical
               (no regression); malformed codes still rejected.
  (b) serving: with ES + DE dealers sharing (province, muni), the real served surfaces
               (``v_servable_dealer`` / ``servable_entity``) scoped to ``country='ES'``
               return the ES dealer and NEVER the DE dealer; and the ES dealer is still
               served (no over-filtering regression).

ISOLATION (inviolable): the DB tests run ONLY against the dry-run DB (:5434). They
HARD-REFUSE :5433 (live production) two ways -- by DSN string and by asserting the
target census is empty before seeding. Every test seeds inside a transaction and
ROLLS BACK, leaving the dry-run byte-identical (``entity`` stays 0). The regex tests
are pure unit (no DB).
"""
from __future__ import annotations

import os

import psycopg2
import pytest

from pipeline.complete import _CDP_CODE_RE

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Crockford base32 (no I, L, O, U) -- the alphabet entity_ulid_shape accepts:
#   CHECK (entity_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$')
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


# ===========================================================================
# (a) MINT VALIDATION -- pure unit, no DB
# ===========================================================================
@pytest.mark.unit
def test_mint_regex_accepts_non_es_country_codes():
    """The G1 cdp_code validator MUST accept a second tenant's codes.

    ``services/api/codes.py`` already mints ``CDP-{country}-{prov}-{8 crockford}``;
    the gate's regex must recognise the same shape for ANY ISO-3166 alpha-2 country,
    not only ES. RED before the fix (``^CDP-ES-`` rejects DE/FR)."""
    assert _CDP_CODE_RE.match("CDP-DE-28-ABCD1234"), (
        "MINT BLIND TO COUNTRY: a valid German cdp_code 'CDP-DE-28-ABCD1234' is "
        "rejected by the G1 identity validator -- _CDP_CODE_RE is hardcoded to ES.")
    assert _CDP_CODE_RE.match("CDP-FR-75-9ABCDEFG"), (
        "MINT BLIND TO COUNTRY: a valid French cdp_code 'CDP-FR-75-9ABCDEFG' is "
        "rejected by the G1 identity validator -- _CDP_CODE_RE is hardcoded to ES.")


@pytest.mark.unit
def test_mint_regex_es_byte_identical_and_rejects_malformed():
    """ES output stays byte-identical (no regression) and malformed codes stay rejected."""
    # ES no-regression: the historical shape still matches.
    assert _CDP_CODE_RE.match("CDP-ES-28-ABCD1234")
    assert _CDP_CODE_RE.match("CDP-ES-01-00000000")
    assert _CDP_CODE_RE.match("CDP-ES-52-ZZZZZZZZ")
    # Malformed: still rejected after generalisation.
    assert not _CDP_CODE_RE.match("CDP-E-28-ABCD1234"), "1-char country must reject"
    assert not _CDP_CODE_RE.match("CDP-ESP-28-ABCD1234"), "3-char country must reject"
    assert not _CDP_CODE_RE.match("CDP-de-28-ABCD1234"), "lowercase country must reject"
    assert not _CDP_CODE_RE.match("CDP-DE-28-ABCDILOU"), "non-Crockford (I,L,O,U) must reject"
    assert not _CDP_CODE_RE.match("CDP-DE-2-ABCD1234"), "1-digit province must reject"
    assert not _CDP_CODE_RE.match("XDP-DE-28-ABCD1234"), "wrong prefix must reject"


# ===========================================================================
# (b) SERVED CENSUS QUERIES -- integration, dry-run only, txn ROLLBACK
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
            "refusing to run the serving-isolation golden against :5433 "
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


def _seed_dealer(cur, *, ulid_tag: str, cdp: str, country: str,
                 province: str = "28", muni: str = "28079") -> str:
    """One in-scope, servable sales point: kind='compraventa', status='active'
    (v_servable_dealer includes compraventa regardless of inventory)."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " province_code, municipality_code, country_code, status) "
        "VALUES (%s, %s, 'compraventa', %s, %s, %s, %s, %s, 'active')",
        (ulid, cdp, f"dealer {country}", f"dealer {country}", province, muni, country),
    )
    return ulid


def _served_cdps(conn, sql: str, params: tuple) -> set[str]:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return {r[0] for r in cur.fetchall()}


# ---------------------------------------------------------------------------
# Structural: the served census views carry a country dimension at all
# ---------------------------------------------------------------------------
@pytest.mark.integration
def test_servable_views_carry_country_dimension(dry_conn):
    """The served census views (servable_entity + v_servable_dealer) MUST expose a
    country_code column -- without it no served query can scope a tenant. RED before
    migration 0058 (neither view projects country_code)."""
    with dry_conn.cursor() as cur:
        for view in ("servable_entity", "v_servable_dealer"):
            cur.execute(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name = %s AND column_name = 'country_code'",
                (view,),
            )
            assert cur.fetchone() is not None, (
                f"SERVED VIEW '{view}' has no country_code dimension -- the served "
                "census cannot be scoped by tenant.")


# ---------------------------------------------------------------------------
# Behaviour: ES scope serves the ES dealer and NEVER the DE dealer
# ---------------------------------------------------------------------------
@pytest.mark.integration
def test_served_dealer_surface_scoped_to_es_excludes_de(dry_conn):
    """ES + DE dealers sharing (province=28, muni=28079): the real served surfaces
    scoped to country='ES' return the ES dealer and never the DE dealer. RED before
    the fix (the views have no country_code, so the predicate cannot exclude DE)."""
    es_cdp = "CDP-ES-28-SRVES001"
    de_cdp = "CDP-DE-28-SRVDE002"
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        _seed_dealer(cur, ulid_tag="SRVES", cdp=es_cdp, country="ES")
        _seed_dealer(cur, ulid_tag="SRVDE", cdp=de_cdp, country="DE")

    # The documented single source of truth for the served dealer census (0056).
    dealer_view = _served_cdps(
        dry_conn,
        "SELECT cdp_code FROM v_servable_dealer WHERE country_code = %s",
        ("ES",),
    )
    assert de_cdp not in dealer_view, (
        f"SERVING LEAK: v_servable_dealer scoped to country='ES' served the GERMAN "
        f"dealer {de_cdp}. The served census is country-blind: {sorted(dealer_view)}")
    assert es_cdp in dealer_view, (
        f"v_servable_dealer scoped to country='ES' did NOT serve the Spanish dealer "
        f"{es_cdp}: {sorted(dealer_view)}")

    # The base view the /geo/{province}/entities endpoints read (FROM servable_entity
    # WHERE province_code = $ ... ) -- same exact surface + the new country predicate.
    base_view = _served_cdps(
        dry_conn,
        "SELECT cdp_code FROM servable_entity "
        "WHERE province_code = %s AND status = 'active' AND kind <> 'particular' "
        "AND country_code = %s",
        ("28", "ES"),
    )
    assert de_cdp not in base_view and es_cdp in base_view, (
        "SERVING LEAK: servable_entity scoped to province=28 + country='ES' returned "
        f"the wrong set {sorted(base_view)} (DE must be absent, ES present).")


@pytest.mark.integration
def test_served_dealer_surface_es_no_regression(dry_conn):
    """No-regression: with only ES dealers, country='ES' serves them all (the country
    predicate must not over-filter the default tenant)."""
    a, b = "CDP-ES-28-REGAA001", "CDP-ES-28-REGBB002"
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_dealer(cur, ulid_tag="REGAA", cdp=a, country="ES")
        _seed_dealer(cur, ulid_tag="REGBB", cdp=b, country="ES")

    served = _served_cdps(
        dry_conn,
        "SELECT cdp_code FROM v_servable_dealer WHERE country_code = %s",
        ("ES",),
    )
    assert {a, b} <= served, (
        f"ES REGRESSION: country='ES' over-filtered the default tenant; expected both "
        f"{a} and {b}, got {sorted(served)}.")

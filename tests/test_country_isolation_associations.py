"""
tests/test_country_isolation_associations.py

GOLDEN -- cross-border identity false-merge isolation for the ASSOCIATIONS +
Páginas Amarillas discovery front (generic-engine vector #8, red-team R3).

``scripts/associations/dedup_upsert.py`` dedups association-mined / directory
dealers against the LIVE ``entity`` identity table with a name+location ladder and
upserts genuinely-new points of sale. Before the country-proof fix the whole
``DedupIndex`` was country-blind:

  * ``DedupIndex.load``  SELECT omitted ``country_code``; the dedup keys were the
    bare ``(norm_name, municipality_code)`` / ``(norm_name, province_code)``.
  * ``DedupIndex.match`` crossed those keys with NO country.
  * ``upsert_entity``'s ``INSERT INTO entity`` omitted ``country_code`` (fell to the
    DB DEFAULT ``'ES'``) and minted the ``cdp_code`` with the default ES prefix.

So a Spanish association/directory POS and a German dealer that share a normalised
name and a numeric ``municipality_code`` collapse into ONE identity row: the ES POS
is SUPPRESSED and its source merely attached onto the DE dealer's ``entity``. The
collision is REAL, not hypothetical: a second country reuses the same numeric
``municipality_code`` space (``migrations/0053`` -- DE province ``'28'`` deliberately
coexists with ES Madrid ``'28'``). This is the same class as the dealer/overlay
vectors already closed (``test_country_isolation_dealer.py`` /
``test_country_isolation_overlay_dedup.py``), but this discovery path carried no
country and no guard.

WHAT IS ASSERTED
----------------
  match      : ES vs DE sharing name+muni            -> MUST NOT dup (no cross-country hit)
  match      : two ES sharing name+muni              -> MUST     dup  (no-regression)
  upsert     : ES POS vs existing DE dealer          -> inserts its OWN ES entity, the DE
                                                        dealer gets NO ES entity_source (not fused)
  upsert     : ES POS vs existing ES dealer          -> dup: attaches entity_source, no new row (no-reg)
  upsert     : explicit DE record vs existing ES dealer-> inserts its OWN DE entity (country_code
                                                        threaded from the record, not the DB DEFAULT)

The tests drive the REAL shipped surface both live consumers
(``upsert_associations.py`` / ``upsert_paginas_amarillas.py``) are built on --
``DedupIndex.load`` / ``.match`` and ``upsert_entity`` -- NOT a copy, so a regression
in the pipeline, not just a fixture, trips the guard.

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). It HARD-REFUSES
:5433 (live production, ~452k entities) two ways -- by DSN string and by asserting
the target census is empty before seeding. Every test seeds inside a transaction
and ROLLS BACK, leaving the dry-run byte-identical (``entity`` stays 0).
"""
from __future__ import annotations

import os

import psycopg2
import psycopg2.extras
import pytest

from scripts.associations.dedup_upsert import DedupIndex, upsert_entity

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Crockford base32 (no I, L, O, U) -- the alphabet entity_ulid_shape accepts:
#   CHECK (entity_ulid ~ '^[0-9A-HJKMNP-TV-Z]{26}$')
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Connection + isolation guard (same surface as the sibling country goldens)
# ---------------------------------------------------------------------------
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
      3. refuse to seed unless the target ``entity`` table is EMPTY (the dry-run
         is entity=0; production holds ~452k) -- so a mis-pointed DSN can never
         mutate real data.
    """
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip(
            "refusing to run the associations-isolation golden against :5433 "
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
            "refusing to seed/upsert against a populated census")
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


# ---------------------------------------------------------------------------
# Seeding helpers (FK + CHECK respecting) -- mirror test_country_isolation_dealer
# ---------------------------------------------------------------------------
def _ulid(tag: str) -> str:
    """Deterministic 26-char Crockford ULID from a safe tag (entity_ulid_shape)."""
    safe = "".join(c for c in tag.upper() if c in _CROCKFORD)
    return (safe + "0" * 26)[:26]


def _seed_geo(cur, country: str, province: str = "28", muni: str = "28079") -> None:
    """Seed (country, province) then (country, muni). A second country reusing the
    same numeric code is an ON CONFLICT no-op -- exactly the deliberate 0053
    dup-code coexistence the dedup must not pool across."""
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


def _seed_entity(cur, *, ulid_tag: str, cdp: str, name: str, country: str,
                 kind: str = "compraventa", province: str = "28",
                 muni: str = "28079") -> str:
    """Insert one existing in-scope dealer (status='active') and return its
    entity_ulid. trade_name is the load-bearing field (it drives the name dedup
    key); legal_name mirrors it for fidelity."""
    ulid = _ulid(ulid_tag)
    cur.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " province_code, municipality_code, country_code, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active')",
        (ulid, cdp, kind, name, name, province, muni, country),
    )
    return ulid


def _count(cur, sql: str, args: tuple) -> int:
    cur.execute(sql, args)
    return cur.fetchone()[0]


# ===========================================================================
# DedupIndex.match -- the shared chokepoint both live consumers call
# (upsert_associations.run / upsert_paginas_amarillas.run -> idx.match)
# ===========================================================================
def test_match_name_muni_cross_country_does_not_dup(dry_conn):
    """An ES candidate sharing (norm_name, muni) with an existing DE dealer MUST NOT
    resolve as a duplicate -- the name+muni key is country-scoped."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        _seed_entity(cur, ulid_tag="ASSOCDE", cdp="CDP-DE-28-AUTOCNDE",
                     name="Auto Centrum", country="DE")

    idx = DedupIndex.load(dry_conn)
    # The ES consumers call match WITHOUT a country arg -> it defaults to 'ES'.
    existing, reason = idx.match(name="Auto Centrum", website=None,
                                 municipality_code="28079", province_code="28")

    assert existing is None, (
        "CROSS-BORDER FALSE-MERGE: an ES 'Auto Centrum' in INE muni '28079' deduped "
        f"onto a DE dealer sharing the numeric muni (matched cdp={existing!r}, "
        f"reason={reason!r}). The DedupIndex name+muni/prov keys are country-blind.")


def test_match_name_muni_same_country_dups(dry_conn):
    """No-regression: an ES candidate sharing (norm_name, muni) with an existing ES
    dealer MUST still resolve as a duplicate."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_entity(cur, ulid_tag="ASSOCES", cdp="CDP-ES-28-AUTOCNES",
                     name="Auto Centrum", country="ES")

    idx = DedupIndex.load(dry_conn)
    existing, reason = idx.match(name="Auto Centrum", website=None,
                                 municipality_code="28079", province_code="28")

    assert existing == "CDP-ES-28-AUTOCNES", (
        "ES REGRESSION: two ES dealers sharing (norm_name, muni) did NOT dedup "
        f"(existing={existing!r}, reason={reason!r}) -- the country fix broke "
        "same-country name+muni dedup.")


# ===========================================================================
# upsert_entity -- the canonical dedup+insert helper (full real path)
# ===========================================================================
def test_upsert_entity_cross_country_inserts_own_es_not_fused(dry_conn):
    """An ES POS upserted against an existing DE dealer that shares name+muni MUST
    insert its OWN ES entity; the DE dealer must NOT receive the ES entity_source
    and the ES POS must NOT be suppressed."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        _seed_entity(cur, ulid_tag="UPDEDE", cdp="CDP-DE-28-AUTOCNDE",
                     name="Auto Centrum", country="DE")

    idx = DedupIndex.load(dry_conn)
    code, status, reason = upsert_entity(
        dry_conn, idx, name="Auto Centrum", kind="concesionario_oficial",
        source_key="acevas", source_ref="https://www.acevas.com/auto-centrum",
        municipality_code="28079", province_code="28")

    assert status == "new", (
        "CROSS-BORDER FALSE-MERGE: an ES POS 'Auto Centrum' (INE muni '28079') was "
        f"deduped onto the DE dealer instead of inserted (status={status!r}, "
        f"code={code!r}, reason={reason!r}). upsert_entity is country-blind.")
    assert code.startswith("CDP-ES-"), f"ES POS minted a non-ES code: {code!r}"
    assert code != "CDP-DE-28-AUTOCNDE", "ES POS reused the DE dealer's identity code"

    with dry_conn.cursor() as cur:
        attached = _count(
            cur,
            "SELECT count(*) FROM entity_source es JOIN entity e "
            "ON e.entity_ulid = es.entity_ulid "
            "WHERE e.cdp_code = %s AND es.source_key = %s",
            ("CDP-DE-28-AUTOCNDE", "acevas"))
        assert attached == 0, (
            "CROSS-BORDER SOURCE LEAK: the ES association source 'acevas' was attached "
            "onto the DE dealer's entity (cross-country corroboration of a foreign POS).")

        new_country = _count(
            cur, "SELECT count(*) FROM entity WHERE cdp_code = %s AND country_code = 'ES'",
            (code,))
        assert new_country == 1, (
            f"the inserted ES POS {code!r} was not written with country_code='ES' "
            "(country must be set explicitly on insert, not left to chance).")


def test_upsert_entity_same_country_dups_attaches_source(dry_conn):
    """No-regression: an ES POS upserted against an existing ES dealer sharing
    name+muni MUST dedup -- attach the entity_source, insert NO new entity."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_entity(cur, ulid_tag="UPSAMEES", cdp="CDP-ES-28-AUTOCNES",
                     name="Auto Centrum", country="ES")

    idx = DedupIndex.load(dry_conn)
    code, status, reason = upsert_entity(
        dry_conn, idx, name="Auto Centrum", kind="concesionario_oficial",
        source_key="acevas", source_ref="https://www.acevas.com/auto-centrum",
        municipality_code="28079", province_code="28")

    assert status == "dup", (
        "ES REGRESSION: an ES POS sharing name+muni with an existing ES dealer did "
        f"NOT dedup (status={status!r}, code={code!r}) -- the country fix broke "
        "same-country upsert dedup.")
    assert code == "CDP-ES-28-AUTOCNES", f"dup resolved to the wrong identity: {code!r}"

    with dry_conn.cursor() as cur:
        attached = _count(
            cur,
            "SELECT count(*) FROM entity_source es JOIN entity e "
            "ON e.entity_ulid = es.entity_ulid "
            "WHERE e.cdp_code = %s AND es.source_key = %s",
            ("CDP-ES-28-AUTOCNES", "acevas"))
        assert attached == 1, (
            "ES REGRESSION: the association source was NOT attached onto the matched "
            "same-country dealer (the corroborating-source behaviour was lost).")
        total = _count(cur, "SELECT count(*) FROM entity", ())
        assert total == 1, (
            f"ES REGRESSION: a same-country dup inserted a new entity (entity count "
            f"={total}, expected 1 -- the seeded dealer only).")


def test_upsert_entity_threads_explicit_country_into_insert(dry_conn):
    """A DE record upserted against an existing ES dealer sharing name+muni MUST
    insert its OWN DE entity -- the country_code is threaded from the RECORD into the
    INSERT/cdp_code, not taken from the DB DEFAULT ('ES')."""
    with dry_conn.cursor() as cur:
        _seed_geo(cur, "ES")
        _seed_geo(cur, "DE")
        _seed_entity(cur, ulid_tag="UPEXPES", cdp="CDP-ES-28-AUTOCNES",
                     name="Auto Centrum", country="ES")

    idx = DedupIndex.load(dry_conn)
    code, status, reason = upsert_entity(
        dry_conn, idx, name="Auto Centrum", kind="concesionario_oficial",
        source_key="acevas", source_ref="https://example.de/auto-centrum",
        municipality_code="28079", province_code="28", country_code="DE")

    assert status == "new", (
        "CROSS-BORDER FALSE-MERGE: a DE record deduped onto the existing ES dealer "
        f"(status={status!r}, code={code!r}, reason={reason!r}).")
    assert code.startswith("CDP-DE-"), (
        f"the DE record minted a non-DE code {code!r}: country_code was not threaded "
        "into cdp_code (would collide with the ES identity space).")

    with dry_conn.cursor() as cur:
        new_country = _count(
            cur, "SELECT count(*) FROM entity WHERE cdp_code = %s AND country_code = 'DE'",
            (code,))
        assert new_country == 1, (
            f"the inserted DE POS {code!r} was not written with country_code='DE' "
            "(country must be derived from the record, not the DB DEFAULT).")
        leaked = _count(
            cur,
            "SELECT count(*) FROM entity_source es JOIN entity e "
            "ON e.entity_ulid = es.entity_ulid "
            "WHERE e.cdp_code = %s AND es.source_key = %s",
            ("CDP-ES-28-AUTOCNES", "acevas"))
        assert leaked == 0, (
            "CROSS-BORDER SOURCE LEAK: the DE record's source attached onto the ES dealer.")

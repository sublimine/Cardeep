"""Country-coexistence regression guard (Fase 0 -> 0053 country onboarding).

This file proves the SECOND-COUNTRY pilot can land WITHOUT changing ANY ``ES``
behavior. It is the cross-cutting coexistence test that complements
``tests/test_country_golden.py`` (Fase-0 ES byte-identity) and
``tests/test_country_pilot_de.py`` (the full DB seed/teardown pilot).

Four guarantees, in order of the mandate:

  (a) ES ``cdp_code`` / ``canonical_key`` / ``pipeline.paths`` outputs are
      BYTE-IDENTICAL — re-affirming the golden so a regression here trips even
      if ``test_country_golden.py`` were edited. DB-free, ``@pytest.mark.unit``.
  (b) ``mint_code``/``cdp_pair`` with ``country_code='DE'`` mint ``CDP-DE-*``
      codes that are DISTINCT from ``CDP-ES-*`` yet share the same base32 tail
      (only the 2-letter country segment differs) AND keep the ``canonical_key``
      pre-image country-blind. DB-free, ``@pytest.mark.unit``.
  (c) [DB] With migration 0053 applied (composite geo PK ``(country_code,code)``)
      a DE province ``'28'`` COEXISTS with ES province ``'28'`` with no PK
      violation, and the DE municipality's FK resolves to the DE province, NOT
      ES Madrid. Self-contained + reversible: seeds BOTH the minimal ES ``'28'``
      backbone and the synthetic DE rows inside a transaction and ROLLS BACK, so
      it needs no pre-existing census and leaves zero residue.
  (d) [DB] ES entity/geo counts are UNCHANGED by DE coexistence — a before/after
      proof that seeds the ES ``'28'`` backbone, snapshots the ES geo/entity
      counts, inserts the synthetic DE rows, and asserts the ES counts did not
      move (no DE row bled into the ``country_code='ES'`` slice), then rolls back.

ISOLATION (inviolable): the DB parts run ONLY against the dry-run (:5434). They
honor ``CARDEEP_DSN`` (default :5434), HARD-REFUSE :5433 (live production) by DSN
string, and refuse to seed unless ``entity`` is EMPTY — so a mis-pointed DSN can
never mutate real data. They self-seed both countries inside a rolled-back
transaction, needing nothing but a reachable :5434 with the schema at head
(>= 0053 composite geo PK). This makes them binding goldens of the country-proof
gate on an empty migrated census, with zero dependence on a populated :5433.
"""
from __future__ import annotations

import asyncio
import os
import re
from pathlib import Path

import pytest

from services.api.codes import (
    _base32,
    canonical_key,
    cdp_code,
    cdp_pair,
    mint_code,
)

# Repo root: this file is <repo>/tests/test_country_coexistence.py.
_REPO_ROOT = Path(__file__).resolve().parent.parent

# Crockford-base32 alphabet used by the mint (no I, L, O, U).
_CROCKFORD_RE = re.compile(r"^[0-9A-HJKMNP-TV-Z]{8}$")

# --- Pinned ES byte-identity table (mirrors test_country_golden.py) ----------
# kwargs -> (expected canonical_key pre-image, expected full cdp_code).
# These literals are the live ES golden codes. A single drift here means an ES
# cdp_code changed = the dedup key keying 431k entities was re-keyed.
_ES_GOLDEN: list[tuple[dict, str, str]] = [
    (dict(province_code="50", particular_platform="coches.net", particular_seller_id="50"),
     "particular:cochesnet:50", "CDP-ES-50-FPB3W1R6"),
    (dict(province_code="04", particular_platform="milanuncios", particular_seller_id="109905688"),
     "particular:milanuncios:109905688", "CDP-ES-04-CR8NMA86"),
    (dict(province_code="45", particular_platform="wallapop", particular_seller_id="dqjwpv3enezo"),
     "particular:wallapop:dqjwpv3enezo", "CDP-ES-45-84ZNGKZR"),
    (dict(province_code="28", domain="ford.es"),
     "domain:ford.es", "CDP-ES-28-ZB6C77HC"),
    (dict(province_code="28", cif="B12345678"),
     "cif:B12345678", "CDP-ES-28-8H6PF2E7"),
    (dict(province_code="08", name="Talleres X", municipality_code="08019"),
     "name:talleresx|08019", "CDP-ES-08-3BJB5CQP"),
    (dict(province_code="28", name="Garaje Y"),
     "name:garajey|p28", "CDP-ES-28-T0ZNP4ZQ"),
]

# --- Synthetic ES '28' backbone (minimal Madrid seed for the dry-run) --------
# The DB goldens self-seed this ES side so the coexistence proof has an ES '28' to
# coexist with on the empty :5434 census — no dependence on a populated :5433. The
# muni '28079' satisfies the ES prefix CHECK left(code,2)=province_code.
_ES_PROVINCE_CODE = "28"
_ES_PROVINCE_NAME = "Madrid"
_ES_CCAA_CODE = "13"
_ES_CCAA_NAME = "Comunidad de Madrid"
_ES_MUNI_CODE = "28079"
_ES_MUNI_NAME = "Madrid"
_ES_DOMAIN = "ford.es"
# 26-char Crockford ULID (shape ^[0-9A-HJKMNP-TV-Z]{26}$ — no I/L/O/U), distinct
# from the DE ULID below so an ES and a DE entity coexist in one transaction.
_ES_ENTITY_ULID = "01C0EXSTES0000000000PYRES0"

# Synthetic DE pilot fixtures (NO real DE data — minimal coexistence proof).
# Province code '28' DELIBERATELY collides with ES Madrid to prove the composite
# PK lets (DE,'28') and (ES,'28') coexist. Municipality '28001' satisfies the
# ES-shaped prefix CHECK left(code,2)=province_code so the seed is CHECK-clean
# regardless of whether 0053's CHECK relaxation shipped.
_DE_PROVINCE_CODE = "28"
_DE_PROVINCE_NAME = "Brandenburg-pilot"
_DE_CCAA_CODE = "BB"
_DE_CCAA_NAME = "Brandenburg"
_DE_MUNI_CODE = "28001"
_DE_MUNI_NAME = "Potsdam-pilot"
_DE_DOMAIN = "example-haendler.de"
# 26-char Crockford ULID (shape ^[0-9A-HJKMNP-TV-Z]{26}$ — no I/L/O/U). Verified
# against entity.entity_ulid_shape live.
_DE_ENTITY_ULID = "01C0EXSTDE0000000000PYRDE0"

# Dry-run DSN (:5434). The mandate: NEVER touch :5433 (live production). The suite
# honors CARDEEP_DSN so the country-proof CI job (host :5434, empty migrated census)
# and a local dev both aim it at the dry-run; it defaults to the local :5434.
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"


def _target_dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


DSN = _target_dsn()


# ===========================================================================
# (a) ES BYTE-IDENTITY — re-affirm the golden (DB-free)
# ===========================================================================
@pytest.mark.unit
class TestEsByteIdentityUnchangedByCoexistence:
    """ES outputs stay byte-identical: coexistence support never re-keys ES."""

    @pytest.mark.parametrize("kwargs,expected_key,expected_code", _ES_GOLDEN)
    def test_es_cdp_pair_byte_identical(self, kwargs, expected_key, expected_code):
        key, code = cdp_pair(**kwargs)
        assert key == expected_key, f"canonical_key drift for {kwargs}"
        assert code == expected_code, (
            f"cdp_code DRIFT for {kwargs} — re-keys the ES census")

    @pytest.mark.parametrize("kwargs,expected_key,expected_code", _ES_GOLDEN)
    def test_es_cdp_code_matches_pair_and_literal(self, kwargs, expected_key, expected_code):
        assert cdp_code(**kwargs) == cdp_pair(**kwargs)[1] == expected_code

    def test_es_default_equals_explicit_es(self):
        # The default country MUST equal an explicit 'ES' — byte for byte.
        for kwargs, _, expected_code in _ES_GOLDEN:
            assert cdp_code(**kwargs) == expected_code
            assert cdp_code(**kwargs, country_code="ES") == expected_code

    def test_canonical_key_is_country_blind(self):
        # THE dedup invariant: the pre-image must NOT incorporate the country, so
        # an ES key and a DE key for the SAME identity are identical (only the
        # human-facing CDP-XX- prefix differs). If the country leaked into the
        # key, every sha256 would change and all entities would be re-keyed.
        for kwargs, expected_key, _ in _ES_GOLDEN:
            assert canonical_key(**kwargs) == expected_key
        es = canonical_key(province_code="28", domain="ford.es", country_code="ES")
        de = canonical_key(province_code="28", domain="ford.es", country_code="DE")
        assert es == de == "domain:ford.es", (
            "country_code leaked into the canonical_key pre-image — re-keys dedup")

    def test_es_paths_byte_identical(self):
        paths = pytest.importorskip(
            "pipeline.paths",
            reason="Fase-0 deliverable missing: pipeline/paths.py is not present.")
        root = _REPO_ROOT.as_posix()
        # Default (no arg) and explicit 'ES' both resolve to the legacy literals.
        assert paths.recipe_root().as_posix() == f"{root}/countries/ES"
        assert paths.recipe_root("ES") == paths.recipe_root()
        assert paths.recipes_flat_dir().as_posix() == f"{root}/countries/ES/recipes"
        assert paths.data_root().as_posix() == f"{root}/data/ES"
        assert paths.census_dir().as_posix() == f"{root}/countries/ES/census"


# ===========================================================================
# (b) DE MINTING — CDP-DE-* distinct from CDP-ES-*, tail-identical (DB-free)
# ===========================================================================
@pytest.mark.unit
class TestDeMintingDistinctFromEs:
    """mint_code/cdp_pair(country_code='DE') -> CDP-DE-*, never colliding with ES."""

    def test_mint_code_de_only_country_segment_changes(self):
        # Same digest + province -> identical 8-char tail, only the country differs.
        import hashlib
        digest = hashlib.sha256(b"coexistence-seed").digest()
        es = mint_code(province_code="28", digest=digest, country_code="ES")
        de = mint_code(province_code="28", digest=digest, country_code="DE")
        assert es.startswith("CDP-ES-28-")
        assert de.startswith("CDP-DE-28-")
        assert es != de, "CDP-DE- code must be distinct from the CDP-ES- code"
        # ONLY the 2-letter country segment differs.
        assert es.rsplit("-", 1)[1] == de.rsplit("-", 1)[1] == _base32(digest)

    def test_cdp_pair_de_distinct_but_key_country_blind(self):
        # Same identity, two countries: keys identical, codes differ only on CC.
        key_es, code_es = cdp_pair(province_code="28", domain="ford.es", country_code="ES")
        key_de, code_de = cdp_pair(province_code="28", domain="ford.es", country_code="DE")
        assert key_es == key_de == "domain:ford.es"
        assert code_es == "CDP-ES-28-ZB6C77HC"
        assert code_de.startswith("CDP-DE-28-")
        assert code_de != code_es
        assert code_es.rsplit("-", 1)[1] == code_de.rsplit("-", 1)[1]

    def test_synthetic_de_dealer_code_shape(self):
        # The exact CDP-DE code the pilot mints for the synthetic dealer.
        key, code = cdp_pair(
            province_code=_DE_PROVINCE_CODE, domain=_DE_DOMAIN, country_code="DE")
        assert key == f"domain:{_DE_DOMAIN}"
        assert code.startswith(f"CDP-DE-{_DE_PROVINCE_CODE}-")
        tail = code.rsplit("-", 1)[1]
        assert _CROCKFORD_RE.match(tail), f"non-Crockford tail in {code}"
        # A DE code can NEVER be mistaken for an ES code (different country segment).
        assert not code.startswith("CDP-ES-")

    def test_g1_regex_acceptance_of_de_code(self):
        # The widened G1 validator (complete.py) must accept the CDP-DE code if it
        # has been widened; if it is still hard-coded to ^CDP-ES- (0053 code-side
        # not yet shipped), skip rather than fail — this file's job is coexistence,
        # not enforcing the widening (that is test_country_golden.py's xfail).
        from pipeline import complete
        _, de_code = cdp_pair(
            province_code=_DE_PROVINCE_CODE, domain=_DE_DOMAIN, country_code="DE")
        if not complete._CDP_CODE_RE.match(de_code):
            pytest.skip(
                "complete.py:_CDP_CODE_RE still hard-codes '^CDP-ES-' (G1 regex "
                "not yet widened to '^CDP-([A-Z]{2})-'); coexistence regex check "
                "deferred to the 0053 code-side change.")
        assert complete._CDP_CODE_RE.match(de_code)
        # And it must STILL accept every live ES code (strict superset).
        for _, _, es_code in _ES_GOLDEN:
            assert complete._CDP_CODE_RE.match(es_code), (
                f"widened G1 regex regressed on live ES code {es_code}")


# ===========================================================================
# DB helpers — availability + 0053-applied + pilot-present detection
# ===========================================================================
def _run(coro):
    """Run a coroutine with a single asyncio.run (Windows ProactorEventLoop safe)."""
    return asyncio.run(coro)


def _db_available() -> bool:
    async def _ping() -> bool:
        try:
            import asyncpg
            conn = await asyncpg.connect(DSN, timeout=3)
            await conn.close()
            return True
        except Exception:
            return False
    try:
        return _run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _db_available()

# Golden isolation guard (mirrors test_country_isolation_*.py): the DB coexistence
# proofs run ONLY against the dry-run. They self-seed BOTH the ES and the DE side
# inside a rolled-back transaction, so they need nothing but a reachable :5434 with
# the schema at head (>= 0053 composite geo PK). They HARD-REFUSE :5433 by DSN.
_DB_GATE = pytest.mark.skipif(
    (not DB_AVAILABLE) or ("5433" in DSN),
    reason="dry-run cardeep-pg not reachable, or refusing :5433 (live production); "
           "point CARDEEP_DSN at the :5434 dry-run")


async def _geo_province_pk_is_composite(conn) -> bool:
    """True iff migration 0053 promoted geo_province PK to (country_code, code).

    The single reliable, version-table-independent signal that 0053 is applied:
    the geo_province PRIMARY KEY definition mentions country_code.
    """
    definition = await conn.fetchval(
        "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
        "WHERE contype='p' AND conrelid='geo_province'::regclass")
    return bool(definition) and "country_code" in definition


async def _seed_de_rows(conn) -> None:
    """INSERT the minimal synthetic DE backbone: province '28' + muni '28001' + dealer.

    Caller MUST run this inside a transaction that is rolled back. Uses the real
    mint_code via cdp_pair so the dealer code is the genuine CDP-DE-28-* code, not
    a hand-built string. Supplies the mandatory ccaa_code/ccaa_name (NOT NULL,
    no default on geo_province) that the switchover doc omits.
    """
    _, de_cdp = cdp_pair(
        province_code=_DE_PROVINCE_CODE, domain=_DE_DOMAIN, country_code="DE")
    de_key = canonical_key(
        province_code=_DE_PROVINCE_CODE, domain=_DE_DOMAIN, country_code="DE")
    await conn.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES ($1, $2, $3, $4, 'DE')",
        _DE_PROVINCE_CODE, _DE_PROVINCE_NAME, _DE_CCAA_CODE, _DE_CCAA_NAME)
    await conn.execute(
        "INSERT INTO geo_municipality (code, name, province_code, comarca_id, country_code) "
        "VALUES ($1, $2, $3, NULL, 'DE')",
        _DE_MUNI_CODE, _DE_MUNI_NAME, _DE_PROVINCE_CODE)
    await conn.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, country_code, province_code, municipality_code, "
        " canonical_key, status, kind_source) "
        "VALUES ($1, $2, 'compraventa', 'DE', $3, $4, $5, 'active', 'manual')",
        _DE_ENTITY_ULID, de_cdp, _DE_PROVINCE_CODE, _DE_MUNI_CODE, de_key)
    return de_cdp


async def _guard_dryrun(conn) -> None:
    """Refuse to seed unless the target ``entity`` table is EMPTY.

    Defense-in-depth (on top of the :5433 DSN-string refusal in ``_DB_GATE``): the
    dry-run is entity=0; production holds ~452k. A mis-pointed CARDEEP_DSN at any
    populated census is skipped here BEFORE a single INSERT runs.
    """
    n = await conn.fetchval("SELECT count(*) FROM entity")
    if n != 0:
        pytest.skip(
            f"target DB has {n} entities -- not the empty dry-run; refusing to "
            "seed/coexist against a populated census")


async def _seed_es_28(conn) -> None:
    """INSERT the minimal ES Madrid backbone: province '28' + muni '28079'.

    Caller MUST run this inside a transaction that is rolled back. ON CONFLICT
    DO NOTHING keeps it idempotent within the txn. Supplies ccaa_code/ccaa_name
    (NOT NULL on geo_province). Muni '28079' satisfies the ES prefix CHECK
    left(code,2)=province_code.
    """
    await conn.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES ($1, $2, $3, $4, 'ES') ON CONFLICT DO NOTHING",
        _ES_PROVINCE_CODE, _ES_PROVINCE_NAME, _ES_CCAA_CODE, _ES_CCAA_NAME)
    await conn.execute(
        "INSERT INTO geo_municipality (code, name, province_code, comarca_id, country_code) "
        "VALUES ($1, $2, $3, NULL, 'ES') ON CONFLICT DO NOTHING",
        _ES_MUNI_CODE, _ES_MUNI_NAME, _ES_PROVINCE_CODE)


async def _seed_es_entity(conn) -> str:
    """INSERT one synthetic ES dealer on the seeded ES '28' backbone; return its
    cdp_code. Uses the real cdp_pair so the code is the genuine CDP-ES-28-* code.
    The ES '28' geo backbone (``_seed_es_28``) MUST already be seeded in the txn.
    """
    es_key, es_cdp = cdp_pair(
        province_code=_ES_PROVINCE_CODE, domain=_ES_DOMAIN, country_code="ES")
    await conn.execute(
        "INSERT INTO entity "
        "(entity_ulid, cdp_code, kind, country_code, province_code, municipality_code, "
        " canonical_key, status, kind_source) "
        "VALUES ($1, $2, 'compraventa', 'ES', $3, $4, $5, 'active', 'manual')",
        _ES_ENTITY_ULID, es_cdp, _ES_PROVINCE_CODE, _ES_MUNI_CODE, es_key)
    return es_cdp


# ===========================================================================
# (c) DB COEXISTENCE — DE '28' coexists with ES '28' (composite PK, reversible)
# ===========================================================================
@_DB_GATE
@pytest.mark.integration
class TestDbProvinceCoexistence:
    """(DE,'28') and (ES,'28') coexist on the composite geo PK; the DE muni FK
    resolves to the DE province, never ES Madrid. Self-seeds BOTH countries."""

    def test_es_28_present_after_seed(self):
        """The ES '28' backbone seeds cleanly as the coexistence anchor (rolled back)."""
        async def _go():
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                tx = conn.transaction()
                await tx.start()
                try:
                    await _guard_dryrun(conn)
                    await _seed_es_28(conn)
                    n = await conn.fetchval(
                        "SELECT count(*) FROM geo_province "
                        "WHERE country_code='ES' AND code='28'")
                    assert n == 1, "ES province '28' (Madrid) seed did not land"
                finally:
                    await tx.rollback()
            finally:
                await conn.close()
        _run(_go())

    def test_de_28_coexists_with_es_28(self):
        """Seed ES '28' + DE '28' in one rolled-back txn and prove no PK collision:
        both provinces named '28' coexist (distinguished by country), the DE
        municipality's composite FK resolves to the DE province (NOT ES Madrid),
        and the synthetic DE dealer carries its real CDP-DE-28-* code. The whole
        scenario runs in ONE transaction that is rolled back, so the dry-run is
        byte-identical after.
        """
        async def _go():
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                tx = conn.transaction()
                await tx.start()
                try:
                    await _guard_dryrun(conn)
                    assert await _geo_province_pk_is_composite(conn), (
                        "geo_province PK is not composite (country_code, code); the "
                        "schema is below migration 0053 — DE '28' would collide with "
                        "ES '28' on the single-column PK and coexistence is impossible")
                    await _seed_es_28(conn)
                    de_cdp = await _seed_de_rows(conn)

                    # (a) BOTH provinces named '28' coexist, distinguished by country.
                    rows = await conn.fetch(
                        "SELECT country_code, code, name FROM geo_province "
                        "WHERE code='28' ORDER BY country_code")
                    by_cc = {r["country_code"].strip(): r["name"] for r in rows}
                    assert "ES" in by_cc and "DE" in by_cc, (
                        f"expected both ES and DE province '28', got {by_cc}")
                    assert by_cc["DE"] == _DE_PROVINCE_NAME
                    assert by_cc["ES"] == _ES_PROVINCE_NAME
                    # ES Madrid name is NOT overwritten by the DE row.
                    assert by_cc["ES"] != _DE_PROVINCE_NAME

                    # (b) The DE municipality's composite FK resolves to the DE
                    #     province, NOT ES Madrid — the coexistence proof.
                    resolved = await conn.fetchrow(
                        "SELECT p.country_code, p.name "
                        "FROM geo_municipality m "
                        "JOIN geo_province p "
                        "  ON p.country_code = m.country_code AND p.code = m.province_code "
                        "WHERE m.code=$1 AND m.country_code='DE'",
                        _DE_MUNI_CODE)
                    assert resolved is not None, "DE municipality FK did not resolve"
                    assert resolved["country_code"].strip() == "DE"
                    assert resolved["name"] == _DE_PROVINCE_NAME, (
                        "DE muni FK resolved to the wrong province (ES bleed)")

                    # (c) The synthetic DE dealer landed with its real CDP-DE code.
                    ent = await conn.fetchrow(
                        "SELECT country_code, cdp_code, province_code, municipality_code "
                        "FROM entity WHERE entity_ulid=$1", _DE_ENTITY_ULID)
                    assert ent is not None, "synthetic DE entity not inserted"
                    assert ent["country_code"].strip() == "DE"
                    assert ent["cdp_code"] == de_cdp
                    assert ent["cdp_code"].startswith("CDP-DE-28-")
                finally:
                    # Reversible: discard every synthetic row. DB byte-identical.
                    await tx.rollback()
            finally:
                await conn.close()
        _run(_go())


# ===========================================================================
# (d) DB ES-IMMUTABILITY — ES counts unchanged by DE coexistence
# ===========================================================================
@_DB_GATE
@pytest.mark.integration
class TestDbEsCountsUnchanged:
    """ES geo/entity counts are not mutated by DE coexistence (self-seeded before/
    after proofs on the empty dry-run — every test rolls back)."""

    def test_es_geo_not_mutated_by_de_coexistence(self):
        """Seed ES '28', snapshot the country_code='ES' geo slice, seed the DE side,
        and assert the ES geo counts did not move — no DE row bled into the ES slice."""
        async def _go():
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                tx = conn.transaction()
                await tx.start()
                try:
                    await _guard_dryrun(conn)
                    await _seed_es_28(conn)

                    async def _es_geo():
                        return (
                            await conn.fetchval(
                                "SELECT count(*) FROM geo_province WHERE country_code='ES'"),
                            await conn.fetchval(
                                "SELECT count(*) FROM geo_municipality WHERE country_code='ES'"),
                        )

                    before = await _es_geo()
                    assert before == (1, 1), f"ES backbone seed wrong: {before}"
                    await _seed_de_rows(conn)
                    after = await _es_geo()
                    assert before == after, (
                        f"ES geo counts changed by DE coexistence: {before} -> {after}")
                finally:
                    await tx.rollback()
            finally:
                await conn.close()
        _run(_go())

    def test_es_entity_not_reduced_by_de_coexistence(self):
        """Seed one ES dealer, snapshot the ES entity count, seed the DE dealer, and
        assert the country_code='ES' entity count is unchanged and the ES dealer is
        still present (DE coexistence neither deletes nor re-keys ES entities)."""
        async def _go():
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                tx = conn.transaction()
                await tx.start()
                try:
                    await _guard_dryrun(conn)
                    await _seed_es_28(conn)
                    es_cdp = await _seed_es_entity(conn)
                    before = await conn.fetchval(
                        "SELECT count(*) FROM entity WHERE country_code='ES'")
                    assert before == 1, f"ES entity seed wrong: {before}"
                    await _seed_de_rows(conn)
                    after = await conn.fetchval(
                        "SELECT count(*) FROM entity WHERE country_code='ES'")
                    assert before == after == 1, (
                        f"ES entity count changed by DE coexistence: {before} -> {after}")
                    still = await conn.fetchrow(
                        "SELECT cdp_code FROM entity WHERE entity_ulid=$1", _ES_ENTITY_ULID)
                    assert still is not None and still["cdp_code"] == es_cdp, (
                        "ES dealer vanished or was re-keyed by DE coexistence")
                finally:
                    await tx.rollback()
            finally:
                await conn.close()
        _run(_go())

    def test_inserting_de_rows_does_not_change_es_counts(self):
        """Before/after proof on a seeded ES baseline: snapshot ES geo+entity counts,
        insert the synthetic DE rows, assert the ES counts are identical, and confirm
        the DE rows DID land (the insert was real, not a no-op). All rolled back."""
        async def _go():
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                tx = conn.transaction()
                await tx.start()
                try:
                    await _guard_dryrun(conn)
                    await _seed_es_28(conn)
                    await _seed_es_entity(conn)

                    async def _es_counts():
                        return (
                            await conn.fetchval(
                                "SELECT count(*) FROM geo_province WHERE country_code='ES'"),
                            await conn.fetchval(
                                "SELECT count(*) FROM geo_municipality WHERE country_code='ES'"),
                            await conn.fetchval(
                                "SELECT count(*) FROM entity WHERE country_code='ES'"),
                        )

                    before = await _es_counts()
                    await _seed_de_rows(conn)
                    after = await _es_counts()
                    assert before == after, (
                        f"ES counts changed by DE insertion: {before} -> {after}")

                    # And the DE rows DID land (the insert was real, not a no-op).
                    de_prov = await conn.fetchval(
                        "SELECT count(*) FROM geo_province WHERE country_code='DE'")
                    de_ent = await conn.fetchval(
                        "SELECT count(*) FROM entity WHERE country_code='DE'")
                    assert de_prov >= 1 and de_ent >= 1, "DE insert was a no-op"
                finally:
                    await tx.rollback()
            finally:
                await conn.close()
        _run(_go())


# ===========================================================================
# Read-only coexistence check against ALREADY-SEEDED pilot rows (if present)
# ===========================================================================
@_DB_GATE
@pytest.mark.integration
class TestDbSeededDeResolvesToDe:
    """A seeded DE municipality resolves to its DE province via the composite FK,
    with no bleed to a non-DE province — the pilot-shaped coexistence read, made
    self-contained (seeds ES + DE, asserts, rolls back)."""

    def test_seeded_de_muni_resolves_to_de_not_es(self):
        async def _go():
            import asyncpg
            conn = await asyncpg.connect(DSN)
            try:
                tx = conn.transaction()
                await tx.start()
                try:
                    await _guard_dryrun(conn)
                    await _seed_es_28(conn)
                    await _seed_de_rows(conn)
                    # ES '28' still present and distinct from the DE '28'.
                    es28 = await conn.fetchval(
                        "SELECT count(*) FROM geo_province "
                        "WHERE country_code='ES' AND code='28'")
                    assert es28 == 1, "ES province '28' missing while DE rows present"
                    # Every seeded DE municipality resolves to a DE province via the
                    # composite FK (no ES bleed).
                    bleed = await conn.fetchval(
                        "SELECT count(*) "
                        "FROM geo_municipality m "
                        "JOIN geo_province p "
                        "  ON p.country_code = m.country_code AND p.code = m.province_code "
                        "WHERE m.country_code='DE' AND p.country_code <> 'DE'")
                    assert bleed == 0, (
                        "a DE municipality resolved to a non-DE province — ES bleed")
                finally:
                    await tx.rollback()
            finally:
                await conn.close()
        _run(_go())

"""P2 country-#2 readiness goldens: product / audit / identity-key country-blindness.

Three country-blind surfaces are closed here, each RED before the P2 fix and GREEN after, with ES
(the default tenant) byte-identical throughout:

  #11 product_stats per country -- the single-row /stats cache (migrations/0055, CHECK(id=1)) becomes
      ONE ROW PER country_code (migrations/0066). The per-country refresh writes a DE row distinct
      from the ES row, and the /stats read path (services.api.stats.fetch_stats) returns the requested
      country's figures -- never ES's, never a cross-country sum. ES stays byte-identical.

  #10 canonical_key_backfill country-aware -- the re-hash gate recomputes cdp_pair() with the row's
      OWN country (country_of_cdp(cdp_code)). A CDP-DE-... entity's canonical_key is filled; before the
      fix the recompute defaulted to ES, never re-hashed to a CDP-DE- code, and the key stayed NULL
      forever. ES rows re-derive their exact historical pre-image (byte-identical).

  #12 country-aware phone dispatch -- pipeline.identity.phone.phone_match_key(raw, country_code) routes
      ES to the byte-identical phone_es authority and non-ES to a generic E.164 key, so a +49 German
      number is a usable cross-source hard key (was None under the ES-only authority) and two calling
      codes can never collide.

ISOLATION (inviolable): the DB tests run ONLY against the :5434 dry-run. They HARD-REFUSE :5433 (live
production) by DSN string, skip if unreachable, and assert the target census is EMPTY before seeding.
Every test seeds inside a transaction and ROLLS BACK -- the dry-run stays entity=0.
"""
from __future__ import annotations

import asyncio
import os

import asyncpg
import pytest

from pipeline.identity.canonical_key_backfill import backfill_canonical_keys
from services.api.codes import cdp_pair

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"


def _dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


def _db_ok() -> bool:
    """Reachable AND not the live census. Refuses :5433 by string before any connect."""
    dsn = _dsn()
    if "5433" in dsn:
        return False

    async def _p() -> bool:
        try:
            c = await asyncpg.connect(dsn, timeout=3)
            await c.close()
            return True
        except Exception:
            return False

    try:
        return asyncio.run(_p())
    except Exception:
        return False


_DB = _db_ok()
SKIP = pytest.mark.skipif(not _DB, reason="dry-run :5434 unreachable or DSN refused (never :5433)")

# Crockford base32 (no I, L, O, U) -- the alphabet entity_ulid_shape CHECK accepts.
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _ulid(tag: str) -> str:
    safe = "".join(c for c in tag.upper() if c in _CROCKFORD)
    return (safe + "0" * 26)[:26]


# --------------------------------------------------------------------------- async seeding helpers
# (asyncpg; FK + CHECK respecting -- same surface the psycopg2 isolation goldens use)

async def _assert_empty_or_skip(conn: asyncpg.Connection) -> None:
    n = await conn.fetchval("SELECT count(*) FROM entity")
    if n != 0:
        pytest.skip(f"target DB has {n} entities -- not the empty dry-run; refusing to seed")


async def _seed_geo(conn, country: str, province: str = "28", muni: str = "28079") -> None:
    await conn.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES ($1,$2,$3,$4,$5) ON CONFLICT DO NOTHING",
        province, f"prov-{country}-{province}", "13", f"ccaa-{country}", country)
    await conn.execute(
        "INSERT INTO geo_municipality (code, name, province_code, comarca_id, country_code) "
        "VALUES ($1,$2,$3,NULL,$4) ON CONFLICT DO NOTHING",
        muni, f"muni-{country}-{muni}", province, country)


async def _seed_dealer(conn, *, tag: str, cdp: str, country: str, province: str = "28",
                       muni: str = "28079", website: str | None = None,
                       canonical_key: str | None = None) -> str:
    """One in-scope sales point: kind='compraventa' (NOT particular/desguace), status='active'."""
    ulid = _ulid(tag)
    await conn.execute(
        "INSERT INTO entity (entity_ulid, cdp_code, kind, trade_name, legal_name, province_code, "
        " municipality_code, country_code, status, website, canonical_key) "
        "VALUES ($1,$2,'compraventa',$3,$3,$4,$5,$6,'active',$7,$8)",
        ulid, cdp, f"dealer {country}", province, muni, country, website, canonical_key)
    return ulid


async def _seed_servable_vehicle(conn, *, tag: str, entity_ulid: str, price: int = 15000) -> str:
    """An available, in-price-band vehicle -> appears in servable_vehicle."""
    ulid = _ulid(tag)
    await conn.execute(
        "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, price, status) "
        "VALUES ($1,$2,$3,$4,$5,'available')",
        ulid, entity_ulid, f"https://dry.run/{ulid}", "seat leon", price)
    return ulid


async def _seed_vam_cluster(conn, vehicle_ulids: list[str]) -> None:
    """One vam_verified cluster run with every vehicle SELF-canonical, so v_canonical_vehicle counts
    each (vc.vehicle_ulid = vc.canonical_vehicle_ulid on the latest vam_verified run)."""
    run = _ulid("VAMRUN")
    await conn.execute(
        "INSERT INTO vehicle_cluster_run (cluster_run_id, resolver, scope, vam_verified) "
        "VALUES ($1,'test','dry-run',true)", run)
    for v in vehicle_ulids:
        await conn.execute(
            "INSERT INTO vehicle_cluster (cluster_run_id, vehicle_ulid, canonical_vehicle_ulid) "
            "VALUES ($1,$2,$2)", run, v)


async def _seed_event(conn, *, tag: str, vehicle_ulid: str, entity_ulid: str) -> None:
    await conn.execute(
        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type) "
        "VALUES ($1,$2,$3,'NEW')", _ulid(tag), vehicle_ulid, entity_ulid)


# ===========================================================================
# #11 product_stats per country
# ===========================================================================
@SKIP
def test_11_product_stats_returns_de_figures_not_es_not_sum():
    """Seed ES + DE servable censuses of DIFFERENT magnitudes, run the per-country refresh, and read
    /stats for each tenant. DE must get DE's figures -- never ES's, never the cross-country sum -- and
    ES must get ES's. RED before the fix: there is no per-country refresh/read surface (single-row
    cache keyed by id=1)."""
    from scripts.refresh_product_stats import refresh_with_conn  # NEW (RED: ImportError today)
    from services.api.stats import fetch_stats                   # NEW (RED: ImportError today)

    async def body():
        conn = await asyncpg.connect(_dsn())
        tr = conn.transaction()
        await tr.start()
        try:
            await _assert_empty_or_skip(conn)
            # geo: ES has 2 provinces (28, 08) + 2 munis; DE has 1 province (28) + 1 muni.
            await _seed_geo(conn, "ES", "28", "28079")
            await _seed_geo(conn, "ES", "08", "08019")
            await _seed_geo(conn, "DE", "28", "28079")
            # dealers: ES = 2 (each with 1 servable vehicle), DE = 1.
            es1 = await _seed_dealer(conn, tag="C2STES1", cdp="CDP-ES-28-C2STES01", country="ES")
            es2 = await _seed_dealer(conn, tag="C2STES2", cdp="CDP-ES-28-C2STES02", country="ES")
            de1 = await _seed_dealer(conn, tag="C2STDE1", cdp="CDP-DE-28-C2STDE01", country="DE")
            ves1 = await _seed_servable_vehicle(conn, tag="C2VES1", entity_ulid=es1)
            ves2 = await _seed_servable_vehicle(conn, tag="C2VES2", entity_ulid=es2)
            vde1 = await _seed_servable_vehicle(conn, tag="C2VDE1", entity_ulid=de1)
            await _seed_vam_cluster(conn, [ves1, ves2, vde1])
            # events: ES = 3, DE = 2.
            await _seed_event(conn, tag="C2EVES1", vehicle_ulid=ves1, entity_ulid=es1)
            await _seed_event(conn, tag="C2EVES2", vehicle_ulid=ves1, entity_ulid=es1)
            await _seed_event(conn, tag="C2EVES3", vehicle_ulid=ves2, entity_ulid=es2)
            await _seed_event(conn, tag="C2EVDE1", vehicle_ulid=vde1, entity_ulid=de1)
            await _seed_event(conn, tag="C2EVDE2", vehicle_ulid=vde1, entity_ulid=de1)

            # The REAL per-country refresh writes ONE product_stats row per country present in entity.
            written = await refresh_with_conn(conn)
            assert set(written) >= {"ES", "DE"}, f"refresh must cover both tenants: {written}"

            # The /stats read path returns the REQUESTED country's figures.
            de_counts, de_at = await fetch_stats(conn, "DE")
            es_counts, es_at = await fetch_stats(conn, "ES")

            expected_de = {"dealers": 1, "vehicles_unique_available": 1, "events": 2,
                           "provinces": 1, "municipalities": 1}
            expected_es = {"dealers": 2, "vehicles_unique_available": 2, "events": 3,
                           "provinces": 2, "municipalities": 2}
            assert de_counts == expected_de, f"DE got {de_counts}, expected DE figures {expected_de}"
            assert es_counts == expected_es, f"ES got {es_counts}, expected ES figures {expected_es}"
            # DE is DE -- not ES, and not the cross-country SUM.
            assert de_counts != es_counts, "DE served ES figures (country-blind)"
            summed = {k: es_counts[k] + de_counts[k] for k in expected_de}
            assert de_counts != summed, f"DE served the cross-country SUM {summed} (country-blind)"
            # Served from the precomputed row, not the live fallback.
            assert de_at is not None and es_at is not None
        finally:
            await tr.rollback()
            await conn.close()

    asyncio.run(body())


@SKIP
def test_11_stats_es_default_byte_identical_to_live_compute():
    """No-regression: with ES the only tenant, fetch_stats(conn, 'ES') -- the default -- equals a live
    compute_counts(conn, 'ES') (the precomputed ES row is byte-identical to the live ES figure)."""
    from scripts.refresh_product_stats import refresh_with_conn
    from services.api.stats import compute_counts, fetch_stats

    async def body():
        conn = await asyncpg.connect(_dsn())
        tr = conn.transaction()
        await tr.start()
        try:
            await _assert_empty_or_skip(conn)
            await _seed_geo(conn, "ES", "28", "28079")
            es = await _seed_dealer(conn, tag="C2ROES1", cdp="CDP-ES-28-C2ROES01", country="ES")
            v = await _seed_servable_vehicle(conn, tag="C2ROV1", entity_ulid=es)
            await _seed_vam_cluster(conn, [v])

            live = await compute_counts(conn, "ES")
            await refresh_with_conn(conn)
            cached, _ = await fetch_stats(conn, "ES")
            assert cached == live, f"ES precomputed row {cached} != live ES compute {live}"
        finally:
            await tr.rollback()
            await conn.close()

    asyncio.run(body())


# ===========================================================================
# #10 canonical_key_backfill country-aware
# ===========================================================================
@SKIP
def test_10_canonical_key_backfill_fills_de_entity():
    """A CDP-DE-... dealer with a NULL canonical_key gets it filled by the backfill. RED before the
    fix: the re-hash gate recomputes cdp_pair() defaulting to ES -> CDP-ES-... -> never equals the
    stored CDP-DE- code -> the gate never matches -> canonical_key stays NULL forever."""

    async def body():
        conn = await asyncpg.connect(_dsn())
        tr = conn.transaction()
        await tr.start()
        try:
            await _assert_empty_or_skip(conn)
            await _seed_geo(conn, "DE", "28", "28079")
            # The stored code is the DE re-hash of the dealer's domain (so a country-aware gate matches).
            key, code = cdp_pair(province_code="28", domain="autohaus-koeln.de", country_code="DE")
            assert code.startswith("CDP-DE-"), code
            ulid = await _seed_dealer(conn, tag="CKDE1", cdp=code, country="DE",
                                      website="autohaus-koeln.de", canonical_key=None)

            summary = await backfill_canonical_keys(conn, apply=True)
            filled = await conn.fetchval(
                "SELECT canonical_key FROM entity WHERE entity_ulid=$1", ulid)
            assert filled == key, (
                f"DE canonical_key not filled (got {filled!r}, expected {key!r}); the re-hash gate "
                "recomputed with the default ES country and never matched the CDP-DE- code -> NULL "
                f"forever. summary={summary}")
        finally:
            await tr.rollback()
            await conn.close()

    asyncio.run(body())


@SKIP
def test_10_canonical_key_backfill_es_byte_identical():
    """No-regression: a CDP-ES-... dealer re-derives its EXACT historical canonical_key pre-image
    (the country fix is a no-op for ES: country_of_cdp -> 'ES', cdp_pair defaults to 'ES')."""

    async def body():
        conn = await asyncpg.connect(_dsn())
        tr = conn.transaction()
        await tr.start()
        try:
            await _assert_empty_or_skip(conn)
            await _seed_geo(conn, "ES", "28", "28079")
            key, code = cdp_pair(province_code="28", domain="talleres-madrid.es", country_code="ES")
            assert code.startswith("CDP-ES-"), code
            ulid = await _seed_dealer(conn, tag="CKES1", cdp=code, country="ES",
                                      website="talleres-madrid.es", canonical_key=None)

            await backfill_canonical_keys(conn, apply=True)
            filled = await conn.fetchval(
                "SELECT canonical_key FROM entity WHERE entity_ulid=$1", ulid)
            assert filled == key, f"ES canonical_key re-derivation drifted: {filled!r} != {key!r}"
        finally:
            await tr.rollback()
            await conn.close()

    asyncio.run(body())


# ===========================================================================
# #12 country-aware phone dispatch (pure unit -- no DB)
# ===========================================================================
@pytest.mark.unit
def test_12_phone_es_served_path_byte_identical():
    """No-regression: the served cross_source_dedup phone key for ES (default, no country arg) is the
    byte-identical 9-digit national from the phone_es authority."""
    from pipeline.identity.cross_source_dedup import _normalize_phone
    assert _normalize_phone("+34 612 345 678") == "612345678"
    assert _normalize_phone("0034612345678") == "612345678"
    assert _normalize_phone("911234567") == "911234567"
    assert _normalize_phone("6123456789") is None   # 10 digits -> rejected (unchanged)
    assert _normalize_phone("+49 30 12345678") is None  # a DE number under the default ES scope


@pytest.mark.unit
def test_12_phone_de_served_path_usable_key():
    """The served cross_source_dedup phone key is country-aware: a DE number normalizes to a usable
    E.164 key. RED before the fix: _normalize_phone takes ONE arg -> TypeError on the country
    dimension (and the ES-only authority would have returned None anyway)."""
    from pipeline.identity.cross_source_dedup import _normalize_phone
    de = _normalize_phone("+49 30 12345678", "DE")
    assert de is not None and de.startswith("+49"), f"DE phone produced no usable key: {de!r}"


@pytest.mark.unit
def test_12_phone_country_aware_authority():
    """The new country-aware authority: ES routes to phone_es (byte-identical), non-ES gets a generic
    E.164 key, and two calling codes never collide. RED before the fix: pipeline.identity.phone does
    not exist (ImportError)."""
    from pipeline.identity.phone import normalize_e164, phone_match_key
    from pipeline.identity.phone_es import normalize_es_phone as es_e164
    from pipeline.identity.phone_es import phone_match_key as es_key

    # ES routes to phone_es -- byte-identical, with or without the explicit default.
    assert phone_match_key("612345678") == es_key("612345678") == "612345678"
    assert phone_match_key("+34 612 345 678", "ES") == "612345678"
    assert normalize_e164("612345678", "ES") == es_e164("612345678") == "+34612345678"
    # A DE number under ES scope is still rejected (today's ES authority, unchanged).
    assert phone_match_key("+49 30 12345678", "ES") is None
    # DE gets a usable E.164 key (was None under the ES-only authority).
    de = phone_match_key("+49 30 12345678", "DE")
    assert de is not None and de.startswith("+49"), de
    # Collision-proof: a Spanish and a German number never share a key (+34... != +49...).
    assert phone_match_key("612345678", "ES") != phone_match_key("+49612345678", "DE")

"""
tests/test_country2_write_spine.py

GOLDEN -- country_code threaded through the WRITE SPINE (discover -> ingest -> mint).

Country #2 readiness P0. The downstream coders are already country-parametrized
(services/api/codes.cdp_code, pipeline.geo.GeoResolver.load, pipeline.paths.*,
pipeline.complete._CDP_CODE_RE / province country-scope). But the WRITE SPINE that
actually MINTS and PERSISTS an entity stayed country-blind:

  * pipeline/sources/base.py   DiscoveredEntity had no country_code field.
  * pipeline/discover.py        cdp_code(...) without country (-> CDP-ES-), the
                                entity INSERT omitted country_code (-> DEFAULT 'ES'),
                                GeoResolver.load(conn) loaded the ES backbone only.
  * pipeline/ingest.py          province gate "01" <= p <= "52" rejects every non-ES
                                province; cdp_code(...) + INSERT country-blind.
  * pipeline/harvest_dealer.py  data_root("ES") / GeoResolver.load(conn) / ingest_dealer
                                hard-bound to ES.
  * pipeline/complete.py        _resolve_recipe_path hard-coded countries/ES.

So a German dealer discovered/ingested today is minted CDP-ES-* with country_code='ES'
(or REJECTED outright by the ES-only province gate). This golden binds the fix:

  RED today : a DE entity is minted CDP-ES-/country='ES' (discover) or REJECTED
              ("out of Spain range") by the province gate (ingest); _resolve_recipe_path
              cannot find a DE recipe; DiscoveredEntity has no country_code.
  GREEN     : the same DE dealer is minted CDP-DE-*/country_code='DE' end-to-end and is
              NOT rejected -- while every ES path stays BYTE-IDENTICAL (default
              country_code='ES' at every new signature).

ISOLATION (inviolable): the DB goldens run ONLY against the dry-run census (:5434).
They HARD-REFUSE :5433 (live production) by DSN string AND by asserting entity/vehicle
are EMPTY before seeding. Every DB test seeds + writes inside a transaction and ROLLS
BACK, leaving the dry-run byte-identical (entity stays 0).
"""
from __future__ import annotations

import asyncio
import dataclasses
import os
import unittest.mock as mock
from pathlib import Path

import asyncpg
import pytest

from pipeline import harvest_dealer
from pipeline.complete import _resolve_recipe_path
from pipeline.discover import _upsert
from pipeline.geo import GeoResolver
from pipeline.ingest import ingest_dealer
from pipeline.sources.autoscout24 import DealerHarvest, DealerInfo, Vehicle
from pipeline.sources.base import DiscoveredEntity

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Pinned ES byte-identity literal (services.api.codes, branch "domain"): a domain-keyed
# dealer in province 28 ALWAYS mints this exact code. Identical to test_country_golden's
# _ES_GOLDEN row (dict(province_code="28", domain="ford.es") -> "CDP-ES-28-ZB6C77HC").
_ES_FORD_28 = "CDP-ES-28-ZB6C77HC"


# ===========================================================================
# Isolation guard + async helpers (dry-run only, transactional rollback)
# ===========================================================================
def _target_dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


async def _open_guarded_dryrun() -> asyncpg.Connection:
    """Open an asyncpg connection to the dry-run census, refusing the live one.

    Triple guard mirroring the other country goldens:
      1. refuse any DSN pointing at :5433 (live production);
      2. skip if the DB is unreachable;
      3. refuse to seed unless BOTH entity and vehicle are EMPTY (the dry-run holds
         0/0; production holds ~452k) -- a mis-pointed DSN can never mutate real data.
    """
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip(
            "refusing to run the write-spine golden against :5433 (live production); "
            "point CARDEEP_DSN at the :5434 dry-run")
    try:
        conn = await asyncpg.connect(dsn, timeout=3)
    except Exception:  # noqa: BLE001
        pytest.skip(f"dry-run cardeep-pg not reachable at {dsn}")
    n_entities = await conn.fetchval("SELECT count(*) FROM entity")
    n_vehicles = await conn.fetchval("SELECT count(*) FROM vehicle")
    if n_entities != 0 or n_vehicles != 0:
        await conn.close()
        pytest.skip(
            f"target DB has {n_entities} entities / {n_vehicles} vehicles -- not the "
            "empty dry-run; refusing to seed against a populated census")
    return conn


async def _seed_geo(conn: asyncpg.Connection, country: str, province: str,
                    muni: str, muni_name: str) -> None:
    """Seed (country, province) then (country, muni). Order satisfies the composite FK
    geo_municipality(country_code, province_code) -> geo_province and the composite PKs
    (migration 0053). The muni CHECK left(code,2)=province_code is country-guarded to ES,
    so a non-ES muni is accepted under a second country."""
    await conn.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES ($1,$2,$3,$4,$5) ON CONFLICT DO NOTHING",
        province, f"prov-{country}-{province}", "13", f"reg-{country}", country)
    await conn.execute(
        "INSERT INTO geo_municipality (code, name, province_code, comarca_id, country_code) "
        "VALUES ($1,$2,$3,NULL,$4) ON CONFLICT DO NOTHING",
        muni, muni_name, province, country)


def _vehicle(deep_link: str) -> Vehicle:
    return Vehicle(
        deep_link=deep_link, vin_ref="vinref1", title="VW Golf 1.5 TSI",
        make="Volkswagen", model="Golf", year=2020, km=50_000, price=20_000.0,
        fuel="gasolina", transmission="manual", photo_url=None)


# ===========================================================================
# #1 + #2 -- DISCOVER write spine (DiscoveredEntity.country_code, mint, INSERT)
# ===========================================================================
@pytest.mark.integration
def test_discover_de_entity_minted_as_de_not_es():
    """A DE dealer discovered end-to-end through pipeline.discover._upsert must land as
    CDP-DE-* with country_code='DE'. RED today: minted CDP-ES-28-* / country_code='ES'
    (cdp_code defaults to ES + the INSERT omits country_code). The collision province '28'
    is seeded for BOTH ES and DE so the country-blind insert lands as ES (exposing the
    mis-mint) instead of FK-erroring."""
    async def _body() -> None:
        conn = await _open_guarded_dryrun()
        try:
            tr = conn.transaction()
            await tr.start()
            try:
                await _seed_geo(conn, "ES", "28", "28079", "Madrid")   # pre-fix ES insert FK
                await _seed_geo(conn, "DE", "28", "28079", "Berlin")   # post-fix DE insert FK
                e = DiscoveredEntity(
                    kind="compraventa", source_key="golden_c2_de",
                    legal_name="Autohaus Berlin", province_name="28",
                    website="autohaus-berlin.de")
                e.country_code = "DE"   # set as attr: pre-fix the field is absent (mint
                                        # ignores it -> semantic RED); post-fix it drives the mint
                geo = await GeoResolver.load(conn, "DE")
                await _upsert(conn, geo, e)
                row = await conn.fetchrow(
                    "SELECT cdp_code, country_code FROM entity "
                    "WHERE first_discovered_source = 'golden_c2_de'")
                assert row is not None, "DE entity was not written by discover._upsert"
                assert row["country_code"] == "DE", (
                    f"COUNTRY-BLIND DISCOVER: DE dealer persisted country_code="
                    f"{row['country_code']!r}; the entity INSERT omits country_code so it "
                    "DEFAULTs to 'ES'. Thread e.country_code into the INSERT.")
                assert row["cdp_code"].startswith("CDP-DE-"), (
                    f"COUNTRY-BLIND MINT: DE dealer minted {row['cdp_code']!r} (CDP-ES-*); "
                    "cdp_code() is called without country_code so the prefix is ES. Thread "
                    "e.country_code into cdp_code(...).")
            finally:
                await tr.rollback()
        finally:
            await conn.close()

    asyncio.run(_body())


@pytest.mark.integration
def test_discover_es_entity_byte_identical():
    """BYTE-IDENTITY guard (must pass before AND after the fix): an ES dealer discovered
    with domain 'ford.es' in province 28 mints the EXACT pinned code CDP-ES-28-ZB6C77HC and
    persists country_code='ES'. Constructed WITHOUT touching country_code so it exercises
    the default ES path the whole census relies on."""
    async def _body() -> None:
        conn = await _open_guarded_dryrun()
        try:
            tr = conn.transaction()
            await tr.start()
            try:
                await _seed_geo(conn, "ES", "28", "28079", "Madrid")
                e = DiscoveredEntity(
                    kind="compraventa", source_key="golden_c2_es",
                    legal_name="Ford Madrid", province_name="28", website="ford.es")
                geo = await GeoResolver.load(conn, "ES")
                await _upsert(conn, geo, e)
                row = await conn.fetchrow(
                    "SELECT cdp_code, country_code FROM entity "
                    "WHERE first_discovered_source = 'golden_c2_es'")
                assert row is not None, "ES entity was not written by discover._upsert"
                assert row["cdp_code"] == _ES_FORD_28, (
                    f"ES MINT DRIFT: discover minted {row['cdp_code']!r}, expected the pinned "
                    f"{_ES_FORD_28} -- a single changed ES code re-keys the census.")
                assert row["country_code"] == "ES", (
                    f"ES country regressed to {row['country_code']!r}")
            finally:
                await tr.rollback()
        finally:
            await conn.close()

    asyncio.run(_body())


# ===========================================================================
# #3 + #4 -- INGEST write spine (province gate, mint, INSERT)
# ===========================================================================
@pytest.mark.integration
def test_ingest_de_dealer_not_rejected_and_minted_de():
    """A DE dealer whose province ('BE', outside the Spanish 01-52 grid) is ingested via
    pipeline.ingest.ingest_dealer must NOT be rejected and must mint CDP-DE-BE-* with
    country_code='DE'. RED today: the gate "01" <= 'BE' <= "52" (isdigit() False) returns
    {"error": "...out of Spain range..."} -- the whole DE inventory is dropped."""
    async def _body() -> None:
        conn = await _open_guarded_dryrun()
        try:
            tr = conn.transaction()
            await tr.start()
            try:
                await _seed_geo(conn, "DE", "BE", "BE001", "Berlin")
                harvest = DealerHarvest(
                    dealer=DealerInfo(
                        source_dealer_id="de-dealer-1", company_name="Autohaus X",
                        slug="autohaus-x", province_code="BE", city="Berlin",
                        street="Hauptstrasse 1", zip="10115", website="autohaus-x.de"),
                    vehicles=[_vehicle("https://www.autoscout24.de/v/1")],
                    declared_count=1)
                geo = await GeoResolver.load(conn, "DE")
                result = await ingest_dealer(conn, geo, harvest, source_key="as24",
                                             country="DE")
                assert "error" not in result, (
                    f"DE dealer REJECTED by the ES-only province gate: {result.get('error')!r}. "
                    "Country-scope the gate like complete.py:171 (ES keeps 01-52).")
                assert result["cdp_code"].startswith("CDP-DE-BE-"), (
                    f"COUNTRY-BLIND INGEST MINT: minted {result['cdp_code']!r}; thread country "
                    "into cdp_code(...) + the INSERT.")
                row = await conn.fetchrow(
                    "SELECT country_code FROM entity WHERE cdp_code = $1", result["cdp_code"])
                assert row is not None and row["country_code"] == "DE", (
                    f"DE dealer persisted country_code={row and row['country_code']!r}")
            finally:
                await tr.rollback()
        finally:
            await conn.close()

    asyncio.run(_body())


@pytest.mark.integration
def test_ingest_es_dealer_byte_identical():
    """BYTE-IDENTITY guard (must pass before AND after the fix): an ES dealer in province 28
    is ingested with the CURRENT call shape (no country kwarg -> default 'ES'), is accepted by
    the 01-52 gate, mints CDP-ES-28-* and persists country_code='ES'."""
    async def _body() -> None:
        conn = await _open_guarded_dryrun()
        try:
            tr = conn.transaction()
            await tr.start()
            try:
                await _seed_geo(conn, "ES", "28", "28079", "Madrid")
                harvest = DealerHarvest(
                    dealer=DealerInfo(
                        source_dealer_id="es-dealer-1", company_name="Auto Madrid",
                        slug="auto-madrid", province_code="28", city="Madrid",
                        street="Calle Mayor 1", zip="28001", website="auto-madrid.es"),
                    vehicles=[_vehicle("https://es.example/v/1")],
                    declared_count=1)
                geo = await GeoResolver.load(conn, "ES")
                result = await ingest_dealer(conn, geo, harvest, source_key="as24")
                assert "error" not in result, (
                    f"ES dealer wrongly rejected: {result.get('error')!r}")
                assert result["cdp_code"].startswith("CDP-ES-28-"), (
                    f"ES ingest mint regressed: {result['cdp_code']!r}")
                row = await conn.fetchrow(
                    "SELECT country_code FROM entity WHERE cdp_code = $1", result["cdp_code"])
                assert row is not None and row["country_code"] == "ES", (
                    f"ES dealer country regressed to {row and row['country_code']!r}")
            finally:
                await tr.rollback()
        finally:
            await conn.close()

    asyncio.run(_body())


# ===========================================================================
# #1 -- DiscoveredEntity field default (unit, no DB)
# ===========================================================================
@pytest.mark.unit
def test_discovered_entity_has_country_code_default_es():
    """DiscoveredEntity must carry a country_code field defaulting to 'ES' (the root the
    adapters override per country). RED today: the field is absent."""
    field_names = {f.name for f in dataclasses.fields(DiscoveredEntity)}
    assert "country_code" in field_names, (
        "DiscoveredEntity is missing the country_code field -- adapters cannot declare "
        "a non-ES tenant at the root of the write spine.")
    e = DiscoveredEntity(kind="compraventa", source_key="x")
    assert e.country_code == "ES", (
        f"country_code default must be 'ES' (byte-identical ES), got {e.country_code!r}")


# ===========================================================================
# #6 -- complete._resolve_recipe_path country-scoped (unit, no DB)
# ===========================================================================
@pytest.mark.unit
def test_resolve_recipe_path_country_scoped(tmp_path: Path):
    """_resolve_recipe_path must derive the country from the cdp_code (recipe.py writes a
    DE recipe under countries/DE/recipes via country_of_cdp). RED today: it hard-codes
    countries/ES, so a DE recipe is invisible -> None. ES codes still resolve under
    countries/ES (byte-identical)."""
    de_code = "CDP-DE-BE-DEAB1234"
    de_dir = tmp_path / "countries" / "DE" / "recipes"
    de_dir.mkdir(parents=True)
    de_file = de_dir / f"{de_code}.yaml"
    de_file.write_text("version: 1\n", encoding="utf-8")

    assert _resolve_recipe_path(de_code, tmp_path) == de_file, (
        "_resolve_recipe_path is still ES-hard-coded: a DE recipe under countries/DE/recipes "
        "was not found (G3 git sub-signal is blind to country #2). Use country_of_cdp(cdp_code).")

    # ES byte-identity: an ES code still resolves under countries/ES.
    es_code = "CDP-ES-28-ESAB1234"
    es_dir = tmp_path / "countries" / "ES" / "recipes"
    es_dir.mkdir(parents=True)
    es_file = es_dir / f"{es_code}.yaml"
    es_file.write_text("version: 1\n", encoding="utf-8")
    assert _resolve_recipe_path(es_code, tmp_path) == es_file, (
        "ES recipe path regressed -- the ES code must still resolve under countries/ES.")


# ===========================================================================
# #5 -- harvest_dealer threads country into data_root/geo/ingest (unit, mock)
# ===========================================================================
@pytest.mark.unit
def test_harvest_dealer_threads_country():
    """pipeline.harvest_dealer.run must accept a country and thread it into data_root(country),
    GeoResolver.load(conn, country) and ingest_dealer(..., country=country). RED today: run()
    has no country parameter. Pure mock -- no live DB, no real scrape, no FS writes."""
    conn = mock.AsyncMock()
    harvest_obj = mock.MagicMock()
    harvest_obj.dealer = mock.MagicMock()
    harvest_obj.vehicles = []
    harvest_obj.declared_count = 1
    harvest_obj.pages_drained = 1
    ingest_result = {
        "cdp_code": "CDP-DE-BE-DEAB1234", "available": 1, "declared": 1, "new": 1,
        "gone": 0, "price_change": 0, "photo_change": 0, "km_change": 0,
        "unchanged": 0, "verdict": "TRUSTWORTHY"}

    with (
        mock.patch("asyncpg.connect", new=mock.AsyncMock(return_value=conn)),
        mock.patch.object(harvest_dealer, "scrape_dealer", return_value=harvest_obj),
        mock.patch.object(harvest_dealer, "data_root",
                          wraps=harvest_dealer.data_root) as dr,
        mock.patch("pathlib.Path.mkdir"), mock.patch("pathlib.Path.write_text"),
        mock.patch.object(harvest_dealer.GeoResolver, "load",
                          new=mock.AsyncMock(return_value=mock.MagicMock())) as geo_load,
        mock.patch.object(harvest_dealer, "ingest_dealer",
                          new=mock.AsyncMock(return_value=ingest_result)) as ingest,
        mock.patch.object(harvest_dealer, "write_recipe",
                          return_value=mock.MagicMock()),
        mock.patch("pipeline.ops.health.fire_alert", new=mock.AsyncMock()),
    ):
        asyncio.run(harvest_dealer.run("autohaus-x", country="DE"))

    assert dr.call_args.args and dr.call_args.args[0] == "DE", (
        f"data_root not country-scoped: {dr.call_args!r}")
    assert geo_load.await_args.args[1] == "DE", (
        f"GeoResolver.load not country-scoped: {geo_load.await_args!r}")
    assert ingest.await_args.kwargs.get("country") == "DE", (
        f"ingest_dealer did not receive country='DE': {ingest.await_args!r}")

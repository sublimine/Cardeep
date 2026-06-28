"""Live rolled-back tests for the recipe->delta bridge (country-autopilot §02 build-order D).

Verifies ``pipeline.recipe_delta_bridge.ingest_and_delta`` — the OPT-IN tie that takes the
cracker's VERIFIED cars (today VERIFIED-then-DELETED, never ingested) and routes them into
the live delta engine, emitting the five canonical events:

  (1) a set of XX VERIFIED cars              -> NEW
  (2) a second run with one car fewer        -> GONE
  (3) a re-seen car with a changed price     -> PRICE_CHANGE
  (+) the load-bearing SAFETY case: a BOUNDED sample (harvested << declared) must NEVER
      retire real stock — GONE is suppressed, not fired.

The bridge REUSES ``pipeline.delta.emit_change_deltas`` / ``emit_gone_events`` /
``pipeline.delta_guard.should_emit_gone`` (it does not reimplement the delta).

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). It HARD-REFUSES :5433
(live production, ~452k entities) three ways — by DSN string, by skip-if-unreachable, and by
asserting the target ``entity`` census is EMPTY before seeding. Every test seeds + ingests
inside a transaction and ROLLS BACK, leaving the dry-run byte-identical (``entity`` stays 0,
ES untouched). The bridge's own writes run in a SAVEPOINT of that transaction.
"""
from __future__ import annotations

import asyncio
import os
from types import SimpleNamespace

import asyncpg
import pytest

from pipeline.recipe_delta_bridge import ingest_and_delta

pytestmark = pytest.mark.integration

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# Crockford base32 (no I, L, O, U) — the alphabet entity_ulid_shape accepts.
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


# ---------------------------------------------------------------------------
# Connection + isolation harness (asyncpg; the bridge is async)
# ---------------------------------------------------------------------------
def _target_dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


def _reachable(dsn: str) -> bool:
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


def _run(body) -> None:
    """Drive one async test body against a transactional :5434 connection, rolled back.

    Triple isolation guard (identical contract to test_country_isolation_dealer.py):
      1. refuse any DSN pointing at :5433;
      2. skip if the DB is unreachable;
      3. refuse to seed unless the target ``entity`` table is EMPTY (the dry-run is
         entity=0; production holds ~452k) — a mis-pointed DSN can never mutate real data.
    """
    dsn = _target_dsn()
    if ":5433" in dsn:
        pytest.skip("refusing :5433 (live production); point CARDEEP_DSN at the :5434 dry-run")
    if not _reachable(dsn):
        pytest.skip(f"dry-run cardeep-pg not reachable at {dsn}")

    async def _driver() -> None:
        conn = await asyncpg.connect(dsn)
        try:
            n_entities = await conn.fetchval("SELECT count(*) FROM entity")
            if n_entities != 0:
                pytest.skip(
                    f"target DB has {n_entities} entities — not the empty dry-run; "
                    "refusing to seed/ingest against a populated census")
            tr = conn.transaction()
            await tr.start()
            try:
                await body(conn)
            finally:
                await tr.rollback()  # leave :5434 byte-identical (ES untouched)
        finally:
            await conn.close()

    asyncio.run(_driver())


# ---------------------------------------------------------------------------
# Seeding helpers (FK + CHECK respecting; mirrors the proven isolation seed)
# ---------------------------------------------------------------------------
def _ulid(tag: str) -> str:
    safe = "".join(c for c in tag.upper() if c in _CROCKFORD)
    return (safe + "0" * 26)[:26]


async def _seed_geo(conn, country: str = "ES", province: str = "28", muni: str = "28079") -> None:
    await conn.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES ($1,$2,$3,$4,$5) ON CONFLICT DO NOTHING",
        province, f"prov-{country}-{province}", "13", f"ccaa-{country}", country)
    await conn.execute(
        "INSERT INTO geo_municipality (code, name, province_code, comarca_id, country_code) "
        "VALUES ($1,$2,$3,NULL,$4) ON CONFLICT DO NOTHING",
        muni, f"muni-{country}-{muni}", province, country)


async def _seed_entity(conn, *, tag: str, cdp: str, name: str = "bridge test dealer",
                       country: str = "ES", province: str = "28", muni: str = "28079") -> str:
    """Seed one in-scope dealer (kind='compraventa', status='active') and return entity_ulid."""
    await _seed_geo(conn, country, province, muni)
    eulid = _ulid(tag)
    await conn.execute(
        "INSERT INTO entity (entity_ulid, cdp_code, kind, trade_name, legal_name, "
        "province_code, municipality_code, country_code, status) "
        "VALUES ($1,$2,'compraventa',$3,$3,$4,$5,$6,'active')",
        eulid, cdp, name, province, muni, country)
    return eulid


def _car(deep_link: str, *, price=None, km=None, photo_url=None, title="Seat Leon 1.5 TSI",
         make="Seat", model="Leon", year=2020, vin_ref=None, fuel="gasolina",
         transmission="manual", photo_hash=None) -> dict:
    """A cracker sample car — the Vehicle dataclass field shape (Sample.parsed = asdict(Vehicle))."""
    return {"deep_link": deep_link, "vin_ref": vin_ref or deep_link, "title": title,
            "make": make, "model": model, "year": year, "km": km, "price": price,
            "fuel": fuel, "transmission": transmission, "photo_url": photo_url,
            "photo_hash": photo_hash}


async def _event_types(conn, eulid: str) -> list[str]:
    rows = await conn.fetch(
        "SELECT event_type FROM vehicle_event WHERE entity_ulid=$1 ORDER BY observed_at", eulid)
    return [r["event_type"] for r in rows]


async def _available_links(conn, eulid: str) -> set[str]:
    rows = await conn.fetch(
        "SELECT deep_link FROM vehicle WHERE entity_ulid=$1 AND status='available'", eulid)
    return {r["deep_link"] for r in rows}


# ---------------------------------------------------------------------------
# (1) NEW — a set of VERIFIED cars ingests + emits NEW deltas
# ---------------------------------------------------------------------------
def test_verified_cars_emit_new_deltas():
    async def body(conn):
        cdp = "CDP-ES-28-BRDGNEW1"
        eulid = await _seed_entity(conn, tag="BRDGNEWA", cdp=cdp)
        cars = [_car(f"https://dealer.test/v{i}", price=10_000 + i * 100, km=50_000 + i)
                for i in range(5)]

        res = await ingest_and_delta(conn, cdp, "cracker:autoscout24", cars,
                                     declared=5, dry_run=False)

        assert res["entity_ulid"] == eulid
        assert res["new"] == 5
        assert res["gone"] == 0 and res["price_change"] == 0
        # 5 vehicles available + exactly 5 NEW events, nothing else.
        assert await _available_links(conn, eulid) == {f"https://dealer.test/v{i}" for i in range(5)}
        assert await _event_types(conn, eulid) == ["NEW"] * 5
        # NEW event carries the {price,title} snapshot (old=NULL), the ingest.py convention.
        ev = await conn.fetchrow(
            "SELECT old_value, new_value FROM vehicle_event WHERE entity_ulid=$1 LIMIT 1", eulid)
        assert ev["old_value"] is None
        import json
        assert set(json.loads(ev["new_value"])) == {"price", "title"}

    _run(body)


# ---------------------------------------------------------------------------
# (2) GONE — a second (complete) run with one car fewer retires the dropped car
# ---------------------------------------------------------------------------
def test_second_run_one_fewer_emits_gone():
    async def body(conn):
        cdp = "CDP-ES-28-BRDGGON1"
        eulid = await _seed_entity(conn, tag="BRDGGONE", cdp=cdp)
        links = [f"https://dealer.test/g{i}" for i in range(4)]

        # Run 1: full inventory of 4 (declared=4) -> 4 NEW.
        run1 = await ingest_and_delta(
            conn, cdp, "cracker:autoscout24",
            [_car(lk, price=12_000) for lk in links], declared=4, dry_run=False)
        assert run1["new"] == 4

        # Run 2: complete harvest of the SAME dealer minus the last car (declared=3).
        run2 = await ingest_and_delta(
            conn, cdp, "cracker:autoscout24",
            [_car(lk, price=12_000) for lk in links[:3]], declared=3, dry_run=False)

        assert run2["gone_allowed"] is True, run2["gone_reason"]
        assert run2["gone"] == 1
        assert run2["new"] == 0 and run2["reseen"] == 3
        # The dropped car is retired; the other three stay available; one GONE event exists.
        assert await _available_links(conn, eulid) == set(links[:3])
        gone_row = await conn.fetchrow(
            "SELECT status FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2", eulid, links[3])
        assert gone_row["status"] == "gone"
        assert (await _event_types(conn, eulid)).count("GONE") == 1

    _run(body)


# ---------------------------------------------------------------------------
# (3) PRICE_CHANGE — a re-seen car with a changed price emits PRICE_CHANGE + refreshes
# ---------------------------------------------------------------------------
def test_reseen_price_delta_emits_price_change():
    async def body(conn):
        cdp = "CDP-ES-28-BRDGPRC1"
        eulid = await _seed_entity(conn, tag="BRDGPRCE", cdp=cdp)
        links = [f"https://dealer.test/p{i}" for i in range(3)]

        await ingest_and_delta(conn, cdp, "cracker:coches_net",
                               [_car(lk, price=20_000) for lk in links], declared=3, dry_run=False)

        # Re-run: same 3 cars, ONE with a new price.
        cars2 = [_car(links[0], price=18_500),  # -1500 EUR
                 _car(links[1], price=20_000),
                 _car(links[2], price=20_000)]
        run2 = await ingest_and_delta(conn, cdp, "cracker:coches_net", cars2,
                                      declared=3, dry_run=False)

        assert run2["price_change"] == 1
        assert run2["new"] == 0 and run2["gone"] == 0 and run2["km_change"] == 0
        assert (await _event_types(conn, eulid)).count("PRICE_CHANGE") == 1
        # The served row is refreshed to the new price (emit_change_deltas bulk-refresh).
        refreshed = await conn.fetchval(
            "SELECT price FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2", eulid, links[0])
        assert float(refreshed) == 18_500.0

    _run(body)


# ---------------------------------------------------------------------------
# KM_CHANGE + PHOTO_CHANGE — the remaining two re-seen deltas (completing the five)
# ---------------------------------------------------------------------------
def test_reseen_km_and_photo_deltas_emit():
    async def body(conn):
        cdp = "CDP-ES-28-BRDGKMP1"
        eulid = await _seed_entity(conn, tag="BRDGKMPH", cdp=cdp)
        link = "https://dealer.test/k0"

        await ingest_and_delta(
            conn, cdp, "cracker:autoscout24",
            [_car(link, price=17_000, km=40_000, photo_url="https://img.test/a.jpg")],
            declared=1, dry_run=False)

        # Re-run: same car, new km AND new photo (price unchanged).
        run2 = await ingest_and_delta(
            conn, cdp, "cracker:autoscout24",
            [_car(link, price=17_000, km=42_500, photo_url="https://img.test/b.jpg")],
            declared=1, dry_run=False)

        assert run2["km_change"] == 1 and run2["photo_change"] == 1
        assert run2["price_change"] == 0 and run2["new"] == 0 and run2["gone"] == 0
        types = await _event_types(conn, eulid)
        assert types.count("KM_CHANGE") == 1 and types.count("PHOTO_CHANGE") == 1
        # Served row refreshed to the new km + photo.
        row = await conn.fetchrow(
            "SELECT km, photo_url FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2", eulid, link)
        assert int(row["km"]) == 42_500 and row["photo_url"] == "https://img.test/b.jpg"

    _run(body)


# ---------------------------------------------------------------------------
# SAFETY — a BOUNDED sample (harvested << declared) MUST NOT retire real stock
# ---------------------------------------------------------------------------
def test_bounded_sample_suppresses_false_gone():
    async def body(conn):
        cdp = "CDP-ES-28-BRDGSMP1"
        eulid = await _seed_entity(conn, tag="BRDGSAMP", cdp=cdp)
        links = [f"https://dealer.test/s{i}" for i in range(4)]

        # Establish a 4-car inventory.
        await ingest_and_delta(conn, cdp, "cracker:autoscout24",
                               [_car(lk, price=15_000) for lk in links], declared=4, dry_run=False)

        # A bounded sample of 2 cars but the source still DECLARES 4 (incomplete harvest).
        run2 = await ingest_and_delta(
            conn, cdp, "cracker:autoscout24",
            [_car(lk, price=15_000) for lk in links[:2]], declared=4, dry_run=False)

        assert run2["gone_allowed"] is False, "a 2-of-4 sample must NOT authorize a GONE sweep"
        assert run2["gone"] == 0
        assert run2["gone_suppressed"] == 2  # the 2 un-harvested-but-available cars
        # NO false GONE: all four cars remain available, zero GONE events on the timeline.
        assert await _available_links(conn, eulid) == set(links)
        assert "GONE" not in await _event_types(conn, eulid)

    _run(body)


# ---------------------------------------------------------------------------
# dry_run — the preview computes the deltas but persists NOTHING
# ---------------------------------------------------------------------------
def test_dry_run_previews_counts_without_persisting():
    async def body(conn):
        cdp = "CDP-ES-28-BRDGDRY1"
        eulid = await _seed_entity(conn, tag="BRDGDRYR", cdp=cdp)
        cars = [_car(f"https://dealer.test/d{i}", price=9_000) for i in range(3)]

        res = await ingest_and_delta(conn, cdp, "cracker:autoscout24", cars,
                                     declared=3, dry_run=True)

        assert res["dry_run"] is True
        assert res["new"] == 3  # the counts that WOULD be emitted are reported
        # ...but the savepoint was rolled back: nothing landed.
        assert await conn.fetchval(
            "SELECT count(*) FROM vehicle WHERE entity_ulid=$1", eulid) == 0
        assert await conn.fetchval(
            "SELECT count(*) FROM vehicle_event WHERE entity_ulid=$1", eulid) == 0

    _run(body)


# ---------------------------------------------------------------------------
# Honest failure — a cdp_code with no entity returns an error, never a silent pass
# ---------------------------------------------------------------------------
def test_missing_entity_returns_honest_error():
    async def body(conn):
        res = await ingest_and_delta(conn, "CDP-ES-28-NOENT001", "cracker:autoscout24",
                                     [_car("https://dealer.test/x0", price=1_000)],
                                     declared=1, dry_run=False)
        assert "error" in res and res["entity_ulid"] is None
        assert res["new"] == 0 and res["gone"] == 0
        # No orphan rows were written anywhere.
        assert await conn.fetchval("SELECT count(*) FROM vehicle") == 0
        assert await conn.fetchval("SELECT count(*) FROM vehicle_event") == 0

    _run(body)


# ---------------------------------------------------------------------------
# Input contract — dict cars and object cars ingest identically
# ---------------------------------------------------------------------------
def test_accepts_dicts_and_objects_alike():
    async def body(conn):
        cdp_d = "CDP-ES-28-BRDGDIC1"
        cdp_o = "CDP-ES-28-BRDGOBJ1"
        ed = await _seed_entity(conn, tag="BRDGDICT", cdp=cdp_d)
        eo = await _seed_entity(conn, tag="BRDGOBJS", cdp=cdp_o)

        dict_cars = [_car(f"https://d/{i}", price=8_000 + i) for i in range(3)]
        obj_cars = [SimpleNamespace(**_car(f"https://o/{i}", price=8_000 + i)) for i in range(3)]

        rd = await ingest_and_delta(conn, cdp_d, "cracker:test", dict_cars, declared=3, dry_run=False)
        ro = await ingest_and_delta(conn, cdp_o, "cracker:test", obj_cars, declared=3, dry_run=False)

        assert rd["new"] == 3 and ro["new"] == 3
        assert await _event_types(conn, ed) == ["NEW"] * 3
        assert await _event_types(conn, eo) == ["NEW"] * 3

    _run(body)


# ---------------------------------------------------------------------------
# Input contract — cars with no deep_link are skipped (unkeyable), siblings still ingest
# ---------------------------------------------------------------------------
def test_skips_cars_without_deep_link():
    async def body(conn):
        cdp = "CDP-ES-28-BRDGSKP1"
        eulid = await _seed_entity(conn, tag="BRDGSKIP", cdp=cdp)
        cars = [
            _car("https://dealer.test/ok0", price=5_000),
            {"deep_link": None, "price": 5_000, "title": "no link"},
            {"deep_link": "", "price": 5_000, "title": "empty link"},
            _car("https://dealer.test/ok1", price=5_000),
        ]
        res = await ingest_and_delta(conn, cdp, "cracker:test", cars, declared=2, dry_run=False)

        assert res["skipped_no_link"] == 2
        assert res["new"] == 2
        # only the two keyable cars landed — no orphan rows from the skipped ones.
        assert await _available_links(conn, eulid) == {
            "https://dealer.test/ok0", "https://dealer.test/ok1"}
        assert await _event_types(conn, eulid) == ["NEW"] * 2

    _run(body)


# ---------------------------------------------------------------------------
# Re-listing — a previously-GONE car reappearing in the harvest flips back to available
# ---------------------------------------------------------------------------
def test_relisted_gone_car_returns_available():
    async def body(conn):
        cdp = "CDP-ES-28-BRDGRLS1"
        eulid = await _seed_entity(conn, tag="BRDGRELS", cdp=cdp)
        link = "https://dealer.test/relisted"
        # Seed the car directly as GONE (a prior baja), priced at 30k.
        await conn.execute(
            "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, price, status) "
            "VALUES ($1,$2,$3,$4,$5,'gone')",
            _ulid("VEHRELST"), eulid, link, "Relisted car", 30_000)

        res = await ingest_and_delta(conn, cdp, "cracker:autoscout24",
                                     [_car(link, price=28_000)], declared=1, dry_run=False)

        assert res["new"] == 0 and res["reseen"] == 1 and res["gone"] == 0
        assert res["price_change"] == 1  # re-listed car also diffs price (30k -> 28k)
        # The car is live again at the new price.
        row = await conn.fetchrow(
            "SELECT status, price FROM vehicle WHERE entity_ulid=$1 AND deep_link=$2", eulid, link)
        assert row["status"] == "available"
        assert float(row["price"]) == 28_000.0

    _run(body)


# ---------------------------------------------------------------------------
# Byte-identity — a non-dry ingest fully reverts on rollback (ES/:5434 untouched)
# ---------------------------------------------------------------------------
def test_rollback_leaves_db_byte_identical():
    dsn = _target_dsn()
    if ":5433" in dsn:
        pytest.skip("refusing :5433 (live production); point CARDEEP_DSN at the :5434 dry-run")
    if not _reachable(dsn):
        pytest.skip(f"dry-run cardeep-pg not reachable at {dsn}")

    async def _driver() -> None:
        conn = await asyncpg.connect(dsn)
        try:
            before = (
                await conn.fetchval("SELECT count(*) FROM entity"),
                await conn.fetchval("SELECT count(*) FROM vehicle"),
                await conn.fetchval("SELECT count(*) FROM vehicle_event"),
            )
            if before[0] != 0:
                pytest.skip(f"target DB has {before[0]} entities — not the empty dry-run")

            tr = conn.transaction()
            await tr.start()
            try:
                cdp = "CDP-ES-28-BRDGRBK1"
                await _seed_entity(conn, tag="BRDGRBCK", cdp=cdp)
                res = await ingest_and_delta(
                    conn, cdp, "cracker:autoscout24",
                    [_car(f"https://dealer.test/r{i}", price=11_000) for i in range(4)],
                    declared=4, dry_run=False)
                assert res["new"] == 4  # data really was written inside the tx
            finally:
                await tr.rollback()

            after = (
                await conn.fetchval("SELECT count(*) FROM entity"),
                await conn.fetchval("SELECT count(*) FROM vehicle"),
                await conn.fetchval("SELECT count(*) FROM vehicle_event"),
            )
            assert after == before, f"rollback left residue: {before} -> {after}"
        finally:
            await conn.close()

    asyncio.run(_driver())

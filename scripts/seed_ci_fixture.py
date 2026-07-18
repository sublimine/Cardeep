"""Seed a TINY synthetic census fixture for the CI `db-tests` job.

Why: the db-tests job runs against an ephemeral, migrated, geo-seeded Postgres with NO census, so the
census-dependent tests (which read real entities/vehicles) fail. This inserts a SMALL, deterministic,
idempotent fixture so a first batch of those tests can run in CI. It is ADDITIVE and ON CONFLICT DO
NOTHING — re-running is a no-op, and it must never break the tests that already pass on the empty DB.

Scope (batch A): a handful of active compraventa dealers in province 28 / municipality 28079 (both
present from the geo seed), each with an entity_source, plus a few available vehicles. Enough for
test_evict (reads one real dealer), test_entity_muni_province_invariant (needs one entity with a
municipality), and test_emit_gone_events (needs an available vehicle with no prior GONE event).

Scope (batch B): one `vehicle_cluster_run` row with vam_verified=TRUE and ZERO attached
`vehicle_cluster` rows. This is the F0 precondition every market-intelligence fetch_m* query
depends on (`v_canonical_vehicle` / the COALESCE-canon CTEs in pipeline/market/*.py all resolve
against "the most recent vam_verified run" — with none present the view/CTEs are permanently
empty and pipeline.market's own test helper (`tests/market_test_helpers.vam_verified_run_id`)
raises before a single query runs). Deliberately EMPTY of real clusters: the market test suite
(tests/test_market_compute_stats.py, tests/test_market_metrics_f2.py) inserts its OWN
self-canonical `vehicle_cluster` rows against this run_id inside a rolled-back transaction. The
fixture dealers/vehicles above are unaffected (no make/model/year/fuel set on them, so they never
match any fetch_m* segment filter) and are NEVER clustered under this run.

Scope (batch C): a dedicated dealer + platform entity pair, a 19-vehicle (make, model, year)
cohort sized/priced to clear the 04-arbitrage F1 cohort gates (pipeline/gestionador/cohorts.py:
COHORT_MIN_TIER_A=15, COHORT_MAD_FLOOR=0.05 on ln-price), and one dealer/platform price pair for
a desync signal — tests/test_arbitrage_router.py. The db-tests job never ran the F1 batch job
(pipeline/arbitrage/score.py::run_score) before this batch existed, so `arbitrage_run` never
existed in CI: services/api/routers/arbitrage.py correctly served its documented 503 "no
arbitrage_run yet" (honest empty-state, not a bug — the SAME contract test_time_curves/test_geo
already tolerate), and every TestDeals assertion that assumes a live run threw on the resulting
`data: None`. This batch calls the REAL F1 job against the synthetic cohort below, so
arbitrage_run/cohort_stats/deal_score hold genuine job OUTPUT (real cohort SQL, real median/MAD,
real bands) — never a fabricated deal_score literal. The two "chollo" prices were chosen by
hand-computing the exact robust-z formula run_score uses (percentile_cont(0.5) median/MAD,
z=(lp-med_lp)/(1.4826*mad_lp)) so each lands comfortably inside its target band, away from both
boundaries. The desync vehicle/make are kept OUT of the cohort (different make) so they never
perturb the cohort's median/MAD.

IDs use the Crockford-26 / cdp_code formats the schema + G1 validator require. Run AFTER `migrate up`
and the geo seed. Reads CARDEEP_DSN (the CI job points it at the ephemeral 127.0.0.1:5433).
Usage: python -m scripts.seed_ci_fixture
"""
from __future__ import annotations

import asyncio
import os

import asyncpg

from pipeline.arbitrage.score import run_score

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# Crockford-safe (no I/L/O/U) fixed identifiers — deterministic so re-runs are idempotent.
_PROV = "28"
_MUNI = "28079"
_N_DEALERS = 25  # >=20 so province-28 pagination (OLA 2) has two distinct pages later, too
_N_VEHICLES = 25

# Batch B: F0 precondition anchor for pipeline/market/*.py (see module docstring). Plain
# descriptive tag, same style as production's own cluster_run_id convention (e.g.
# pipeline/identity/cluster_vehicles.py's 'vehicle-identity-det-v1') rather than a ULID —
# this is a caller-supplied id, never mistaken for a real production run.
_VEHICLE_CLUSTER_RUN_ID = "ci-fixture-vehicle-cluster-run-v1"


def _entity_ulid(i: int) -> str:
    return f"FXTRE{str(i).zfill(21)}"  # 5 + 21 = 26 Crockford chars


def _cdp(i: int) -> str:
    return f"CDP-ES-{_PROV}-FXTRE{str(i).zfill(3)}"  # suffix FXTRE001 = 8 Crockford chars


def _vehicle_ulid(i: int) -> str:
    return f"FXTVH{str(i).zfill(21)}"


# Batch C: 04-arbitrage F1 corpus (see module docstring). Same Crockford-safe ULID convention,
# distinct 5-char prefixes so batch C never collides with batch A's FXTRE/FXTVH ids.
_ARB_MAKE = "CIArbFixture"
_ARB_MODEL = "SedanCI"
_ARB_YEAR = 2021
# 17 "market" vehicles (spread wide enough to clear the 5% ln-price MAD floor) + one
# chollo_fuerte candidate (z ~= -4.58, comfortably inside -6.0 < z <= -3.5) + one bajo_mercado
# candidate (z ~= -2.26, comfortably inside -3.5 < z <= -2.0). n=19 clears COHORT_MIN_TIER_A (15).
_ARB_COHORT_PRICES: tuple[int, ...] = (
    15000, 15800, 16200, 16900, 17400, 17800, 18200, 18600, 19000,
    19400, 19800, 20200, 20700, 21300, 22000, 22800, 23800,
    9000,
    13000,
)

# Kept OUT of the cohort above (different make) so it never perturbs its median/MAD — exists
# only to give TestDesync a real dealer<->platform price pair (delta 1 200€ / 6%, clears
# GREATEST(100€, 1%) both ways).
_ARB_DESYNC_MAKE = "CIDesyncFixture"
_ARB_DESYNC_MODEL = "SedanD"
_ARB_DESYNC_YEAR = 2022
_ARB_DESYNC_DEALER_PRICE = 20000
_ARB_DESYNC_PLATFORM_PRICE = 21200


def _arb_dealer_ulid() -> str:
    return "FXARB" + "0" * 21


def _arb_dealer_cdp() -> str:
    return f"CDP-ES-{_PROV}-FXARB001"


def _arb_platform_ulid() -> str:
    return "FXPTF" + "0" * 21


def _arb_platform_cdp() -> str:
    return f"CDP-ES-{_PROV}-FXPTF001"


def _arb_vehicle_ulid(i: int) -> str:
    return f"FXAVH{str(i).zfill(21)}"


def _arb_desync_vehicle_ulid() -> str:
    return "FXDVH" + "0" * 21


async def _seed_arbitrage_fixture(conn: asyncpg.Connection) -> None:
    """Batch C — see module docstring. Entities/vehicles/listing are additive/idempotent (ON
    CONFLICT DO NOTHING), same as batch A. The F1 job itself (run_score) is deliberately NOT
    idempotent (INSERT-only, a fresh run_id every call — mirrors its real production cadence,
    04-arbitrage.md F1), so this must only run once per fixture invocation (called once from
    ``main()``, same as every other batch here).
    """
    dealer = _arb_dealer_ulid()
    platform = _arb_platform_ulid()

    await conn.executemany(
        "INSERT INTO entity (entity_ulid, cdp_code, kind, trade_name, province_code, "
        "municipality_code, status, sells_cars) "
        "VALUES ($1,$2,$3::entity_kind,$4,$5,$6,$7::entity_status,$8) "
        "ON CONFLICT (entity_ulid) DO NOTHING",
        [
            (dealer, _arb_dealer_cdp(), "compraventa", "CI Arbitrage Fixture Dealer",
             _PROV, _MUNI, "active", True),
            (platform, _arb_platform_cdp(), "plataforma", "CI Arbitrage Fixture Platform",
             _PROV, _MUNI, "active", False),
        ],
    )
    await conn.executemany(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) "
        "VALUES ($1, 'ci_fixture', 'seed') ON CONFLICT (entity_ulid, source_key) DO NOTHING",
        [(dealer,), (platform,)],
    )

    cohort_vehicles = [
        (_arb_vehicle_ulid(i), dealer, f"https://ci.fixture/arb/{i}", f"CI Arb Car {i}",
         _ARB_MAKE, _ARB_MODEL, _ARB_YEAR, price)
        for i, price in enumerate(_ARB_COHORT_PRICES, start=1)
    ]
    await conn.executemany(
        "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model, year, "
        "price, status) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,'available') "
        "ON CONFLICT (vehicle_ulid) DO NOTHING",
        cohort_vehicles,
    )

    desync_vehicle = _arb_desync_vehicle_ulid()
    await conn.execute(
        "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model, year, "
        "price, status) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,'available') "
        "ON CONFLICT (vehicle_ulid) DO NOTHING",
        desync_vehicle, dealer, "https://ci.fixture/arb/desync-1", "CI Desync Car 1",
        _ARB_DESYNC_MAKE, _ARB_DESYNC_MODEL, _ARB_DESYNC_YEAR, _ARB_DESYNC_DEALER_PRICE,
    )
    await conn.execute(
        "INSERT INTO platform_listing (vehicle_ulid, platform_entity_ulid, listing_url, "
        "platform_price) VALUES ($1,$2,$3,$4) "
        "ON CONFLICT (vehicle_ulid, platform_entity_ulid) DO NOTHING",
        desync_vehicle, platform, "https://ci.fixture/platform/desync-1",
        _ARB_DESYNC_PLATFORM_PRICE,
    )

    run_id, checks = await run_score(conn, make_filter=[_ARB_MAKE])
    n_deals = await conn.fetchval("SELECT n_deals FROM arbitrage_run WHERE run_id = $1", run_id)
    print(f"ci-fixture seeded: arbitrage_run={run_id} n_deals={n_deals} crosscheck_passed={checks['passed']}")


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        dealers = [
            (
                _entity_ulid(i), _cdp(i), "compraventa", f"CI Fixture Dealer {i}",
                _PROV, _MUNI, "active", True,
            )
            for i in range(1, _N_DEALERS + 1)
        ]
        await conn.executemany(
            "INSERT INTO entity (entity_ulid, cdp_code, kind, trade_name, province_code, "
            "municipality_code, status, sells_cars) "
            "VALUES ($1,$2,$3::entity_kind,$4,$5,$6,$7::entity_status,$8) "
            "ON CONFLICT (entity_ulid) DO NOTHING",
            dealers,
        )
        await conn.executemany(
            "INSERT INTO entity_source (entity_ulid, source_key, source_ref) "
            "VALUES ($1, 'ci_fixture', 'seed') ON CONFLICT (entity_ulid, source_key) DO NOTHING",
            [(_entity_ulid(i),) for i in range(1, _N_DEALERS + 1)],
        )
        # Available vehicles under the FIRST dealer (servable: status='available', 0<price<=5M).
        first = _entity_ulid(1)
        vehicles = [
            (_vehicle_ulid(i), first, f"https://ci.fixture/veh/{i}", f"CI Car {i}", 12000 + i * 100)
            for i in range(1, _N_VEHICLES + 1)
        ]
        await conn.executemany(
            "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, price, status) "
            "VALUES ($1,$2,$3,$4,$5,'available') ON CONFLICT (vehicle_ulid) DO NOTHING",
            vehicles,
        )
        ne = await conn.fetchval("SELECT count(*) FROM entity WHERE cdp_code LIKE 'CDP-ES-28-FXTRE%'")
        nv = await conn.fetchval("SELECT count(*) FROM vehicle WHERE entity_ulid = $1", first)
        print(f"ci-fixture seeded: dealers={ne} vehicles_under_first={nv}")

        # Batch B — see module docstring: the market-intelligence F0 precondition anchor.
        # Deliberately zero vehicle_cluster rows attached; vam_verdict_id stays NULL (the
        # proof-required trigger, 0070_vam_verified_needs_proof.sql, guards
        # canonical_dedup_run only — vehicle_cluster_run has no such constraint).
        await conn.execute(
            "INSERT INTO vehicle_cluster_run "
            "(cluster_run_id, resolver, scope, vam_verified, notes) "
            "VALUES ($1, 'ci_fixture', "
            "'CI fixture F0 anchor — no real clusters, market test suite attaches its own "
            "self-canonical rows against this run_id inside a rolled-back transaction', "
            "TRUE, 'seeded by scripts/seed_ci_fixture.py, safe to leave in place indefinitely') "
            "ON CONFLICT (cluster_run_id) DO NOTHING",
            _VEHICLE_CLUSTER_RUN_ID,
        )
        n_vcr = await conn.fetchval(
            "SELECT count(*) FROM vehicle_cluster_run WHERE cluster_run_id = $1", _VEHICLE_CLUSTER_RUN_ID
        )
        print(f"ci-fixture seeded: vam_verified vehicle_cluster_run={n_vcr}")

        # Batch C — see module docstring: the 04-arbitrage F1 corpus (arbitrage_run/cohort_stats/
        # deal_score) + a desync pair for tests/test_arbitrage_router.py.
        await _seed_arbitrage_fixture(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())

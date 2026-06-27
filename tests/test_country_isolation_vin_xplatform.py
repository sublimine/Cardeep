"""
tests/test_country_isolation_vin_xplatform.py

GOLDEN -- cross-border VIN-exact cross-platform dedup isolation
(generic-engine vector #2, the STRONG-KEY arm).

``scripts/cross_platform_dedup_watermark._vin_exact_resolver`` is the one
doctrine-permitted auto-merge: it collapses every group of >=2 DISTINCT ``vehicle``
rows that share one VIN-17 across platforms into a single survivor (oldest
``first_seen``), repointing the folded rows' ``platform_listing`` + ``vehicle_event``
edges onto the survivor and then DELETING the folded ``vehicle`` rows.

THE COUNTRY BLINDNESS (the bug this golden binds). Before the country fix the group
key is ``upper(v.vin_ref)`` ALONE -- there is NO JOIN to ``entity`` and NO
``country_code`` in the GROUP BY. So an ES vehicle and a DE vehicle that share a
VIN-17 land in ONE group and collapse ACROSS THE BORDER: the foreign listing (and
its delta history) is repointed onto the domestic survivor and the other country's
vehicle row is deleted -- mixing two countries in what the API serves per national
counter. ``pipeline/identity/cluster_vehicles.py`` already scopes BOTH its signals
by ``country_code`` (via entity) and blocks a cross-country cluster pre-write; this
VIN strong-key resolver was the single path that did NOT.

The ``vehicle`` row has NO ``country_code`` (``migrations/0003``); the country of a
vehicle is the country of its selling dealer, reached by JOIN
``vehicle.entity_ulid -> entity.country_code`` (``migrations/0052``, NOT NULL). This
is the binding regression guard for the VIN/strong-key layer of the COUNTRY-PROOF
invariant (``docs/generic-engine-bible/COUNTRY-PROOF-INVARIANT.md``):

  * cross-country, shared VIN-17  -> MUST NOT collapse (no delete, no foreign repoint)
  * same-country,  shared VIN-17  -> MUST     collapse (ES no-regression, byte-identical)
  * mixed 2xES + 1xDE same VIN-17 -> ONLY the ES pair collapses; DE stays untouched

ISOLATION (inviolable): runs ONLY against the dry-run DB (:5434). It HARD-REFUSES
:5433 (live production) two ways -- by DSN string and by asserting the target census
(entity AND vehicle) is EMPTY before seeding. Every scenario seeds + runs the REAL
resolver inside ONE asyncpg transaction that is ROLLED BACK, leaving :5434
byte-identical. The resolver is async (asyncpg); each test drives it via
``asyncio.run`` (no pytest-asyncio dependency, matching the suite's default mode).
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone

import asyncpg
import pytest

from scripts import cross_platform_dedup_watermark as cpd

# Hard-pinned dry-run DSN. The mandate: NEVER touch :5433 (live production).
_DRYRUN_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep"

# A real 17-char VIN over the WMI charset (no I, O, Q) -- matches the resolver's
# _VIN_SQL gate exactly: length 17 AND ~ '^[a-hj-npr-zA-HJ-NPR-Z0-9]{17}$'.
_VIN = "WVWZZZ1KZAW123456"

# Explicit first_seen stamps so survivor selection (oldest first_seen) is
# deterministic and never depends on insert wall-clock.
_T_OLD = datetime(2019, 1, 1, tzinfo=timezone.utc)
_T_MID = datetime(2020, 1, 1, tzinfo=timezone.utc)
_T_NEW = datetime(2021, 1, 1, tzinfo=timezone.utc)

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# DSN + isolation
# ---------------------------------------------------------------------------
def _target_dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


def _require_dryrun() -> str:
    """Refuse the live census by DSN string before any connection is opened."""
    dsn = _target_dsn()
    if "5433" in dsn:
        pytest.skip(
            "refusing to run the VIN x-platform isolation golden against :5433 "
            "(live production); point CARDEEP_DSN at the :5434 dry-run")
    return dsn


class _SkipScenario(Exception):
    """Raised inside the async scenario to turn a guard failure into pytest.skip."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


async def _connect_guarded(dsn: str) -> asyncpg.Connection:
    """Open the dry-run connection and refuse to seed a populated census.

    Triple guard mirrors tests/test_country_isolation_vehicle.py:
      1. :5433 already refused by _require_dryrun (DSN string);
      2. unreachable -> skip;
      3. refuse unless BOTH entity and vehicle are EMPTY (the dry-run holds 0/0;
         production holds ~452k entities) -- a mis-pointed DSN can never mutate real
         data, and the scenario's own rollback keeps :5434 byte-identical regardless.
    """
    try:
        conn = await asyncpg.connect(dsn, timeout=5)
    except Exception as exc:  # noqa: BLE001 - any connect failure -> skip, never fail
        raise _SkipScenario(f"dry-run cardeep-pg not reachable at {dsn}: {exc}")
    n_entities = await conn.fetchval("SELECT count(*) FROM entity")
    n_vehicles = await conn.fetchval("SELECT count(*) FROM vehicle")
    if n_entities != 0 or n_vehicles != 0:
        await conn.close()
        raise _SkipScenario(
            f"target DB has {n_entities} entities / {n_vehicles} vehicles -- not the "
            "empty dry-run; refusing to seed/cluster against a populated census")
    return conn


# ---------------------------------------------------------------------------
# Deterministic ULID + seeding helpers (asyncpg; FK + CHECK respecting)
# ---------------------------------------------------------------------------
def _ulid(prefix: str, n: int) -> str:
    """A 26-char id using only chars inside entity_ulid_shape
    (CHECK '^[0-9A-HJKMNP-TV-Z]{26}$'): the prefix uses A/B/D/E/G/P/S/V/W only,
    the rest are digits. vehicle_ulid/event_ulid have no shape CHECK but reuse it."""
    return (prefix + str(n).zfill(26 - len(prefix)))[:26]


async def _seed_entity(
    conn: asyncpg.Connection, *, prefix: str, n: int, cdp: str, country: str,
    kind: str = "compraventa",
) -> str:
    """Insert one entity (province/muni left NULL so the composite geo FK is not
    exercised -- the VIN resolver never reads province; country_code is the only
    geo field it needs and it is NOT NULL since migrations/0052). Returns entity_ulid."""
    ulid = _ulid(prefix, n)
    await conn.execute(
        "INSERT INTO entity (entity_ulid, cdp_code, kind, trade_name, legal_name, "
        " country_code, status) VALUES ($1, $2, $3, $4, $4, $5, 'active')",
        ulid, cdp, kind, f"test-{prefix}", country)
    return ulid


async def _seed_vehicle(
    conn: asyncpg.Connection, *, prefix: str, n: int, entity_ulid: str,
    deep_link: str, vin: str, first_seen: datetime,
) -> str:
    """Insert one in-scope vehicle (status defaults 'available'). first_seen is set
    explicitly (tz-aware datetime) so survivor selection (oldest first_seen) is
    deterministic."""
    ulid = _ulid(prefix, n)
    await conn.execute(
        "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, vin_ref, "
        " first_seen, last_seen, status) "
        "VALUES ($1, $2, $3, $4, $5, $5, 'available')",
        ulid, entity_ulid, deep_link, vin, first_seen)
    return ulid


async def _seed_listing(
    conn: asyncpg.Connection, *, vehicle_ulid: str, platform_ulid: str, url: str,
) -> None:
    """Insert one platform_listing edge (status defaults 'listed' -- the resolver
    only joins pl.status='listed')."""
    await conn.execute(
        "INSERT INTO platform_listing (vehicle_ulid, platform_entity_ulid, listing_url) "
        "VALUES ($1, $2, $3)",
        vehicle_ulid, platform_ulid, url)


async def _seed_event(
    conn: asyncpg.Connection, *, prefix: str, n: int, vehicle_ulid: str, entity_ulid: str,
) -> str:
    """Insert one vehicle_event (the delta history the resolver repoints). Returns
    event_ulid so the test can prove it was NOT repointed across the border."""
    ulid = _ulid(prefix, n)
    await conn.execute(
        "INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type) "
        "VALUES ($1, $2, $3, 'NEW')",
        ulid, vehicle_ulid, entity_ulid)
    return ulid


# ---------------------------------------------------------------------------
# Scenarios -- seed + run the REAL resolver + snapshot, all inside a rolled-back tx
# ---------------------------------------------------------------------------
async def _scenario_cross_country(dsn: str) -> dict:
    """ES + DE vehicles sharing one VIN-17, on two distinct platforms. ES is the
    OLDER row, so pre-fix it is the survivor and the DE listing+event are repointed
    onto it (the foreign-over-domestic mix) and the DE vehicle row is deleted."""
    conn = await _connect_guarded(dsn)
    tr = conn.transaction()
    await tr.start()
    try:
        es_dealer = await _seed_entity(conn, prefix="ES", n=1, cdp="CDP-ES-28-VINX01", country="ES")
        de_dealer = await _seed_entity(conn, prefix="DE", n=2, cdp="CDP-DE-28-VINX02", country="DE")
        plat_a = await _seed_entity(conn, prefix="PA", n=3, cdp="CDP-ES-28-VINXPA", country="ES", kind="plataforma")
        plat_b = await _seed_entity(conn, prefix="PB", n=4, cdp="CDP-ES-28-VINXPB", country="ES", kind="plataforma")

        es_veh = await _seed_vehicle(
            conn, prefix="VE", n=5, entity_ulid=es_dealer,
            deep_link="https://es.plat/vin-es", vin=_VIN, first_seen=_T_MID)
        de_veh = await _seed_vehicle(
            conn, prefix="VD", n=6, entity_ulid=de_dealer,
            deep_link="https://de.plat/vin-de", vin=_VIN, first_seen=_T_NEW)

        await _seed_listing(conn, vehicle_ulid=es_veh, platform_ulid=plat_a, url="https://es.plat/vin-es")
        await _seed_listing(conn, vehicle_ulid=de_veh, platform_ulid=plat_b, url="https://de.plat/vin-de")

        es_event = await _seed_event(conn, prefix="GE", n=7, vehicle_ulid=es_veh, entity_ulid=es_dealer)
        de_event = await _seed_event(conn, prefix="GD", n=8, vehicle_ulid=de_veh, entity_ulid=de_dealer)

        result = await cpd._vin_exact_resolver(conn, apply=True)

        present = [r["vehicle_ulid"] for r in await conn.fetch(
            "SELECT vehicle_ulid FROM vehicle WHERE vehicle_ulid = ANY($1::text[])",
            [es_veh, de_veh])]
        edge_a = await conn.fetchval(
            "SELECT vehicle_ulid FROM platform_listing WHERE platform_entity_ulid=$1", plat_a)
        edge_b = await conn.fetchval(
            "SELECT vehicle_ulid FROM platform_listing WHERE platform_entity_ulid=$1", plat_b)
        ev_es = await conn.fetchval(
            "SELECT vehicle_ulid FROM vehicle_event WHERE event_ulid=$1", es_event)
        ev_de = await conn.fetchval(
            "SELECT vehicle_ulid FROM vehicle_event WHERE event_ulid=$1", de_event)
        return {
            "folded_rows": result["folded_rows"], "groups": result["groups"],
            "present": set(present), "es_veh": es_veh, "de_veh": de_veh,
            "edge_a": edge_a, "edge_b": edge_b, "ev_es": ev_es, "ev_de": ev_de,
        }
    finally:
        await tr.rollback()
        await conn.close()


async def _scenario_same_country(dsn: str) -> dict:
    """Two ES vehicles (distinct dealers) sharing one VIN-17 on two platforms MUST
    still collapse to one survivor carrying both edges (ES no-regression)."""
    conn = await _connect_guarded(dsn)
    tr = conn.transaction()
    await tr.start()
    try:
        d1 = await _seed_entity(conn, prefix="SA", n=1, cdp="CDP-ES-28-VINS01", country="ES")
        d2 = await _seed_entity(conn, prefix="SB", n=2, cdp="CDP-ES-28-VINS02", country="ES")
        plat_a = await _seed_entity(conn, prefix="PA", n=3, cdp="CDP-ES-28-VINSPA", country="ES", kind="plataforma")
        plat_b = await _seed_entity(conn, prefix="PB", n=4, cdp="CDP-ES-28-VINSPB", country="ES", kind="plataforma")

        v1 = await _seed_vehicle(
            conn, prefix="WA", n=5, entity_ulid=d1,
            deep_link="https://es.plat/s1", vin=_VIN, first_seen=_T_MID)
        v2 = await _seed_vehicle(
            conn, prefix="WB", n=6, entity_ulid=d2,
            deep_link="https://es.plat/s2", vin=_VIN, first_seen=_T_NEW)

        await _seed_listing(conn, vehicle_ulid=v1, platform_ulid=plat_a, url="https://es.plat/s1")
        await _seed_listing(conn, vehicle_ulid=v2, platform_ulid=plat_b, url="https://es.plat/s2")

        result = await cpd._vin_exact_resolver(conn, apply=True)

        present = [r["vehicle_ulid"] for r in await conn.fetch(
            "SELECT vehicle_ulid FROM vehicle WHERE vehicle_ulid = ANY($1::text[])", [v1, v2])]
        edges_on_survivor = None
        if len(present) == 1:
            edges_on_survivor = await conn.fetchval(
                "SELECT count(*) FROM platform_listing WHERE vehicle_ulid=$1", present[0])
        return {
            "folded_rows": result["folded_rows"], "groups": result["groups"],
            "present": present, "edges_on_survivor": edges_on_survivor,
        }
    finally:
        await tr.rollback()
        await conn.close()


async def _scenario_mixed(dsn: str) -> dict:
    """2x ES + 1x DE vehicles, all one VIN-17. ONLY the ES pair may collapse; the DE
    row must stay untouched (proves the fix partitions by country, not a global
    VIN-merge kill)."""
    conn = await _connect_guarded(dsn)
    tr = conn.transaction()
    await tr.start()
    try:
        es1 = await _seed_entity(conn, prefix="SA", n=1, cdp="CDP-ES-28-VINM01", country="ES")
        es2 = await _seed_entity(conn, prefix="SB", n=2, cdp="CDP-ES-28-VINM02", country="ES")
        de1 = await _seed_entity(conn, prefix="DE", n=3, cdp="CDP-DE-28-VINM03", country="DE")
        pa = await _seed_entity(conn, prefix="PA", n=4, cdp="CDP-ES-28-VINMPA", country="ES", kind="plataforma")
        pb = await _seed_entity(conn, prefix="PB", n=5, cdp="CDP-ES-28-VINMPB", country="ES", kind="plataforma")
        pc = await _seed_entity(conn, prefix="PV", n=6, cdp="CDP-DE-28-VINMPC", country="DE", kind="plataforma")

        ev1 = await _seed_vehicle(conn, prefix="WA", n=7, entity_ulid=es1,
                                  deep_link="https://es.plat/m1", vin=_VIN, first_seen=_T_MID)
        ev2 = await _seed_vehicle(conn, prefix="WB", n=8, entity_ulid=es2,
                                  deep_link="https://es.plat/m2", vin=_VIN, first_seen=_T_NEW)
        dv1 = await _seed_vehicle(conn, prefix="VD", n=9, entity_ulid=de1,
                                  deep_link="https://de.plat/m3", vin=_VIN, first_seen=_T_OLD)

        await _seed_listing(conn, vehicle_ulid=ev1, platform_ulid=pa, url="https://es.plat/m1")
        await _seed_listing(conn, vehicle_ulid=ev2, platform_ulid=pb, url="https://es.plat/m2")
        await _seed_listing(conn, vehicle_ulid=dv1, platform_ulid=pc, url="https://de.plat/m3")

        result = await cpd._vin_exact_resolver(conn, apply=True)

        es_present = [r["vehicle_ulid"] for r in await conn.fetch(
            "SELECT vehicle_ulid FROM vehicle WHERE vehicle_ulid = ANY($1::text[])", [ev1, ev2])]
        de_present = await conn.fetchval(
            "SELECT count(*) FROM vehicle WHERE vehicle_ulid=$1", dv1)
        de_edge = await conn.fetchval(
            "SELECT vehicle_ulid FROM platform_listing WHERE platform_entity_ulid=$1", pc)
        return {
            "folded_rows": result["folded_rows"], "groups": result["groups"],
            "es_present_count": len(es_present), "de_present": de_present,
            "de_edge": de_edge, "dv1": dv1,
        }
    finally:
        await tr.rollback()
        await conn.close()


def _run(scenario, dsn: str) -> dict:
    try:
        return asyncio.run(scenario(dsn))
    except _SkipScenario as skip:
        pytest.skip(skip.reason)


# ---------------------------------------------------------------------------
# GOLDENS
# ---------------------------------------------------------------------------
def test_vin_cross_country_does_not_collapse():
    """ES + DE vehicles sharing one VIN-17 MUST NOT collapse across the border:
    no fold, both rows survive, and neither the foreign listing nor its delta event
    is repointed onto the domestic survivor."""
    snap = _run(_scenario_cross_country, _require_dryrun())

    assert snap["folded_rows"] == 0 and snap["groups"] == 0, (
        "CROSS-BORDER VIN FALSE-MERGE: the VIN-exact resolver folded "
        f"{snap['folded_rows']} row(s) in {snap['groups']} group(s) across ES/DE. "
        "The VIN group key is country-blind (upper(vin_ref) with no entity JOIN).")
    assert snap["present"] == {snap["es_veh"], snap["de_veh"]}, (
        "CROSS-BORDER VIN FALSE-MERGE: a vehicle row was DELETED across the border "
        f"(survivors={snap['present']!r}, expected both ES+DE present).")
    assert snap["edge_a"] == snap["es_veh"], "ES platform listing was moved off its ES vehicle."
    assert snap["edge_b"] == snap["de_veh"], (
        "CROSS-BORDER REPUNT: the DE platform listing was repointed onto the ES "
        f"survivor (edge now on {snap['edge_b']!r}, expected the DE vehicle).")
    assert snap["ev_es"] == snap["es_veh"], "ES delta event was moved off its ES vehicle."
    assert snap["ev_de"] == snap["de_veh"], (
        "CROSS-BORDER REPUNT: the DE delta history (vehicle_event) was repointed onto "
        f"the ES survivor (event now on {snap['ev_de']!r}, expected the DE vehicle).")


def test_vin_same_country_still_collapses():
    """ES no-regression: two ES vehicles sharing one VIN-17 across platforms MUST
    still collapse to a single survivor that carries BOTH platform edges."""
    snap = _run(_scenario_same_country, _require_dryrun())

    assert snap["folded_rows"] == 1 and snap["groups"] == 1, (
        "ES REGRESSION: the same-country VIN-exact merge stopped folding "
        f"(folded_rows={snap['folded_rows']} groups={snap['groups']}, expected 1/1) -- "
        "the country fix must be byte-identical within one country.")
    assert len(snap["present"]) == 1, (
        "ES REGRESSION: same-country VIN pair did not collapse to one survivor "
        f"(survivors={snap['present']!r}).")
    assert snap["edges_on_survivor"] == 2, (
        "ES REGRESSION: the survivor did not absorb both platform edges "
        f"(edges_on_survivor={snap['edges_on_survivor']!r}, expected 2).")


def test_vin_mixed_collapses_only_the_domestic_pair():
    """2x ES + 1x DE, one shared VIN-17: ONLY the ES pair collapses; the DE row and
    its listing stay untouched (the fix partitions by country, it does not disable
    VIN merging globally)."""
    snap = _run(_scenario_mixed, _require_dryrun())

    assert snap["folded_rows"] == 1 and snap["groups"] == 1, (
        "MIXED VIN: expected exactly the ES pair to fold (1 row, 1 group); got "
        f"folded_rows={snap['folded_rows']} groups={snap['groups']} -- a country-blind "
        "key folds all three across the border.")
    assert snap["es_present_count"] == 1, (
        f"MIXED VIN: the ES pair must collapse to one survivor (es_present={snap['es_present_count']}).")
    assert snap["de_present"] == 1, (
        "MIXED VIN: the DE vehicle row was DELETED by a cross-border collapse.")
    assert snap["de_edge"] == snap["dv1"], (
        "MIXED VIN: the DE platform listing was repointed onto an ES survivor "
        f"(edge now on {snap['de_edge']!r}, expected the DE vehicle {snap['dv1']!r}).")

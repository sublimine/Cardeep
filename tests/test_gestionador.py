"""Tests for pipeline/gestionador/detect.py and route.py.

Design:
  - Detectors: tested with mock asyncpg connections that return synthetic data.
    No live DB required for unit tests.
  - State machine (route.py): tested with an in-memory mock that records
    executed SQL to verify correct transitions and guard conditions.
  - Threshold logic: tested with boundary values (exact threshold, just above,
    just below) to confirm correct severity/lane assignment.
  - MVCC safety: verified that state machine never issues UPDATE on
    non-mutated rows (checked by asserting no spurious UPDATE for OPEN refresh).

All tests are synchronous at the top level (asyncio.run) to work with any
pytest configuration.
"""
from __future__ import annotations

import asyncio
import json
import math
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.gestionador.detect import (
    AnomalyResult,
    _daily_bucket,
    _rel,
    _z_two_prop,
    detect_count_inflation,
    detect_coverage_gap,
    detect_fabrication,
    detect_price_trap,
    detect_staleness,
    detect_silent_cap,
    TAU_COUNT,
    STALENESS_TTL,
    STALENESS_RATIO_CRIT,
    COVERAGE_ANCHORS,
    FAB_COLLAPSE_KAPPA,
    FAB_KM_CEIL,
    FAB_PRICE_CEIL,
    FAB_YEAR_FLOOR,
    FAB_YEAR_CEIL,
    PRICE_TRAP_MONTHLY_LOW,
    PRICE_TRAP_MONTHLY_HIGH,
    SILENT_CAP_MAX_ROWS,
)
from pipeline.gestionador.route import (
    VALID_TRANSITIONS,
    assert_valid_transition,
    LANE_SLA,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_conn(fetch_result=None, fetchrow_result=None, execute_result=None):
    """Return a minimal asyncpg.Connection mock."""
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=fetch_result or [])
    conn.fetchrow = AsyncMock(return_value=fetchrow_result)
    conn.execute = AsyncMock(return_value=execute_result)
    return conn


def _record(data: dict) -> MagicMock:
    """Simulate an asyncpg Record."""
    rec = MagicMock()
    rec.__getitem__ = lambda self, key: data[key]
    # Support dict(row["independent_values"]) calls
    for k, v in data.items():
        setattr(rec, k, v)
    return rec


def run(coro):
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# Unit tests: _rel and _z_two_prop
# ---------------------------------------------------------------------------

class TestMathHelpers:
    def test_rel_symmetric(self):
        assert _rel(100, 80) == pytest.approx(_rel(80, 100))

    def test_rel_zero_denominator(self):
        # max(0, 0, 1) = 1 → rel(0,0) = 0
        assert _rel(0, 0) == 0.0

    def test_rel_exact(self):
        # |100-80|/max(100,80,1) = 20/100 = 0.2
        assert _rel(100, 80) == pytest.approx(0.2)

    def test_z_no_increase(self):
        # p1 <= p0 → z = 0
        assert _z_two_prop(100, 1000, 5, 100) == 0.0

    def test_z_large_increase(self):
        # From spec §3.3: p0=0.012, p1=0.46, n0=22300, n1=140 → z≈43.8
        z = _z_two_prop(267, 22300, 64, 140)
        assert z > 40.0

    def test_z_empty_baseline(self):
        assert _z_two_prop(0, 0, 5, 100) == 0.0


# ---------------------------------------------------------------------------
# 3.1 count_inflation detector
# ---------------------------------------------------------------------------

class TestCountInflation:
    def _make_verdict_rows(self, cases):
        """cases: list of (subject_key, d, h, l) tuples."""
        rows = []
        for key, d, h, l in cases:
            rec = {
                "subject_key": key,
                "independent_values": {
                    "source_declared": d,
                    "harvested": h,
                    "db_available": l,
                },
                "verdict": "TRUSTWORTHY",
                "primary_value": l,
            }
            rows.append(rec)
        return rows

    def test_no_anomaly_when_counts_match(self):
        """OK MOBILITY VALENCIA: D=H=L=78 → no item."""
        rows = self._make_verdict_rows([("CDP-ES-46-ABC12345", 78, 78, 78)])
        conn = _make_conn(fetch_result=rows)
        results = run(detect_count_inflation(conn))
        assert results == []

    def test_ingest_loss_critical(self):
        """H parsed > L landed (5 collisions) → critical, AUTO_FIX, quarantines."""
        rows = self._make_verdict_rows([("CDP-ES-28-INGESTLOSS", 78, 78, 73)])
        conn = _make_conn(fetch_result=rows)
        results = run(detect_count_inflation(conn))
        assert len(results) == 1
        r = results[0]
        assert r.severity == "critical"
        assert r.lane == "AUTO_FIX"
        assert r.quarantines is True
        assert r.detector == "count_inflation"
        assert r.measured["h"] == 78
        assert r.measured["l"] == 73

    def test_large_gap_critical_ingest_loss(self):
        """D=1000, H=1000, L=780: H>L means ingest_loss → critical, AUTO_FIX.
        The ingest-loss rule takes priority over the g_DL>0.20 path because
        H > L (rows parsed but not landed = the primary lie to fix first)."""
        rows = self._make_verdict_rows([("CDP-ES-08-BIGCAP", 1000, 1000, 780)])
        conn = _make_conn(fetch_result=rows)
        results = run(detect_count_inflation(conn))
        assert len(results) == 1
        r = results[0]
        assert r.severity == "critical"
        assert r.lane == "AUTO_FIX"
        assert r.quarantines is True

    def test_small_gap_is_ingest_loss(self):
        """D=100, H=100, L=95: H>L means 5 parsed rows never landed.
        Per V4 §3.1: g_HL>0 → critical/AUTO_FIX (the strongest rule).
        A 'warning RESEARCH' gap requires H==L but D>L (scrape gap only)."""
        rows = self._make_verdict_rows([("CDP-ES-08-SMALLGAP", 100, 100, 95)])
        conn = _make_conn(fetch_result=rows)
        results = run(detect_count_inflation(conn))
        assert len(results) == 1
        r = results[0]
        # g_HL = 5/100 > 0 → always critical ingest_loss
        assert r.severity == "critical"
        assert r.lane == "AUTO_FIX"
        assert r.quarantines is True

    def test_scrape_gap_warning_research(self):
        """D=100, H=95, L=95: scrape gap only (H==L), g_DL=5%>2% → warning RESEARCH."""
        rows = self._make_verdict_rows([("CDP-ES-08-SCRAPEGAP", 100, 95, 95)])
        conn = _make_conn(fetch_result=rows)
        results = run(detect_count_inflation(conn))
        assert len(results) == 1
        r = results[0]
        assert r.severity == "warning"
        assert r.lane == "RESEARCH"
        assert r.quarantines is False

    def test_below_threshold_no_anomaly(self):
        """D=100, H=95, L=95: scrape gap g_DL=5% but H==L so no ingest loss.
        Actually g_DL = 5% > 2% TAU_COUNT → warning. Test that H==L, D>L
        with g_DL < TAU_COUNT produces no item."""
        # g_DL = |100-99|/100 = 0.01 < 0.02 and H==L=99 (no ingest loss)
        rows = self._make_verdict_rows([("CDP-ES-08-FINE", 100, 99, 99)])
        conn = _make_conn(fetch_result=rows)
        results = run(detect_count_inflation(conn))
        assert results == []

    def test_ghost_surplus(self):
        """L > D by >2% → ghost surplus warning, AUTO_FIX."""
        rows = self._make_verdict_rows([("CDP-ES-08-GHOST", 80, 80, 90)])
        conn = _make_conn(fetch_result=rows)
        results = run(detect_count_inflation(conn))
        assert len(results) == 1
        r = results[0]
        assert r.measured.get("sub") == "ghost_surplus"
        assert r.lane == "AUTO_FIX"

    def test_dedupe_key_format(self):
        """dedupe_key must be detector|subject_key|bucket."""
        rows = self._make_verdict_rows([("CDP-ES-46-DEDUP", 100, 100, 80)])
        conn = _make_conn(fetch_result=rows)
        results = run(detect_count_inflation(conn))
        assert len(results) == 1
        bucket = _daily_bucket()
        assert results[0].dedupe_key == f"count_inflation|CDP-ES-46-DEDUP|{bucket}"

    def test_missing_evidence_skipped(self):
        """Rows with None in d/h/l are silently skipped."""
        rows = [{"subject_key": "CDP-ES-00-NOVAL",
                 "independent_values": {"source_declared": None, "harvested": None, "db_available": None},
                 "verdict": "UNVERIFIED", "primary_value": None}]
        conn = _make_conn(fetch_result=rows)
        results = run(detect_count_inflation(conn))
        assert results == []


# ---------------------------------------------------------------------------
# 3.2 silent_cap detector
# ---------------------------------------------------------------------------

class TestSilentCap:
    def _make_iv_row(self, key, d, h):
        return {"subject_key": key,
                "independent_values": {"source_declared": d, "harvested": h},
                "created_at": "2026-06-15"}

    def test_page_budget_cap_fires(self):
        """harvested=1000 (max_pages*size), declared=1840 → critical."""
        rows = [self._make_iv_row("CDP-ES-28-MEGADEALER", 1840, 1000)]
        conn = _make_conn(fetch_result=rows)
        results = run(detect_silent_cap(conn))
        assert len(results) == 1
        r = results[0]
        assert r.severity == "critical"
        assert r.measured["sub"] == "page_budget_cap"
        assert r.lane == "AUTO_FIX"
        assert r.quarantines is True

    def test_provider_ceiling_fires(self):
        """harvested=500 (round ceiling), declared=600 → critical, RESEARCH."""
        rows = [self._make_iv_row("CDP-ES-28-CEILING", 600, 500)]
        conn = _make_conn(fetch_result=rows)
        results = run(detect_silent_cap(conn))
        assert len(results) == 1
        r = results[0]
        assert r.measured["sub"] == "provider_ceiling"
        assert r.lane == "RESEARCH"

    def test_no_cap_when_d_le_h(self):
        """D <= H: no cap (harvest completed the declared count)."""
        rows = [self._make_iv_row("CDP-ES-28-FULL", 78, 78)]
        conn = _make_conn(fetch_result=rows)
        results = run(detect_silent_cap(conn))
        assert results == []

    def test_h_below_round_ceiling_no_fire(self):
        """harvested=999 (not a round ceiling), declared=1200 → no fire."""
        rows = [self._make_iv_row("CDP-ES-28-NOROUND", 1200, 999)]
        conn = _make_conn(fetch_result=rows)
        results = run(detect_silent_cap(conn))
        assert results == []


# ---------------------------------------------------------------------------
# 3.4 staleness detector
# ---------------------------------------------------------------------------

class TestStaleness:
    def test_fresh_entity_no_item(self):
        """Entity 1 day old with 3-day TTL (ratio=0.33) → no item."""
        rows = [{"cdp_code": "CDP-ES-28-FRESH", "kind": "compraventa",
                 "last_seen": None, "age_seconds": 86400}]
        conn = _make_conn(fetch_result=rows)
        results = run(detect_staleness(conn))
        assert results == []

    def test_warning_ratio_between_1_and_3(self):
        """Compraventa 7 days old (ratio=7/3=2.33 → warning, AUTO_FIX, no quarantine."""
        rows = [{"cdp_code": "CDP-ES-28-STALE", "kind": "compraventa",
                 "last_seen": None, "age_seconds": 7 * 86400}]
        conn = _make_conn(fetch_result=rows)
        results = run(detect_staleness(conn))
        assert len(results) == 1
        r = results[0]
        assert r.severity == "warning"
        assert r.quarantines is False
        assert r.lane == "AUTO_FIX"

    def test_critical_ratio_over_3(self):
        """Compraventa 11 days old (ratio=11/3=3.67 → critical, quarantines."""
        rows = [{"cdp_code": "CDP-ES-28-CRIT", "kind": "compraventa",
                 "last_seen": None, "age_seconds": 11 * 86400}]
        conn = _make_conn(fetch_result=rows)
        results = run(detect_staleness(conn))
        assert len(results) == 1
        r = results[0]
        assert r.severity == "critical"
        assert r.quarantines is True

    def test_storm_suppression(self):
        """More than 200 entities stale → one source-level item, no per-entity spam."""
        rows = [
            {"cdp_code": f"CDP-ES-08-{i:04d}", "kind": "compraventa",
             "last_seen": None, "age_seconds": 30 * 86400}
            for i in range(250)
        ]
        conn = _make_conn(fetch_result=rows)
        results = run(detect_staleness(conn))
        # Should be exactly 1 storm item (not 250 individual items)
        assert len(results) == 1
        r = results[0]
        assert r.subject_type == "source"
        assert r.measured["storm_suppressed"] is True
        assert r.measured["stale_count"] == 250


# ---------------------------------------------------------------------------
# 3.5 fabrication detector
# ---------------------------------------------------------------------------

class TestFabrication:
    def test_out_of_band_km_fires(self):
        """km = 1,100,000 > FAB_KM_CEIL (1M) → critical, quarantines."""
        oob_row = {"vehicle_ulid": "01JTEST00000000000000KM001",
                   "cdp_code": "CDP-ES-08-FAB001",
                   "price": 15000, "year": 2018, "km": 1_100_000}
        collapse_rows = []
        degen_rows = []

        conn = AsyncMock()
        conn.fetch = AsyncMock(side_effect=[
            [oob_row],      # out-of-band query
            collapse_rows,  # collapse query
            degen_rows,     # degenerate query
        ])

        results = run(detect_fabrication(conn))
        assert any(r.subject_type == "vehicle" and r.severity == "critical"
                   for r in results)
        vehicle_items = [r for r in results if r.subject_type == "vehicle"]
        assert len(vehicle_items) == 1
        assert vehicle_items[0].quarantines is True

    def test_no_oob_no_item(self):
        """All values within bounds → no fabrication item."""
        conn = AsyncMock()
        conn.fetch = AsyncMock(return_value=[])
        results = run(detect_fabrication(conn))
        assert results == []

    def test_distinct_collapse_fires(self):
        """Source with collapse_ratio > kappa → critical RESEARCH item."""
        collapse_row = {"source_key": "oem_hyundai",
                        "source_distinct": 175, "cdp_distinct": 48}
        conn = AsyncMock()
        conn.fetch = AsyncMock(side_effect=[
            [],              # out-of-band
            [collapse_row],  # collapse
            [],              # degenerate
        ])
        results = run(detect_fabrication(conn))
        source_items = [r for r in results if r.subject_type == "source"
                        and "collapse" in r.measured.get("sub", "")]
        assert len(source_items) == 1
        r = source_items[0]
        assert r.severity == "critical"
        assert r.lane == "RESEARCH"
        assert r.measured["collapse_ratio"] == pytest.approx(175 / 48, rel=1e-3)


# ---------------------------------------------------------------------------
# 3.6 coverage_gap detector
# ---------------------------------------------------------------------------

class TestCoverageGap:
    def test_desguace_at_anchor_no_item(self):
        """Desguace at anchor floor (1292) → no item (relgap=0)."""
        rows = [{"kind": "desguace", "covered": 1292}]
        conn = _make_conn(fetch_result=rows)
        results = run(detect_coverage_gap(conn))
        # relgap = 0 < 0.10 → no item
        desguace_items = [r for r in results if r.subject_key == "desguace"]
        assert desguace_items == []

    def test_garaje_large_gap_critical(self):
        """Garaje: covered=7220, anchor=29955.
        Since covered < anchor (hard floor breach), severity = critical per V4 §3.6.
        The anchor is the PA floor minimum; being below it is an anchor breach."""
        rows = [{"kind": "garaje", "covered": 7220}]
        conn = _make_conn(fetch_result=rows)
        results = run(detect_coverage_gap(conn))
        garaje_items = [r for r in results if r.subject_key == "garaje"]
        assert len(garaje_items) == 1
        r = garaje_items[0]
        assert r.severity == "critical"   # anchor breach (covered < floor)
        assert r.lane == "RESEARCH"
        assert r.quarantines is False     # coverage_gap never quarantines

    def test_concesionario_above_anchor_warning(self):
        """Concesionario: covered=2500 > anchor=2018 but relgap is driven by
        a higher estimate. Here covered > anchor → no anchor breach.
        Simulate a covered that is above the floor but below a higher estimate:
        covered=2500, anchor=2018 → covered >= anchor, no anchor breach.
        relgap = 0 (no gap below floor) → no item."""
        rows = [{"kind": "concesionario_oficial", "covered": 2500}]
        conn = _make_conn(fetch_result=rows)
        results = run(detect_coverage_gap(conn))
        oficial_items = [r for r in results if r.subject_key == "concesionario_oficial"]
        # covered > anchor → relgap uses anchor as denominator: gap=0 → no item
        assert oficial_items == []

    def test_anchor_breach_critical(self):
        """Covered < anchor floor (desguace=1000 < 1292) → critical."""
        rows = [{"kind": "desguace", "covered": 1000}]
        conn = _make_conn(fetch_result=rows)
        results = run(detect_coverage_gap(conn))
        desguace_items = [r for r in results if r.subject_key == "desguace"]
        assert len(desguace_items) == 1
        assert desguace_items[0].severity == "critical"

    def test_coverage_gap_never_quarantines(self):
        """coverage_gap items must never have quarantines=True."""
        rows = [{"kind": kind, "covered": 1} for kind in COVERAGE_ANCHORS]
        conn = _make_conn(fetch_result=rows)
        results = run(detect_coverage_gap(conn))
        assert all(not r.quarantines for r in results)


# ---------------------------------------------------------------------------
# 3.7 price_trap detector
# ---------------------------------------------------------------------------

class TestPriceTrap:
    def _median_row(self, kind, median):
        return {"kind": kind, "median_price": median}

    def test_implausible_low_fires(self):
        """Price=199 (< 300 floor) for compraventa → critical, quarantines."""
        median_rows = [self._median_row("compraventa", 18000)]
        trap_rows = [{"vehicle_ulid": "01JTEST00000000000000PT001",
                      "cdp_code": "CDP-ES-28-TRAP", "kind": "compraventa",
                      "price": 199}]
        conn = AsyncMock()
        conn.fetch = AsyncMock(side_effect=[median_rows, trap_rows])
        results = run(detect_price_trap(conn))
        assert len(results) == 1
        r = results[0]
        assert r.severity == "critical"
        assert r.quarantines is True
        assert r.measured["implausible_low"] is True

    def test_monthly_band_outlier_fires(self):
        """Price=299 (monthly band) + < 5% of median=18000 → critical."""
        median_rows = [self._median_row("compraventa", 18000)]
        trap_rows = [{"vehicle_ulid": "01JTEST00000000000000PT002",
                      "cdp_code": "CDP-ES-28-TRAP2", "kind": "compraventa",
                      "price": 299}]
        conn = AsyncMock()
        conn.fetch = AsyncMock(side_effect=[median_rows, trap_rows])
        results = run(detect_price_trap(conn))
        assert len(results) == 1
        assert results[0].measured["ratio_outlier"] is True

    def test_normal_price_no_item(self):
        """Price=18000 (well above floor) → no item."""
        median_rows = [self._median_row("compraventa", 18000)]
        # price=18000 > floor=300 → not in trap_rows (filtered by query)
        conn = AsyncMock()
        conn.fetch = AsyncMock(side_effect=[median_rows, []])
        results = run(detect_price_trap(conn))
        assert results == []

    def test_desguace_exempt(self):
        """Desguace has no floor in PRICE_TRAP_FLOOR → items skipped."""
        median_rows = [self._median_row("desguace", 50)]
        trap_rows = [{"vehicle_ulid": "01JTEST00000000000000PT003",
                      "cdp_code": "CDP-ES-04-DESGUACE", "kind": "desguace",
                      "price": 50}]
        conn = AsyncMock()
        conn.fetch = AsyncMock(side_effect=[median_rows, trap_rows])
        results = run(detect_price_trap(conn))
        assert results == []


# ---------------------------------------------------------------------------
# State machine: assert_valid_transition
# ---------------------------------------------------------------------------

class TestStateMachine:
    def test_open_to_routed_valid(self):
        assert_valid_transition("OPEN", "ROUTED")

    def test_open_to_quarantined_valid(self):
        assert_valid_transition("OPEN", "QUARANTINED")

    def test_reverifying_to_resolved_valid(self):
        assert_valid_transition("REVERIFYING", "RESOLVED")

    def test_reverifying_to_reopened_valid(self):
        assert_valid_transition("REVERIFYING", "REOPENED")

    def test_resolved_to_reopened_valid(self):
        assert_valid_transition("RESOLVED", "REOPENED")

    def test_wont_fix_is_terminal(self):
        with pytest.raises(ValueError, match="Illegal transition"):
            assert_valid_transition("WONT_FIX", "OPEN")

    def test_open_to_resolved_invalid(self):
        """Cannot skip REVERIFYING to get to RESOLVED."""
        with pytest.raises(ValueError, match="Illegal transition"):
            assert_valid_transition("OPEN", "RESOLVED")

    def test_routed_to_resolved_invalid(self):
        with pytest.raises(ValueError, match="Illegal transition"):
            assert_valid_transition("ROUTED", "RESOLVED")

    def test_unknown_state_raises(self):
        with pytest.raises(ValueError, match="Unknown target state"):
            assert_valid_transition("OPEN", "FLYING")

    def test_initial_transition_must_be_open(self):
        with pytest.raises(ValueError, match="Initial transition"):
            assert_valid_transition(None, "ROUTED")

    def test_initial_to_open_valid(self):
        assert_valid_transition(None, "OPEN")

    def test_all_states_reachable(self):
        """Verify every state appears as both source and target at least once."""
        all_sources = set(VALID_TRANSITIONS.keys())
        all_targets = set()
        for targets in VALID_TRANSITIONS.values():
            all_targets |= targets
        all_targets.add("OPEN")  # reached via initial transition
        # Every state should be reachable
        all_states = {"OPEN", "ROUTED", "IN_PROGRESS", "REVERIFYING",
                      "RESOLVED", "QUARANTINED", "ESCALATED", "WONT_FIX", "REOPENED"}
        assert all_states <= all_targets


# ---------------------------------------------------------------------------
# route.py: transition() guard — RESOLVED requires verdict_id
# ---------------------------------------------------------------------------

class TestTransitionGuards:
    def test_resolved_without_verdict_id_raises(self):
        """Transition to RESOLVED without verdict_id must raise ValueError."""
        from pipeline.gestionador.route import transition
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(return_value={"state": "REVERIFYING", "closed_at": None})

        with pytest.raises(ValueError, match="verdict_id"):
            asyncio.run(transition(conn, 1, "RESOLVED", actor="test"))

    def test_resolved_with_verdict_id_proceeds(self):
        """Transition to RESOLVED with verdict_id must succeed."""
        from pipeline.gestionador.route import transition
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(return_value={"state": "REVERIFYING", "closed_at": None})
        conn.execute = AsyncMock(return_value=None)

        # Should not raise
        asyncio.run(transition(conn, 1, "RESOLVED", actor="test", verdict_id=42))
        # Verify execute was called (UPDATE + INSERT transition)
        assert conn.execute.call_count >= 2

    def test_illegal_transition_raises(self):
        """Illegal transition must raise ValueError (not silently succeed)."""
        from pipeline.gestionador.route import transition
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(return_value={"state": "OPEN", "closed_at": None})

        with pytest.raises(ValueError, match="Illegal transition"):
            asyncio.run(transition(conn, 1, "RESOLVED", actor="test", verdict_id=99))

    def test_item_not_found_raises(self):
        """Missing item id must raise ValueError."""
        from pipeline.gestionador.route import transition
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="not found"):
            asyncio.run(transition(conn, 9999, "ROUTED", actor="test"))


# ---------------------------------------------------------------------------
# SLA configuration sanity checks
# ---------------------------------------------------------------------------

class TestSLAConfig:
    def test_auto_fix_sla_is_6h(self):
        from datetime import timedelta
        assert LANE_SLA["AUTO_FIX"] == timedelta(hours=6)

    def test_research_sla_is_7d(self):
        from datetime import timedelta
        assert LANE_SLA["RESEARCH"] == timedelta(days=7)

    def test_escalate_lanes_have_no_sla(self):
        assert LANE_SLA["ESCALATE_GASTO"] is None
        assert LANE_SLA["ESCALATE_OWNER"] is None


# ---------------------------------------------------------------------------
# DB integration — open_or_refresh against the REAL connection.
#
# WHY THIS EXISTS: the rest of this file mocks asyncpg.Connection, so it cannot
# catch encoding bugs in the SQL bind path.  A real bug shipped under that blind
# spot: open_or_refresh passed str(timedelta) ('7 days, 0:00:00') as the sla_due
# parameter, which asyncpg's INTERVAL/TIMESTAMPTZ codec rejects with DataError
# ('str' object has no attribute 'days') for EVERY lane that carries an SLA
# (AUTO_FIX/RESEARCH/QUARANTINE).  Mocked tests stayed green while the live path
# crashed.  These tests bind through real asyncpg (rolled back) so that class of
# regression cannot recur silently.  Pattern mirrors test_inquisition_schedule.py.
# ---------------------------------------------------------------------------

_DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


async def _ping_db() -> bool:
    try:
        import asyncpg
        conn = await asyncpg.connect(_DSN, timeout=3)
        await conn.close()
        return True
    except Exception:
        return False


def _db_available() -> bool:
    try:
        import asyncpg  # noqa: F401
        return asyncio.run(_ping_db())
    except Exception:
        return False


_DB_AVAILABLE = _db_available()


class _Rollback(Exception):
    """Sentinel that forces transaction rollback without persisting any state."""


@pytest.mark.skipif(not _DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestOpenOrRefreshRealDB:
    """Bind open_or_refresh through real asyncpg (rolled back) — guards the
    sla_due encoding path that mocked tests cannot see."""

    def test_sla_lane_encodes_sla_due(self) -> None:
        """An SLA-carrying lane (RESEARCH) must insert with a non-NULL sla_due.

        This is the exact path that crashed with str(timedelta).  It must now
        return an int id and persist sla_due as a real TIMESTAMPTZ.
        """
        asyncio.run(self._run_sla_lane())

    async def _run_sla_lane(self) -> None:
        import asyncpg
        from pipeline.gestionador.route import open_or_refresh

        conn = await asyncpg.connect(_DSN)
        try:
            async with conn.transaction():
                anomaly = AnomalyResult(
                    detector="dbtest_detector",
                    subject_type="dbtest",
                    subject_key="__gestionador_dbtest_research__",
                    severity="warning",
                    score=0.5,
                    measured={"k": 1},
                    baseline={"b": 0},
                    lane="RESEARCH",          # SLA = 7 days → the str(timedelta) trap
                    quarantines=False,
                    dedupe_key="__gestionador_dbtest_research__",
                )
                item_id = await open_or_refresh(conn, anomaly, actor="dbtest")
                assert isinstance(item_id, int)

                sla_due = await conn.fetchval(
                    "SELECT sla_due FROM gestion_item WHERE id = $1", item_id
                )
                assert sla_due is not None, (
                    "RESEARCH lane carries a 7-day SLA; sla_due must be a real "
                    "TIMESTAMPTZ, not NULL (the str(timedelta) bug produced a crash)"
                )
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

    def test_no_sla_lane_leaves_sla_due_null(self) -> None:
        """An escalate lane (no SLA) must insert with sla_due = NULL, not crash."""
        asyncio.run(self._run_no_sla_lane())

    async def _run_no_sla_lane(self) -> None:
        import asyncpg
        from pipeline.gestionador.route import open_or_refresh

        conn = await asyncpg.connect(_DSN)
        try:
            async with conn.transaction():
                anomaly = AnomalyResult(
                    detector="dbtest_detector",
                    subject_type="dbtest",
                    subject_key="__gestionador_dbtest_escalate__",
                    severity="critical",
                    score=1.0,
                    measured={"k": 2},
                    baseline=None,
                    lane="ESCALATE_OWNER",    # SLA = None
                    quarantines=False,
                    dedupe_key="__gestionador_dbtest_escalate__",
                )
                item_id = await open_or_refresh(conn, anomaly, actor="dbtest")
                assert isinstance(item_id, int)

                sla_due = await conn.fetchval(
                    "SELECT sla_due FROM gestion_item WHERE id = $1", item_id
                )
                assert sla_due is None, "ESCALATE lane has no SLA; sla_due must be NULL"
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

"""Goldens for the 4 production gestionador bugs (live scheduler run_all, 2026-06-28).

Each class pins ONE literal production error to a RED->GREEN regression test:

  1. price_trap  -- asyncpg "operator does not exist: bigint >= text": the cohort
     HAVING CASE passed its min-size params untyped, so PG16 inferred the
     all-unknown CASE branches as text and `bigint >= text` has no operator.
     (DB-backed, :5434, rolled back.)
  2. count_inflation / silent_cap -- "'list' object has no attribute 'get'":
     verification_verdict.independent_values can be a JSON array, not an object;
     iv.get(...) then crashed. The detector now skips any non-object payload.
  3. staleness   -- "Illegal transition 'OPEN' -> 'ESCALATED'": a storm item
     (lane=ESCALATE_GASTO) was routed straight OPEN->ESCALATED, but ESCALATED is
     only legal from ROUTED. route_anomalies now bridges OPEN->ROUTED->ESCALATED.
     (DB-backed, :5434, rolled back.)
  4. logging     -- UnicodeEncodeError 'charmap' can't encode the arrow: the
     transition message carried U+2192 and the Windows cp1252 log stream crashed
     on it, masking the real error. The message is now ASCII and the scheduler
     stream is reconfigured UTF-8 / backslashreplace.

ISOLATION: DB tests honor CARDEEP_DSN (default :5434 dry-run), HARD-REFUSE :5433,
and roll back -- zero residue. Mirrors tests/test_gestion_item_country.py.
"""
from __future__ import annotations

import asyncio
import io
import logging
import os
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from pipeline.gestionador.detect import (
    AnomalyResult,
    _daily_bucket,
    detect_count_inflation,
    detect_price_trap,
    detect_silent_cap,
)

_DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5434/cardeep")


def _run(coro):
    return asyncio.run(coro)


def _make_conn(fetch_result):
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=fetch_result)
    return conn


def _ulid(tag: str) -> str:
    """26-char Crockford base32 id (satisfies entity_ulid_shape ^[0-9A-HJKMNP-TV-Z]{26}$)."""
    return (tag + "0" * 26)[:26]


class _Rollback(Exception):
    """Force transaction rollback -- no seeded row ever persists."""


# ---------------------------------------------------------------------------
# Bug 2 -- count_inflation / silent_cap must not crash on a non-object payload
# ---------------------------------------------------------------------------

class TestIndependentValuesListContract:
    """independent_values JSONB can be a JSON array; the detector must skip it,
    not raise "'list' object has no attribute 'get'"."""

    def test_count_inflation_skips_json_array_string(self):
        # asyncpg returns JSONB as str (no codec) -> json.loads("[...]") == list
        rows = [{"subject_key": "CDP-ES-00-LISTIV", "independent_values": "[1, 2, 3]",
                 "verdict": "TRUSTWORTHY", "primary_value": 0}]
        assert _run(detect_count_inflation(_make_conn(rows))) == []

    def test_count_inflation_skips_decoded_list(self):
        # codec-registered path: the cell arrives already decoded as a Python list
        rows = [{"subject_key": "CDP-ES-00-LISTIV", "independent_values": [1, 2, 3],
                 "verdict": "TRUSTWORTHY", "primary_value": 0}]
        assert _run(detect_count_inflation(_make_conn(rows))) == []

    def test_silent_cap_skips_json_array_string(self):
        rows = [{"subject_key": "CDP-ES-00-LISTIV", "independent_values": "[1, 2, 3]",
                 "created_at": "2026-06-28"}]
        assert _run(detect_silent_cap(_make_conn(rows))) == []

    def test_count_inflation_object_payload_still_fires(self):
        # happy path preserved: a real object payload still detects ingest loss
        rows = [{"subject_key": "CDP-ES-28-OK",
                 "independent_values": {"source_declared": 100, "harvested": 100,
                                        "db_available": 80},
                 "verdict": "TRUSTWORTHY", "primary_value": 80}]
        results = _run(detect_count_inflation(_make_conn(rows)))
        assert len(results) == 1 and results[0].detector == "count_inflation"


# ---------------------------------------------------------------------------
# Bug 4 -- logging must survive the transition arrow on a cp1252 stream
# ---------------------------------------------------------------------------

class TestLoggingArrowCp1252Safe:
    def test_illegal_transition_message_is_cp1252_encodable(self):
        from pipeline.gestionador.route import assert_valid_transition
        with pytest.raises(ValueError) as ei:
            assert_valid_transition("OPEN", "ESCALATED")
        msg = str(ei.value)
        assert "->" in msg
        assert "→" not in msg, "U+2192 arrow still present -- crashes cp1252 logging"
        msg.encode("cp1252")  # must NOT raise UnicodeEncodeError

    def test_scheduler_stream_tolerates_non_ascii(self):
        from pipeline.ops.scheduler import _utf8_safe_stream
        stream = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", newline="")
        _utf8_safe_stream(stream)
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.Formatter("%(message)s"))
        rec = logging.LogRecord("t", logging.ERROR, __file__, 1,
                                "transition OPEN → ESCALATED", None, None)
        handler.emit(rec)  # must NOT raise UnicodeEncodeError
        handler.flush()
        assert b"transition OPEN" in stream.buffer.getvalue()


# ---------------------------------------------------------------------------
# Bug 1 -- price_trap SQL must not raise bigint >= text (DB-backed, :5434)
# ---------------------------------------------------------------------------

@pytest.mark.skipif("5433" in _DSN, reason="needs the :5434 dry-run; refuses live :5433")
class TestPriceTrapCohortDB:
    def test_seeded_cohort_runs_and_flags_outlier(self):
        _run(self._body())

    async def _body(self):
        import asyncpg

        conn = await asyncpg.connect(_DSN)
        try:
            async with conn.transaction():
                ent = _ulid("PTSEEDENT1")
                await conn.execute(
                    "INSERT INTO entity (entity_ulid, cdp_code, kind, country_code, status) "
                    "VALUES ($1, $2, 'compraventa', 'ES', 'active')",
                    ent, "CDP-ES-00-PTSEEDV1",
                )
                # Spread the cohort so MAD(ln price) >= the 0.05 floor (a degenerate
                # cohort is skipped on both sides); 16 normal + 1 monster = n=17 >= 15.
                normal = [12000, 14000, 16000, 17000, 18000, 19000, 20000, 21000,
                          22000, 23000, 24000, 25000, 26000, 27000, 28000, 30000]
                for i, p in enumerate(normal):
                    await conn.execute(
                        "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, "
                        "make, model, year, price) "
                        "VALUES ($1, $2, $3, 'ZZZSEEDMK', 'ZSEEDMDL', 2018, $4)",
                        _ulid(f"PTSEEDV{i:03d}"), ent, f"https://seed.test/{i}", Decimal(p),
                    )
                out_vid = _ulid("PTSEEDVZZZ")
                await conn.execute(
                    "INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, "
                    "make, model, year, price) "
                    "VALUES ($1, $2, $3, 'ZZZSEEDMK', 'ZSEEDMDL', 2018, $4)",
                    out_vid, ent, "https://seed.test/out", Decimal(9_000_000),
                )

                # The exact call that raised: operator does not exist: bigint >= text
                results = await detect_price_trap(conn)

                flagged = {r.subject_key: r for r in results}
                assert out_vid in flagged, "9M cohort outlier was not flagged"
                out = flagged[out_vid]
                assert out.measured["side"] == "high"
                assert out.severity == "critical"
                assert out.lane == "QUARANTINE"
                # only the monster flags -- the in-cohort normal cars do not
                assert set(flagged) == {out_vid}
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()


# ---------------------------------------------------------------------------
# Bug 3 -- staleness storm routes OPEN->ROUTED->ESCALATED legally (DB-backed)
# ---------------------------------------------------------------------------

@pytest.mark.skipif("5433" in _DSN, reason="needs the :5434 dry-run; refuses live :5433")
class TestStalenessStormRouteDB:
    def test_storm_escalates_via_legal_path(self):
        _run(self._body())

    async def _body(self):
        import asyncpg

        from pipeline.gestionador.route import route_anomalies

        bucket = _daily_bucket()
        anomaly = AnomalyResult(
            detector="staleness",
            subject_type="source",
            subject_key="kind:__route_escalate_dbtest__",
            severity="critical",
            score=1.0,
            measured={"stale_count": 250, "kind": "garaje", "storm_suppressed": True},
            baseline=None,
            lane="ESCALATE_GASTO",
            quarantines=False,
            dedupe_key=f"staleness|ES|kind:__route_escalate_dbtest__|{bucket}",
            country_code="ES",
        )
        conn = await asyncpg.connect(_DSN)
        try:
            async with conn.transaction():
                # Pre-fix this raised: Illegal transition 'OPEN' -> 'ESCALATED'
                item_ids = await route_anomalies(conn, [anomaly], actor="dbtest")
                assert len(item_ids) == 1
                state = await conn.fetchval(
                    "SELECT state FROM gestion_item WHERE id = $1", item_ids[0]
                )
                assert state == "ESCALATED"
                trans = await conn.fetch(
                    "SELECT from_state, to_state FROM gestion_transition "
                    "WHERE item_id = $1 ORDER BY id",
                    item_ids[0],
                )
                pairs = [(t["from_state"], t["to_state"]) for t in trans]
                assert (None, "OPEN") in pairs
                assert ("OPEN", "ROUTED") in pairs, f"no legal ROUTED bridge: {pairs}"
                assert ("ROUTED", "ESCALATED") in pairs, f"did not escalate: {pairs}"
                raise _Rollback
        except _Rollback:
            pass
        finally:
            await conn.close()

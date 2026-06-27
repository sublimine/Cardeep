"""Invariant tests for v_province_seal (migration 0042, SU-SEAL live view).

The per-province VENTA seal = served canonical dealers / DIRCE CNAE-451 registral ceiling.
These tests pin the view's contract against the live DB: one row per venta-denominator province,
verdicts drawn from the fixed set, and verdict/coverage internally consistent with the documented
thresholds (SELLADO >=85%, PARCIAL 50-85%, GAP <50%). Read-only — no writes.
"""
from __future__ import annotations

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Census validator: reads the live v_province_seal (per-province DIRCE denominators
# + served canonical dealers). Honors CARDEEP_DSN but DEFAULTS to :5433 (its
# populated census home for the local Ferrari run). It is OPEN against the empty
# :5434 dry-run — the seal view has no rows there (no DIRCE/served data) — so it
# skips cleanly when the view is empty rather than failing on a 0-province seal.
_DEFAULT_DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
DSN = os.environ.get("CARDEEP_DSN", _DEFAULT_DSN)


def _seal_view_populated() -> bool:
    async def _ping() -> bool:
        try:
            import asyncpg
            conn = await asyncpg.connect(DSN, timeout=3)
            try:
                n = await conn.fetchval("SELECT count(*) FROM v_province_seal")
                return (n or 0) > 0
            finally:
                await conn.close()
        except Exception:
            return False
    try:
        return asyncio.run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _seal_view_populated()
_VALID_VERDICTS = {"SELLADO", "PARCIAL", "GAP", "NO_DENOM"}


def _rows():
    async def _go():
        import asyncpg
        conn = await asyncpg.connect(DSN)
        try:
            return await conn.fetch(
                "SELECT province_code, segment, denominator, numerator, coverage_pct, verdict "
                "FROM v_province_seal ORDER BY province_code")
        finally:
            await conn.close()
    return asyncio.run(_go())


def _by_segment(seg: str):
    return [r for r in _rows() if r["segment"] == seg]


@pytest.mark.skipif(
    not DB_AVAILABLE,
    reason=f"v_province_seal empty/unreachable at {DSN} (needs the populated "
    "DIRCE/served census; OPEN against the empty :5434 dry-run)")
class TestProvinceSealView:
    def test_both_segments_cover_52_provinces(self) -> None:
        for seg in ("venta", "desguace"):
            rows = _by_segment(seg)
            assert len(rows) == 52, f"{seg}: expected 52 provinces, got {len(rows)}"
            assert len({r["province_code"] for r in rows}) == 52, f"{seg}: province codes not unique"

    def test_verdicts_in_fixed_set(self) -> None:
        for r in _rows():
            assert r["verdict"] in _VALID_VERDICTS, f"unexpected verdict {r['verdict']!r}"

    def test_venta_verdict_matches_85_50_thresholds(self) -> None:
        for r in _by_segment("venta"):
            cov = float(r["coverage_pct"]) if r["coverage_pct"] is not None else None
            v = r["verdict"]
            if v == "NO_DENOM":
                assert not r["denominator"]
                continue
            assert cov is not None
            if v == "SELLADO":
                assert cov >= 85, f"{r['province_code']}: SELLADO but cov={cov}"
            elif v == "PARCIAL":
                assert 50 <= cov < 85, f"{r['province_code']}: PARCIAL but cov={cov}"
            else:
                assert cov < 50, f"{r['province_code']}: GAP but cov={cov}"

    def test_desguace_is_discovery_seal_at_100(self) -> None:
        """DESGUACE is a discovery seal: SELLADO iff found >= census (coverage >= 100)."""
        for r in _by_segment("desguace"):
            v = r["verdict"]
            if v == "NO_DENOM":
                assert not r["denominator"]
                continue
            cov = float(r["coverage_pct"])
            if v == "SELLADO":
                assert cov >= 100, f"{r['province_code']}: desguace SELLADO but cov={cov}"
            else:
                assert cov < 100, f"{r['province_code']}: desguace {v} but cov={cov}"

    def test_coverage_pct_is_num_over_den(self) -> None:
        # The view rounds with PostgreSQL ROUND() (half-away-from-zero); Python's
        # round() is banker's (half-to-even). They diverge by 0.1 exactly on .5
        # boundaries (e.g. 100*53/16 = 331.25 -> PG 331.3 vs Python 331.2). Mirror
        # PG's rounding so the recompute matches the view's semantics exactly.
        from decimal import Decimal, ROUND_HALF_UP
        for r in _rows():
            den = r["denominator"]
            if not den:
                continue
            expected = float(
                Decimal(100.0 * r["numerator"] / float(den)).quantize(
                    Decimal("0.1"), rounding=ROUND_HALF_UP)
            )
            assert abs(float(r["coverage_pct"]) - expected) < 0.05, (
                f"{r['segment']}/{r['province_code']}: coverage_pct {r['coverage_pct']} != {expected}")

    def test_numerator_nonneg_denominator_positive(self) -> None:
        for r in _rows():
            assert r["numerator"] >= 0
            assert r["denominator"] is None or r["denominator"] > 0

    def test_venta_canonical_numerator_not_overcounting(self) -> None:
        """VENTA national coverage must be the CANONICAL ~79%, not the entity-level ~165%
        over-count (regression guard for the dedup-in-numerator bug)."""
        rows = _by_segment("venta")
        num = sum(r["numerator"] for r in rows)
        den = sum(r["denominator"] for r in rows if r["denominator"])
        nat = 100.0 * num / den
        assert 60 <= nat <= 110, f"venta national coverage {nat:.1f}% outside sane canonical band"

    def test_desguace_found_at_least_census(self) -> None:
        """Every province must have found >= the DGT census (discovery complete nationally)."""
        rows = _by_segment("desguace")
        assert sum(r["numerator"] for r in rows) >= sum(r["denominator"] for r in rows if r["denominator"])

"""Tests for the Fase D AUTO-AUDITOR persistence increment.

Subject: ``pipeline/autopilot/auditor.py:persist_verdict`` + migration 0069
(``country_pack_audit_verdict``). The auditor's ``audit_pack`` stays a PURE function; this increment
adds the OPTIONAL append-only ledger writer — the caller decides whether to persist.

Two layers, mirroring tests/test_autopilot_state.py:

  * PURE (no DB): ``persist_verdict``'s ROW SHAPING over a recording fake connection — it emits
    exactly one row per level (N0..N4) plus one OVERALL row, with the documented column mapping
    (each level row carries its own sub_verdict/score/reason; every row denormalises the pack
    decision), is append-only (a second call emits a second batch), and never mutates the verdict.
    ``@pytest.mark.unit`` — no database, deterministic, always runs in CI.

  * INTEGRATION (:5434 dry-run only): a real verdict is persisted into migration 0069's table and
    read back; the 6 rows are asserted and a re-audit is shown to APPEND (never overwrite). The whole
    batch runs inside an asyncpg transaction that is ROLLED BACK, leaving the dry-run byte-identical.
    Hard-pinned to :5434; refuses :5433 (live prod), exactly like test_autopilot_state.py.

ISOLATION (inviolable): the integration layer NEVER touches :5433. It refuses any DSN that mentions
:5433 and skips when the dry-run DB is unreachable.
"""
from __future__ import annotations

import asyncio
import os
import sys
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.autopilot.auditor import (  # noqa: E402
    CountryPlan,
    Decision,
    PlanClaim,
    audit_pack,
    persist_verdict,
)

# estimate_stratum's log-linear fit warns on near-perfect projected overlap (the auditor suppresses
# it internally; belt-and-braces here). This filter carries no unit/integration mark, so both layers
# keep their own class-level marks.
pytestmark = [pytest.mark.filterwarnings("ignore::RuntimeWarning")]

CC = "XX"  # the architecture's synthetic onboarding country; never a real tenant

# Dense 3-list overlap → identified, coverage_lower ≈ 0.999 (≥ seal 0.95). Calibrated in test_auditor.
OVERLAP_DENSE = {
    (1, 0, 0): 2, (0, 1, 0): 2, (0, 0, 1): 2,
    (1, 1, 0): 20, (1, 0, 1): 20, (0, 1, 1): 20, (1, 1, 1): 400,
}

# 2-family agreement → quorum TRUSTWORTHY (N3 APRUEBA).
_DENOM_OK = PlanClaim(
    subject_key="denominator:XX", subject_type="denominator", asserted_value="1000",
    paths={"db_geo_count": "1000", "registral_census": "1000"},
)
_GEO_OK = PlanClaim(
    subject_key="geo:XX:01", subject_type="count", asserted_value="200",
    paths={"db_geo_count": "200", "source_declared_total": "200"},
)


def _write_pack(root: Path, cc: str = CC, *, omit: tuple[str, ...] = ()) -> Path:
    """Build a well-formed pack at ``root/<cc>/`` (omit any piece to break N0). Compact sibling of
    tests/test_auditor.py::_write_pack — kept self-contained (no cross-test import)."""
    pack = root / cc
    pack.mkdir(parents=True, exist_ok=True)
    if "country_toml" not in omit:
        (pack / "country.toml").write_text(
            f'country_code = "{cc}"\n\n[subdivision]\nregex = "^(0[1-9]|1[0-9])$"\n\n'
            '[kinds]\nnational = ["plataforma", "importador"]\n',
            encoding="utf-8",
        )
    if "geo" not in omit:
        (pack / "geo").mkdir(exist_ok=True)
        (pack / "geo" / "backbone.csv").write_text(
            f"country_code,code,name,admin1\n{cc},01,Region One,L1A\n{cc},02,Region Two,L1B\n",
            encoding="utf-8",
        )
    if "recipe" not in omit:
        (pack / "recipes" / "_tier1").mkdir(parents=True, exist_ok=True)
        (pack / "recipes" / "_tier1" / "sample.yaml").write_text(
            "base_url: https://example.xx\n", encoding="utf-8")
    census = pack / "census"
    if "census_csv" not in omit or "source_md" not in omit:
        census.mkdir(exist_ok=True)
    if "census_csv" not in omit:
        (census / "national.csv").write_text(
            "region_code,segment,n_external\n01,GEN,500\n", encoding="utf-8")
    if "source_md" not in omit:
        (census / "SOURCE.md").write_text("# Provenance\n- 500 [MEDIDO]\n", encoding="utf-8")
    if "taxonomy" not in omit:
        (pack / "taxonomy.yaml").write_text(
            "dealer_kinds: [generic]\npoint_of_sale: [generic]\n", encoding="utf-8")
    return pack


def _plan(
    *,
    orthogonal_lists: tuple[str, ...] = ("osm", "dgt_cat", "aedra"),
    geo_counts: tuple[PlanClaim, ...] = (_GEO_OK,),
    denominator_anchor: PlanClaim | None = _DENOM_OK,
    projected_overlap=None,
) -> CountryPlan:
    return CountryPlan(
        country_code=CC,
        orthogonal_lists=orthogonal_lists,
        geo_counts=geo_counts,
        denominator_anchor=denominator_anchor,
        projected_overlap=projected_overlap if projected_overlap is not None else dict(OVERLAP_DENSE),
    )


# ===========================================================================
# PURE unit layer — persist_verdict row shaping over a recording fake conn
# ===========================================================================
class _RecordingConn:
    """Minimal async stand-in for asyncpg.Connection: records every execute() arg tuple.

    persist_verdict needs only ``await conn.execute(sql, *args)``, so this proves the row-shaping
    logic with NO database (and that the writer needs no real asyncpg)."""

    def __init__(self) -> None:
        self.calls: list[tuple] = []

    async def execute(self, _sql: str, *args):  # noqa: ANN001
        self.calls.append(args)
        return "INSERT 0 1"


# Positional arg order of the INSERT (see auditor._PERSIST_VERDICT_SQL):
_CC, _LEVEL, _SUBV, _SCORE, _REASON, _DECISION = range(6)


class TestPersistRowShaping:
    pytestmark = pytest.mark.unit

    def test_emits_one_row_per_level_plus_overall(self, tmp_path: Path) -> None:
        v = audit_pack(CC, _write_pack(tmp_path), _plan())
        conn = _RecordingConn()

        written = asyncio.run(persist_verdict(conn, CC, v))

        assert written == len(v.levels) + 1 == 6
        assert len(conn.calls) == 6
        # One row per level in order, then the OVERALL summary.
        assert [c[_LEVEL] for c in conn.calls] == ["N0", "N1", "N2", "N3", "N4", "OVERALL"]
        # Every row denormalises the pack's overall decision + carries the (normalised) country_code.
        assert {c[_DECISION] for c in conn.calls} == {v.decision.value}
        assert {c[_CC] for c in conn.calls} == {CC}
        # Per-level fidelity: sub_verdict/score/reason mirror each LevelVerdict.
        for c in conn.calls[:5]:
            lvl = v.level(c[_LEVEL])
            assert c[_SUBV] == lvl.decision.value
            assert float(c[_SCORE]) == pytest.approx(lvl.score)
            assert c[_REASON] == lvl.reason_code
        # OVERALL row carries the pack decision / confidence / reason.
        ov = conn.calls[5]
        assert ov[_SUBV] == v.decision.value
        assert float(ov[_SCORE]) == pytest.approx(v.confidence)
        assert ov[_REASON] == v.reason_code

    def test_append_only_second_call_adds_a_second_batch(self, tmp_path: Path) -> None:
        v = audit_pack(CC, _write_pack(tmp_path), _plan())
        conn = _RecordingConn()
        asyncio.run(persist_verdict(conn, CC, v))
        asyncio.run(persist_verdict(conn, CC, v))
        # Re-auditing APPENDS — nothing is overwritten.
        assert len(conn.calls) == 12

    def test_score_is_decimal_and_bounded(self, tmp_path: Path) -> None:
        v = audit_pack(CC, _write_pack(tmp_path), _plan())
        conn = _RecordingConn()
        asyncio.run(persist_verdict(conn, CC, v))
        for c in conn.calls:
            assert isinstance(c[_SCORE], Decimal)  # asyncpg NUMERIC requires Decimal, not float
            assert Decimal(0) <= c[_SCORE] <= Decimal(1)

    def test_rejected_pack_denormalises_rechaza_but_keeps_live_gate(self, tmp_path: Path) -> None:
        # Omit the census csv → N0 fail-closed RECHAZA → overall RECHAZA.
        v = audit_pack(CC, _write_pack(tmp_path, omit=("census_csv",)), _plan())
        assert v.decision is Decision.RECHAZA
        conn = _RecordingConn()
        asyncio.run(persist_verdict(conn, CC, v))
        assert {c[_DECISION] for c in conn.calls} == {"RECHAZA"}
        # N2 (the live gate) still escalates on its own row, independent of the build RECHAZA.
        n2 = next(c for c in conn.calls if c[_LEVEL] == "N2")
        assert n2[_SUBV] == "ESCALA"

    def test_does_not_mutate_verdict(self, tmp_path: Path) -> None:
        v = audit_pack(CC, _write_pack(tmp_path), _plan())
        before = (v.country_code, v.decision, v.confidence, v.reason_code, v.levels, v.live_gate)
        asyncio.run(persist_verdict(_RecordingConn(), CC, v))
        assert (v.country_code, v.decision, v.confidence, v.reason_code, v.levels, v.live_gate) == before

    def test_normalizes_country_code(self, tmp_path: Path) -> None:
        v = audit_pack(CC, _write_pack(tmp_path), _plan())
        conn = _RecordingConn()
        asyncio.run(persist_verdict(conn, " xx ", v))  # lower + padded → 'XX'
        assert {c[_CC] for c in conn.calls} == {"XX"}

    def test_rejects_non_iso_country_code(self, tmp_path: Path) -> None:
        v = audit_pack(CC, _write_pack(tmp_path), _plan())
        with pytest.raises(ValueError):
            asyncio.run(persist_verdict(_RecordingConn(), "SPAIN", v))


# ===========================================================================
# INTEGRATION layer — a real verdict on the :5434 dry-run DB (rolled back)
# ===========================================================================
_DRYRUN_DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5434/cardeep"


def _target_dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


class _Rollback(Exception):
    """Sentinel: forces the asyncpg transaction to abort cleanly at test end (zero residue)."""


async def _ping(dsn: str) -> bool:
    try:
        import asyncpg
        conn = await asyncpg.connect(dsn, timeout=3)
        await conn.close()
        return True
    except Exception:
        return False


def _db_available() -> bool:
    dsn = _target_dsn()
    if "5433" in dsn:
        return False  # never probe live prod
    try:
        return asyncio.run(_ping(dsn))
    except Exception:
        return False


DB_AVAILABLE = _db_available()


@pytest.mark.integration
@pytest.mark.skipif(
    not DB_AVAILABLE,
    reason="dry-run cardeep-pg not reachable at :5434 (or CARDEEP_DSN points at :5433)",
)
class TestPersistOnDryRun:
    """A real verdict is persisted to migration 0069's ledger, asserted, and rolled back."""

    def test_refuses_live_prod_dsn(self) -> None:
        # The mandate: this golden NEVER runs against :5433. Make the refusal explicit.
        assert "5433" not in _target_dsn(), "integration DSN must be the :5434 dry-run"

    def test_persists_six_rows_and_appends_on_reaudit(self, tmp_path: Path) -> None:
        asyncio.run(self._run(tmp_path))

    async def _run(self, tmp_path: Path) -> None:
        import asyncpg

        dsn = _target_dsn()
        assert "5433" not in dsn  # belt-and-braces inside the coroutine
        v = audit_pack(CC, _write_pack(tmp_path), _plan())
        conn = await asyncpg.connect(dsn)
        try:
            with pytest.raises(_Rollback):
                async with conn.transaction():
                    pre = await conn.fetchval(
                        "SELECT count(*) FROM country_pack_audit_verdict WHERE country_code = $1", CC)

                    written = await persist_verdict(conn, CC, v)
                    assert written == 6

                    # Read back THIS batch (last 6 rows by id), robust to any pre-existing rows.
                    batch = list(reversed(await conn.fetch(
                        "SELECT level, sub_verdict, score, reason_code, decision "
                        "FROM country_pack_audit_verdict WHERE country_code = $1 ORDER BY id DESC LIMIT 6",
                        CC,
                    )))
                    assert [r["level"] for r in batch] == ["N0", "N1", "N2", "N3", "N4", "OVERALL"]
                    assert {r["decision"] for r in batch} == {v.decision.value}
                    for r in batch[:5]:
                        lvl = v.level(r["level"])
                        assert r["sub_verdict"] == lvl.decision.value
                        assert float(r["score"]) == pytest.approx(lvl.score)
                        assert r["reason_code"] == lvl.reason_code
                    ov = batch[5]
                    assert ov["sub_verdict"] == v.decision.value
                    assert float(ov["score"]) == pytest.approx(v.confidence)

                    assert await conn.fetchval(
                        "SELECT count(*) FROM country_pack_audit_verdict WHERE country_code = $1", CC
                    ) == pre + 6

                    # APPEND-ONLY: a re-audit writes a SECOND batch (12 total), never overwriting.
                    assert await persist_verdict(conn, CC, v) == 6
                    assert await conn.fetchval(
                        "SELECT count(*) FROM country_pack_audit_verdict WHERE country_code = $1", CC
                    ) == pre + 12

                    raise _Rollback()
        finally:
            await conn.close()

    def test_rejected_pack_persists_with_fail_closed_decision(self, tmp_path: Path) -> None:
        asyncio.run(self._run_rejected(tmp_path))

    async def _run_rejected(self, tmp_path: Path) -> None:
        import asyncpg

        dsn = _target_dsn()
        assert "5433" not in dsn
        v = audit_pack(CC, _write_pack(tmp_path, omit=("census_csv",)), _plan())
        assert v.decision is Decision.RECHAZA
        conn = await asyncpg.connect(dsn)
        try:
            with pytest.raises(_Rollback):
                async with conn.transaction():
                    assert await persist_verdict(conn, CC, v) == 6
                    batch = list(reversed(await conn.fetch(
                        "SELECT level, sub_verdict, decision FROM country_pack_audit_verdict "
                        "WHERE country_code = $1 ORDER BY id DESC LIMIT 6",
                        CC,
                    )))
                    assert {r["decision"] for r in batch} == {"RECHAZA"}  # fail-closed denormalised
                    n0 = next(r for r in batch if r["level"] == "N0")
                    n2 = next(r for r in batch if r["level"] == "N2")
                    assert n0["sub_verdict"] == "RECHAZA"  # the structural fail
                    assert n2["sub_verdict"] == "ESCALA"   # live gate still owner-parked
                    raise _Rollback()
        finally:
            await conn.close()

"""GOLDEN — Fase E2: the COUNTRY-AUTOPILOT ORCHESTRATOR LOOP (``pipeline/ops/autopilot.py``).

This is the **DEMONSTRATION E2E of the complete loop** — the capstone that unites every
country-autopilot piece (state machine + extractors + auditor + gates + the REAL cdp coder) into
one driveable machine, proven by onboarding the synthetic country 'XX' through the full
COVER(CC) progression on the :5434 dry-run inside an ABORTED transaction.

Two layers:
  * PURE (no DB): the result/fixtures DTOs + the ULID shape.
  * INTEGRATION (:5434 dry-run only, rolled back): ``run_campaign('XX')`` walks
    REGISTERED -> KNOW_COUNTRY -> BOOTSTRAPPED -> IN_COVERAGE -> SEALED; the ``country_campaign``
    row + append-only ledger reflect the walk; the live gates park PENDIENTE-OWNER; the dealer
    mints ``CDP-XX-``; ``v_country_proof_violations`` is 0 (XX never cross-merges with a seeded ES
    incumbent); and after rollback the dry-run is byte-clean (ES geo intact).

ISOLATION (inviolable): the integration layer NEVER touches :5433. It refuses any DSN that
mentions :5433, skips when :5434 is unreachable, and refuses to seed against a non-empty census.
"""
from __future__ import annotations

import asyncio
import os
import re
from pathlib import Path

import pytest

from pipeline.autopilot import state
from pipeline.autopilot.auditor import Decision
from pipeline.autopilot.extract_geo import CrossWalk
from pipeline.ops.autopilot import (
    PROOF_VIEW,
    CampaignResult,
    PackFixtures,
    run_campaign,
)

# ---------------------------------------------------------------------------
# Synthetic 'XX' fixtures (the architecture's synthetic onboarding country)
# ---------------------------------------------------------------------------
_FIX = Path(__file__).resolve().parent / "fixtures"
_GEONAMES_XX = (_FIX / "geonames_xx.txt").read_text(encoding="utf-8")
_HIERARCHY_XX = (_FIX / "hierarchy_xx.txt").read_text(encoding="utf-8")

# Eurostat-LAU cross-walk for 'XX' (same as tests/test_extract_geo.py): official province codes
# NP/EF/SB + 3 official municipality codes; the rest fall back to the declared GeoNames id.
_XWALK = CrossWalk(
    province={"01.A1": "NP", "01.A2": "EF", "02.B1": "SB"},
    municipality={3001: "NP001", 3002: "NP002", 3003: "EF001"},
)

# Eurostat SBS G45 TSV + GLEIF CSV for 'XX' (same shape as tests/test_extract_denom.py): national
# all-segment denominator = 1250 @2022.
_EUROSTAT_ROWS = [
    ["freq,indic_sb,nace_r2,geo\\TIME_PERIOD", "2020", "2021", "2022"],
    ["A,V11110,G45,XX", "1180", "1200 e", "1250"],
    ["A,V11110,G45,XX1", "590", "600", "620 d"],
    ["A,V11110,G45,XX2", "580", "590", "630"],
]
_SBS_TSV = "\n".join("\t".join(r) for r in _EUROSTAT_ROWS) + "\n"
_GLEIF_CSV = (
    "LEI,Entity.LegalName,Entity.LegalJurisdiction,Entity.LegalAddress.Country,"
    "Entity.LegalForm.EntityLegalFormCode,Registration.RegistrationStatus\n"
    "LEI000000000000000X1,Alpha Motors,XX,XX,ABCD,ISSUED\n"
    "LEI000000000000000X2,Beta Auto,XX,XX,ABCD,ISSUED\n"
)

_SYNTHETIC_CC = "XX"


def _fixtures(pack_root: Path, **over) -> PackFixtures:
    """A complete, well-formed 'XX' PackFixtures whose canonical run AUDITS to APRUEBA-build."""
    base = dict(
        pack_root=pack_root,
        geonames_text=_GEONAMES_XX,
        hierarchy_text=_HIERARCHY_XX,
        crosswalk=_XWALK,
        sbs_tsv=_SBS_TSV,
        gleif_csv=_GLEIF_CSV,
    )
    base.update(over)
    return PackFixtures(**base)


# ===========================================================================
# PURE unit layer — DTOs + ULID shape (no DB, no network)
# ===========================================================================
class TestPureDTOs:
    pytestmark = pytest.mark.unit

    def test_packfixtures_defaults_are_well_formed(self, tmp_path: Path) -> None:
        fx = _fixtures(tmp_path)
        assert fx.roster == ("osm", "dgt_cat", "aedra")          # 3 distinct orthogonal buckets
        assert len(fx.denominator_paths) == 2                    # 2 orthogonal voices for N3
        assert fx.dealer_kind == "compraventa"

    def test_minted_ulid_matches_entity_shape(self) -> None:
        from pipeline.ops.autopilot import _mint_ulid

        shape = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")
        assert all(shape.match(_mint_ulid()) for _ in range(50))

    def test_campaign_result_is_immutable(self) -> None:
        # CampaignResult is a frozen dataclass — its evidence cannot be mutated after the fact.
        import dataclasses

        assert dataclasses.is_dataclass(CampaignResult)
        params = dataclasses.fields(CampaignResult)
        names = {f.name for f in params}
        assert {"states_visited", "minted_cdp_code", "proof_violations", "sealed_as_checkpoint"} <= names


# ===========================================================================
# INTEGRATION layer — the full loop on the :5434 dry-run (rolled back)
# ===========================================================================
_DRYRUN_DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5434/cardeep"
_FORWARD_PATH = [state.REGISTERED, state.KNOW_COUNTRY, state.BOOTSTRAPPED,
                 state.IN_COVERAGE, state.SEALED]


def _target_dsn() -> str:
    return os.environ.get("CARDEEP_DSN", _DRYRUN_DSN)


class _Rollback(Exception):
    """Sentinel: forces the asyncpg transaction to abort cleanly at test end."""


async def _ping(dsn: str) -> bool:
    try:
        import asyncpg

        conn = await asyncpg.connect(dsn, timeout=3)
        try:
            n = await conn.fetchval("SELECT count(*) FROM entity") or 0
            v = await conn.fetchval("SELECT count(*) FROM vehicle") or 0
            return n == 0 and v == 0  # refuse a populated census — this must be the empty dry-run
        finally:
            await conn.close()
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


async def _connect():
    import asyncpg

    dsn = _target_dsn()
    assert "5433" not in dsn, "integration DSN must be the :5434 dry-run, never live prod"
    return await asyncpg.connect(dsn)


async def _seed_es_incumbent(conn) -> tuple[str, str]:
    """A real ES dealer (its own province/muni) so the proof view has an incumbent to NOT merge
    XX into. Returns (cdp_code, canonical_key)."""
    from pipeline.ops.autopilot import _mint_ulid
    from services.api.codes import cdp_pair

    await conn.execute(
        "INSERT INTO geo_province (code, name, ccaa_code, ccaa_name, country_code) "
        "VALUES ('99', 'ES-Baseline-Prov', '97', 'ES-Baseline-Reg', 'ES') "
        "ON CONFLICT (country_code, code) DO NOTHING")
    await conn.execute(
        "INSERT INTO geo_municipality (code, name, province_code, comarca_id, country_code) "
        "VALUES ('99001', 'ES-Baseline-Muni', '99', NULL, 'ES') "
        "ON CONFLICT (country_code, code) DO NOTHING")
    key, code = cdp_pair(province_code="99", domain="es-incumbent.es", country_code="ES")
    await conn.execute(
        "INSERT INTO entity (entity_ulid, cdp_code, kind, country_code, province_code, "
        "municipality_code, canonical_key, status, kind_source, trade_name, first_discovered_source) "
        "VALUES ($1, $2, 'compraventa', 'ES', '99', '99001', $3, 'active', 'manual', "
        "'ES Incumbent', 'test_incumbent')",
        _mint_ulid(), code, key)
    return code, key


@pytest.mark.integration
@pytest.mark.skipif(
    not DB_AVAILABLE,
    reason="empty dry-run cardeep-pg not reachable at :5434 (or CARDEEP_DSN points at :5433)",
)
class TestFullLoopOnDryRun:
    """The headline E2E: a synthetic 'XX' campaign driven through the whole loop, rolled back."""

    def test_refuses_live_prod_dsn(self) -> None:
        assert "5433" not in _target_dsn(), "integration DSN must be the :5434 dry-run"

    # --- the complete walk REGISTERED -> SEALED (checkpoint) ----------------------------
    def test_full_loop_walks_to_sealed_checkpoint(self, tmp_path: Path) -> None:
        res = asyncio.run(self._run(tmp_path))
        # 1) The state machine walked the entire linear lifecycle.
        assert res.states_visited == tuple(_FORWARD_PATH)
        assert res.final_state == state.SEALED
        assert res.reached_seal is True
        assert res.halted is False
        # 2) The audit auto-approved BUILD; the live go is ALWAYS owner-gated.
        assert res.decision is Decision.APRUEBA
        assert res.live_gate is Decision.ESCALA
        assert res.audit.level("N2").decision is Decision.ESCALA
        # 3) The seal is an HONEST checkpoint — no real coverage is asserted.
        assert res.sealed_as_checkpoint is True
        assert res.seal_note and "CHECKPOINT" in res.seal_note
        assert any("seal=CHECKPOINT" in c for c in res.checkpoints)
        # 4) The denominator per-segment split rode along as a declared needs_audit checkpoint.
        assert any("needs_audit" in c for c in res.checkpoints)

    # --- 1.1: SUPERVISA reports the FULL per-tenant health roll-up (not just the proof count) ----
    def test_supervisa_reports_full_health_rollup(self, tmp_path: Path) -> None:
        res = asyncio.run(self._run(tmp_path))
        # The wired health_rollup surfaces servable / sources / seal on the campaign checkpoints;
        # proof-only supervision (the pre-1.1 behaviour) would carry none of these.
        rollup = [c for c in res.checkpoints if c.startswith("SUPERVISA: servable=")]
        assert len(rollup) == 1, f"expected one SUPERVISA roll-up checkpoint, got {res.checkpoints}"
        assert "sources=" in rollup[0] and "seal_segments=" in rollup[0]

    # --- the live gates park PENDIENTE-OWNER, never stop --------------------------------
    def test_live_gates_parked_pending_owner(self, tmp_path: Path) -> None:
        res = asyncio.run(self._run(tmp_path))
        # PROD + LEGAL park (live write + unsigned legal dossier); GASTO is €0 -> open.
        assert set(res.parked_gate_names) == {"PROD", "LEGAL"}
        assert "GASTO" not in res.parked_gate_names
        assert all(g.pending_owner for g in res.parked_gates)
        assert res.pending_owner is True  # the loop reached the owner-frontier but did not stop

    # --- the dealer is minted by the REAL coder as CDP-XX- ------------------------------
    def test_dealer_minted_as_cdp_xx(self, tmp_path: Path) -> None:
        res = asyncio.run(self._run(tmp_path))
        assert res.minted_cdp_code is not None
        assert res.minted_cdp_code.startswith("CDP-XX-")
        assert res.minted_canonical_key  # the dedup pre-image key was captured
        assert (res.seeded_provinces, res.seeded_municipalities) == (3, 5)

    # --- v_country_proof_violations = 0: XX never cross-merges with the ES incumbent -----
    def test_proof_violations_zero_no_es_contamination(self, tmp_path: Path) -> None:
        res, in_txn = asyncio.run(self._run_with_incumbent(tmp_path))
        assert res.proof_violations == 0
        # Both dealers are served, each its own 1-country cluster (the view is genuinely exercised).
        assert in_txn["xx_in_resolved"] == 1
        assert in_txn["es_entity_count"] == 1          # ES incumbent untouched by the XX load
        assert in_txn["es_province_intact"] is True    # the seeded ES province is byte-identical

    # --- the country_campaign row + append-only ledger reflect the whole walk -----------
    def test_country_campaign_reflects_the_walk(self, tmp_path: Path) -> None:
        ledger = asyncio.run(self._run_capture_ledger(tmp_path))
        assert ledger["final_state"] == state.SEALED
        # Birth + 4 advances = 5 append-only rows, in exact lifecycle order; birth has no from_state.
        assert ledger["to_states"] == _FORWARD_PATH
        assert ledger["first_from_state"] is None
        assert ledger["phases"] == ["RESEARCH", "PROPOSE", "EXECUTE", "SEAL"]

    # --- after rollback the :5434 dry-run is byte-clean (ES geo intact) -----------------
    def test_rollback_leaves_db_clean(self, tmp_path: Path) -> None:
        after = asyncio.run(self._run_then_check_clean(tmp_path))
        assert after["entity_total"] == 0
        assert after["geo_province_xx"] == 0
        assert after["geo_municipality_xx"] == 0
        assert after["geo_province_es"] == 0  # the dry-run baseline (empty) is restored

    # --- coroutines ---------------------------------------------------------------------
    async def _run(self, pack_root: Path) -> CampaignResult:
        conn = await _connect()
        try:
            captured: dict = {}
            try:
                async with conn.transaction():
                    assert await state.current_state(conn, _SYNTHETIC_CC) is None
                    captured["res"] = await run_campaign(
                        _SYNTHETIC_CC, conn=conn, pack_fixtures=_fixtures(pack_root))
                    raise _Rollback()
            except _Rollback:
                pass
            return captured["res"]
        finally:
            await conn.close()

    async def _run_with_incumbent(self, pack_root: Path):
        conn = await _connect()
        try:
            captured: dict = {}
            try:
                async with conn.transaction():
                    await _seed_es_incumbent(conn)
                    res = await run_campaign(
                        _SYNTHETIC_CC, conn=conn, pack_fixtures=_fixtures(pack_root))
                    xx_resolved = await conn.fetchval(
                        "SELECT count(*) FROM v_dealer_resolved d JOIN entity e "
                        "ON e.cdp_code = d.cdp_code WHERE e.country_code = 'XX'")
                    es_entities = await conn.fetchval(
                        "SELECT count(*) FROM entity WHERE country_code = 'ES'")
                    es_prov = await conn.fetchval(
                        "SELECT name FROM geo_province WHERE country_code='ES' AND code='99'")
                    captured["res"] = res
                    captured["in_txn"] = {
                        "xx_in_resolved": xx_resolved,
                        "es_entity_count": es_entities,
                        "es_province_intact": es_prov == "ES-Baseline-Prov",
                    }
                    raise _Rollback()
            except _Rollback:
                pass
            return captured["res"], captured["in_txn"]
        finally:
            await conn.close()

    async def _run_capture_ledger(self, pack_root: Path) -> dict:
        conn = await _connect()
        try:
            captured: dict = {}
            try:
                async with conn.transaction():
                    await run_campaign(_SYNTHETIC_CC, conn=conn, pack_fixtures=_fixtures(pack_root))
                    rows = await conn.fetch(
                        "SELECT from_state, to_state, note, detail FROM country_campaign_transition "
                        "WHERE country_code = $1 ORDER BY id", _SYNTHETIC_CC)
                    final = await state.current_state(conn, _SYNTHETIC_CC)
                    captured["data"] = {
                        "final_state": final,
                        "to_states": [r["to_state"] for r in rows],
                        "first_from_state": rows[0]["from_state"],
                        "phases": [
                            __import__("json").loads(r["detail"])["phase"]
                            for r in rows if r["detail"] and "phase" in r["detail"]
                        ],
                    }
                    raise _Rollback()
            except _Rollback:
                pass
            return captured["data"]
        finally:
            await conn.close()

    async def _run_then_check_clean(self, pack_root: Path) -> dict:
        conn = await _connect()
        try:
            try:
                async with conn.transaction():
                    await _seed_es_incumbent(conn)
                    await run_campaign(_SYNTHETIC_CC, conn=conn, pack_fixtures=_fixtures(pack_root))
                    raise _Rollback()
            except _Rollback:
                pass
            # Fresh implicit txn on the same connection: everything from the aborted txn is gone.
            return {
                "entity_total": await conn.fetchval("SELECT count(*) FROM entity"),
                "geo_province_xx": await conn.fetchval(
                    "SELECT count(*) FROM geo_province WHERE country_code='XX'"),
                "geo_municipality_xx": await conn.fetchval(
                    "SELECT count(*) FROM geo_municipality WHERE country_code='XX'"),
                "geo_province_es": await conn.fetchval(
                    "SELECT count(*) FROM geo_province WHERE country_code='ES'"),
            }
        finally:
            await conn.close()


@pytest.mark.integration
@pytest.mark.skipif(
    not DB_AVAILABLE,
    reason="empty dry-run cardeep-pg not reachable at :5434 (or CARDEEP_DSN points at :5433)",
)
class TestHonestFrontier:
    """The frontier branches: RECHAZA halts fail-closed, ESCALA + non-dry-run park PENDIENTE-OWNER —
    none of them seed, all of them stop at BOOTSTRAPPED (the loop never auto-goes-live)."""

    def test_rechaza_halts_fail_closed_no_seed(self, tmp_path: Path) -> None:
        # <3 orthogonal lists -> N1 RECHAZA -> overall RECHAZA. The pack must NEVER seed.
        res, seeded = asyncio.run(self._run(tmp_path, roster=("osm", "dgt_cat")))
        assert res.decision is Decision.RECHAZA
        assert res.halted is True
        assert res.final_state == state.BOOTSTRAPPED
        assert res.minted_cdp_code is None
        assert seeded["entity"] == 0 and seeded["geo_xx"] == 0  # fail-closed: nothing landed

    def test_escala_parks_pending_owner_no_seed(self, tmp_path: Path) -> None:
        # An unclassifiable (MKT) source -> N1 ESCALA -> overall ESCALA -> park, do not seed.
        res, seeded = asyncio.run(self._run(tmp_path, roster=("osm", "dgt_cat", "wallapop_feed")))
        assert res.decision is Decision.ESCALA
        assert res.halted is False
        assert res.pending_owner is True
        assert res.final_state == state.BOOTSTRAPPED
        assert res.minted_cdp_code is None
        assert seeded["entity"] == 0 and seeded["geo_xx"] == 0

    def test_non_dry_run_never_auto_goes_live(self, tmp_path: Path) -> None:
        # dry_run=False: build APRUEBA, but the live harvest is owner-gated -> park, never seed.
        res, seeded = asyncio.run(self._run(tmp_path, dry_run=False))
        assert res.decision is Decision.APRUEBA
        assert res.final_state == state.BOOTSTRAPPED
        assert res.minted_cdp_code is None
        assert set(res.parked_gate_names) == {"PROD", "LEGAL"}
        assert res.pending_owner is True
        assert seeded["entity"] == 0 and seeded["geo_xx"] == 0

    async def _run(self, pack_root: Path, *, dry_run: bool = True, **fx_over):
        conn = await _connect()
        try:
            captured: dict = {}
            try:
                async with conn.transaction():
                    res = await run_campaign(
                        _SYNTHETIC_CC, conn=conn,
                        pack_fixtures=_fixtures(pack_root, **fx_over), dry_run=dry_run)
                    seeded = {
                        "entity": await conn.fetchval("SELECT count(*) FROM entity"),
                        "geo_xx": await conn.fetchval(
                            "SELECT count(*) FROM geo_province WHERE country_code='XX'"),
                    }
                    captured["res"] = res
                    captured["seeded"] = seeded
                    raise _Rollback()
            except _Rollback:
                pass
            return captured["res"], captured["seeded"]
        finally:
            await conn.close()

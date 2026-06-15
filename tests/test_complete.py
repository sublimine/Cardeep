"""Unit tests for pipeline/complete.py — SU-B2 completion gate evaluator.

Covers G1-G4 with synthetic mock data (no live DB required).
Uses the same mocked asyncpg pattern as test_delta.py.

Test design:
  - Each gate has TRUE (pass) and FALSE (fail) cases.
  - derive_verdict is tested for all meaningful combinations.
  - The COMPLETED verdict requires G1∧G2∧G3∧G4 TRUE + G5 deferred.
  - G5 stub always returns (None, reason), so verdict is always INCOMPLETE
    until G5 is implemented (correct per spec).

Gate definitions (V2 refined 2026-06-15):
  G1: entity exists + cdp_code well-formed + province_code 01-52.
      lat/lon NOT required (SU-A6 declared geo gap).
  G2: field_integrity = D_valid/D >= 0.98 where D_valid = deep_link NOT NULL.
      recipe_version NOT included (G3 responsibility, only 537 AS24 dealers).
      VAM quorum D==S enforced when s_declared available.
  G3: v_dealer_recipe.recipe_kind <> 'none' (connector OR per_dealer).
      git sub-signal is diagnostic only, does NOT gate G3.
  G4: entity in v_dealer_resolved + served_count > 0.

No live DB, no HTTP, no filesystem git calls needed for the unit suite.
G3 uses AsyncMock for v_dealer_recipe query (no subprocess mock needed for primary check).
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.complete import (
    SLA_STANDARD,
    _CDP_CODE_RE,
    _FIELD_INTEGRITY_FLOOR,
    _PROVINCE_RE,
    check_g1,
    check_g2,
    check_g3,
    check_g4,
    check_g5_stub,
    compute_completion,
    derive_verdict,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_CDP = "CDP-ES-28-7Q2K9ABX"
_VALID_PROV = "28"
_ENTITY_ULID = "01HX_TEST_ENT"


def _make_conn() -> AsyncMock:
    """Return a minimal asyncpg connection mock."""
    return AsyncMock()


# ---------------------------------------------------------------------------
# G1 — Identity (no lat/lon required per V2 refined 2026-06-15)
# ---------------------------------------------------------------------------

class TestCheckG1:
    """G1: entity row exists, province_code valid (01-52), cdp_code well-formed.

    lat/lon are NOT required: geo gap is declared SU-A6 data gap, not an identity failure.
    """

    @pytest.mark.asyncio
    async def test_g1_pass_minimal_fields(self) -> None:
        """G1 passes with only cdp_code and province_code — no lat/lon needed."""
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value={
            "cdp_code": _VALID_CDP,
            "province_code": _VALID_PROV,
        })
        passed, reason = await check_g1(conn, _VALID_CDP)
        assert passed is True
        assert reason == "ok"

    @pytest.mark.asyncio
    async def test_g1_pass_without_lat_lon(self) -> None:
        """G1 passes even when lat/lon are null — geo is SU-A6 gap, not identity."""
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value={
            "cdp_code": _VALID_CDP,
            "province_code": _VALID_PROV,
            # lat and lon deliberately absent from the row
        })
        passed, reason = await check_g1(conn, _VALID_CDP)
        assert passed is True
        assert reason == "ok"

    @pytest.mark.asyncio
    async def test_g1_fail_entity_not_found(self) -> None:
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value=None)
        passed, reason = await check_g1(conn, _VALID_CDP)
        assert passed is False
        assert "entity_not_found" in reason

    @pytest.mark.asyncio
    async def test_g1_fail_province_null(self) -> None:
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value={
            "cdp_code": _VALID_CDP,
            "province_code": None,
        })
        passed, reason = await check_g1(conn, _VALID_CDP)
        assert passed is False
        assert "invalid_province_code" in reason

    @pytest.mark.asyncio
    async def test_g1_fail_province_out_of_range(self) -> None:
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value={
            "cdp_code": _VALID_CDP,
            "province_code": "99",  # invalid: Spain has 01-52
        })
        passed, reason = await check_g1(conn, _VALID_CDP)
        assert passed is False
        assert "invalid_province_code" in reason

    @pytest.mark.asyncio
    async def test_g1_fail_cdp_code_malformed(self) -> None:
        bad_code = "CDP-ES-28-IILLOOUU"  # contains I, L, O, U — invalid Crockford
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value={
            "cdp_code": bad_code,
            "province_code": "28",
        })
        passed, reason = await check_g1(conn, bad_code)
        assert passed is False
        assert "cdp_code_format_invalid" in reason

    def test_province_regex_valid_range(self) -> None:
        """Province codes 01–52 all match; 00 and 53+ do not."""
        for n in range(1, 53):
            assert _PROVINCE_RE.match(f"{n:02d}"), f"{n:02d} should be valid"
        assert not _PROVINCE_RE.match("00")
        assert not _PROVINCE_RE.match("53")
        assert not _PROVINCE_RE.match("99")

    def test_cdp_code_regex_valid(self) -> None:
        """Valid CDP codes pass the regex (exactly 8 Crockford-base32 chars).

        Note: _CDP_CODE_RE validates FORMAT only (prefix + 2 digits + 8 Crockford
        chars). Province RANGE validation (01-52) is done separately by _PROVINCE_RE
        applied to entity.province_code and by the FK to geo_province in the DB.
        A code like CDP-ES-53-XXXXXXXX is format-valid even if province 53 does not
        exist — that out-of-range check is G1's _PROVINCE_RE, not this regex.
        """
        # _VALID_CDP = "CDP-ES-28-7Q2K9ABX" — 8 chars, valid Crockford alphabet
        assert _CDP_CODE_RE.match(_VALID_CDP), f"{_VALID_CDP} should match"
        assert _CDP_CODE_RE.match("CDP-ES-01-01234567")   # 8 chars: digits only
        assert _CDP_CODE_RE.match("CDP-ES-52-ABCDEFGH")   # 8 chars: valid uppercase
        # 9 chars in suffix — too long, should NOT match
        assert not _CDP_CODE_RE.match("CDP-ES-28-7Q2K9ABXY")
        # 7 chars in suffix — too short, should NOT match
        assert not _CDP_CODE_RE.match("CDP-ES-28-7Q2K9AB")
        # Contains invalid Crockford chars I, L, O, U
        assert not _CDP_CODE_RE.match("CDP-ES-28-IOILLOUU")
        # Wrong prefix
        assert not _CDP_CODE_RE.match("CDD-ES-28-7Q2K9ABX")


# ---------------------------------------------------------------------------
# G2 — Inventory completeness (deep_link only, no recipe_version)
# ---------------------------------------------------------------------------

class TestCheckG2:
    """G2: db-landed count >= 1, field_integrity >= 0.98 (deep_link NOT NULL only).

    recipe_version excluded: only written for 537 AS24 dealers (G3 responsibility).
    VAM quorum D==S enforced when s_declared available.
    """

    def _build_conn(
        self,
        entity_rows: list[dict] | None = None,
        d_landed: int = 100,
        d_valid: int = 99,
    ) -> AsyncMock:
        conn = _make_conn()
        # fetch: entity_ulid rows
        if entity_rows is None:
            entity_rows = [{"entity_ulid": _ENTITY_ULID}]

        def _fake_row(d: dict) -> MagicMock:
            r = MagicMock()
            r.__getitem__ = lambda self, k: d[k]
            r["entity_ulid"] = d.get("entity_ulid", _ENTITY_ULID)
            return r

        conn.fetch = AsyncMock(return_value=[_fake_row(r) for r in entity_rows])

        # fetchval: first call = d_landed, second = d_valid (deep_link only now)
        calls = iter([d_landed, d_valid])
        conn.fetchval = AsyncMock(side_effect=lambda *a, **kw: next(calls))

        return conn

    @pytest.mark.asyncio
    async def test_g2_pass_high_field_integrity(self) -> None:
        conn = self._build_conn(d_landed=100, d_valid=99)
        passed, reason, evidence = await check_g2(conn, _VALID_CDP)
        assert passed is True
        assert reason == "ok"
        assert evidence["field_integrity"] == pytest.approx(0.99)

    @pytest.mark.asyncio
    async def test_g2_pass_exact_floor(self) -> None:
        """field_integrity exactly at 0.98 should pass."""
        conn = self._build_conn(d_landed=100, d_valid=98)
        passed, reason, evidence = await check_g2(conn, _VALID_CDP)
        assert passed is True
        assert evidence["field_integrity"] == pytest.approx(_FIELD_INTEGRITY_FLOOR)

    @pytest.mark.asyncio
    async def test_g2_pass_with_deep_link_only_no_recipe_version(self) -> None:
        """G2 passes when all vehicles have deep_link even if recipe_version is NULL.

        This is the key change: recipe_version is G3's concern, not G2's.
        A dealer with 100% deep_link coverage but 0% recipe_version should pass G2.
        """
        # d_landed=100 vehicles; d_valid=100 (all have deep_link, recipe_version ignored)
        conn = self._build_conn(d_landed=100, d_valid=100)
        passed, reason, evidence = await check_g2(conn, _VALID_CDP)
        assert passed is True
        assert evidence["field_integrity"] == pytest.approx(1.0)

    @pytest.mark.asyncio
    async def test_g2_fail_no_available_vehicles(self) -> None:
        conn = self._build_conn(d_landed=0, d_valid=0)
        passed, reason, evidence = await check_g2(conn, _VALID_CDP)
        assert passed is False
        assert "no_available_vehicles" in reason
        assert evidence["d_landed"] == 0

    @pytest.mark.asyncio
    async def test_g2_fail_field_integrity_below_floor(self) -> None:
        """97 valid out of 100 = 0.97 < 0.98 → FAIL."""
        conn = self._build_conn(d_landed=100, d_valid=97)
        passed, reason, evidence = await check_g2(conn, _VALID_CDP)
        assert passed is False
        assert "field_integrity_below_floor" in reason
        assert evidence["field_integrity"] == pytest.approx(0.97)

    @pytest.mark.asyncio
    async def test_g2_fail_entity_not_found(self) -> None:
        conn = _make_conn()
        conn.fetch = AsyncMock(return_value=[])
        passed, reason, evidence = await check_g2(conn, _VALID_CDP)
        assert passed is False
        assert "entity_not_found" in reason

    @pytest.mark.asyncio
    async def test_g2_evidence_contains_required_keys(self) -> None:
        conn = self._build_conn(d_landed=50, d_valid=50)
        _, _, evidence = await check_g2(conn, _VALID_CDP)
        assert "d_landed" in evidence
        assert "d_valid" in evidence
        assert "field_integrity" in evidence

    @pytest.mark.asyncio
    async def test_g2_pass_s_declared_always_none_in_evidence(self) -> None:
        """s_declared is not a column on entity table; evidence always None.

        VAM quorum D=S for entity_inventory lives in verification_verdict (B1 work).
        G2 field_integrity is the primary gate signal; s_declared is reserved for
        future backfill from verification_verdict at block β-complete time.
        """
        conn = self._build_conn(d_landed=100, d_valid=99)
        passed, reason, evidence = await check_g2(conn, _VALID_CDP)
        assert passed is True
        assert evidence["s_declared"] is None  # not a column on entity


# ---------------------------------------------------------------------------
# G3 — Recipe coverage via v_dealer_recipe (DB-based, async)
# ---------------------------------------------------------------------------

class TestCheckG3:
    """G3: v_dealer_recipe.recipe_kind <> 'none'.

    Primary check is a DB query — no git required.
    git sub-signal is diagnostic only (tested via _check_g3_git_subsignal separately).
    """

    def _make_recipe_row(self, kind: str, ref: str | None = None) -> MagicMock:
        row = MagicMock()
        row.__getitem__ = lambda self, k: kind if k == "recipe_kind" else ref
        row["recipe_kind"] = kind
        row["recipe_ref"] = ref
        return row

    @pytest.mark.asyncio
    async def test_g3_pass_connector_recipe(self) -> None:
        """G3 passes for connector-covered dealer (97.5% of fleet)."""
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value=self._make_recipe_row("connector", "coches_net_wholesale"))
        passed, reason, sha = await check_g3(conn, _VALID_CDP)
        assert passed is True
        assert "ok" in reason
        assert "connector" in reason
        # sha is None for connector (git sub-signal skipped)
        assert sha is None

    @pytest.mark.asyncio
    async def test_g3_pass_per_dealer_recipe(self) -> None:
        """G3 passes for per_dealer recipe (AS24 cohort, 537 dealers).

        G3 is TRUE based on recipe_kind; git sub-signal is attempted but does not gate.
        We mock the git subprocess to avoid filesystem dependency.
        """
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value=self._make_recipe_row("per_dealer", None))

        # Mock the git sub-signal: simulate git unavailable (Docker scenario).
        # G3 must still pass because recipe_kind='per_dealer' is the primary check.
        with patch("pipeline.complete.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("git not found")
            passed, reason, sha = await check_g3(conn, _VALID_CDP)

        assert passed is True
        assert "ok" in reason
        assert "per_dealer" in reason
        # sha is None because git unavailable (sub-signal failed but gate is TRUE)
        assert sha is None

    @pytest.mark.asyncio
    async def test_g3_fail_recipe_kind_none(self) -> None:
        """G3 fails when recipe_kind='none' (0.2% of fleet with no recipe coverage)."""
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value=self._make_recipe_row("none", None))
        passed, reason, sha = await check_g3(conn, _VALID_CDP)
        assert passed is False
        assert "none" in reason or "recipe_kind" in reason
        assert sha is None

    @pytest.mark.asyncio
    async def test_g3_fail_dealer_not_in_view(self) -> None:
        """G3 fails when dealer is absent from v_dealer_recipe (not a served dealer)."""
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value=None)
        passed, reason, sha = await check_g3(conn, _VALID_CDP)
        assert passed is False
        assert "dealer_not_in_v_dealer_recipe" in reason
        assert sha is None

    @pytest.mark.asyncio
    async def test_g3_pass_connector_git_unavailable_does_not_fail_gate(self) -> None:
        """Connector recipe: git sub-signal is skipped entirely; G3 is TRUE regardless."""
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value=self._make_recipe_row("connector"))
        # Even if we patch subprocess to raise, G3 should still pass (git not called for connector)
        with patch("pipeline.complete.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("git not found")
            passed, reason, sha = await check_g3(conn, _VALID_CDP)

        assert passed is True
        # subprocess.run should NOT have been called for connector recipes
        mock_run.assert_not_called()


# ---------------------------------------------------------------------------
# G3 git sub-signal (diagnostic only — _check_g3_git_subsignal)
# ---------------------------------------------------------------------------

class TestCheckG3GitSubsignal:
    """Tests for the git sub-signal function (diagnostic, does not gate G3)."""

    from pipeline.complete import _check_g3_git_subsignal  # import here to be explicit

    @patch("pipeline.complete.subprocess.run")
    def test_subsignal_pass(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """All checks pass: file exists, git available, tracked, committed, YAML valid."""
        recipe_dir = tmp_path / "countries" / "ES" / "recipes"
        recipe_dir.mkdir(parents=True)
        (recipe_dir / f"{_VALID_CDP}.yaml").write_text("version: 1\nurl: https://example.com\n", encoding="utf-8")

        mock_run.return_value = MagicMock(returncode=0, stdout=b"abc123def456\n")

        from pipeline.complete import _check_g3_git_subsignal
        sha, reason = _check_g3_git_subsignal(_VALID_CDP, repo_root=tmp_path)
        assert sha is not None
        assert "tracked_and_committed" in reason

    @patch("pipeline.complete.subprocess.run")
    def test_subsignal_git_unavailable(self, mock_run: MagicMock, tmp_path: Path) -> None:
        recipe_dir = tmp_path / "countries" / "ES" / "recipes"
        recipe_dir.mkdir(parents=True)
        (recipe_dir / f"{_VALID_CDP}.yaml").write_text("version: 1\n", encoding="utf-8")

        mock_run.side_effect = FileNotFoundError("git not found")

        from pipeline.complete import _check_g3_git_subsignal
        sha, reason = _check_g3_git_subsignal(_VALID_CDP, repo_root=tmp_path)
        assert sha is None
        assert "git_unavailable" in reason

    @patch("pipeline.complete.subprocess.run")
    def test_subsignal_file_missing(self, mock_run: MagicMock, tmp_path: Path) -> None:
        from pipeline.complete import _check_g3_git_subsignal
        sha, reason = _check_g3_git_subsignal(_VALID_CDP, repo_root=tmp_path)
        assert sha is None
        assert "file_missing" in reason
        mock_run.assert_not_called()

    @patch("pipeline.complete.subprocess.run")
    def test_subsignal_not_tracked(self, mock_run: MagicMock, tmp_path: Path) -> None:
        recipe_dir = tmp_path / "countries" / "ES" / "recipes"
        recipe_dir.mkdir(parents=True)
        (recipe_dir / f"{_VALID_CDP}.yaml").write_text("version: 1\n", encoding="utf-8")

        mock_run.side_effect = [
            MagicMock(returncode=0),  # git --version
            MagicMock(returncode=1),  # ls-files: not tracked
        ]

        from pipeline.complete import _check_g3_git_subsignal
        sha, reason = _check_g3_git_subsignal(_VALID_CDP, repo_root=tmp_path)
        assert sha is None
        assert "not_tracked" in reason


# ---------------------------------------------------------------------------
# G4 — Served (DB-equivalent)
# ---------------------------------------------------------------------------

class TestCheckG4:
    """G4: entity in v_dealer_resolved + served_count > 0."""

    def _build_conn(
        self,
        in_resolved: bool = True,
        entity_ulids: list[str] | None = None,
        served_count: int = 84,
    ) -> AsyncMock:
        conn = _make_conn()

        # fetchrow: v_dealer_resolved lookup
        if in_resolved:
            def _fake_resolved_row(d: dict) -> MagicMock:
                r = MagicMock()
                r.__getitem__ = lambda self, k: d[k]
                return r
            conn.fetchrow = AsyncMock(return_value=_fake_resolved_row(
                {"resolved_cdp_code": _VALID_CDP}
            ))
        else:
            conn.fetchrow = AsyncMock(return_value=None)

        # fetch: entity_ulid rows
        if entity_ulids is None:
            entity_ulids = [_ENTITY_ULID]

        def _fake_entity_row(ulid: str) -> MagicMock:
            r = MagicMock()
            r.__getitem__ = lambda self, k: ulid if k == "entity_ulid" else None
            r["entity_ulid"] = ulid
            return r

        conn.fetch = AsyncMock(return_value=[_fake_entity_row(u) for u in entity_ulids])

        # fetchval: served_count
        conn.fetchval = AsyncMock(return_value=served_count)
        return conn

    @pytest.mark.asyncio
    async def test_g4_pass_entity_served(self) -> None:
        conn = self._build_conn(in_resolved=True, served_count=84)
        passed, reason, count = await check_g4(conn, _VALID_CDP, d_landed=84)
        assert passed is True
        assert reason == "ok"
        assert count == 84

    @pytest.mark.asyncio
    async def test_g4_fail_not_in_resolved(self) -> None:
        conn = self._build_conn(in_resolved=False)
        passed, reason, count = await check_g4(conn, _VALID_CDP, d_landed=84)
        assert passed is False
        assert "not_in_v_dealer_resolved" in reason
        assert count is None

    @pytest.mark.asyncio
    async def test_g4_fail_served_count_zero(self) -> None:
        conn = self._build_conn(in_resolved=True, served_count=0)
        passed, reason, count = await check_g4(conn, _VALID_CDP, d_landed=0)
        assert passed is False
        assert "served_count_zero" in reason

    @pytest.mark.asyncio
    async def test_g4_pass_no_d_landed_comparison(self) -> None:
        """G4 passes even if d_landed is None (G2 not yet computed)."""
        conn = self._build_conn(in_resolved=True, served_count=50)
        passed, reason, count = await check_g4(conn, _VALID_CDP, d_landed=None)
        assert passed is True
        assert count == 50

    @pytest.mark.asyncio
    async def test_g4_fail_entity_not_found(self) -> None:
        """Entity in resolved view but not in entity table (edge case)."""
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value=MagicMock())
        conn.fetch = AsyncMock(return_value=[])  # no entity_ulids
        passed, reason, count = await check_g4(conn, _VALID_CDP, d_landed=None)
        assert passed is False
        assert "entity_not_found" in reason


# ---------------------------------------------------------------------------
# G5 — Deferred stub
# ---------------------------------------------------------------------------

class TestCheckG5Stub:
    """G5: always returns (None, reason) — deferred until second harvest."""

    def test_g5_always_none(self) -> None:
        result, reason = check_g5_stub(_VALID_CDP)
        assert result is None
        assert "G5" in reason or "harvest" in reason.lower() or "deferred" in reason.lower()

    def test_g5_reason_non_empty(self) -> None:
        _, reason = check_g5_stub("CDP-ES-01-ANYCODE1")
        assert isinstance(reason, str) and len(reason) > 0


# ---------------------------------------------------------------------------
# derive_verdict
# ---------------------------------------------------------------------------

class TestDeriveVerdict:
    """Verdict logic: COMPLETED ⟺ g1∧g2∧g3∧g4∧g5=TRUE ∧ is_fresh."""

    def test_all_true_with_g5_deferred_is_incomplete(self) -> None:
        """G5=None (deferred) → always INCOMPLETE, even if G1-G4 pass."""
        v = derive_verdict(True, True, True, True, g5=None, is_fresh=True)
        assert v == "INCOMPLETE"

    def test_all_five_true_and_fresh_is_completed(self) -> None:
        v = derive_verdict(True, True, True, True, g5=True, is_fresh=True)
        assert v == "COMPLETED"

    def test_g1_false_is_incomplete(self) -> None:
        v = derive_verdict(False, True, True, True, g5=True, is_fresh=True)
        assert v == "INCOMPLETE"

    def test_g2_false_is_incomplete(self) -> None:
        v = derive_verdict(True, False, True, True, g5=True, is_fresh=True)
        assert v == "INCOMPLETE"

    def test_g3_false_is_incomplete(self) -> None:
        v = derive_verdict(True, True, False, True, g5=True, is_fresh=True)
        assert v == "INCOMPLETE"

    def test_g4_false_is_incomplete(self) -> None:
        v = derive_verdict(True, True, True, False, g5=True, is_fresh=True)
        assert v == "INCOMPLETE"

    def test_g5_false_is_incomplete(self) -> None:
        v = derive_verdict(True, True, True, True, g5=False, is_fresh=True)
        assert v == "INCOMPLETE"

    def test_stale_when_all_pass_but_not_fresh(self) -> None:
        v = derive_verdict(True, True, True, True, g5=True, is_fresh=False)
        assert v == "STALE"

    def test_incomplete_when_any_fail_and_not_fresh(self) -> None:
        """Not fresh + any gate False → INCOMPLETE (not STALE, since not all passed)."""
        v = derive_verdict(True, False, True, True, g5=True, is_fresh=False)
        assert v == "INCOMPLETE"

    def test_all_false_is_incomplete(self) -> None:
        v = derive_verdict(False, False, False, False, g5=False, is_fresh=True)
        assert v == "INCOMPLETE"


# ---------------------------------------------------------------------------
# compute_completion — integration of G1-G5 logic
# ---------------------------------------------------------------------------

class TestComputeCompletion:
    """compute_completion: full gate pipeline with mocked DB (G3 now async DB-based)."""

    def _build_full_conn(
        self,
        *,
        entity_row: dict | None = None,
        d_landed: int = 100,
        d_valid: int = 100,
        in_resolved: bool = True,
        served_count: int = 100,
        recipe_kind: str = "connector",
    ) -> AsyncMock:
        conn = _make_conn()

        if entity_row is None:
            entity_row = {
                "cdp_code": _VALID_CDP,
                "province_code": "28",
                # No lat/lon — tests the new G1 definition
            }

        def _make_recipe_row(kind: str) -> MagicMock:
            r = MagicMock()
            r.__getitem__ = lambda self, k: kind if k == "recipe_kind" else None
            r["recipe_kind"] = kind
            r["recipe_ref"] = None
            return r

        # fetchrow calls in order:
        #   1. G1: entity lookup
        #   2. G3: v_dealer_recipe lookup
        #   3. G4: v_dealer_resolved lookup
        # (G2 no longer issues a fetchrow — s_declared not a column on entity)
        fetchrow_results = [
            entity_row,                                             # G1
            _make_recipe_row(recipe_kind),                          # G3
            MagicMock() if in_resolved else None,                   # G4
        ]
        fetchrow_iter = iter(fetchrow_results)
        conn.fetchrow = AsyncMock(side_effect=lambda *a, **kw: next(fetchrow_iter))

        # fetch: G2 entity_ulids, G4 entity_ulids
        def _fake_row(d: dict) -> MagicMock:
            r = MagicMock()
            r.__getitem__ = lambda self, k: d[k]
            r["entity_ulid"] = d.get("entity_ulid", _ENTITY_ULID)
            return r

        conn.fetch = AsyncMock(return_value=[_fake_row({"entity_ulid": _ENTITY_ULID})])

        # fetchval: G2 d_landed, G2 d_valid, G4 served_count
        fetchval_results = iter([d_landed, d_valid, served_count])
        conn.fetchval = AsyncMock(side_effect=lambda *a, **kw: next(fetchval_results))
        return conn

    @pytest.mark.asyncio
    async def test_compute_g1_to_g4_all_pass_verdict_incomplete(self) -> None:
        """G1-G4 all pass (connector recipe, no lat/lon), G5 deferred → INCOMPLETE."""
        conn = self._build_full_conn()
        result = await compute_completion(conn, _VALID_CDP)

        assert result["g1_identity"] is True
        assert result["g2_inventory"] is True
        assert result["g3_recipe"] is True
        assert result["g4_served"] is True
        assert result["g5_delta"] is False  # stored as False (G5 deferred)
        assert result["verdict"] == "INCOMPLETE"  # G5 not proven yet
        assert result["d_landed"] == 100
        assert result["field_integrity"] == pytest.approx(1.0)
        # recipe_sha is None for connector (git sub-signal skipped)
        assert result["recipe_sha"] is None
        assert result["served_count"] == 100

    @pytest.mark.asyncio
    async def test_compute_g1_pass_without_lat_lon(self) -> None:
        """G1 passes even with no lat/lon in entity row (geo gap is SU-A6, not identity)."""
        conn = self._build_full_conn(entity_row={
            "cdp_code": _VALID_CDP,
            "province_code": "28",
            # no lat, no lon
        })
        result = await compute_completion(conn, _VALID_CDP)
        assert result["g1_identity"] is True

    @pytest.mark.asyncio
    async def test_compute_g2_pass_with_deep_link_no_recipe_version(self) -> None:
        """G2 passes when D_valid counts only deep_link (recipe_version irrelevant)."""
        # d_valid=100 means all vehicles have deep_link; recipe_version is ignored
        conn = self._build_full_conn(d_landed=100, d_valid=100)
        result = await compute_completion(conn, _VALID_CDP)
        assert result["g2_inventory"] is True
        assert result["field_integrity"] == pytest.approx(1.0)

    @pytest.mark.asyncio
    async def test_compute_g3_pass_with_connector_recipe(self) -> None:
        """G3 passes for connector-covered dealer without any git check."""
        conn = self._build_full_conn(recipe_kind="connector")
        result = await compute_completion(conn, _VALID_CDP)
        assert result["g3_recipe"] is True

    @pytest.mark.asyncio
    async def test_compute_g3_fail_recipe_kind_none(self) -> None:
        """G3 fails when v_dealer_recipe returns 'none'."""
        conn = self._build_full_conn(recipe_kind="none")
        result = await compute_completion(conn, _VALID_CDP)
        assert result["g3_recipe"] is False
        assert result["verdict"] == "INCOMPLETE"

    @pytest.mark.asyncio
    async def test_compute_g1_fail_propagates(self) -> None:
        """If G1 fails (entity not found), verdict must be INCOMPLETE."""
        conn = _make_conn()
        conn.fetchrow = AsyncMock(side_effect=[None, None, None, None])
        conn.fetch = AsyncMock(return_value=[])
        conn.fetchval = AsyncMock(return_value=0)
        result = await compute_completion(conn, _VALID_CDP)
        assert result["g1_identity"] is False
        assert result["verdict"] == "INCOMPLETE"

    @pytest.mark.asyncio
    async def test_compute_result_has_all_required_keys(self) -> None:
        """compute_completion result must include all entity_completion columns."""
        conn = self._build_full_conn()
        result = await compute_completion(conn, _VALID_CDP)
        required_keys = {
            "cdp_code", "g1_identity", "g2_inventory", "g3_recipe",
            "g4_served", "g5_delta", "verdict",
            "s_declared", "h_harvested", "d_landed", "d_valid",
            "field_integrity", "recipe_sha", "served_count",
        }
        assert required_keys.issubset(result.keys()), (
            f"Missing keys: {required_keys - result.keys()}"
        )

    @pytest.mark.asyncio
    async def test_compute_g5_always_deferred(self) -> None:
        """G5 is always stored as False (deferred); check that _reasons reflects this."""
        conn = self._build_full_conn()
        result = await compute_completion(conn, _VALID_CDP)
        assert result["g5_delta"] is False
        g5_reason = result.get("_reasons", {}).get("g5", "")
        assert "G5" in g5_reason or "harvest" in g5_reason.lower() or "deferred" in g5_reason.lower()

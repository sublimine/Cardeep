"""Unit tests for pipeline/complete.py — SU-B2 completion gate evaluator.

Covers G1-G4 with synthetic mock data (no live DB required).
Uses the same mocked asyncpg pattern as test_delta.py.

Test design:
  - Each gate has TRUE (pass) and FALSE (fail) cases.
  - derive_verdict is tested for all meaningful combinations.
  - The COMPLETED verdict requires G1∧G2∧G3∧G4 TRUE + G5 deferred.
  - G5 stub always returns (None, reason), so verdict is always INCOMPLETE
    until G5 is implemented (correct per spec).

No live DB, no HTTP, no filesystem git calls needed for the unit suite.
G3 filesystem/git calls are tested by mocking subprocess.run and Path.exists.
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
# G1 — Identity & geo
# ---------------------------------------------------------------------------

class TestCheckG1:
    """G1: entity row exists, province_code valid, cdp_code well-formed, lat/lon set."""

    @pytest.mark.asyncio
    async def test_g1_pass_all_fields_valid(self) -> None:
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value={
            "cdp_code": _VALID_CDP,
            "province_code": _VALID_PROV,
            "lat": 40.4168,
            "lon": -3.7038,
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
            "lat": 40.4168,
            "lon": -3.7038,
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
            "lat": 40.4168,
            "lon": -3.7038,
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
            "lat": 40.4168,
            "lon": -3.7038,
        })
        passed, reason = await check_g1(conn, bad_code)
        assert passed is False
        assert "cdp_code_format_invalid" in reason

    @pytest.mark.asyncio
    async def test_g1_fail_lat_null(self) -> None:
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value={
            "cdp_code": _VALID_CDP,
            "province_code": "28",
            "lat": None,
            "lon": -3.7038,
        })
        passed, reason = await check_g1(conn, _VALID_CDP)
        assert passed is False
        assert "geo_missing" in reason

    @pytest.mark.asyncio
    async def test_g1_fail_lon_null(self) -> None:
        conn = _make_conn()
        conn.fetchrow = AsyncMock(return_value={
            "cdp_code": _VALID_CDP,
            "province_code": "28",
            "lat": 40.4168,
            "lon": None,
        })
        passed, reason = await check_g1(conn, _VALID_CDP)
        assert passed is False
        assert "geo_missing" in reason

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
# G2 — Inventory completeness
# ---------------------------------------------------------------------------

class TestCheckG2:
    """G2: db-landed count >= 1, field_integrity >= 0.98."""

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

        # fetchval: first call = d_landed, second = d_valid
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


# ---------------------------------------------------------------------------
# G3 — Recipe durable (git-committed)
# ---------------------------------------------------------------------------

class TestCheckG3:
    """G3: recipe.yaml exists and is git-committed at HEAD."""

    def _mock_git_ok(self, fake_root: Path) -> dict[str, Any]:
        """Return a patcher context for a fully passing G3."""
        return {}

    @patch("pipeline.complete.subprocess.run")
    @patch("pipeline.complete.Path.exists")
    def test_g3_pass(self, mock_exists: MagicMock, mock_run: MagicMock, tmp_path: Path) -> None:
        """All checks pass: file exists, git available, tracked, committed, YAML valid."""
        # Create a real YAML file in a temp dir
        recipe_dir = tmp_path / "countries" / "ES" / "recipes"
        recipe_dir.mkdir(parents=True)
        recipe_file = recipe_dir / f"{_VALID_CDP}.yaml"
        recipe_file.write_text("version: 1\nurl: https://example.com\n", encoding="utf-8")

        # mock subprocess.run: git --version, ls-files, cat-file, rev-parse all succeed
        mock_run.return_value = MagicMock(returncode=0, stdout=b"abc123def456\n")
        mock_exists.return_value = True

        passed, reason, sha = check_g3(_VALID_CDP, repo_root=tmp_path)
        assert passed is True, f"Expected pass but got reason={reason!r}"
        assert reason == "ok"

    @patch("pipeline.complete.subprocess.run")
    def test_g3_fail_file_missing(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """Recipe file does not exist → G3 FAIL before git check."""
        # No file created — path does not exist
        passed, reason, sha = check_g3(_VALID_CDP, repo_root=tmp_path)
        assert passed is False
        assert "recipe_file_missing" in reason
        mock_run.assert_not_called()  # git never called if file missing

    @patch("pipeline.complete.subprocess.run")
    def test_g3_fail_git_unavailable(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """git not in PATH → G3 FAIL with git_unavailable."""
        recipe_dir = tmp_path / "countries" / "ES" / "recipes"
        recipe_dir.mkdir(parents=True)
        (recipe_dir / f"{_VALID_CDP}.yaml").write_text("version: 1\n", encoding="utf-8")

        import subprocess as sp
        mock_run.side_effect = FileNotFoundError("git not found")

        passed, reason, sha = check_g3(_VALID_CDP, repo_root=tmp_path)
        assert passed is False
        assert "git_unavailable" in reason

    @patch("pipeline.complete.subprocess.run")
    def test_g3_fail_not_tracked(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """File exists but not git-tracked (ls-files exits 1)."""
        recipe_dir = tmp_path / "countries" / "ES" / "recipes"
        recipe_dir.mkdir(parents=True)
        (recipe_dir / f"{_VALID_CDP}.yaml").write_text("version: 1\n", encoding="utf-8")

        # git --version ok, ls-files FAILS (returncode=1)
        mock_run.side_effect = [
            MagicMock(returncode=0),   # git --version
            MagicMock(returncode=1),   # ls-files: not tracked
        ]
        passed, reason, sha = check_g3(_VALID_CDP, repo_root=tmp_path)
        assert passed is False
        assert "recipe_not_git_tracked" in reason

    @patch("pipeline.complete.subprocess.run")
    def test_g3_fail_not_committed(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """File is tracked (staged) but not committed (cat-file exits 1)."""
        recipe_dir = tmp_path / "countries" / "ES" / "recipes"
        recipe_dir.mkdir(parents=True)
        (recipe_dir / f"{_VALID_CDP}.yaml").write_text("version: 1\n", encoding="utf-8")

        mock_run.side_effect = [
            MagicMock(returncode=0),  # git --version
            MagicMock(returncode=0),  # ls-files ok
            MagicMock(returncode=1),  # cat-file: not at HEAD
        ]
        passed, reason, sha = check_g3(_VALID_CDP, repo_root=tmp_path)
        assert passed is False
        assert "recipe_not_committed_at_HEAD" in reason

    @patch("pipeline.complete.subprocess.run")
    def test_g3_fail_yaml_invalid(self, mock_run: MagicMock, tmp_path: Path) -> None:
        """File exists and is tracked but YAML is malformed."""
        recipe_dir = tmp_path / "countries" / "ES" / "recipes"
        recipe_dir.mkdir(parents=True)
        (recipe_dir / f"{_VALID_CDP}.yaml").write_text(
            "---\n: invalid: [unclosed\n", encoding="utf-8"
        )
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=b""),   # git --version
            MagicMock(returncode=0, stdout=b""),   # ls-files
            MagicMock(returncode=0, stdout=b""),   # cat-file
            MagicMock(returncode=0, stdout=b"abc123\n"),  # rev-parse
        ]
        passed, reason, sha = check_g3(_VALID_CDP, repo_root=tmp_path)
        assert passed is False
        assert "recipe_yaml" in reason


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
    """compute_completion: full gate pipeline with mocked DB and git."""

    def _build_full_conn(
        self,
        *,
        entity_row: dict | None = None,
        d_landed: int = 100,
        d_valid: int = 100,
        in_resolved: bool = True,
        served_count: int = 100,
    ) -> AsyncMock:
        conn = _make_conn()

        if entity_row is None:
            entity_row = {
                "cdp_code": _VALID_CDP,
                "province_code": "28",
                "lat": 40.4168,
                "lon": -3.7038,
            }

        # fetchrow: G1 entity lookup, then G4 v_dealer_resolved
        fetchrow_results = [
            entity_row,
            MagicMock() if in_resolved else None,
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
    @patch("pipeline.complete.check_g3")
    async def test_compute_g1_to_g4_all_pass_verdict_incomplete(
        self, mock_g3: MagicMock
    ) -> None:
        """G1-G4 all pass, G5 deferred → INCOMPLETE (correct per spec)."""
        mock_g3.return_value = (True, "ok", "abc123")
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
        assert result["recipe_sha"] == "abc123"
        assert result["served_count"] == 100

    @pytest.mark.asyncio
    @patch("pipeline.complete.check_g3")
    async def test_compute_g1_fail_propagates(self, mock_g3: MagicMock) -> None:
        """If G1 fails (entity not found), verdict must be INCOMPLETE."""
        mock_g3.return_value = (True, "ok", "sha")
        conn = _make_conn()
        conn.fetchrow = AsyncMock(side_effect=[None, None])
        conn.fetch = AsyncMock(return_value=[])
        conn.fetchval = AsyncMock(return_value=0)
        result = await compute_completion(conn, _VALID_CDP)
        assert result["g1_identity"] is False
        assert result["verdict"] == "INCOMPLETE"

    @pytest.mark.asyncio
    @patch("pipeline.complete.check_g3")
    async def test_compute_g3_fail_propagates(self, mock_g3: MagicMock) -> None:
        """G3 failure (recipe not committed) → verdict INCOMPLETE."""
        mock_g3.return_value = (False, "recipe_not_committed_at_HEAD", None)
        conn = self._build_full_conn()
        result = await compute_completion(conn, _VALID_CDP)
        assert result["g3_recipe"] is False
        assert result["recipe_sha"] is None
        assert result["verdict"] == "INCOMPLETE"

    @pytest.mark.asyncio
    @patch("pipeline.complete.check_g3")
    async def test_compute_result_has_all_required_keys(self, mock_g3: MagicMock) -> None:
        """compute_completion result must include all entity_completion columns."""
        mock_g3.return_value = (True, "ok", "sha")
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
    @patch("pipeline.complete.check_g3")
    async def test_compute_g5_always_deferred(self, mock_g3: MagicMock) -> None:
        """G5 is always stored as False (deferred); check that _reasons reflects this."""
        mock_g3.return_value = (True, "ok", "sha")
        conn = self._build_full_conn()
        result = await compute_completion(conn, _VALID_CDP)
        assert result["g5_delta"] is False
        g5_reason = result.get("_reasons", {}).get("g5", "")
        assert "G5" in g5_reason or "harvest" in g5_reason.lower() or "deferred" in g5_reason.lower()

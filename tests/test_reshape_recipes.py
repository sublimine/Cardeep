"""Unit tests for scripts/reshape_recipes_geo.py + complete.py G3 path resolver.

SU-E2 — recipe geo-reshape + Tier-1 separation.

Coverage:
  1. _slug() helper — accents, spaces, NULL, edge cases.
  2. _compute_target() routing — tier1, national platform, geo dealer,
     _sin-comarca, _sin-municipio, orphan (via _orphan_target).
  3. complete._resolve_recipe_path() — finds new geo layout, falls back to
     legacy flat, returns None when absent.
  4. complete._check_g3_git_subsignal() — returns 'recipe_file_missing'
     when neither layout has the file; otherwise proceeds to git check.

No live DB.  No filesystem writes to countries/.  Uses tmp_path for isolation.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Import the modules under test
# ---------------------------------------------------------------------------

# Make sure repo root is on sys.path so both pipeline and scripts are importable
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.reshape_recipes_geo import (  # noqa: E402
    RecipeRow,
    _COUNTRIES_ES,
    _compute_target,
    _orphan_target,
    _slug,
)
from pipeline.complete import _resolve_recipe_path  # noqa: E402


# ---------------------------------------------------------------------------
# 1. _slug() — deterministic slug generation
# ---------------------------------------------------------------------------

class TestSlug:
    def test_plain_ascii(self) -> None:
        assert _slug("Barcelona") == "barcelona"

    def test_accent_removal(self) -> None:
        # á é í ó ú ñ ü → a e i o u n u
        assert _slug("Málaga") == "malaga"
        assert _slug("Ávila") == "avila"
        assert _slug("Córdoba") == "cordoba"
        assert _slug("Cádiz") == "cadiz"
        assert _slug("Almería") == "almeria"
        assert _slug("Logroño") == "logrono"

    def test_spaces_become_dashes(self) -> None:
        assert _slug("Sant Joan d'Alacant") == "sant-joan-d-alacant"

    def test_special_chars_collapsed(self) -> None:
        assert _slug("L'Hospitalet de Llobregat") == "l-hospitalet-de-llobregat"

    def test_consecutive_dashes_collapsed(self) -> None:
        # Multiple spaces / punctuation → single dash
        result = _slug("foo  --  bar")
        assert "--" not in result
        assert result == "foo-bar"

    def test_leading_trailing_dashes_stripped(self) -> None:
        assert not _slug("-foo-").startswith("-")
        assert not _slug("-foo-").endswith("-")

    def test_empty_string(self) -> None:
        assert _slug("") == ""

    def test_none_returns_empty(self) -> None:
        assert _slug(None) == ""  # type: ignore[arg-type]

    def test_numbers_preserved(self) -> None:
        assert _slug("Comarca 12") == "comarca-12"

    def test_all_special_chars(self) -> None:
        # Should not raise; result is either empty or all dashes stripped
        result = _slug("---")
        assert result == ""

    def test_catalan_chars(self) -> None:
        # l·l (middle dot) → stripped to l-l then collapsed to l-l
        # ç → c
        assert "ç" not in _slug("Torroella de Montgrí")


# ---------------------------------------------------------------------------
# 2. _compute_target() — routing logic
# ---------------------------------------------------------------------------

def _make_row(
    cdp_code: str = "CDP-ES-28-TESTTEST",
    source_group: str | None = "oem_vo_portal",
    is_tier1: bool = False,
    province_code: str | None = None,
    municipality_code: str | None = None,
    comarca_id: int | None = None,
    comarca_name: str | None = None,
    muni_name: str | None = None,
) -> RecipeRow:
    return RecipeRow(
        cdp_code=cdp_code,
        source_group=source_group,
        is_tier1=is_tier1,
        province_code=province_code,
        municipality_code=municipality_code,
        comarca_id=comarca_id,
        comarca_name=comarca_name,
        muni_name=muni_name,
    )


class TestComputeTarget:
    # --- Tier-1 ---

    def test_tier1_marketplace_motor(self) -> None:
        row = _make_row(
            cdp_code="CDP-ES-00-TIER1MKT",
            source_group="marketplace_motor",
            is_tier1=True,
        )
        tgt = _compute_target(row)
        assert tgt == _COUNTRIES_ES / "_tier1" / "CDP-ES-00-TIER1MKT" / "recipe.yaml"

    def test_tier1_marketplace_generalist(self) -> None:
        row = _make_row(
            cdp_code="CDP-ES-00-WALLAPOP",
            source_group="marketplace_generalist",
            is_tier1=True,
        )
        tgt = _compute_target(row)
        assert tgt == _COUNTRIES_ES / "_tier1" / "CDP-ES-00-WALLAPOP" / "recipe.yaml"

    def test_tier1_oem_vo_portal(self) -> None:
        """is_tier1=TRUE overrides source_group — OEM portals can be Tier-1."""
        row = _make_row(
            cdp_code="CDP-ES-00-OEMTIER1",
            source_group="oem_vo_portal",
            is_tier1=True,
        )
        tgt = _compute_target(row)
        assert "_tier1" in str(tgt)

    # --- National platforms (province NULL, NOT tier1) ---

    def test_national_chain(self) -> None:
        row = _make_row(
            cdp_code="CDP-ES-00-CHAINABC",
            source_group="chain",
            is_tier1=False,
            province_code=None,
        )
        tgt = _compute_target(row)
        assert tgt == _COUNTRIES_ES / "_platforms" / "chain" / "CDP-ES-00-CHAINABC" / "recipe.yaml"

    def test_national_oem_vo_portal(self) -> None:
        row = _make_row(
            cdp_code="CDP-ES-00-OEMVOABC",
            source_group="oem_vo_portal",
            is_tier1=False,
        )
        tgt = _compute_target(row)
        assert "_platforms/oem_vo_portal" in str(tgt).replace("\\", "/")

    def test_national_unknown_source_group(self) -> None:
        """NULL source_group → _unknown sentinel."""
        row = _make_row(
            cdp_code="CDP-ES-00-UNKNOWN1",
            source_group=None,
            is_tier1=False,
        )
        tgt = _compute_target(row)
        assert "_unknown" in str(tgt)

    def test_national_marketplace_motor_not_tier1(self) -> None:
        """marketplace_motor with province NULL and is_tier1=FALSE → _platforms."""
        row = _make_row(
            cdp_code="CDP-ES-00-MKTMOTOR",
            source_group="marketplace_motor",
            is_tier1=False,
            province_code=None,
        )
        tgt = _compute_target(row)
        assert "_platforms" in str(tgt)
        assert "_tier1" not in str(tgt)

    # --- Geo dealers ---

    def test_geo_full_details(self) -> None:
        row = _make_row(
            cdp_code="CDP-ES-28-GEOTEST1",
            source_group="oem_dealer_network",
            is_tier1=False,
            province_code="28",
            municipality_code="28079",
            comarca_id=42,
            comarca_name="Área Metropolitana de Madrid",
            muni_name="Madrid",
        )
        tgt = _compute_target(row)
        tgt_str = str(tgt).replace("\\", "/")
        assert "/28/" in tgt_str
        assert "area-metropolitana-de-madrid" in tgt_str
        assert "/madrid/" in tgt_str
        assert "/dealers/CDP-ES-28-GEOTEST1/recipe.yaml" in tgt_str

    def test_geo_sin_comarca(self) -> None:
        """NULL comarca_name → _sin-comarca."""
        row = _make_row(
            cdp_code="CDP-ES-10-SINCOM01",
            source_group="directory",
            is_tier1=False,
            province_code="10",
            municipality_code="10001",
            comarca_id=None,
            comarca_name=None,
            muni_name="Abadía",
        )
        tgt = _compute_target(row)
        tgt_str = str(tgt).replace("\\", "/")
        assert "/_sin-comarca/" in tgt_str
        assert "/abadia/" in tgt_str

    def test_geo_sin_municipio(self) -> None:
        """NULL muni_name → _sin-municipio."""
        row = _make_row(
            cdp_code="CDP-ES-05-SINMUN01",
            source_group="directory",
            is_tier1=False,
            province_code="05",
            municipality_code=None,
            comarca_id=99,
            comarca_name="Sierra de Ávila",
            muni_name=None,
        )
        tgt = _compute_target(row)
        tgt_str = str(tgt).replace("\\", "/")
        assert "/_sin-municipio/" in tgt_str
        assert "sierra-de-avila" in tgt_str

    def test_geo_accented_names_slugged(self) -> None:
        row = _make_row(
            cdp_code="CDP-ES-03-ACCENTTX",
            source_group="directory",
            is_tier1=False,
            province_code="03",
            municipality_code="03065",
            comarca_id=16,
            comarca_name="Meridional",
            muni_name="Elx/Elche",
        )
        tgt = _compute_target(row)
        tgt_str = str(tgt).replace("\\", "/")
        assert "/meridional/" in tgt_str
        assert "elx" in tgt_str  # slug contains "elx"

    # --- Orphan ---

    def test_orphan_target(self) -> None:
        cdp = "CDP-ES-99-ORPHANXX"
        tgt = _orphan_target(cdp)
        assert tgt == _COUNTRIES_ES / "_orphan" / cdp / "recipe.yaml"


# ---------------------------------------------------------------------------
# 3. complete._resolve_recipe_path() — path resolution
# ---------------------------------------------------------------------------

class TestResolveRecipePath:
    def test_finds_new_geo_layout(self, tmp_path: Path) -> None:
        """New geo layout (countries/ES/<prov>/<comarca>/<muni>/dealers/<cdp>/recipe.yaml)."""
        cdp = "CDP-ES-28-NEWLAYOUT"
        recipe_dir = tmp_path / "countries" / "ES" / "28" / "centro" / "madrid" / "dealers" / cdp
        recipe_dir.mkdir(parents=True)
        (recipe_dir / "recipe.yaml").write_text("source: test\n")

        found = _resolve_recipe_path(cdp, tmp_path)
        assert found is not None
        assert found.exists()
        assert found.name == "recipe.yaml"
        assert cdp in str(found)

    def test_finds_tier1_layout(self, tmp_path: Path) -> None:
        """Tier-1 layout (countries/ES/_tier1/<cdp>/recipe.yaml)."""
        cdp = "CDP-ES-00-TIER1TST"
        recipe_dir = tmp_path / "countries" / "ES" / "_tier1" / cdp
        recipe_dir.mkdir(parents=True)
        (recipe_dir / "recipe.yaml").write_text("source: tier1\n")

        found = _resolve_recipe_path(cdp, tmp_path)
        assert found is not None
        assert found.exists()

    def test_falls_back_to_legacy_flat(self, tmp_path: Path) -> None:
        """Legacy flat layout (countries/ES/recipes/<cdp>.yaml) is the fallback."""
        cdp = "CDP-ES-41-FLATFBCK"
        flat_dir = tmp_path / "countries" / "ES" / "recipes"
        flat_dir.mkdir(parents=True)
        (flat_dir / f"{cdp}.yaml").write_text("source: legacy\n")

        found = _resolve_recipe_path(cdp, tmp_path)
        assert found is not None
        assert found.exists()
        assert found.name == f"{cdp}.yaml"

    def test_new_layout_preferred_over_legacy(self, tmp_path: Path) -> None:
        """When both exist, the new geo layout is returned (glob finds it first)."""
        cdp = "CDP-ES-08-BOTHLAYO"
        # New geo layout
        new_dir = tmp_path / "countries" / "ES" / "08" / "_sin-comarca" / "_sin-municipio" / "dealers" / cdp
        new_dir.mkdir(parents=True)
        (new_dir / "recipe.yaml").write_text("layout: new\n")
        # Legacy flat
        flat_dir = tmp_path / "countries" / "ES" / "recipes"
        flat_dir.mkdir(parents=True)
        (flat_dir / f"{cdp}.yaml").write_text("layout: legacy\n")

        found = _resolve_recipe_path(cdp, tmp_path)
        assert found is not None
        assert found.read_text() == "layout: new\n"

    def test_returns_none_when_absent(self, tmp_path: Path) -> None:
        """No recipe in either layout → None."""
        (tmp_path / "countries" / "ES").mkdir(parents=True)
        found = _resolve_recipe_path("CDP-ES-00-NOSUCHCD", tmp_path)
        assert found is None


# ---------------------------------------------------------------------------
# 4. _check_g3_git_subsignal() — missing file path
# ---------------------------------------------------------------------------

class TestG3GitSubsignalMissing:
    def test_missing_in_both_layouts_returns_file_missing(self, tmp_path: Path) -> None:
        """When recipe is absent in both layouts, sub-signal reports file_missing."""
        from pipeline.complete import _check_g3_git_subsignal

        (tmp_path / "countries" / "ES").mkdir(parents=True)
        sha, reason = _check_g3_git_subsignal("CDP-ES-99-NOTEXIST", repo_root=tmp_path)
        assert sha is None
        assert "recipe_file_missing" in reason

    def test_found_in_legacy_flat_proceeds_to_git(self, tmp_path: Path) -> None:
        """When recipe exists (flat), sub-signal tries git (will fail: no .git)."""
        from pipeline.complete import _check_g3_git_subsignal

        cdp = "CDP-ES-28-FLATONLY"
        flat_dir = tmp_path / "countries" / "ES" / "recipes"
        flat_dir.mkdir(parents=True)
        (flat_dir / f"{cdp}.yaml").write_text("source: test\n")

        sha, reason = _check_g3_git_subsignal(cdp, repo_root=tmp_path)
        # No .git in tmp_path → either git_unavailable or recipe_not_tracked
        # (depends on whether git binary is on PATH; both are valid sub-signal outcomes)
        assert sha is None
        assert reason in (
            "git_unavailable",
            "git_subsignal:recipe_not_tracked",
            "git_subsignal:recipe_not_committed_at_HEAD",
        )

    def test_found_in_new_geo_layout_proceeds_to_git(self, tmp_path: Path) -> None:
        """When recipe exists in new geo layout, sub-signal finds it and tries git."""
        from pipeline.complete import _check_g3_git_subsignal

        cdp = "CDP-ES-28-NEWGEOONLY"
        geo_dir = tmp_path / "countries" / "ES" / "_tier1" / cdp
        geo_dir.mkdir(parents=True)
        (geo_dir / "recipe.yaml").write_text("source: tier1\n")

        sha, reason = _check_g3_git_subsignal(cdp, repo_root=tmp_path)
        assert sha is None
        assert reason in (
            "git_unavailable",
            "git_subsignal:recipe_not_tracked",
            "git_subsignal:recipe_not_committed_at_HEAD",
        )

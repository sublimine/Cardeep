#!/usr/bin/env python3
"""SU-E2 — Recipe geo-reshape + Tier-1 separation.

Deterministically re-routes every countries/ES/recipes/<cdp>.yaml to its
canonical new location:

  Tier-1 (entity.is_tier1 = TRUE)
      → countries/ES/_tier1/<cdp>/recipe.yaml

  National platforms (is_tier1=FALSE AND province_code IS NULL)
      → countries/ES/_platforms/<source_group>/<cdp>/recipe.yaml
      <source_group> = the entity.source_group value, or '_unknown' if NULL.

  Geo dealers (province_code IS NOT NULL)
      → countries/ES/<province_code>/<comarca_slug>/<municipality_slug>/
            dealers/<cdp>/recipe.yaml
      comarca_slug  : slugified geo_comarca.name  (NULL → '_sin-comarca')
      municipality_slug: slugified geo_municipality.name (NULL → '_sin-municipio')

  Orphan (no entity row for the cdp)
      → countries/ES/_orphan/<cdp>/recipe.yaml

Usage:
    python scripts/reshape_recipes_geo.py [--dry-run] [--apply]

Default: --dry-run (no filesystem changes).
--apply: executes `git mv` for each unmoved recipe.  Idempotent; already-moved
         recipes are skipped.  NEVER deletes, NEVER overwrites.

Count invariant: sum of all buckets == number of recipe files on disk.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import unicodedata
from pathlib import Path, PurePosixPath
from typing import NamedTuple

import asyncpg  # type: ignore[import-untyped]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CARDEEP_DSN: str = os.environ.get(
    "CARDEEP_DSN",
    "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep",
)

_REPO_ROOT: Path = Path(__file__).resolve().parent.parent
_RECIPES_DIR: Path = _REPO_ROOT / "countries" / "ES" / "recipes"
_COUNTRIES_ES: Path = _REPO_ROOT / "countries" / "ES"

# Tier-1 classification: entity.is_tier1 = TRUE
# (is_tier1 is the authoritative flag; source_group is informational only)
_MARKETPLACE_GROUPS: frozenset[str] = frozenset(
    {"marketplace_motor", "marketplace_generalist"}
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slug(name: str | None) -> str:
    """Return a deterministic, filesystem-safe slug from a geo name.

    Rules:
      - NULL / empty → returns empty string (caller substitutes sentinel)
      - NFD decompose → strip combining marks (accent removal)
      - lowercase
      - non-alphanumeric chars → '-'
      - collapse consecutive '-' to one
      - strip leading/trailing '-'
    """
    if not name:
        return ""
    # NFD decompose and strip combining characters (accents)
    nfd = unicodedata.normalize("NFD", name)
    ascii_approx = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    lowered = ascii_approx.lower()
    # Replace any non-alphanumeric character with '-'
    chars: list[str] = []
    for ch in lowered:
        chars.append(ch if ch.isalnum() else "-")
    joined = "".join(chars)
    # Collapse repeated dashes and strip edges
    while "--" in joined:
        joined = joined.replace("--", "-")
    return joined.strip("-")


class RecipeRow(NamedTuple):
    """All data needed to route one recipe file."""

    cdp_code: str
    source_group: str | None
    is_tier1: bool
    province_code: str | None      # CHAR(2) trimmed; None = national
    municipality_code: str | None  # CHAR(5) trimmed
    comarca_id: int | None
    comarca_name: str | None
    muni_name: str | None


def _compute_target(row: RecipeRow) -> Path:
    """Return the target Path (relative to _REPO_ROOT) for this recipe row."""
    cdp = row.cdp_code

    # --- Tier-1 ---
    if row.is_tier1:
        return _COUNTRIES_ES / "_tier1" / cdp / "recipe.yaml"

    # --- National platform (province NULL and NOT tier1) ---
    if not row.province_code:
        sg = (row.source_group or "_unknown").strip()
        return _COUNTRIES_ES / "_platforms" / sg / cdp / "recipe.yaml"

    # --- Geo dealer (province_code present) ---
    prov = row.province_code.strip()

    comarca_slug = _slug(row.comarca_name) if row.comarca_name else ""
    comarca_part = comarca_slug if comarca_slug else "_sin-comarca"

    muni_slug = _slug(row.muni_name) if row.muni_name else ""
    muni_part = muni_slug if muni_slug else "_sin-municipio"

    return (
        _COUNTRIES_ES / prov / comarca_part / muni_part / "dealers" / cdp / "recipe.yaml"
    )


def _orphan_target(cdp_code: str) -> Path:
    """Target for a recipe with no entity row."""
    return _COUNTRIES_ES / "_orphan" / cdp_code / "recipe.yaml"


# ---------------------------------------------------------------------------
# DB query
# ---------------------------------------------------------------------------

async def _fetch_routing_data(cdp_codes: list[str]) -> dict[str, RecipeRow]:
    """Return a mapping cdp_code → RecipeRow for every cdp that exists in entity."""
    conn: asyncpg.Connection = await asyncpg.connect(CARDEEP_DSN)
    try:
        rows = await conn.fetch(
            """
            SELECT
                e.cdp_code,
                e.source_group::text          AS source_group,
                e.is_tier1,
                TRIM(e.province_code)         AS province_code,
                TRIM(e.municipality_code)     AS municipality_code,
                e.comarca_id,
                gc.name                       AS comarca_name,
                gm.name                       AS muni_name
            FROM entity e
            LEFT JOIN geo_comarca    gc ON gc.id    = e.comarca_id
            LEFT JOIN geo_municipality gm ON gm.code = e.municipality_code
            WHERE e.cdp_code = ANY($1::text[])
            """,
            cdp_codes,
        )
    finally:
        await conn.close()

    result: dict[str, RecipeRow] = {}
    for r in rows:
        result[r["cdp_code"]] = RecipeRow(
            cdp_code=r["cdp_code"],
            source_group=r["source_group"],
            is_tier1=bool(r["is_tier1"]),
            province_code=r["province_code"] or None,
            municipality_code=r["municipality_code"] or None,
            comarca_id=r["comarca_id"],
            comarca_name=r["comarca_name"],
            muni_name=r["muni_name"],
        )
    return result


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def _discover_recipes() -> list[Path]:
    """Return sorted list of existing flat CDP recipe files.

    Excludes non-CDP files (e.g. family_*.yaml templates) that also live in
    the recipes/ directory but are not per-dealer recipe files.
    """
    return sorted(_RECIPES_DIR.glob("CDP-ES-*.yaml"))


def _build_routing_plan(
    recipe_files: list[Path],
    entity_map: dict[str, RecipeRow],
) -> list[tuple[Path, Path, str]]:
    """Build the full routing plan.

    Returns list of (source_abs, target_abs, bucket_label) for each recipe.
    """
    plan: list[tuple[Path, Path, str]] = []
    for recipe_path in recipe_files:
        cdp_code = recipe_path.stem  # filename without .yaml
        if cdp_code in entity_map:
            row = entity_map[cdp_code]
            target = _compute_target(row)
            # Determine bucket label for reporting
            if row.is_tier1:
                bucket = "_tier1"
            elif not row.province_code:
                sg = (row.source_group or "_unknown").strip()
                bucket = f"_platforms/{sg}"
            else:
                prov = row.province_code.strip()
                comarca_slug = _slug(row.comarca_name) if row.comarca_name else ""
                comarca_part = comarca_slug if comarca_slug else "_sin-comarca"
                muni_slug = _slug(row.muni_name) if row.muni_name else ""
                muni_part = muni_slug if muni_slug else "_sin-municipio"
                bucket = f"geo/{prov}/{comarca_part}/{muni_part}"
        else:
            target = _orphan_target(cdp_code)
            bucket = "_orphan"

        plan.append((recipe_path, target, bucket))
    return plan


def _summarise(plan: list[tuple[Path, Path, str]]) -> dict[str, int]:
    """Return bucket → count mapping from the routing plan."""
    counts: dict[str, int] = {}
    for _src, _tgt, bucket in plan:
        # Normalise geo entries to top-level keys for summary
        top_key: str
        if bucket.startswith("geo/"):
            parts = bucket.split("/")
            prov = parts[1] if len(parts) > 1 else "?"
            # Further detail: _sin-comarca or _sin-municipio
            comarca = parts[2] if len(parts) > 2 else ""
            muni = parts[3] if len(parts) > 3 else ""
            if comarca == "_sin-comarca":
                top_key = f"geo/prov={prov}/_sin-comarca"
            elif muni == "_sin-municipio":
                top_key = f"geo/prov={prov}/_sin-municipio"
            else:
                top_key = f"geo/prov={prov}"
        else:
            top_key = bucket
        counts[top_key] = counts.get(top_key, 0) + 1
    return counts


def _print_dry_run_report(
    plan: list[tuple[Path, Path, str]],
    recipe_files: list[Path],
) -> None:
    """Print the dry-run routing summary without touching the filesystem."""
    total = len(recipe_files)
    counts = _summarise(plan)

    print("=" * 70)
    print("SU-E2 DRY-RUN — recipe geo-reshape routing summary")
    print("=" * 70)
    print(f"\nTotal recipe files on disk : {total}")
    print(f"Total entries in routing plan: {len(plan)}")
    print()

    # Tier-1
    tier1_count = sum(v for k, v in counts.items() if k == "_tier1")
    print(f"  _tier1                    : {tier1_count:>4}")

    # Platforms
    for key, cnt in sorted(counts.items()):
        if key.startswith("_platforms/"):
            print(f"  {key:<36}: {cnt:>4}")

    # Orphans
    orphan_count = counts.get("_orphan", 0)
    print(f"  _orphan                   : {orphan_count:>4}")

    # Geo totals (by province)
    geo_by_prov: dict[str, int] = {}
    for key, cnt in counts.items():
        if key.startswith("geo/"):
            prov = key.split("/")[1].split("=")[1] if "=" in key else key.split("/")[1]
            geo_by_prov[prov] = geo_by_prov.get(prov, 0) + cnt

    geo_total = sum(geo_by_prov.values())
    sin_comarca_total = sum(v for k, v in counts.items() if "_sin-comarca" in k)
    sin_muni_total = sum(v for k, v in counts.items() if "_sin-municipio" in k)

    print(f"\n  geo dealers total         : {geo_total:>4}")
    print(f"    of which _sin-comarca   : {sin_comarca_total:>4}")
    print(f"    of which _sin-municipio : {sin_muni_total:>4}")

    if geo_by_prov:
        print("\n  Geo breakdown by province:")
        for prov in sorted(geo_by_prov):
            print(f"    prov={prov}               : {geo_by_prov[prov]:>4}")

    # Count assertion
    plan_total = len(plan)
    print()
    print("-" * 70)
    assert_label = "PASS" if plan_total == total else f"FAIL  delta={plan_total - total}"
    print(f"ASSERT: sum-of-plan ({plan_total}) == on-disk CDP ({total}) : {assert_label}")
    print("-" * 70)
    if plan_total != total:
        sys.exit(1)

    # 10 sample mappings
    print("\n10 sample source -> target mappings:")
    for i, (src, tgt, bucket) in enumerate(plan[:10]):
        src_rel = src.relative_to(_REPO_ROOT)
        tgt_rel = tgt.relative_to(_REPO_ROOT)
        print(f"  [{bucket[:20]:<20}] {str(src_rel)} -> {str(tgt_rel)}")

    # Orphan detail
    if orphan_count:
        print(f"\nORPHAN recipes ({orphan_count}) — cdp_codes with no entity row:")
        for src, tgt, bucket in plan:
            if bucket == "_orphan":
                print(f"  {src.stem}")
    else:
        print("\nNo orphan recipes - all cdp_codes have entity rows.")


def _git_mv(src: Path, dst: Path, repo_root: Path) -> None:
    """Execute git mv -f src dst, creating parent directory first.

    The -f (force) overwrites an existing target: this is the staging→canonical
    reconcile. write_recipe writes fresh recipes to the flat staging dir
    (countries/ES/recipes/<cdp>.yaml); re-running the reshape moves each into its
    geo-tree home, OVERWRITING any stale copy a prior reshape left there. Without
    -f, `git mv` fails when the target exists (a re-harvested dealer) and the flat
    duplicate would linger — exactly the coherence bug the local harvest validation
    surfaced (an audi run re-created the flat recipe alongside its geo-tree copy).
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    src_rel = str(PurePosixPath(src.relative_to(repo_root)))
    dst_rel = str(PurePosixPath(dst.relative_to(repo_root)))
    result = subprocess.run(
        ["git", "mv", "-f", src_rel, dst_rel],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        # write_recipe writes fresh recipes to the flat staging dir UNTRACKED; git mv
        # only moves tracked files. For an untracked source, do a plain filesystem move
        # (overwriting any stale tracked target) + stage the result, so the reconcile
        # still lands the recipe in its geo-tree home.
        if "not under version control" in stderr or "not under source control" in stderr:
            import shutil
            shutil.move(str(src), str(dst))
            add = subprocess.run(
                ["git", "add", dst_rel], cwd=str(repo_root),
                capture_output=True, text=True, timeout=30,
            )
            if add.returncode != 0:
                raise RuntimeError(f"git add after untracked move failed: {add.stderr.strip()}")
            return
        raise RuntimeError(
            f"git mv failed: {stderr}\n  src={src_rel}\n  dst={dst_rel}"
        )


def _apply(plan: list[tuple[Path, Path, str]], recipe_files: list[Path]) -> None:
    """Execute the move plan using git mv.  Idempotent."""
    total = len(plan)
    moved = 0
    skipped = 0
    errors: list[str] = []

    for src, tgt, _bucket in plan:
        if not src.exists():
            # Already moved (target may already exist)
            if tgt.exists():
                skipped += 1
                continue
            errors.append(f"MISSING: {src} (and target {tgt} also absent)")
            continue

        if tgt.exists() and tgt.samefile(src):
            skipped += 1
            continue

        if tgt == src:
            skipped += 1
            continue

        try:
            _git_mv(src, tgt, _REPO_ROOT)
            moved += 1
        except RuntimeError as exc:
            errors.append(str(exc))

    print(f"\nMoved  : {moved}")
    print(f"Skipped: {skipped}")
    print(f"Total  : {total}")

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    # Re-assert on-disk count
    remaining_flat = list(_RECIPES_DIR.glob("CDP-ES-*.yaml"))
    new_total = sum(
        1 for _, tgt, _ in plan if tgt.exists()
    )
    print(f"\nPost-apply recipe count check:")
    print(f"  Flat recipes remaining : {len(remaining_flat)}")
    print(f"  Targets now present    : {new_total}")
    print(f"  Expected total         : {total}")
    if len(remaining_flat) + new_total == total:
        print("  COUNT INVARIANT: PASS")
    else:
        print("  COUNT INVARIANT: FAIL")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def _main(dry_run: bool) -> None:
    recipe_files = _discover_recipes()
    if not recipe_files:
        print(f"ERROR: no recipe files found under {_RECIPES_DIR}", file=sys.stderr)
        sys.exit(1)

    cdp_codes = [p.stem for p in recipe_files]
    print(f"Loading routing data from DB for {len(cdp_codes)} recipes...")
    entity_map = await _fetch_routing_data(cdp_codes)
    print(f"Entity rows found: {len(entity_map)} / {len(cdp_codes)}")

    plan = _build_routing_plan(recipe_files, entity_map)

    if dry_run:
        _print_dry_run_report(plan, recipe_files)
    else:
        print("=" * 70)
        print("SU-E2 APPLY — executing git mv moves")
        print("=" * 70)
        _apply(plan, recipe_files)
        print("\nAll moves complete.  Run --dry-run to verify new layout.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SU-E2 recipe geo-reshape + Tier-1 separation"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        default=True,
        help="Print routing plan only — no filesystem changes (DEFAULT)",
    )
    mode.add_argument(
        "--apply",
        dest="dry_run",
        action="store_false",
        help="Execute git mv moves (Director-only)",
    )
    args = parser.parse_args()

    import asyncio

    asyncio.run(_main(dry_run=args.dry_run))


if __name__ == "__main__":
    main()

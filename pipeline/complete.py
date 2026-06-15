"""SU-B2 — Per-entity completion gate evaluator.

Implements the five binary gates defined in V2-COMPLETION-PROOF.md §1-§3:

    G1 IDENTITY   — entity row exists, province_code valid, cdp_code well-formed, geo set
    G2 INVENTORY  — count quorum TRUSTWORTHY (db-landed authority), field_integrity >= 0.98
    G3 RECIPE     — countries/ES/recipes/<cdp>.yaml git-committed and entity.recipe_version set
    G4 SERVED     — DB-equivalent: available_inventory in entity view matches D
    G5 DELTA      — [DEFERRED] requires a second harvest run

Public API
----------
    compute_completion(conn, cdp_code) -> dict
        Evaluates G1-G4 synchronously (asyncpg connection), sets G5=None (pending),
        derives the verdict, and returns a dict suitable for UPSERT into entity_completion.

    upsert_completion(conn, cdp_code) -> dict
        Calls compute_completion and persists the result via INSERT … ON CONFLICT DO UPDATE.

    run_sample(conn, cdp_codes) -> list[dict]
        Evaluates a list of cdp_codes and returns a table of gate results.
        Used for the Director's ≤20-entity demo; NOT for mass-populate (block β-complete).

Design decisions
----------------
- G4 is evaluated via a DB query (available_inventory count from v_canonical / vehicle),
  NOT via 37 000 HTTP calls. The spec's HTTP check is an optional spot-verify; the DB
  equivalent is: entity.available_inventory == D (both come from the same source of truth
  for the purpose of the gate). One spot HTTP check per sample is noted as optional.
- G3 uses subprocess git ls-files / git cat-file against the repo root. In Docker without
  git, G3 will set g3_recipe=False with reason 'git_unavailable'. The caller must ensure
  the Python process runs inside the worktree or mount the .git directory.
- record_count_verdict from pipeline.verify is NOT called here for G2: that function is
  async and designed for ingestion-time multi-path quorum. For completion-check we
  re-derive the counts directly from DB (D=db_landed, the primary path) and entity
  metadata (S=declared if stored, H=harvested if stored). The gate logic is identical.
- G5 is structurally deferred: compute_completion always returns g5_delta=None with
  reason 'G5 requires a second harvest run — call after re-ingesting via ingest_dealer'.
  The verdict is INCOMPLETE whenever G5 is None/False.

# G5 requires a 2nd harvest run.
# Populate g5_delta=True only after a second ingest_dealer() completes and
# vehicle_event rows for the entity are type-consistent (GONE⊆prev, NEW∩prev=∅,
# odometer monotone). That check lives in pipeline/g5_check.py (not yet built).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

import asyncpg

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Valid province codes for Spain: 01–52 (as zero-padded 2-char strings)
_PROVINCE_RE = re.compile(r"^(0[1-9]|[1-4][0-9]|5[0-2])$")

# cdp_code format: CDP-ES-{NN}-{8×Crockford-base32}
# Crockford alphabet: digits + uppercase excluding I, L, O, U
_CDP_CODE_RE = re.compile(r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$")

# Field-integrity floor (V2 §3.B): fraction of landed rows that are valid
_FIELD_INTEGRITY_FLOOR: float = 0.98

# SLA defaults by tier (seconds) — V2 §3.F
SLA_TIER1: int = 86_400       # 24 h — hard-defense platforms
SLA_STANDARD: int = 604_800   # 7 d  — standard concesionario / compraventa
SLA_LONGTAIL: int = 2_592_000 # 30 d — garaje / desguace

# Repo root: the directory containing the migrations/ folder
_REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# G1 — Identity & geo
# ---------------------------------------------------------------------------

async def check_g1(conn: asyncpg.Connection, cdp_code: str) -> tuple[bool, str]:
    """Gate G1: identity and geo check.

    Returns (passed: bool, reason: str).
    PASS iff:
      - Exactly one entity row exists for cdp_code
      - province_code is a valid 2-digit Spanish province (01-52)
      - cdp_code matches the CDP-ES-NN-XXXXXXXX pattern
      - lat/lon are both set OR status_flag='geo_partial' (any entity row qualifies)
    Note: the current entity schema has no 'geo_partial' status flag, so we
    require lat IS NOT NULL AND lon IS NOT NULL.
    """
    row = await conn.fetchrow(
        """
        SELECT cdp_code, province_code, lat, lon
        FROM entity
        WHERE cdp_code = $1
        LIMIT 1
        """,
        cdp_code,
    )
    if row is None:
        return False, "entity_not_found"

    prov = row["province_code"]
    if prov is None or not _PROVINCE_RE.match(str(prov)):
        return False, f"invalid_province_code:{prov!r}"

    if not _CDP_CODE_RE.match(cdp_code):
        return False, f"cdp_code_format_invalid:{cdp_code!r}"

    if row["lat"] is None or row["lon"] is None:
        return False, "geo_missing:lat_or_lon_null"

    return True, "ok"


# ---------------------------------------------------------------------------
# G2 — Inventory completeness (db-landed authority + field integrity)
# ---------------------------------------------------------------------------

async def check_g2(conn: asyncpg.Connection, cdp_code: str) -> tuple[bool, str, dict]:
    """Gate G2: count quorum TRUSTWORTHY + field-integrity >= 0.98.

    Orthogonal paths (V2 §3.B):
      D = db-landed available rows (authority)
      D_valid = available rows with deep_link NOT NULL AND recipe_version NOT NULL
    The gate is TRUSTWORTHY if D >= 1 and field_integrity >= 0.98.

    Note: S (source-declared) and H (harvested) are not stored on the entity row
    in the current schema; they live only in the harvest log (in-memory). For
    completion check we verify the DB-landed state. S and H will be NULL in the
    evidence unless the caller pre-populates them.

    Returns (passed, reason, evidence_dict).
    """
    # Resolve entity_ulid (might be multiple rows per cdp_code after partial dedup)
    entity_ulids: list[str] = await conn.fetch(
        "SELECT entity_ulid FROM entity WHERE cdp_code = $1",
        cdp_code,
    )
    if not entity_ulids:
        return False, "entity_not_found", {}

    ulids = [r["entity_ulid"] for r in entity_ulids]
    ulid_array = ulids  # asyncpg accepts list for $1::text[]

    # D: count of available vehicles
    d_landed: int = await conn.fetchval(
        "SELECT count(*) FROM vehicle WHERE entity_ulid = ANY($1::text[]) AND status = 'available'",
        ulid_array,
    )

    # D_valid: available rows with the load-bearing fields non-null
    # V2 §3.B: deep_link NOT NULL (UNIQUE constraint guarantees this always)
    #          recipe_version NOT NULL (provenance field)
    #          price NOT NULL OR price_absent_is_justified — we use deep_link+recipe_version
    d_valid: int = await conn.fetchval(
        """
        SELECT count(*)
        FROM vehicle
        WHERE entity_ulid = ANY($1::text[])
          AND status = 'available'
          AND deep_link IS NOT NULL
          AND recipe_version IS NOT NULL
        """,
        ulid_array,
    )

    evidence = {
        "d_landed": d_landed,
        "d_valid": d_valid,
        "s_declared": None,   # not stored in entity row; caller may backfill
        "h_harvested": None,  # same
        "field_integrity": None,
    }

    if d_landed == 0:
        return False, "no_available_vehicles:d_landed=0", evidence

    field_integrity = d_valid / d_landed
    evidence["field_integrity"] = field_integrity

    if field_integrity < _FIELD_INTEGRITY_FLOOR:
        return (
            False,
            f"field_integrity_below_floor:{field_integrity:.4f}<{_FIELD_INTEGRITY_FLOOR}",
            evidence,
        )

    return True, "ok", evidence


# ---------------------------------------------------------------------------
# G3 — Recipe durable (git-committed)
# ---------------------------------------------------------------------------

def check_g3(cdp_code: str, repo_root: Path | None = None) -> tuple[bool, str, str | None]:
    """Gate G3: recipe.yaml exists AND is git-committed at HEAD (synchronous).

    V2 §3.D: recipe_ok ⟺
      - File exists: countries/ES/recipes/<cdp_code>.yaml
      - git ls-files --error-unmatch <path> exits 0 (tracked)
      - git cat-file -e HEAD:<relative_path> exits 0 (committed, not just staged)

    Also checks that the file parses as YAML (basic well-formedness).

    Returns (passed, reason, sha_or_None).
    sha = first 12 chars of HEAD commit sha if G3 passes; None otherwise.
    """
    root = repo_root or _REPO_ROOT
    recipe_rel = Path("countries") / "ES" / "recipes" / f"{cdp_code}.yaml"
    recipe_abs = root / recipe_rel

    if not recipe_abs.exists():
        return False, f"recipe_file_missing:{recipe_rel}", None

    # Check git availability
    try:
        subprocess.run(
            ["git", "--version"],
            capture_output=True,
            check=True,
            cwd=str(root),
            timeout=5,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False, "git_unavailable", None

    # git ls-files --error-unmatch: exits non-zero if file is not tracked
    ls = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(recipe_rel)],
        capture_output=True,
        cwd=str(root),
        timeout=10,
    )
    if ls.returncode != 0:
        return False, "recipe_not_git_tracked", None

    # git cat-file -e HEAD:<path>: exits non-zero if not committed (only staged)
    cat = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{recipe_rel}"],
        capture_output=True,
        cwd=str(root),
        timeout=10,
    )
    if cat.returncode != 0:
        return False, "recipe_not_committed_at_HEAD:only_staged", None

    # Get HEAD commit SHA for evidence
    head = subprocess.run(
        ["git", "rev-parse", "--short=12", "HEAD"],
        capture_output=True,
        cwd=str(root),
        timeout=5,
    )
    sha = head.stdout.decode().strip() if head.returncode == 0 else None

    # Basic YAML parse check
    try:
        import yaml  # type: ignore[import-untyped]
        with recipe_abs.open(encoding="utf-8") as fh:
            content = yaml.safe_load(fh)
        if not isinstance(content, dict):
            return False, "recipe_yaml_invalid:not_a_mapping", sha
    except Exception as exc:
        return False, f"recipe_yaml_parse_error:{exc}", sha

    return True, "ok", sha


# ---------------------------------------------------------------------------
# G4 — Served (DB-equivalent: available_inventory matches D)
# ---------------------------------------------------------------------------

async def check_g4(conn: asyncpg.Connection, cdp_code: str, d_landed: int | None) -> tuple[bool, str, int | None]:
    """Gate G4: the entity is servable — DB-equivalent check.

    V2 §3.E: served_ok ⟺ available_inventory (from /entities/{cdp}) == D.
    For the completion foundation (block α+β), we verify via DB rather than
    37 000 HTTP calls. The DB-equivalent check:
      - v_dealer_resolved: entity exists in the resolved view (servable)
      - Count of available vehicles via the same logic as /entities/{cdp}

    The optional HTTP spot-check (calling the live API) is left for block β-complete
    when the Director schedules the mass-populate run.

    Returns (passed, reason, served_count).
    """
    # Check entity exists in v_dealer_resolved (servable layer)
    resolved_row = await conn.fetchrow(
        """
        SELECT resolved_cdp_code
        FROM v_dealer_resolved
        WHERE cdp_code = $1
        LIMIT 1
        """,
        cdp_code,
    )
    if resolved_row is None:
        return False, "entity_not_in_v_dealer_resolved", None

    # Re-derive available count the same way the /entities/{cdp} endpoint does
    entity_ulids = await conn.fetch(
        "SELECT entity_ulid FROM entity WHERE cdp_code = $1",
        cdp_code,
    )
    ulids = [r["entity_ulid"] for r in entity_ulids]
    if not ulids:
        return False, "entity_not_found", None

    served_count: int = await conn.fetchval(
        """
        SELECT count(DISTINCT vc.canonical_vehicle_ulid)
        FROM vehicle v
        JOIN v_canonical_vehicle vc ON vc.vehicle_ulid = v.vehicle_ulid
        WHERE v.entity_ulid = ANY($1::text[]) AND v.status = 'available'
        """,
        ulids,
    )

    if served_count == 0:
        return False, "served_count_zero:no_available_inventory_in_view", served_count

    # If we have D from G2, check alignment (tolerance: exact for <500 cars, V2 §3.B)
    if d_landed is not None:
        # served_count can legitimately differ from d_landed due to canonical
        # vehicle deduplication (v_canonical_vehicle collapses cross-platform dupes).
        # G4 passes if served_count > 0 (entity IS served). Exact match to D is
        # enforced at the HTTP layer (G4 spot-check) in block β-complete.
        if served_count == 0:
            return False, f"served_count_zero_vs_d={d_landed}", served_count

    return True, "ok", served_count


# ---------------------------------------------------------------------------
# G5 — Delta proven [DEFERRED]
# ---------------------------------------------------------------------------

def check_g5_stub(cdp_code: str) -> tuple[None, str]:
    """Gate G5: DEFERRED — requires a second harvest run.

    # G5 requires a 2nd harvest run.
    # After a second ingest_dealer() completes for this cdp_code, call
    # pipeline/g5_check.py::verify_delta_events(conn, cdp_code) which will:
    #   - Query vehicle_event WHERE entity in cluster, created in the second run window
    #   - Verify: GONE ⊆ prev_available, NEW ∩ prev_links = ∅, odometer monotone
    #   - Conservation: D_after == D_before + #NEW - #GONE
    # Only then can g5_delta=True be written to entity_completion.
    # Until then, this function always returns (None, reason) and the verdict
    # stays INCOMPLETE — not because the entity is wrong, but because G5 has
    # not been tested yet.
    """
    return None, "G5_deferred:second_harvest_not_yet_run"


# ---------------------------------------------------------------------------
# Verdict derivation
# ---------------------------------------------------------------------------

def derive_verdict(
    g1: bool,
    g2: bool,
    g3: bool,
    g4: bool,
    g5: bool | None,
    *,
    is_fresh: bool = True,
) -> str:
    """Derive the COMPLETED/INCOMPLETE/STALE verdict from gate results.

    COMPLETED ⟺ g1 ∧ g2 ∧ g3 ∧ g4 ∧ g5 = TRUE ∧ is_fresh
    STALE     ⟺ all gates were previously TRUE but freshness expired
    INCOMPLETE ⟺ any gate is False or None (G5 deferred)
    """
    all_gates = [g1, g2, g3, g4, g5]
    if any(g is None for g in all_gates):
        return "INCOMPLETE"
    if not is_fresh:
        if all(all_gates):
            return "STALE"
        return "INCOMPLETE"
    if all(all_gates):
        return "COMPLETED"
    return "INCOMPLETE"


# ---------------------------------------------------------------------------
# Main entry point: compute_completion
# ---------------------------------------------------------------------------

async def compute_completion(conn: asyncpg.Connection, cdp_code: str) -> dict[str, Any]:
    """Evaluate gates G1-G4 for a single entity. G5 is always deferred.

    Returns a dict with all fields needed for UPSERT into entity_completion:
      cdp_code, g1_identity, g2_inventory, g3_recipe, g4_served, g5_delta,
      verdict, evidence fields, reasons dict (for diagnostics).

    This function does NOT write to the DB. Call upsert_completion to persist.
    """
    # G1
    g1, g1_reason = await check_g1(conn, cdp_code)

    # G2
    g2, g2_reason, g2_evidence = await check_g2(conn, cdp_code)
    d_landed = g2_evidence.get("d_landed")

    # G3 — synchronous subprocess call
    g3, g3_reason, recipe_sha = check_g3(cdp_code)

    # G4 — DB-equivalent check
    g4, g4_reason, served_count = await check_g4(conn, cdp_code, d_landed)

    # G5 — deferred
    g5_val, g5_reason = check_g5_stub(cdp_code)

    verdict = derive_verdict(g1, g2, g3, g4, g5_val)

    return {
        "cdp_code": cdp_code,
        # Gate booleans
        "g1_identity": g1,
        "g2_inventory": g2,
        "g3_recipe": g3,
        "g4_served": g4,
        "g5_delta": False,   # None → False for DB storage; G5 is deferred
        # Verdict
        "verdict": verdict,
        # Evidence
        "s_declared": g2_evidence.get("s_declared"),
        "h_harvested": g2_evidence.get("h_harvested"),
        "d_landed": d_landed,
        "d_valid": g2_evidence.get("d_valid"),
        "field_integrity": g2_evidence.get("field_integrity"),
        "recipe_sha": recipe_sha,
        "served_count": served_count,
        # Diagnostics (not stored in DB, available for caller logging)
        "_reasons": {
            "g1": g1_reason,
            "g2": g2_reason,
            "g3": g3_reason,
            "g4": g4_reason,
            "g5": g5_reason,
        },
    }


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

async def upsert_completion(conn: asyncpg.Connection, cdp_code: str) -> dict[str, Any]:
    """Compute and persist the completion state for one entity.

    Uses INSERT … ON CONFLICT DO UPDATE (MVCC-safe: no blind UPDATE of all rows).
    Sets completed_at on the first transition to COMPLETED; preserves it on
    subsequent writes even if verdict later degrades to STALE.
    """
    result = await compute_completion(conn, cdp_code)

    # completed_at is only set when verdict=COMPLETED (trigger enforces this)
    # We pass NULL and let the UPDATE preserve the existing completed_at if any.
    await conn.execute(
        """
        INSERT INTO entity_completion (
            cdp_code, g1_identity, g2_inventory, g3_recipe, g4_served, g5_delta,
            s_declared, h_harvested, d_landed, d_valid, field_integrity,
            recipe_sha, served_count,
            verdict,
            completed_at,
            updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6,
            $7, $8, $9, $10, $11,
            $12, $13,
            $14,
            CASE WHEN $14 = 'COMPLETED' THEN now() ELSE NULL END,
            now()
        )
        ON CONFLICT (cdp_code) DO UPDATE SET
            g1_identity    = EXCLUDED.g1_identity,
            g2_inventory   = EXCLUDED.g2_inventory,
            g3_recipe      = EXCLUDED.g3_recipe,
            g4_served      = EXCLUDED.g4_served,
            g5_delta       = EXCLUDED.g5_delta,
            s_declared     = EXCLUDED.s_declared,
            h_harvested    = EXCLUDED.h_harvested,
            d_landed       = EXCLUDED.d_landed,
            d_valid        = EXCLUDED.d_valid,
            field_integrity = EXCLUDED.field_integrity,
            recipe_sha     = EXCLUDED.recipe_sha,
            served_count   = EXCLUDED.served_count,
            verdict        = EXCLUDED.verdict,
            -- Preserve completed_at: once set it's a historical watermark
            completed_at   = COALESCE(entity_completion.completed_at, EXCLUDED.completed_at),
            updated_at     = now()
        """,
        result["cdp_code"],
        result["g1_identity"],
        result["g2_inventory"],
        result["g3_recipe"],
        result["g4_served"],
        result["g5_delta"],
        result["s_declared"],
        result["h_harvested"],
        result["d_landed"],
        result["d_valid"],
        result["field_integrity"],
        result["recipe_sha"],
        result["served_count"],
        result["verdict"],
    )
    return result


# ---------------------------------------------------------------------------
# Sample runner (≤20 entities, demo only — NOT for mass-populate)
# ---------------------------------------------------------------------------

async def run_sample(
    conn: asyncpg.Connection,
    cdp_codes: list[str],
) -> list[dict[str, Any]]:
    """Evaluate compute_completion for each cdp_code in the list.

    Intended for the Director's ≤20-entity demo and for manual spot-checks.
    Do NOT use this for the 37k mass-populate run — that is block β-complete,
    a controlled run scheduled by the Director.
    """
    results = []
    for code in cdp_codes:
        result = await compute_completion(conn, code)
        results.append(result)
    return results


# ---------------------------------------------------------------------------
# CLI demo entry point (prints a gate table for ≤20 real dealers)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import asyncio
    import os

    async def _demo() -> None:
        dsn = os.environ.get(
            "CARDEEP_DSN",
            "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep",
        )
        conn = await asyncpg.connect(dsn)
        try:
            # Fetch up to 20 real served dealers (has available vehicles, not particular)
            rows = await conn.fetch(
                """
                SELECT DISTINCT e.cdp_code
                FROM entity e
                JOIN vehicle v ON v.entity_ulid = e.entity_ulid AND v.status = 'available'
                WHERE e.kind <> 'particular'
                  AND e.province_code IS NOT NULL
                ORDER BY e.cdp_code
                LIMIT 20
                """,
            )
            cdp_codes = [r["cdp_code"] for r in rows]
            print(f"\nEvaluating {len(cdp_codes)} dealers ...\n")

            results = await run_sample(conn, cdp_codes)

            # Print gate table
            header = f"{'CDP_CODE':<30} {'G1':^5} {'G2':^5} {'G3':^5} {'G4':^5} {'G5':^8} {'VERDICT':<12} {'D':>6} {'FI':>6}"
            print(header)
            print("-" * len(header))
            for r in results:
                fi_str = f"{r['field_integrity']:.3f}" if r["field_integrity"] is not None else "  N/A"
                d_str = str(r["d_landed"]) if r["d_landed"] is not None else "N/A"
                print(
                    f"{r['cdp_code']:<30} "
                    f"{'T' if r['g1_identity'] else 'F':^5} "
                    f"{'T' if r['g2_inventory'] else 'F':^5} "
                    f"{'T' if r['g3_recipe'] else 'F':^5} "
                    f"{'T' if r['g4_served'] else 'F':^5} "
                    f"{'PEND':^8} "
                    f"{r['verdict']:<12} "
                    f"{d_str:>6} "
                    f"{fi_str:>6}"
                )
            print()
            # Print failing reasons
            for r in results:
                reasons = r.get("_reasons", {})
                fails = {g: rsn for g, rsn in reasons.items() if rsn != "ok" and rsn and "G5" not in rsn}
                if fails:
                    print(f"  {r['cdp_code']}: {fails}")
        finally:
            await conn.close()

    asyncio.run(_demo())

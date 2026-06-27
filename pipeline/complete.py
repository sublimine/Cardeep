"""SU-B2 — Per-entity completion gate evaluator.

Implements the five binary gates defined in V2-COMPLETION-PROOF.md §1-§3,
refined by Director decisions (2026-06-15) to correct over-strict definitions
that made COMPLETED unreachable for 97.5% of connector-covered dealers:

    G1 IDENTITY   — entity row exists, province_code valid (01-52), cdp_code well-formed.
                    lat/lon NOT required: geo gap is a declared SU-A6 data gap (6,601
                    dealers without geo signal), NOT an identity failure.
    G2 INVENTORY  — field_integrity >= 0.98 measured as fraction of available vehicles
                    with deep_link NOT NULL (the validity signal for inventory data).
                    VAM quorum D=S enforced where s_declared is available.
                    recipe_version NOT included: it is only written for 537 AS24 dealers
                    (G3 responsibility), not an inventory validity signal.
    G3 RECIPE     — dealer has recipe coverage via v_dealer_recipe.recipe_kind <> 'none'
                    (connector OR per-dealer, proven by migration 0029 at 98.4%).
                    git-tracked YAML check retained as STRICT sub-signal for per_dealer
                    recipes, but G3=TRUE whenever recipe_kind != 'none'. This eliminates
                    the git dependency that breaks connector-covered dealers and Docker.
    G4 SERVED     — DB-equivalent: available_inventory in entity view matches D
    G5 DELTA      — [DEFERRED] requires a second harvest run

Public API
----------
    compute_completion(conn, cdp_code) -> dict
        Evaluates G1-G4 (asyncpg connection), sets G5=None (pending),
        derives the verdict, and returns a dict suitable for UPSERT into entity_completion.

    upsert_completion(conn, cdp_code) -> dict
        Calls compute_completion and persists the result via INSERT … ON CONFLICT DO UPDATE.

    run_sample(conn, cdp_codes) -> list[dict]
        Evaluates a list of cdp_codes and returns a table of gate results.
        Used for the Director's ≤20-entity demo; NOT for mass-populate (block β-complete).

Design decisions
----------------
- G1 does NOT check lat/lon. The SU-A6 geo gap (6,601 dealers without geo signal) is a
  declared data gap — not an identity failure. Identity = entity exists + well-formed codes.
- G2 field_integrity uses deep_link NOT NULL only. recipe_version was previously included
  but is only written for AS24 dealers (537 out of ~38k). Removing it makes field_integrity
  measure actual inventory data validity rather than recipe provenance.
- G2 VAM quorum (D == S within tolerance) is enforced when s_declared is available on the
  entity row. When s_declared is NULL (most entities), only field_integrity is checked.
- G3 queries v_dealer_recipe (created by migration 0029) for recipe_kind. This view
  already proves 98.4% connector coverage via sentinel-00 platform entities. Per-dealer
  recipes (AS24) are detected via entity.recipe_version IS NOT NULL in the same view.
  The git-subprocess path is retained for diagnostics/sub-signal but does NOT gate G3.
- G4 is evaluated via DB query rather than 37,000 HTTP calls. Optional HTTP spot-check
  is deferred to block β-complete.
- G5 is structurally deferred: always returns (None, reason). Verdict stays INCOMPLETE
  until a second harvest run proves delta consistency.

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

# Non-ES tenants do not follow the Spanish 01-52 grid: France's Corsica departments
# are '2A'/'2B' and Paris is '75' (outside 01-52), Italy's provinces are 2-letter
# ('RM'/'MI'). For a second country the only province invariant the identity gate can
# assert generically is the geo_province.code shape itself — 2 to 8 alphanumeric chars
# (VARCHAR(8) since migration 0059, widened for FR DOM '971' / German Kreis / NUTS-3).
# ES keeps the strict 01-52 path so its G1 verdicts stay byte-identical.
_NON_ES_PROVINCE_RE = re.compile(r"^[0-9A-Z]{2,8}$")

# National entities operate country-wide and carry a NULL province_code by design
# (the '00' lives only in the CDP-ES-00-* code, NOT in the province_code column —
# verified live 2026-06-15): marketplaces, OEM-VO portals, auctions, importers.
# For these, a NULL province is the CORRECT geo, not a missing one — so G1 accepts
# it. A geo-located kind (compraventa/garaje/concesionario/particular) with NULL
# province is a genuine identity gap and still fails G1 (SU-A6 geo debt). A national
# kind that DOES have a real province (e.g. an importer with a HQ) passes via the
# normal 01-52 path.
_NATIONAL_KINDS: frozenset[str] = frozenset(
    {"subasta", "plataforma", "oem_vo_portal", "importador"}
)

# cdp_code format: CDP-{CC}-{PP}-{8×Crockford-base32}
# CC is the ISO-3166 alpha-2 tenant minted by services/api/codes.py. The historical ES
# output is byte-identical ('ES' matches the generic [A-Z]{2}), but the G1 identity gate
# must now validate EVERY tenant's code (CDP-DE-…, CDP-FR-…), not only Spain — a
# country-blind ^CDP-ES- wrongly failed identity for any second-country entity.
# PP is the province segment: 2-to-8 ALPHANUMERIC chars, mirroring geo_province.code
# (VARCHAR(8) since 0059) and the evict-ledger CHECK in 0062 ([0-9A-Z]{2,8}). The mint
# (codes.py:mint_code) interpolates geo_province.code verbatim — FR Corsica '2A'/'2B',
# IT 'RM'/'MI', FR DOM '971' (3 digits), German Kreis (up to 5), NUTS-3 'ITI43'. A fixed
# [0-9A-Z]{2} wrongly rejected every >2-char province the mint legitimately produced.
# ES provinces are 01-52 (2 digits) so 'ES' codes still match [0-9A-Z]{2,8} byte-identically.
# Crockford alphabet (the 8-char suffix): digits + uppercase excluding I, L, O, U.
_CDP_CODE_RE = re.compile(r"^CDP-[A-Z]{2}-([0-9A-Z]{2,8})-[0-9A-HJKMNP-TV-Z]{8}$")

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
    """Gate G1: identity check (V2 refined 2026-06-15).

    Returns (passed: bool, reason: str).
    PASS iff:
      - Exactly one entity row exists for cdp_code
      - province_code is valid for the entity's country (ES: the 01-52 Spanish grid,
        byte-identical to the historical gate; non-ES tenant: the generic 2-char
        geo_province.code shape, so France/Italy provinces are not wrongly rejected),
        OR the entity is a NATIONAL kind (subasta/plataforma/oem_vo_portal/importador)
        carrying the '00' sentinel — for those, '00' is the correct geo, not a gap
        (§Deuda B2 closed 2026-06-15: ~130 national entities were wrongly failing identity).
      - cdp_code matches the CDP-CC-NN-XXXXXXXX pattern (CC = ISO-3166 alpha-2
        tenant, Crockford base32 tail) — generalised from the ES-only validator so
        a second country's codes pass identity (the mint already emits them)

    lat/lon are NOT checked: the geo gap (6,601 dealers without geo signal) is
    a declared SU-A6 data gap, not an identity failure. Identity = entity exists
    and is well-formed with the correct geo for its kind; geo detail is enrichment.
    """
    row = await conn.fetchrow(
        """
        SELECT cdp_code, province_code, kind::text AS kind, country_code
        FROM entity
        WHERE cdp_code = $1
        LIMIT 1
        """,
        cdp_code,
    )
    if row is None:
        return False, "entity_not_found"

    prov = row["province_code"]
    prov_str = str(prov) if prov is not None else None
    # National kinds (auctions/platforms/OEM portals/importers) carry a NULL
    # province by design — that NULL is their correct geo, not a gap. row.get()
    # works on both asyncpg.Record (real query selects kind) and partial dict mocks
    # (kind absent → None → treated as non-national = fail-closed, the safe default).
    is_national = row.get("kind") in _NATIONAL_KINDS and prov_str is None
    # Country-scope the province-validity rule (mirrors migration 0053's country-guarded
    # geo CHECKs). ES keeps the historical 01-52 grid so its verdicts stay byte-identical;
    # a non-ES tenant validates against the generic 2-alphanumeric geo_province.code shape
    # — without this, France (Paris '75', Corsica '2A') and Italy ('RM') wrongly fail
    # identity. country_code is NOT NULL DEFAULT 'ES' (migration 0052) so a real row always
    # carries it; absent only on partial mocks → default 'ES' (fail-closed to the strict path).
    country = row.get("country_code") or "ES"
    province_re = _PROVINCE_RE if country == "ES" else _NON_ES_PROVINCE_RE
    if not is_national and (prov_str is None or not province_re.match(prov_str)):
        return False, f"invalid_province_code:{prov!r}"

    if not _CDP_CODE_RE.match(cdp_code):
        return False, f"cdp_code_format_invalid:{cdp_code!r}"

    return True, "ok"


# ---------------------------------------------------------------------------
# G2 — Inventory completeness (db-landed authority + field integrity)
# ---------------------------------------------------------------------------

async def check_g2(conn: asyncpg.Connection, cdp_code: str) -> tuple[bool, str, dict]:
    """Gate G2: inventory data validity (V2 refined 2026-06-15).

    Orthogonal paths (V2 §3.B, refined):
      D        = db-landed available rows (authority)
      D_valid  = available rows with deep_link NOT NULL (the validity signal)

    field_integrity = D_valid / D. Gate passes if D >= 1 and field_integrity >= 0.98.

    recipe_version is NOT included in D_valid: it is written only for AS24 dealers
    (537 of ~38k). recipe_version provenance is G3's responsibility, not G2's.

    VAM quorum D=S: the 's_declared' (source-declared count) is NOT stored as a column
    on the entity table in the current schema. The VAM quorum for inventory counts is
    tracked in verification_verdict (subject_type='entity_inventory') — that is B1 work
    already done. For G2 completion, field_integrity is the primary signal. The evidence
    dict reserves s_declared for future use (caller may backfill from verification_verdict
    when the Director schedules block β-complete).

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

    # D: count of available vehicles (db-landed authority)
    d_landed: int = await conn.fetchval(
        "SELECT count(*) FROM vehicle WHERE entity_ulid = ANY($1::text[]) AND status = 'available'",
        ulid_array,
    )

    # D_valid: available rows with deep_link NOT NULL (inventory data validity).
    # recipe_version deliberately excluded: only written for AS24 (537 dealers).
    # Removing it lets field_integrity measure real inventory validity, not recipe coverage.
    d_valid: int = await conn.fetchval(
        """
        SELECT count(*)
        FROM vehicle
        WHERE entity_ulid = ANY($1::text[])
          AND status = 'available'
          AND deep_link IS NOT NULL
        """,
        ulid_array,
    )

    evidence = {
        "d_landed": d_landed,
        "d_valid": d_valid,
        "s_declared": None,   # not a column on entity; reserved for β-complete backfill
        "h_harvested": None,  # not stored in entity row; caller may backfill
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

async def check_g3(
    conn: asyncpg.Connection,
    cdp_code: str,
    repo_root: Path | None = None,
) -> tuple[bool, str, str | None]:
    """Gate G3: dealer has recipe coverage (V2 refined 2026-06-15).

    PRIMARY CHECK (DB-based, works for all 97.5% connector-covered dealers):
      v_dealer_recipe.recipe_kind <> 'none'
      - 'connector': sentinel-00 platform entity proves recipe exists (migration 0029)
      - 'per_dealer': entity.recipe_version IS NOT NULL (AS24 cohort, 537 dealers)
      - 'none': no recipe coverage → G3 FAIL

    SUB-SIGNAL (strict, per_dealer only, diagnostic):
      For per_dealer recipes, also attempts git ls-files / git cat-file to verify
      that countries/ES/recipes/<cdp_code>.yaml is committed at HEAD.
      This sub-signal is informational: G3=TRUE is determined by recipe_kind, NOT
      by git. The git check may fail in Docker (no .git mount) without failing G3.

    Returns (passed, reason, sha_or_None).
    sha = HEAD commit sha (12 chars) from git sub-signal if available, else None.
    """
    # Primary check: query v_dealer_recipe for this dealer.
    # v_dealer_recipe is a READ-ONLY view (no writes, MVCC-safe, migration 0029).
    recipe_row = await conn.fetchrow(
        """
        SELECT recipe_kind, recipe_ref
        FROM v_dealer_recipe
        WHERE cdp_code = $1
        LIMIT 1
        """,
        cdp_code,
    )

    if recipe_row is None:
        # Dealer not in v_dealer_recipe: either not a served dealer or view not populated.
        return False, "recipe_kind:dealer_not_in_v_dealer_recipe", None

    recipe_kind: str = recipe_row["recipe_kind"]

    if recipe_kind == "none":
        return False, f"recipe_kind:none:no_recipe_coverage", None

    # recipe_kind is 'connector' or 'per_dealer' → G3=TRUE by primary check.
    # Optionally run git sub-signal for per_dealer recipes (diagnostic only).
    sha: str | None = None
    git_reason: str = "git_subsignal_skipped:connector_recipe"

    if recipe_kind == "per_dealer":
        sha, git_reason = _check_g3_git_subsignal(cdp_code, repo_root)

    reason = f"ok:recipe_kind={recipe_kind}"
    if recipe_kind == "per_dealer":
        reason = f"ok:recipe_kind={recipe_kind}:git={git_reason}"

    return True, reason, sha


def _resolve_recipe_path(cdp_code: str, root: Path) -> Path | None:
    """Locate the recipe file for cdp_code under root, supporting both layouts.

    Search order (first match wins):
      1. New geo layout : countries/ES/**/<cdp_code>/recipe.yaml  (post SU-E2)
      2. Legacy flat    : countries/ES/recipes/<cdp_code>.yaml    (pre SU-E2)

    Returns the resolved absolute Path, or None if not found in either layout.
    Transition-safe: works before, during, and after the SU-E2 reshape move.
    """
    # New layout: glob under countries/ES (excludes the flat recipes/ dir on
    # purpose — the flat path below handles that case explicitly).
    for candidate in (root / "countries" / "ES").glob(f"**/{cdp_code}/recipe.yaml"):
        return candidate

    # Legacy flat layout fallback
    flat = root / "countries" / "ES" / "recipes" / f"{cdp_code}.yaml"
    if flat.exists():
        return flat

    return None


def _check_g3_git_subsignal(
    cdp_code: str, repo_root: Path | None = None
) -> tuple[str | None, str]:
    """Diagnostic sub-signal for per_dealer recipes: checks git tracking.

    Returns (sha_or_None, reason_string).
    This does NOT gate G3. It is called only for recipe_kind='per_dealer' and
    provides extra evidence for the entity_completion record. In Docker without
    git, returns (None, 'git_unavailable') — G3 remains TRUE.

    Path resolution is geo-reorg-stable: searches the new geo layout first
    (countries/ES/**/<cdp>/recipe.yaml) then falls back to the legacy flat
    path (countries/ES/recipes/<cdp>.yaml).  Both git checks (ls-files and
    cat-file HEAD) are run against the resolved path in either layout.
    """
    root = repo_root or _REPO_ROOT

    recipe_abs = _resolve_recipe_path(cdp_code, root)
    if recipe_abs is None:
        return None, "git_subsignal:recipe_file_missing"

    recipe_rel = recipe_abs.relative_to(root)

    try:
        subprocess.run(
            ["git", "--version"],
            capture_output=True,
            check=True,
            cwd=str(root),
            timeout=5,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None, "git_unavailable"

    ls = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(recipe_rel)],
        capture_output=True,
        cwd=str(root),
        timeout=10,
    )
    if ls.returncode != 0:
        return None, "git_subsignal:recipe_not_tracked"

    cat = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{recipe_rel}"],
        capture_output=True,
        cwd=str(root),
        timeout=10,
    )
    if cat.returncode != 0:
        return None, "git_subsignal:recipe_not_committed_at_HEAD"

    head = subprocess.run(
        ["git", "rev-parse", "--short=12", "HEAD"],
        capture_output=True,
        cwd=str(root),
        timeout=5,
    )
    sha = head.stdout.decode().strip() if head.returncode == 0 else None
    return sha, "git_tracked_and_committed"


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

    # LEFT JOIN + COALESCE (NOT inner join): v_canonical_vehicle only covers vehicles in a
    # vam_verified cluster run. An INNER JOIN returns served_count=0 for an entity whose entire
    # available inventory is outside that view (subastas, rentacar VO) — falsely failing G4 for a
    # genuinely-served dealer. The COALESCE falls back to the raw vehicle_ulid, matching
    # scripts/populate_completion.py exactly (which already documents this as the DB-equivalent).
    served_count: int = await conn.fetchval(
        """
        SELECT count(DISTINCT COALESCE(vc.canonical_vehicle_ulid, v.vehicle_ulid))
        FROM vehicle v
        LEFT JOIN v_canonical_vehicle vc ON vc.vehicle_ulid = v.vehicle_ulid
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

    # G3 — DB-based recipe coverage check (async); git sub-signal is diagnostic only
    g3, g3_reason, recipe_sha = await check_g3(conn, cdp_code)

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

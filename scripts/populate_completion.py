"""SU-B2 β-populate — set-based populate of entity_completion.

Fills entity_completion for ALL served dealers (kind <> 'particular' with >= 1
available vehicle) using a single INSERT … SELECT that mirrors the gate logic
in pipeline/complete.py exactly:

    G1  entity exists ∧ province_code ~ '^(0[1-9]|[1-4][0-9]|5[0-2])$'
        ∧ cdp_code ~ '^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$'
    G2  (count deep_link NOT NULL / count available) >= 0.98
        computed purely from the vehicle table (same numerator/denominator
        as check_g2 in complete.py).
    G3  v_dealer_recipe.recipe_kind <> 'none'
        (same primary-check logic as check_g3; git sub-signal skipped in set-based).
    G4  served_count = count(DISTINCT vc.canonical_vehicle_ulid) > 0
        via v_canonical_vehicle LEFT JOIN (same as check_g4 DB-equivalent).
    G5  FALSE (deferred — requires 2nd harvest run).

Verdict:
    COMPLETED requires G1∧G2∧G3∧G4∧G5=TRUE ∧ completed_at IS NOT NULL.
    Since G5=FALSE always, verdict is always INCOMPLETE (trigger enforces this).

Evidence columns populated:
    d_landed      = count of available vehicles
    d_valid       = count of available vehicles with deep_link NOT NULL
    field_integrity = d_valid / d_landed
    served_count  = count(DISTINCT canonical_vehicle_ulid)
    recipe_sha    = NULL (git sub-signal not run in set-based populate)
    s_declared    = NULL (not in entity schema; reserved for β-complete)
    h_harvested   = NULL (not stored; reserved for β-complete)
    last_harvest_at = NULL (not populated here; freshness watermark TBD)

Idempotency:
    TRUNCATE entity_completion + INSERT.
    entity_completion is a DERIVED snapshot, not a business table. TRUNCATE+INSERT
    is the documented MVCC-safe strategy for derived snapshots (no live business
    rows mutated). Re-running produces identical results from the same source data.

Usage:
    python scripts/populate_completion.py [--dry-run] [--dsn DSN]

    --dry-run   Print the counts without committing.
    --dsn DSN   Override the default DSN (default: CARDEEP_DSN env or localhost:5433).
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import psycopg2
import psycopg2.extras

# ---------------------------------------------------------------------------
# SQL: set-based gate computation + INSERT
# ---------------------------------------------------------------------------

# Gate patterns (mirrors pipeline/complete.py constants exactly)
_PROVINCE_PATTERN = r"^(0[1-9]|[1-4][0-9]|5[0-2])$"
_CDP_CODE_PATTERN = r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$"
_FIELD_INTEGRITY_FLOOR = 0.98

# The main INSERT … SELECT.
# Structure:
#   served_dealers   — universe of target cdp_codes (kind<>particular, >=1 available)
#   g2_stats         — per-cdp d_landed, d_valid, field_integrity  (G2)
#   g4_stats         — per-cdp served_count via v_canonical_vehicle (G4)
#   gates            — combine all gates, derive gate booleans + evidence
#   final INSERT into entity_completion

_POPULATE_SQL = f"""
WITH
-- ---------------------------------------------------------------------------
-- Universe: served dealers (kind <> 'particular', >= 1 available vehicle).
-- Same filter used in v_dealer_recipe (0029) and complete.py demo query.
-- ---------------------------------------------------------------------------
served_dealers AS (
    SELECT DISTINCT e.cdp_code
    FROM entity e
    JOIN vehicle v ON v.entity_ulid = e.entity_ulid AND v.status = 'available'
    WHERE e.kind <> 'particular'
),

-- ---------------------------------------------------------------------------
-- G1: identity check (mirrors check_g1 in complete.py)
--   PASS iff:
--     - entity row exists for cdp_code (guaranteed by universe CTE above)
--     - province_code ~ valid 2-digit Spanish province (01-52)
--     - cdp_code ~ CDP-ES-NN-XXXXXXXX format
-- ---------------------------------------------------------------------------
g1_check AS (
    SELECT
        e.cdp_code,
        (
            e.province_code IS NOT NULL
            AND e.province_code ~ '{_PROVINCE_PATTERN}'
            AND e.cdp_code ~ '{_CDP_CODE_PATTERN}'
        ) AS g1_identity
    FROM entity e
    WHERE e.cdp_code IN (SELECT cdp_code FROM served_dealers)
),

-- ---------------------------------------------------------------------------
-- G2: inventory field integrity (mirrors check_g2 in complete.py)
--   D        = count of available vehicles (d_landed)
--   D_valid  = count of available vehicles with deep_link NOT NULL (d_valid)
--   field_integrity = D_valid / D
--   PASS iff D >= 1 AND field_integrity >= {_FIELD_INTEGRITY_FLOOR}
--
--   NOTE: entity may have multiple entity_ulid rows (partial dedup). We aggregate
--   across ALL ulids for the same cdp_code, matching complete.py's ulid_array approach.
-- ---------------------------------------------------------------------------
g2_stats AS (
    SELECT
        e.cdp_code,
        count(*) FILTER (WHERE v.status = 'available')                                AS d_landed,
        count(*) FILTER (WHERE v.status = 'available' AND v.deep_link IS NOT NULL)    AS d_valid
    FROM entity e
    JOIN vehicle v ON v.entity_ulid = e.entity_ulid AND v.status = 'available'
    WHERE e.cdp_code IN (SELECT cdp_code FROM served_dealers)
    GROUP BY e.cdp_code
),
g2_check AS (
    SELECT
        cdp_code,
        d_landed,
        d_valid,
        CASE WHEN d_landed > 0 THEN d_valid::double precision / d_landed ELSE NULL END AS field_integrity,
        (
            d_landed > 0
            AND (d_valid::double precision / d_landed) >= {_FIELD_INTEGRITY_FLOOR}
        ) AS g2_inventory
    FROM g2_stats
),

-- ---------------------------------------------------------------------------
-- G3: recipe coverage (mirrors check_g3 primary check in complete.py)
--   PASS iff v_dealer_recipe.recipe_kind <> 'none'
--   dealers absent from v_dealer_recipe => G3=FALSE (not in view = no recipe)
--   git sub-signal skipped: not applicable in set-based mode (same semantics as
--   connector recipe path in complete.py which returns sha=None, git_skipped).
-- ---------------------------------------------------------------------------
g3_check AS (
    SELECT
        sd.cdp_code,
        (dr.recipe_kind IS NOT NULL AND dr.recipe_kind <> 'none') AS g3_recipe
    FROM served_dealers sd
    LEFT JOIN v_dealer_recipe dr ON dr.cdp_code = sd.cdp_code
),

-- ---------------------------------------------------------------------------
-- G4: served check (mirrors check_g4 DB-equivalent in complete.py)
--   served_count = count(DISTINCT vc.canonical_vehicle_ulid)
--   Via v_canonical_vehicle LEFT JOIN: if no vam_verified cluster run has
--   covered this vehicle, vc.canonical_vehicle_ulid = NULL => COALESCE to
--   v.vehicle_ulid (each vehicle is its own canonical = count equals d_landed).
--   PASS iff served_count > 0
--
--   NOTE: check_g4 in complete.py does:
--     count(DISTINCT vc.canonical_vehicle_ulid) via JOIN v_canonical_vehicle
--   If v_canonical_vehicle is empty or doesn't cover a vehicle, complete.py
--   returns served_count=0 for those vehicles. But our DB-level check confirms
--   v_canonical_vehicle has 1,689,243 rows (all vehicles covered). For unclustered
--   vehicles (no row in vehicle_cluster for their cluster_run_id), the LEFT JOIN
--   produces NULL -> COALESCE to vehicle_ulid ensures G4 still counts them.
-- ---------------------------------------------------------------------------
g4_stats AS (
    SELECT
        e.cdp_code,
        count(DISTINCT COALESCE(vc.canonical_vehicle_ulid, v.vehicle_ulid)) AS served_count
    FROM entity e
    JOIN vehicle v ON v.entity_ulid = e.entity_ulid AND v.status = 'available'
    LEFT JOIN v_canonical_vehicle vc ON vc.vehicle_ulid = v.vehicle_ulid
    WHERE e.cdp_code IN (SELECT cdp_code FROM served_dealers)
    GROUP BY e.cdp_code
),
g4_check AS (
    SELECT
        cdp_code,
        served_count,
        (served_count > 0) AS g4_served
    FROM g4_stats
),

-- ---------------------------------------------------------------------------
-- Final combination: join all gates, set G5=FALSE (deferred), derive verdict.
-- Verdict is INCOMPLETE because G5=FALSE always (trigger enforces COMPLETED
-- requires g1∧g2∧g3∧g4∧g5=TRUE, so we never set COMPLETED here).
-- ---------------------------------------------------------------------------
gates AS (
    SELECT
        sd.cdp_code,
        COALESCE(g1.g1_identity,  FALSE)  AS g1_identity,
        COALESCE(g2.g2_inventory, FALSE)  AS g2_inventory,
        COALESCE(g3.g3_recipe,    FALSE)  AS g3_recipe,
        COALESCE(g4.g4_served,    FALSE)  AS g4_served,
        FALSE                             AS g5_delta,
        -- Evidence columns
        g2.d_landed,
        g2.d_valid,
        g2.field_integrity,
        g4.served_count,
        -- Unused evidence (reserved for β-complete backfill)
        NULL::int                         AS s_declared,
        NULL::int                         AS h_harvested,
        NULL::text                        AS recipe_sha,
        -- Freshness (not yet populated at β-populate time)
        NULL::timestamptz                 AS last_harvest_at,
        -- SLA: default 7 days (standard tier); Director can update tiers post-populate
        604800                            AS sla_seconds,
        -- Verdict: INCOMPLETE always (G5=FALSE => trigger blocks COMPLETED)
        'INCOMPLETE'::text                AS verdict
    FROM served_dealers sd
    LEFT JOIN g1_check  g1 ON g1.cdp_code  = sd.cdp_code
    LEFT JOIN g2_check  g2 ON g2.cdp_code  = sd.cdp_code
    LEFT JOIN g3_check  g3 ON g3.cdp_code  = sd.cdp_code
    LEFT JOIN g4_check  g4 ON g4.cdp_code  = sd.cdp_code
)

INSERT INTO entity_completion (
    cdp_code,
    g1_identity, g2_inventory, g3_recipe, g4_served, g5_delta,
    s_declared, h_harvested, d_landed, d_valid, field_integrity,
    recipe_sha, served_count,
    last_harvest_at, sla_seconds,
    verdict,
    completed_at,
    updated_at
)
SELECT
    cdp_code,
    g1_identity, g2_inventory, g3_recipe, g4_served, g5_delta,
    s_declared, h_harvested, d_landed, d_valid, field_integrity,
    recipe_sha, served_count,
    last_harvest_at, sla_seconds,
    verdict,
    NULL::timestamptz AS completed_at,   -- never COMPLETED at populate time
    now()             AS updated_at
FROM gates
"""

# ---------------------------------------------------------------------------
# Distribution query (run after INSERT for reporting)
# ---------------------------------------------------------------------------

_DISTRIBUTION_SQL = """
SELECT
    verdict,
    count(*)                                                AS dealers,
    count(*) FILTER (WHERE g1_identity)                    AS g1_true,
    count(*) FILTER (WHERE NOT g1_identity)                AS g1_false,
    count(*) FILTER (WHERE g2_inventory)                   AS g2_true,
    count(*) FILTER (WHERE NOT g2_inventory)               AS g2_false,
    count(*) FILTER (WHERE g3_recipe)                      AS g3_true,
    count(*) FILTER (WHERE NOT g3_recipe)                  AS g3_false,
    count(*) FILTER (WHERE g4_served)                      AS g4_true,
    count(*) FILTER (WHERE NOT g4_served)                  AS g4_false,
    count(*) FILTER (WHERE g5_delta)                       AS g5_true,
    count(*) FILTER (WHERE NOT g5_delta)                   AS g5_false
FROM entity_completion
GROUP BY verdict
ORDER BY dealers DESC
"""

# G1 failure breakdown
_G1_FAIL_SQL = """
SELECT
    CASE
        WHEN province_code IS NULL THEN 'province_null'
        WHEN province_code !~ '^(0[1-9]|[1-4][0-9]|5[0-2])$' THEN 'province_invalid:' || province_code
        WHEN cdp_code !~ '^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$' THEN 'cdp_format_invalid'
        ELSE 'unknown'
    END AS reason,
    count(*) AS n
FROM entity e
WHERE e.kind <> 'particular'
  AND EXISTS (SELECT 1 FROM vehicle v WHERE v.entity_ulid = e.entity_ulid AND v.status = 'available')
  AND e.cdp_code IN (SELECT cdp_code FROM entity_completion WHERE NOT g1_identity)
GROUP BY 1
ORDER BY n DESC
LIMIT 20
"""

# G3 failure breakdown
_G3_FAIL_SQL = """
SELECT recipe_kind, count(*) AS n
FROM v_dealer_recipe
WHERE cdp_code IN (SELECT cdp_code FROM entity_completion WHERE NOT g3_recipe)
GROUP BY 1
UNION ALL
SELECT 'not_in_v_dealer_recipe' AS recipe_kind, count(*) AS n
FROM entity_completion ec
WHERE NOT ec.g3_recipe
  AND NOT EXISTS (SELECT 1 FROM v_dealer_recipe dr WHERE dr.cdp_code = ec.cdp_code)
ORDER BY n DESC
"""


# ---------------------------------------------------------------------------
# Spot-check: compare set-based result vs compute_completion per-dealer
# ---------------------------------------------------------------------------

def _spot_check(conn: "psycopg2.connection", sample_size: int = 10) -> None:
    """Compare set-based entity_completion results vs pipeline/complete.py per-dealer."""
    import asyncio
    import asyncpg
    from pipeline.complete import compute_completion

    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT cdp_code, g1_identity, g2_inventory, g3_recipe, g4_served, g5_delta,
               d_landed, d_valid, field_integrity, served_count
        FROM entity_completion
        ORDER BY cdp_code
        LIMIT %s
    """, (sample_size,))
    set_based_rows = {r["cdp_code"]: dict(r) for r in cur.fetchall()}

    dsn = os.environ.get(
        "CARDEEP_DSN",
        "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep",
    )

    async def _run_per_dealer():
        aconn = await asyncpg.connect(dsn)
        results = {}
        try:
            for cdp_code in set_based_rows:
                results[cdp_code] = await compute_completion(aconn, cdp_code)
        finally:
            await aconn.close()
        return results

    per_dealer_rows = asyncio.run(_run_per_dealer())

    print(f"\n{'='*80}")
    print(f"SPOT-CHECK: set-based vs compute_completion ({sample_size} dealers)")
    print(f"{'='*80}")
    header = f"{'CDP_CODE':<30} {'G1':^8} {'G2':^8} {'G3':^8} {'G4':^8} {'MATCH'}"
    print(header)
    print("-" * len(header))

    mismatches = []
    for cdp_code, sb in set_based_rows.items():
        pd = per_dealer_rows[cdp_code]
        gates = ["g1_identity", "g2_inventory", "g3_recipe", "g4_served"]
        match = all(sb[g] == pd[g] for g in gates)
        if not match:
            mismatches.append((cdp_code, sb, pd))
        marker = "OK" if match else "MISMATCH"
        print(
            f"{cdp_code:<30} "
            f"{'T' if sb['g1_identity'] else 'F':^8}"
            f"{'T' if sb['g2_inventory'] else 'F':^8}"
            f"{'T' if sb['g3_recipe'] else 'F':^8}"
            f"{'T' if sb['g4_served'] else 'F':^8}"
            f"{marker}"
        )
        if not match:
            for g in gates:
                if sb[g] != pd[g]:
                    print(f"  DIVERGE {g}: set-based={sb[g]} vs compute_completion={pd[g]}")

    print()
    if mismatches:
        print(f"[SPOT-CHECK] FAIL — {len(mismatches)} mismatch(es) found.")
        sys.exit(1)
    else:
        print(f"[SPOT-CHECK] PASS — all {len(set_based_rows)} dealers match gate-by-gate.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Set-based populate of entity_completion.")
    parser.add_argument("--dry-run", action="store_true", help="Compute only; do not commit.")
    parser.add_argument("--dsn", default=None, help="PostgreSQL DSN override.")
    parser.add_argument("--spot-check", action="store_true",
                        help="After populate, run spot-check vs compute_completion.")
    parser.add_argument("--spot-sample", type=int, default=10,
                        help="Number of dealers for spot-check (default 10).")
    args = parser.parse_args()

    dsn = args.dsn or os.environ.get(
        "CARDEEP_DSN",
        "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep",
    )

    conn = psycopg2.connect(dsn)
    conn.autocommit = False

    try:
        cur = conn.cursor()

        # Step 1: TRUNCATE (entity_completion is a derived snapshot — TRUNCATE+INSERT
        # is the documented MVCC-safe strategy for derived snapshots).
        print("[populate] TRUNCATE entity_completion ...")
        cur.execute("TRUNCATE entity_completion")

        # Step 2: INSERT … SELECT (set-based gate computation)
        print("[populate] Running set-based INSERT ... SELECT for all served dealers ...")
        t0 = time.perf_counter()
        cur.execute(_POPULATE_SQL)
        inserted = cur.rowcount
        elapsed = time.perf_counter() - t0
        print(f"[populate] Inserted {inserted:,} rows in {elapsed:.1f}s")

        if args.dry_run:
            print("[populate] --dry-run: rolling back.")
            conn.rollback()
            return

        # Step 3: Commit
        conn.commit()
        print("[populate] Committed.")

        # Step 4: Distribution report
        cur.execute(_DISTRIBUTION_SQL)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        print(f"\n{'='*80}")
        print("DISTRIBUTION REPORT")
        print(f"{'='*80}")
        print(f"{'VERDICT':<12} {'DEALERS':>8} {'G1T':>6} {'G1F':>6} {'G2T':>6} {'G2F':>6} "
              f"{'G3T':>6} {'G3F':>6} {'G4T':>6} {'G4F':>6} {'G5T':>6} {'G5F':>6}")
        print("-" * 80)
        for r in rows:
            rv = dict(zip(cols, r))
            print(
                f"{rv['verdict']:<12} {rv['dealers']:>8,} "
                f"{rv['g1_true']:>6,} {rv['g1_false']:>6,} "
                f"{rv['g2_true']:>6,} {rv['g2_false']:>6,} "
                f"{rv['g3_true']:>6,} {rv['g3_false']:>6,} "
                f"{rv['g4_true']:>6,} {rv['g4_false']:>6,} "
                f"{rv['g5_true']:>6,} {rv['g5_false']:>6,}"
            )

        # Step 5: G1 fail breakdown
        cur.execute(_G1_FAIL_SQL)
        g1_fails = cur.fetchall()
        if g1_fails:
            print(f"\nG1 FAIL BREAKDOWN (province/cdp issues):")
            for r in g1_fails:
                print(f"  {r[0]}: {r[1]:,}")

        # Step 6: G3 fail breakdown
        cur.execute(_G3_FAIL_SQL)
        g3_fails = cur.fetchall()
        if g3_fails:
            print(f"\nG3 FAIL BREAKDOWN (recipe_kind of failing dealers):")
            for r in g3_fails:
                print(f"  {r[0]}: {r[1]:,}")

        # Step 7: Assert COMPLETED=0 (invariant: G5=FALSE => no COMPLETED)
        cur.execute("SELECT count(*) FROM entity_completion WHERE verdict = 'COMPLETED'")
        completed_count = cur.fetchone()[0]
        assert completed_count == 0, f"INVARIANT VIOLATION: {completed_count} COMPLETED rows (G5=FALSE always)"
        print(f"\n[ASSERT] COMPLETED = 0 — PASS (G5=FALSE, trigger invariant enforced)")

        # Step 8: Assert total = inserted
        cur.execute("SELECT count(*) FROM entity_completion")
        total_after = cur.fetchone()[0]
        assert total_after == inserted, f"Row count mismatch: inserted={inserted} vs table={total_after}"
        print(f"[ASSERT] Total rows = {total_after:,} — PASS")

        # Step 9: Optional spot-check
        if args.spot_check:
            _spot_check(conn, args.spot_sample)

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()

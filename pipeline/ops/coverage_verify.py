"""Post-harvest coverage verification gate (CAMPAIGN B9).

After every successful harvest the connector calls record_run() with declared_total and
captured_distinct.  record_run() in turn calls verify_coverage() here, which:

  1. Counts captured_db via a SQL query (orthogonal to the in-memory harvest counter).
  2. Counts db_edges via platform_listing (structural reference count).
  3. Computes coverage_pct = captured_db / declared_total.
  4. Emits a VAM verdict via record_count_verdict (three orthogonal paths = VAM quorum).
  5. UPSERTs source_coverage (idempotent, always-fresh audit row).
  6. Fires or resolves the exact-origin coverage alert based on coverage_pct vs floor.

The gate is €0: it uses only existing DB data, never adds extra HTTP requests.

Public API
----------
verify_coverage(conn, source_key, *, declared_total, captured_distinct, platform_ulid, phase)
    -> None.  See docstring below.

refresh_global_counts(conn)
    -> dict.  Re-emits fresh vehicle_total + platform_listing_total verdicts.
"""
from __future__ import annotations

import asyncpg

from pipeline.ops.health import (
    SEV_WARNING,
    auto_repair,
    build_origin,
    fire_alert,
    resolve_alerts,
)
from pipeline.verify import record_count_verdict

# Default coverage tolerance for the VAM quorum step.
# The three paths (declared, captured_db, db_edges) are intentionally heterogeneous:
# declared is often clamped or estimated; db_edges counts structural rows; captured_db
# counts vehicles.  A 30 % tolerance lets the quorum fire TRUSTWORTHY when the paths
# roughly converge, without demanding exact agreement across semantically distinct counts.
_COVERAGE_TOLERANCE: float = 0.30

# Coverage floor applied when source_health.coverage_floor cannot be read (e.g. source
# not yet in source_health).  Matches the migration DEFAULT.
_DEFAULT_FLOOR: float = 0.85

# Coverage ceiling: above this, captured >> declared means EITHER the declared figure is
# wrong (under-counted / clamped totalHits) OR our DB is inflated (intra-source duplicates /
# stale-available). Either way it is NOT trustworthy and must alert — symmetric with the floor.
# Without it, milanuncios (captured 397k vs declared 110k = 360%) slipped through as TRUSTWORTHY.
_COVERAGE_CEILING: float = 1.15


async def verify_coverage(
    conn: asyncpg.Connection,
    source_key: str,
    *,
    declared_total: int,
    captured_distinct: int | None = None,
    platform_ulid: str | None = None,
    phase: str = "scrape",
) -> None:
    """Verify post-harvest coverage by three orthogonal paths and seal the result.

    Parameters
    ----------
    conn:
        Live asyncpg connection (must NOT be inside an open transaction; this function
        opens its own transaction for the UPSERT + verdict writes).
    source_key:
        Canonical source key (e.g. 'wallapop_wholesale').
    declared_total:
        Total listings the source DECLARES for this scope.  Comes from the source itself,
        never derived from our DB.
    captured_distinct:
        In-harvest distinct car count reported by the connector (optional; used as a
        fourth evidence path when provided, but NOT as the primary captured count — the
        primary is the DB-query path which is orthogonal to the harvest counter).
    platform_ulid:
        ULID of the platform_entity for this source.  When provided, db_edges is counted
        via a direct platform_listing filter on this ULID (exact + fast).  When absent,
        db_edges falls back to 0 and only two paths contribute to the VAM quorum.
    phase:
        Harvest phase label used to scope alert origins.  Defaults to 'scrape'.

    Side effects
    ------------
    - Inserts/updates source_coverage (idempotent UPSERT).
    - Inserts a verification_verdict row (VAM audit trail).
    - Fires or resolves a '<source_key>:coverage' alert.
    - Calls auto_repair(source_key, 'low_coverage') when coverage_pct < floor.
    """
    if declared_total <= 0:
        # Guard: a zero or negative declared total cannot produce a meaningful ratio.
        # Record an UNVERIFIED verdict so the gap is visible without crashing.
        await _upsert_coverage(
            conn, source_key=source_key,
            declared_total=declared_total, captured_db=0, db_edges=0,
            coverage_pct=None, verdict="UNVERIFIED", verdict_id=None,
        )
        return

    # ------------------------------------------------------------------
    # Path A — captured_db: count of our vehicles attributed to this source.
    # Attribution is via entity_source: entity_source.source_key = source_key
    # links the entity (dealer / platform) to the source that first discovered it.
    # We JOIN vehicle -> entity_source to count distinct available vehicles.
    # ------------------------------------------------------------------
    captured_db: int = await conn.fetchval(
        """SELECT count(DISTINCT v.vehicle_ulid)
           FROM vehicle v
           JOIN entity_source es ON es.entity_ulid = v.entity_ulid
           WHERE v.status = 'available' AND es.source_key = $1""",
        source_key,
    ) or 0

    # ------------------------------------------------------------------
    # Path B — db_edges: count of platform_listing rows for this platform.
    # This is the structural edge count, orthogonal to vehicle attribution.
    # Requires platform_ulid (the entity ULID of the platform entity).
    # Falls back to zero (UNVERIFIED on this path) when not supplied.
    # ------------------------------------------------------------------
    db_edges: int = 0
    if platform_ulid:
        db_edges = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid = $1",
            platform_ulid,
        ) or 0
    else:
        # Secondary fallback: find the platform entity via entity_source and use its
        # platform_listing count.  This covers callers that omit platform_ulid but
        # whose source_key maps to a 'plataforma' kind entity in entity_source.
        row = await conn.fetchrow(
            """SELECT e.entity_ulid FROM entity e
               JOIN entity_source es ON es.entity_ulid = e.entity_ulid
               WHERE es.source_key = $1 AND e.kind = 'plataforma'
               LIMIT 1""",
            source_key,
        )
        if row:
            db_edges = await conn.fetchval(
                "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid = $1",
                row["entity_ulid"],
            ) or 0

    # ------------------------------------------------------------------
    # Coverage ratio: primary metric the gate reports.
    # Can exceed 1.0 when the source under-declares (clamped totalHits etc.).
    # ------------------------------------------------------------------
    coverage_pct: float = captured_db / declared_total

    # ------------------------------------------------------------------
    # VAM verdict — three-path quorum.
    # Primary path: captured_db (what actually landed in the DB).
    # Additional paths: db_edges (structural), declared_total (external oracle).
    # We normalise declared_total as a ratio (1.0) so the three values live on a
    # comparable scale: captured_db_ratio and db_edges_ratio converge toward 1.0
    # when coverage is full.
    # When captured_distinct is available it is added as a fourth path.
    # ------------------------------------------------------------------
    # The coverage verdict measures captured-vs-DECLARED — the ONLY orthogonal comparison
    # (declared is the source's external oracle). captured_db and db_edges are BOTH ours and
    # always agree, so feeding db_edges into this verdict would mask a real coverage divergence
    # behind two internal counts that echo each other — exactly how milanuncios 360% slipped
    # through as TRUSTWORTHY. db_edges stays as an INTERNAL coherence figure in source_coverage,
    # never as a coverage-verdict path. captured_distinct (harvest counter) is also ours; kept
    # only as a secondary echo of captured_db.
    paths: dict[str, int] = {
        "captured_db": captured_db,
        "declared_total": declared_total,
    }
    if captured_distinct is not None:
        paths["captured_distinct"] = captured_distinct

    verdict = await record_count_verdict(
        conn,
        subject_type="source_coverage",
        subject_key=source_key,
        claim=f"captured_db converges with declared_total for source '{source_key}'",
        paths=paths,
        tolerance=_COVERAGE_TOLERANCE,
    )

    # Retrieve the id of the verdict just inserted (most recent for this key).
    verdict_id: int | None = await conn.fetchval(
        "SELECT id FROM verification_verdict "
        "WHERE subject_type = 'source_coverage' AND subject_key = $1 "
        "ORDER BY created_at DESC LIMIT 1",
        source_key,
    )

    # ------------------------------------------------------------------
    # UPSERT source_coverage — always-fresh, idempotent.
    # ------------------------------------------------------------------
    await _upsert_coverage(
        conn,
        source_key=source_key,
        declared_total=declared_total,
        captured_db=captured_db,
        db_edges=db_edges,
        coverage_pct=coverage_pct,
        verdict=verdict,
        verdict_id=verdict_id,
    )

    # ------------------------------------------------------------------
    # Alert logic: read coverage_floor from source_health (fallback = default).
    # ------------------------------------------------------------------
    floor_raw = await conn.fetchval(
        "SELECT coverage_floor FROM source_health WHERE source_key = $1",
        source_key,
    )
    floor: float = float(floor_raw) if floor_raw is not None else _DEFAULT_FLOOR

    coverage_origin = build_origin(source_key, "coverage")
    base_payload = {
        "declared_total": declared_total,
        "captured_db": captured_db,
        "db_edges": db_edges,
        "coverage_pct": round(coverage_pct, 6),
        "floor": float(floor),
        "ceiling": _COVERAGE_CEILING,
        "verdict": verdict,
    }

    if coverage_pct < floor:
        # SUB-coverage: we are MISSING listings the source has (incomplete pagination, ban
        # mid-drain, keyword sweep not reaching the tail).
        await fire_alert(
            conn, coverage_origin, severity=SEV_WARNING,
            message=(
                f"source '{source_key}' coverage BELOW floor: "
                f"{coverage_pct:.1%} < {floor:.0%} "
                f"(captured_db={captured_db}, declared={declared_total})"
            ),
            payload={**base_payload, "direction": "under"},
        )
        await auto_repair(conn, source_key, "low_coverage", phase="coverage")
    elif coverage_pct > _COVERAGE_CEILING:
        # OVER-coverage: we have far MORE than the source declares. The declared figure is
        # wrong/under-counted OR our DB is inflated (intra-source duplicates / stale-available).
        # NOT trustworthy — must surface, symmetric with the floor. (milanuncios 360% case.)
        await fire_alert(
            conn, coverage_origin, severity=SEV_WARNING,
            message=(
                f"source '{source_key}' coverage ABOVE ceiling: "
                f"{coverage_pct:.1%} > {_COVERAGE_CEILING:.0%} "
                f"(captured_db={captured_db}, declared={declared_total}) — "
                f"declared under-counted or DB inflated (dups/stale)"
            ),
            payload={**base_payload, "direction": "over"},
        )
        await auto_repair(conn, source_key, "over_coverage", phase="coverage")
    else:
        # Healthy coverage within [floor, ceiling]: close any prior open coverage alert.
        await resolve_alerts(conn, coverage_origin)


async def _upsert_coverage(
    conn: asyncpg.Connection,
    *,
    source_key: str,
    declared_total: int | None,
    captured_db: int,
    db_edges: int,
    coverage_pct: float | None,
    verdict: str,
    verdict_id: int | None,
) -> None:
    """UPSERT source_coverage.  Idempotent: re-running produces exactly one row."""
    await conn.execute(
        """INSERT INTO source_coverage
               (source_key, declared_total, captured_db, db_edges,
                coverage_pct, verdict, verdict_id, probed_at)
           VALUES ($1, $2, $3, $4, $5, $6, $7, now())
           ON CONFLICT (source_key) DO UPDATE
             SET declared_total = EXCLUDED.declared_total,
                 captured_db    = EXCLUDED.captured_db,
                 db_edges       = EXCLUDED.db_edges,
                 coverage_pct   = EXCLUDED.coverage_pct,
                 verdict        = EXCLUDED.verdict,
                 verdict_id     = EXCLUDED.verdict_id,
                 probed_at      = now()""",
        source_key,
        declared_total,
        captured_db,
        db_edges,
        coverage_pct,
        verdict,
        verdict_id,
    )


async def refresh_global_counts(conn: asyncpg.Connection) -> dict[str, int]:
    """Re-emit fresh global aggregate counts and seal them as VAM verdicts.

    Answers the question "how many vehicles / edges does CARDEEP have right now?"
    without trusting any cached figure.  Called from the coverage gate or the watchdog
    to prevent stale totals (the bug: said 1,332,980 when 1,689,243 were real).

    Returns a dict with the live counts so the caller can log them.
    """
    from pipeline.verify import record_count_verdict  # local to avoid circular import

    # Path A: vehicle table direct count.
    vehicle_total: int = await conn.fetchval(
        "SELECT count(*) FROM vehicle WHERE status = 'available'"
    ) or 0

    # Path B: distinct vehicles reachable via platform_listing edges.
    edge_reachable: int = await conn.fetchval(
        "SELECT count(DISTINCT vehicle_ulid) FROM platform_listing"
    ) or 0

    # Path C: total platform_listing rows (structural count).
    platform_listing_total: int = await conn.fetchval(
        "SELECT count(*) FROM platform_listing"
    ) or 0

    await record_count_verdict(
        conn,
        subject_type="global_count",
        subject_key="vehicle_total",
        claim="vehicle table count == edge-reachable distinct vehicles",
        paths={
            "vehicle_direct": vehicle_total,
            "edge_reachable": edge_reachable,
            "platform_listing_total": platform_listing_total,
        },
        tolerance=0.10,  # up to 10 % divergence tolerated (unattached vehicles / archived).
    )

    return {
        "vehicle_total": vehicle_total,
        "edge_reachable": edge_reachable,
        "platform_listing_total": platform_listing_total,
    }

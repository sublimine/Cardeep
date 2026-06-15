"""/entities/{cdp_code} — entity resolution, inventory, and delta endpoints."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from services.api.deps import err, ok, require_api_key, resolve_cluster

router = APIRouter()


# ---------------------------------------------------------------------------
# Entity resolution endpoints (B1.5 — unchanged)
# ---------------------------------------------------------------------------

@router.get("/entities/{cdp_code}/canonical")
async def get_entity_canonical(
    cdp_code: str,
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Resolve *cdp_code* to its canonical and expose the full cluster."""
    async with request.app.state.pool.acquire() as c:
        cluster = await resolve_cluster(c, cdp_code)
        if cluster is None:
            return err(f"entity {cdp_code} not found")
        return ok(
            {
                "input_cdp_code": cdp_code,
                "canonical_cdp_code": cluster.canonical_cdp_code,
                "is_canonical": cdp_code == cluster.canonical_cdp_code,
                "members": cluster.member_cdp_codes,
                "n_members": len(cluster.member_cdp_codes),
            }
        )


@router.get("/entities/{cdp_code}")
async def get_entity(
    cdp_code: str,
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Return the CANONICAL entity for *cdp_code* with aggregated cluster inventory."""
    async with request.app.state.pool.acquire() as c:
        cluster = await resolve_cluster(c, cdp_code)
        if cluster is None:
            return err(f"entity {cdp_code} not found")

        row = await c.fetchrow(
            "SELECT * FROM entity WHERE entity_ulid = $1",
            cluster.canonical_ulid,
        )
        n_available = await c.fetchval(
            "SELECT count(DISTINCT vc.canonical_vehicle_ulid) "
            "FROM vehicle v "
            "JOIN v_canonical_vehicle vc ON vc.vehicle_ulid = v.vehicle_ulid "
            "WHERE v.entity_ulid = ANY($1::text[]) AND v.status = 'available'",
            cluster.member_ulids,
        )
        data = dict(row)
        data["created_at"] = str(data["created_at"])
        data["last_seen"] = str(data["last_seen"])
        data["available_inventory"] = n_available
        data["canonical_cdp_code"] = cluster.canonical_cdp_code
        data["n_aliases"] = len(cluster.member_cdp_codes) - 1
        data["queried_cdp_code"] = cdp_code
        return ok(data)


# ---------------------------------------------------------------------------
# GAP 6 fix: /inventory serves ONLY canonical vehicles via v_canonical_vehicle
# ---------------------------------------------------------------------------

@router.get("/entities/{cdp_code}/inventory")
async def get_inventory(
    cdp_code: str,
    request: Request,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Return available CANONICAL stock for ALL cluster members.

    GAP-6 fix: dedups WITHIN the cluster via DISTINCT ON (canonical_vehicle_ulid)
    — collapses the dealer's own cross-platform duplicates (same physical car
    listed on two of its platforms -> one) while KEEPING cars whose global
    canonical belongs to another dealer (the dealer genuinely lists them).
    The global canonical-only filter would wrongly drop ~102 449 cross-dealer
    cars from the inventories that list them.

    Pagination (B3.1): accepts ``page`` and ``size``, returns ``has_more`` in meta.
    """
    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        cluster = await resolve_cluster(c, cdp_code)
        if cluster is None:
            return err(f"entity {cdp_code} not found")

        rows = await c.fetch(
            """
            SELECT * FROM (
              SELECT DISTINCT ON (vc.canonical_vehicle_ulid)
                     v.vehicle_ulid, v.deep_link, v.title, v.make, v.model, v.year,
                     v.km, v.price, v.currency, v.fuel, v.transmission, v.photo_url,
                     v.status, v.first_seen, v.last_seen
                FROM vehicle v
                JOIN v_canonical_vehicle vc ON vc.vehicle_ulid = v.vehicle_ulid
               WHERE v.entity_ulid = ANY($1::text[])
                 AND v.status = 'available'
               ORDER BY vc.canonical_vehicle_ulid, v.first_seen DESC, v.vehicle_ulid
            ) dedup
            ORDER BY dedup.first_seen DESC, dedup.vehicle_ulid
            LIMIT $2 OFFSET $3
            """,
            cluster.member_ulids,
            size,
            offset,
        )
        items = [
            {
                **dict(r),
                "price": float(r["price"]) if r["price"] is not None else None,
                "first_seen": str(r["first_seen"]),
                "last_seen": str(r["last_seen"]),
            }
            for r in rows
        ]
        return ok(
            items,
            page=page,
            size=size,
            returned=len(items),
            has_more=len(items) == size,
        )


# ---------------------------------------------------------------------------
# GAP 4 fix: /delta is now cluster-aware (all member_ulids)
# ---------------------------------------------------------------------------

@router.get("/entities/{cdp_code}/delta")
async def get_delta(
    cdp_code: str,
    request: Request,
    since: str | None = None,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Return vehicle events for the FULL CLUSTER of *cdp_code*.

    GAP-4 fix: queries vehicle_event WHERE entity_ulid = ANY(cluster.member_ulids)
    instead of the literal entity_ulid of the requested cdp_code.  Events from
    all cluster members are returned, merged and ordered by observed_at DESC.

    Pagination (B3.1): accepts ``page``/``size`` and optional ``since`` ISO-8601.
    """
    offset = (page - 1) * size
    since_dt: datetime | None = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError:
            return err(
                f"invalid since format '{since}'; use ISO-8601 (e.g. 2024-01-01T00:00:00Z)",
                status=400,
            )
    async with request.app.state.pool.acquire() as c:
        cluster = await resolve_cluster(c, cdp_code)
        if cluster is None:
            return err(f"entity {cdp_code} not found")

        if since_dt is not None:
            rows = await c.fetch(
                """
                SELECT event_type, old_value, new_value, observed_at, entity_ulid
                  FROM vehicle_event
                 WHERE entity_ulid = ANY($1::text[])
                   AND observed_at >= $2
                 ORDER BY observed_at DESC, event_type
                 LIMIT $3 OFFSET $4
                """,
                cluster.member_ulids,
                since_dt,
                size,
                offset,
            )
        else:
            rows = await c.fetch(
                """
                SELECT event_type, old_value, new_value, observed_at, entity_ulid
                  FROM vehicle_event
                 WHERE entity_ulid = ANY($1::text[])
                 ORDER BY observed_at DESC, event_type
                 LIMIT $2 OFFSET $3
                """,
                cluster.member_ulids,
                size,
                offset,
            )
        items = [{**dict(r), "observed_at": str(r["observed_at"])} for r in rows]
        return ok(
            items,
            page=page,
            size=size,
            returned=len(items),
            has_more=len(items) == size,
        )

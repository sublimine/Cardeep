"""/platforms/{cdp_code}/inventory + /vehicles/{ulid}/platforms endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from services.api.deps import err, ok, require_api_key

router = APIRouter()


# ---------------------------------------------------------------------------
# Platform endpoints (unchanged)
# ---------------------------------------------------------------------------

@router.get("/platforms/{cdp_code}/inventory")
async def platform_inventory(
    cdp_code: str,
    request: Request,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Cars linked to a platform via platform_listing, with selling-dealer attribution."""
    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        prow = await c.fetchrow(
            "SELECT entity_ulid, trade_name, kind FROM entity WHERE cdp_code=$1", cdp_code)
        if prow is None:
            return err(f"platform {cdp_code} not found")
        if prow["kind"] != "plataforma":
            return err(f"entity {cdp_code} is kind '{prow['kind']}', not a plataforma", status=400)
        rows = await c.fetch(
            """SELECT pl.listing_ref, pl.listing_url, pl.platform_price, pl.status AS listing_status,
                      pl.first_seen AS listed_first_seen, pl.last_seen AS listed_last_seen,
                      v.vehicle_ulid, v.make, v.model, v.year, v.km, v.price, v.currency,
                      v.fuel, v.transmission, v.photo_url, v.status AS vehicle_status,
                      d.cdp_code AS dealer_cdp_code, d.trade_name AS dealer_name,
                      d.province_code AS dealer_province, d.municipality_code AS dealer_municipality,
                      d.kind AS dealer_kind
                 FROM platform_listing pl
                 JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
                 JOIN entity d ON d.entity_ulid = v.entity_ulid
                WHERE pl.platform_entity_ulid = $1 AND pl.status = 'listed'
                ORDER BY pl.first_seen DESC, pl.vehicle_ulid
                LIMIT $2 OFFSET $3""",
            prow["entity_ulid"], size, offset,
        )
        items = []
        for r in rows:
            d = dict(r)
            d["platform_price"] = float(r["platform_price"]) if r["platform_price"] is not None else None
            d["price"] = float(r["price"]) if r["price"] is not None else None
            d["listed_first_seen"] = str(r["listed_first_seen"])
            d["listed_last_seen"] = str(r["listed_last_seen"])
            items.append(d)
        return ok(
            items,
            page=page,
            size=size,
            returned=len(items),
            has_more=len(items) == size,
            platform=prow["trade_name"],
            cdp_code=cdp_code,
        )


@router.get("/vehicles/{vehicle_ulid}/platforms")
async def vehicle_platforms(
    vehicle_ulid: str,
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Platforms a vehicle is listed on, plus its owning dealer."""
    async with request.app.state.pool.acquire() as c:
        vrow = await c.fetchrow(
            """SELECT v.vehicle_ulid, v.make, v.model, v.year, v.deep_link,
                      d.cdp_code AS dealer_cdp_code, d.trade_name AS dealer_name, d.kind AS dealer_kind
                 FROM vehicle v JOIN entity d ON d.entity_ulid = v.entity_ulid
                WHERE v.vehicle_ulid = $1""", vehicle_ulid)
        if vrow is None:
            return err(f"vehicle {vehicle_ulid} not found")
        rows = await c.fetch(
            """SELECT e.cdp_code, e.trade_name, e.website, e.is_tier1,
                      pl.listing_ref, pl.listing_url, pl.platform_price, pl.status,
                      pl.first_seen, pl.last_seen
                 FROM platform_listing pl
                 JOIN entity e ON e.entity_ulid = pl.platform_entity_ulid
                WHERE pl.vehicle_ulid = $1
                ORDER BY pl.first_seen DESC""", vehicle_ulid)
        platforms = []
        for r in rows:
            d = dict(r)
            d["platform_price"] = float(r["platform_price"]) if r["platform_price"] is not None else None
            d["first_seen"] = str(r["first_seen"])
            d["last_seen"] = str(r["last_seen"])
            platforms.append(d)
        vehicle = {
            "vehicle_ulid": vrow["vehicle_ulid"],
            "make": vrow["make"],
            "model": vrow["model"],
            "year": vrow["year"],
            "deep_link": vrow["deep_link"],
            "owning_dealer": {
                "cdp_code": vrow["dealer_cdp_code"],
                "name": vrow["dealer_name"],
                "kind": vrow["dealer_kind"],
            },
        }
        return ok({"vehicle": vehicle, "platforms": platforms}, count=len(platforms))

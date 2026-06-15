"""/geo/* — geographic entity listing and tree/completeness endpoints.

SU-D2 additions:
  - /geo/completeness: RATE_EXPENSIVE + cached (runs 7 sequential COUNT(*) queries
    over full entity + vehicle tables; changes only between harvests).
  - /geo/{province}/tree: RATE_EXPENSIVE + cached (GROUP BY over 50k+ entity rows
    per province; expensive and stable within a harvest window).
  - /geo/{province}/entities: RATE_DEFAULT + cached (paginated; stable between
    harvests — status/kind filters are enforced at DB write time).
  - /geo/{province}/municipalities/{muni}/entities: RATE_DEFAULT + cached (same
    stability contract as province listing, scoped to municipality).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from services.api.cache import cache_set, try_cache_get
from services.api.deps import err, ok, require_api_key
from services.api.ratelimit import RATE_DEFAULT, RATE_EXPENSIVE, limiter

router = APIRouter()


# ---------------------------------------------------------------------------
# Static-path routes FIRST — must precede any /geo/{province_code}/... routes
# so FastAPI does not swallow "completeness" as a province_code value.
# ---------------------------------------------------------------------------

@router.get("/geo/completeness")
@limiter.limit(RATE_EXPENSIVE)
async def geo_completeness(
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """National geo-completeness report.

    SU-D2: cached (7 sequential COUNT(*) queries; stable between harvests).
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        e_total = await c.fetchval("SELECT count(*) FROM entity")
        e_full = await c.fetchval(
            "SELECT count(*) FROM entity WHERE province_code IS NOT NULL "
            "AND municipality_code IS NOT NULL AND comarca_id IS NOT NULL")
        e_no_comarca_city = await c.fetchval(
            "SELECT count(*) FROM entity WHERE municipality_code IS NOT NULL AND comarca_id IS NULL")
        e_prov_only = await c.fetchval(
            "SELECT count(*) FROM entity WHERE province_code IS NOT NULL AND municipality_code IS NULL")
        e_no_geo = await c.fetchval("SELECT count(*) FROM entity WHERE province_code IS NULL")
        v_total = await c.fetchval("SELECT count(*) FROM vehicle")
        v_full = await c.fetchval(
            "SELECT count(*) FROM vehicle v JOIN entity e ON e.entity_ulid=v.entity_ulid "
            "WHERE e.province_code IS NOT NULL AND e.municipality_code IS NOT NULL "
            "AND e.comarca_id IS NOT NULL")
        geo = {
            "provinces": await c.fetchval("SELECT count(*) FROM geo_province"),
            "comarcas": await c.fetchval("SELECT count(*) FROM geo_comarca"),
            "municipalities": await c.fetchval("SELECT count(*) FROM geo_municipality"),
            "municipalities_with_comarca": await c.fetchval(
                "SELECT count(*) FROM geo_municipality WHERE comarca_id IS NOT NULL"),
        }
        response = ok({
            "geo_grid": geo,
            "entities": {
                "total": e_total, "full_prov_comarca_muni": e_full,
                "municipality_no_comarca_ceuta_melilla": e_no_comarca_city,
                "province_only": e_prov_only, "no_geo": e_no_geo,
                "full_pct": round(100 * e_full / e_total, 2) if e_total else 0,
            },
            "vehicles": {
                "total": v_total, "full_prov_comarca_muni": v_full,
                "full_pct": round(100 * v_full / v_total, 2) if v_total else 0,
            },
        })
    return cache_set(request, response)


# ---------------------------------------------------------------------------
# GAP 1 fix: /geo/{province}/entities filters active non-particular
# GAP 3 new: /geo/{province}/municipalities/{muni}/entities
# ---------------------------------------------------------------------------

@router.get("/geo/{province_code}/entities")
@limiter.limit(RATE_DEFAULT)
async def entities_by_province(
    province_code: str,
    request: Request,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """List active non-particular entities for a province.

    GAP-1 fix: adds WHERE status='active' AND kind <> 'particular'.
    Excludes C2C sellers and unverified entities — only trade point-of-sale
    dealers are returned.

    Pagination (B3.1): accepts ``page``/``size``.

    SU-D2: cached (entity status/kind filtered at write time; stable between
    harvests).
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT cdp_code, kind, trade_name, legal_name, municipality_code,
                   is_tier1, status
              FROM entity
             WHERE province_code = $1
               AND status = 'active'
               AND kind <> 'particular'
             ORDER BY trade_name, cdp_code
             LIMIT $2 OFFSET $3
            """,
            province_code,
            size,
            offset,
        )
        response = ok(
            [dict(r) for r in rows],
            page=page,
            size=size,
            returned=len(rows),
            has_more=len(rows) == size,
            province=province_code,
        )
    return cache_set(request, response)


@router.get("/geo/{province_code}/municipalities/{muni_code}/entities")
@limiter.limit(RATE_DEFAULT)
async def entities_by_municipality(
    province_code: str,
    muni_code: str,
    request: Request,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """GAP-3: List active non-particular dealers in a specific municipality.

    Scopes to province_code + municipality_code so callers can drill
    country → province → municipality without fetching the full province dump.
    Applies the same active/non-particular filter as /geo/{province}/entities.

    Pagination (B3.1): accepts ``page``/``size``.

    SU-D2: cached (same stability contract as province listing, scoped to muni).
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    offset = (page - 1) * size
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT cdp_code, kind, trade_name, legal_name, municipality_code,
                   is_tier1, status
              FROM entity
             WHERE province_code = $1
               AND municipality_code = $2
               AND status = 'active'
               AND kind <> 'particular'
             ORDER BY trade_name, cdp_code
             LIMIT $3 OFFSET $4
            """,
            province_code,
            muni_code,
            size,
            offset,
        )
        response = ok(
            [dict(r) for r in rows],
            page=page,
            size=size,
            returned=len(rows),
            has_more=len(rows) == size,
            province=province_code,
            municipality=muni_code,
        )
    return cache_set(request, response)


# ---------------------------------------------------------------------------
# Existing geo endpoints (unchanged logic)
# ---------------------------------------------------------------------------

@router.get("/geo/{province_code}/tree")
@limiter.limit(RATE_EXPENSIVE)
async def province_inventory_tree(
    province_code: str,
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Province inventory grouped pais -> PROVINCIA -> COMARCA -> ciudad.

    SU-D2: cached (GROUP BY over 50k+ entity rows; stable within a harvest
    window; tree structure changes only when new dealers are ingested).
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        prov = await c.fetchrow(
            "SELECT code, name, ccaa_code, ccaa_name FROM geo_province WHERE code=$1",
            province_code)
        if prov is None:
            return err(f"province {province_code} not found")
        rows = await c.fetch(
            """SELECT co.id AS comarca_id, co.name AS comarca, co.ine_code,
                      m.code AS municipality_code, m.name AS municipality,
                      count(e.entity_ulid) AS entities,
                      count(*) FILTER (WHERE e.kind='compraventa')          AS compraventa,
                      count(*) FILTER (WHERE e.kind='concesionario_oficial') AS oficial,
                      count(*) FILTER (WHERE e.kind='desguace')             AS desguace,
                      count(*) FILTER (WHERE e.kind='plataforma')           AS plataforma
                 FROM entity e
                 JOIN geo_municipality m ON m.code = e.municipality_code
                 JOIN geo_comarca      co ON co.id = m.comarca_id
                WHERE e.province_code = $1 AND e.comarca_id IS NOT NULL
                GROUP BY co.id, co.name, co.ine_code, m.code, m.name
                HAVING count(e.entity_ulid) > 0
                ORDER BY co.ine_code, entities DESC, m.name""",
            province_code)
        comarcas: dict[int, dict[str, Any]] = {}
        prov_total = 0
        for r in rows:
            node = comarcas.setdefault(r["comarca_id"], {
                "comarca_id": r["comarca_id"], "ine_code": r["ine_code"],
                "name": r["comarca"], "entities": 0, "municipalities": []})
            node["entities"] += r["entities"]
            prov_total += r["entities"]
            node["municipalities"].append({
                "municipality_code": r["municipality_code"], "name": r["municipality"],
                "entities": r["entities"], "compraventa": r["compraventa"],
                "oficial": r["oficial"], "desguace": r["desguace"],
                "plataforma": r["plataforma"]})
        province_only = await c.fetchval(
            "SELECT count(*) FROM entity WHERE province_code=$1 AND municipality_code IS NULL",
            province_code)
        tree = {
            "province": {"code": prov["code"], "name": prov["name"],
                         "ccaa_code": prov["ccaa_code"], "ccaa_name": prov["ccaa_name"]},
            "comarcas": list(comarcas.values()),
            "entities_geo_clean": prov_total,
            "entities_province_only_no_municipality": province_only,
        }
        response = ok(tree, comarca_count=len(comarcas), province=province_code)
    return cache_set(request, response)

"""Cardeep live API (F2 skeleton -> F6 full, all 7 gaps closed).

Serves per-entity inventory and delta over the PostgreSQL backbone.
Consistent envelope: {ok, data, error, meta}.

Run: uvicorn services.api.main:app --host 127.0.0.1 --port 8090

Pagination (B3.1)
-----------------
Endpoints that can return unbounded rows accept:
  page: int >= 1          (default 1)
  size: int in [1..200]   (default 50, clamped)

The ``meta`` block for paginated responses carries:
  {page, size, returned, has_more}

``has_more`` is True when the DB returned exactly ``size`` rows, meaning
there MAY be a next page.  A full COUNT(*) is intentionally avoided on
tables with 500 k+ rows.

Sealed product surface
----------------------
  - /entities/{cdp}/inventory dedups WITHIN the dealer cluster by
    canonical_vehicle_ulid (collapses the dealer's own cross-platform
    duplicates; KEEPS cars whose global canonical sits in another dealer —
    the dealer genuinely lists them). /health reports the GLOBAL unique count
    (v_canonical_vehicle canonical-only + available = 1 486 285).
  - /geo endpoints serve only active non-particular entities (status='active'
    AND kind <> 'particular').
  - /health reports sealed dealer count (v_canonical) and sealed vehicle
    count (v_canonical_vehicle canonical + available).
  - /delta is cluster-aware: events from ALL cluster members.
  - /vehicles/{ulid} resolves aliases to canonical; /vehicles/{ulid}/history
    returns the full event stream for a vehicle.
  - /geo/{province}/municipalities/{muni}/entities scopes to a municipality.
  - /alerts returns active (unresolved) alerts with origin.
  - /sources returns source_health rows for monitoring.
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

import asyncpg
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")


# ---------------------------------------------------------------------------
# B3.5 — API key authentication (backward-compatible).
#
# Behaviour:
#   CARDEEP_API_KEY not set in environment  ->  public mode; all callers pass
#   CARDEEP_API_KEY set in environment      ->  protected mode; X-API-Key required
#
# Applied via Depends(require_api_key) on data endpoints only.
# NOT applied to /health so that liveness probes always reach it.
# ---------------------------------------------------------------------------

def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """FastAPI dependency: enforce the API key when CARDEEP_API_KEY is set."""
    configured_key = os.environ.get("CARDEEP_API_KEY")
    if configured_key is None:
        return
    if x_api_key != configured_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(DSN, min_size=1, max_size=8)
    try:
        yield
    finally:
        await app.state.pool.close()


app = FastAPI(title="Cardeep API", version="0.2.0", lifespan=lifespan)


def ok(data: Any, **meta: Any) -> JSONResponse:
    return JSONResponse({"ok": True, "data": data, "error": None, "meta": meta or None})


def err(message: str, status: int = 404) -> JSONResponse:
    return JSONResponse({"ok": False, "data": None, "error": message, "meta": None}, status_code=status)


# ---------------------------------------------------------------------------
# Cluster resolution helper (CAMPAIGN B1.5)
# ---------------------------------------------------------------------------

class ClusterInfo:
    """Result of resolving a cdp_code to its canonical cluster."""

    __slots__ = (
        "canonical_cdp_code",
        "canonical_ulid",
        "member_ulids",
        "member_cdp_codes",
    )

    def __init__(
        self,
        canonical_cdp_code: str,
        canonical_ulid: str,
        member_ulids: list[str],
        member_cdp_codes: list[str],
    ) -> None:
        self.canonical_cdp_code = canonical_cdp_code
        self.canonical_ulid = canonical_ulid
        self.member_ulids = member_ulids
        self.member_cdp_codes = member_cdp_codes


async def resolve_cluster(conn: asyncpg.Connection, cdp_code: str) -> ClusterInfo | None:
    """Resolve *cdp_code* to its canonical and return the full cluster membership.

    Algorithm
    ---------
    1. Look up the entity for *cdp_code* — return None if it does not exist.
    2. Compute the canonical_ulid using v_dealer_resolved (transitive VAM-verified
       clusters), falling back to the entity's own ulid for non-clustered entities.
    3. Collect ALL entities whose canonical (via the same COALESCE logic) equals
       that canonical_ulid — those form the complete cluster.

    Note: uses v_dealer_resolved instead of the deprecated v_canonical so that
    resolution is consistent with the sealed B1 dealer count (40 016).
    """
    entity_row = await conn.fetchrow(
        """
        SELECT e.entity_ulid,
               COALESCE(vdr.resolved_ulid, e.entity_ulid)     AS canonical_ulid,
               COALESCE(vdr.resolved_cdp_code, e.cdp_code)    AS canonical_cdp_code
          FROM entity e
          LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid = e.entity_ulid
         WHERE e.cdp_code = $1
        """,
        cdp_code,
    )
    if entity_row is None:
        return None

    canonical_ulid: str = entity_row["canonical_ulid"]
    canonical_cdp_code: str = entity_row["canonical_cdp_code"]

    member_rows = await conn.fetch(
        """
        SELECT e.entity_ulid,
               e.cdp_code
          FROM entity e
          LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid = e.entity_ulid
         WHERE COALESCE(vdr.resolved_ulid, e.entity_ulid) = $1
        """,
        canonical_ulid,
    )
    member_ulids = [r["entity_ulid"] for r in member_rows]
    member_cdp_codes = [r["cdp_code"] for r in member_rows]

    return ClusterInfo(
        canonical_cdp_code=canonical_cdp_code,
        canonical_ulid=canonical_ulid,
        member_ulids=member_ulids,
        member_cdp_codes=member_cdp_codes,
    )


# ---------------------------------------------------------------------------
# GAP 1+7 fix: /health reports sealed counts
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> JSONResponse:
    """Liveness probe with sealed product counts.

    dealers        — sealed dealer count from v_dealer_resolved excluding
                     particulares (40 016: kind <> 'particular').
    vehicles_unique_available — canonical-only + status='available' (1 486 285,
                    not the 1 689 243 raw including cross-entity aliases).
    events         — total event rows (not filtered: historical record).
    provinces      — static geo table row count.
    municipalities — static geo table row count.
    """
    async with app.state.pool.acquire() as c:
        counts = {
            "dealers": await c.fetchval(
                """
                SELECT count(DISTINCT vdr.resolved_cdp_code)
                  FROM v_dealer_resolved vdr
                  JOIN entity e ON e.entity_ulid = vdr.entity_ulid
                 WHERE e.kind <> 'particular'
                """
            ),
            "vehicles_unique_available": await c.fetchval(
                """
                SELECT count(*)
                  FROM v_canonical_vehicle vc
                  JOIN vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
                 WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid
                   AND v.status = 'available'
                """
            ),
            "events": await c.fetchval("SELECT count(*) FROM vehicle_event"),
            "provinces": await c.fetchval("SELECT count(*) FROM geo_province"),
            "municipalities": await c.fetchval("SELECT count(*) FROM geo_municipality"),
        }
    return ok({"status": "live", "counts": counts})


# ---------------------------------------------------------------------------
# Entity resolution endpoints (B1.5 — unchanged)
# ---------------------------------------------------------------------------

@app.get("/entities/{cdp_code}/canonical")
async def get_entity_canonical(cdp_code: str, _: None = Depends(require_api_key)) -> JSONResponse:
    """Resolve *cdp_code* to its canonical and expose the full cluster."""
    async with app.state.pool.acquire() as c:
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


@app.get("/entities/{cdp_code}")
async def get_entity(cdp_code: str, _: None = Depends(require_api_key)) -> JSONResponse:
    """Return the CANONICAL entity for *cdp_code* with aggregated cluster inventory."""
    async with app.state.pool.acquire() as c:
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

@app.get("/entities/{cdp_code}/inventory")
async def get_inventory(
    cdp_code: str,
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
    async with app.state.pool.acquire() as c:
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

@app.get("/entities/{cdp_code}/delta")
async def get_delta(
    cdp_code: str,
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
    async with app.state.pool.acquire() as c:
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


# ---------------------------------------------------------------------------
# GAP 1 fix: /geo/{province}/entities filters active non-particular
# GAP 3 new: /geo/{province}/municipalities/{muni}/entities
# ---------------------------------------------------------------------------

@app.get("/geo/{province_code}/entities")
async def entities_by_province(
    province_code: str,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """List active non-particular entities for a province.

    GAP-1 fix: adds WHERE status='active' AND kind <> 'particular'.
    Excludes C2C sellers and unverified entities — only trade point-of-sale
    dealers are returned.

    Pagination (B3.1): accepts ``page``/``size``.
    """
    offset = (page - 1) * size
    async with app.state.pool.acquire() as c:
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
        return ok(
            [dict(r) for r in rows],
            page=page,
            size=size,
            returned=len(rows),
            has_more=len(rows) == size,
            province=province_code,
        )


@app.get("/geo/{province_code}/municipalities/{muni_code}/entities")
async def entities_by_municipality(
    province_code: str,
    muni_code: str,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """GAP-3: List active non-particular dealers in a specific municipality.

    Scopes to province_code + municipality_code so callers can drill
    country → province → municipality without fetching the full province dump.
    Applies the same active/non-particular filter as /geo/{province}/entities.

    Pagination (B3.1): accepts ``page``/``size``.
    """
    offset = (page - 1) * size
    async with app.state.pool.acquire() as c:
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
        return ok(
            [dict(r) for r in rows],
            page=page,
            size=size,
            returned=len(rows),
            has_more=len(rows) == size,
            province=province_code,
            municipality=muni_code,
        )


# ---------------------------------------------------------------------------
# Existing geo endpoints (unchanged)
# ---------------------------------------------------------------------------

@app.get("/geo/{province_code}/tree")
async def province_inventory_tree(province_code: str, _: None = Depends(require_api_key)) -> JSONResponse:
    """Province inventory grouped pais -> PROVINCIA -> COMARCA -> ciudad."""
    async with app.state.pool.acquire() as c:
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
        return ok(tree, comarca_count=len(comarcas), province=province_code)


@app.get("/geo/completeness")
async def geo_completeness(_: None = Depends(require_api_key)) -> JSONResponse:
    """National geo-completeness report."""
    async with app.state.pool.acquire() as c:
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
        return ok({
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


# ---------------------------------------------------------------------------
# Platform endpoints (unchanged)
# ---------------------------------------------------------------------------

@app.get("/platforms/{cdp_code}/inventory")
async def platform_inventory(
    cdp_code: str,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Cars linked to a platform via platform_listing, with selling-dealer attribution."""
    offset = (page - 1) * size
    async with app.state.pool.acquire() as c:
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


@app.get("/vehicles/{vehicle_ulid}/platforms")
async def vehicle_platforms(vehicle_ulid: str, _: None = Depends(require_api_key)) -> JSONResponse:
    """Platforms a vehicle is listed on, plus its owning dealer."""
    async with app.state.pool.acquire() as c:
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


# ---------------------------------------------------------------------------
# GAP 2 new: /vehicles/{ulid} detail + /vehicles/{ulid}/history
# ---------------------------------------------------------------------------

@app.get("/vehicles/{vehicle_ulid}/history")
async def vehicle_history(
    vehicle_ulid: str,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """GAP-2: Full event history for a vehicle (NEW→PRICE_CHANGE→GONE), oldest first.

    If *vehicle_ulid* is a non-canonical alias the history is still served —
    the alias vehicle_ulid is a real row in vehicle_event; aliasing is an
    entity-level concept for cross-dealer duplicates, not an erasure of history.

    Pagination: oldest events first (ASC) so callers can replay the timeline.
    """
    offset = (page - 1) * size
    async with app.state.pool.acquire() as c:
        exists = await c.fetchval(
            "SELECT 1 FROM vehicle WHERE vehicle_ulid = $1", vehicle_ulid)
        if exists is None:
            return err(f"vehicle {vehicle_ulid} not found")
        rows = await c.fetch(
            """
            SELECT event_type, old_value, new_value, observed_at
              FROM vehicle_event
             WHERE vehicle_ulid = $1
             ORDER BY observed_at ASC, event_type
             LIMIT $2 OFFSET $3
            """,
            vehicle_ulid,
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
            vehicle_ulid=vehicle_ulid,
        )


@app.get("/vehicles/{vehicle_ulid}")
async def vehicle_detail(
    vehicle_ulid: str,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """GAP-2: Full detail for a single vehicle.

    If *vehicle_ulid* is a non-canonical alias (per v_canonical_vehicle),
    the canonical_vehicle_ulid is exposed so callers can redirect.
    Returns 404 with coherent message when the ulid does not exist at all.
    """
    async with app.state.pool.acquire() as c:
        row = await c.fetchrow(
            """
            SELECT v.vehicle_ulid, v.make, v.model, v.year, v.km, v.price, v.currency,
                   v.photo_url, v.deep_link, v.title, v.fuel, v.transmission,
                   v.status, v.first_seen, v.last_seen,
                   vc.canonical_vehicle_ulid
              FROM vehicle v
              LEFT JOIN v_canonical_vehicle vc ON vc.vehicle_ulid = v.vehicle_ulid
             WHERE v.vehicle_ulid = $1
            """,
            vehicle_ulid,
        )
        if row is None:
            return err(f"vehicle {vehicle_ulid} not found")
        data = dict(row)
        data["price"] = float(data["price"]) if data["price"] is not None else None
        data["first_seen"] = str(data["first_seen"])
        data["last_seen"] = str(data["last_seen"])
        canonical = data.pop("canonical_vehicle_ulid")
        data["is_canonical"] = (canonical is None) or (canonical == vehicle_ulid)
        data["canonical_vehicle_ulid"] = canonical if canonical else vehicle_ulid
        return ok(data)


# ---------------------------------------------------------------------------
# GAP 5 new: /alerts (active unresolved) + /sources (source_health)
# ---------------------------------------------------------------------------

@app.get("/alerts")
async def list_alerts(
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """GAP-5: Active (unresolved) alerts with exact origin.

    Columns served: id, origin, severity, message, payload, created_at.
    Sorted by severity priority (critical → warning → info) then by most
    recent first so the most urgent alerts surface at the top.

    Only rows WHERE resolved_at IS NULL are returned — resolved alerts
    are not surfaced here (historical; use a separate query if needed).
    """
    offset = (page - 1) * size
    async with app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT id, origin, severity, message, payload, created_at
              FROM alert
             WHERE resolved_at IS NULL
             ORDER BY
               CASE severity
                 WHEN 'critical' THEN 0
                 WHEN 'warning'  THEN 1
                 ELSE                 2
               END,
               created_at DESC
             LIMIT $1 OFFSET $2
            """,
            size,
            offset,
        )
        items = [
            {
                **dict(r),
                "created_at": str(r["created_at"]),
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


@app.get("/sources")
async def list_sources(_: None = Depends(require_api_key)) -> JSONResponse:
    """GAP-5: Source health overview for all known scrapers/sources.

    Columns: source_key, status, consecutive_fails, last_ok, last_fail, is_tier1.
    Sorted: degraded/down first (most urgent), then by consecutive_fails DESC
    so the sickest sources are at the top.
    """
    async with app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT source_key, status, consecutive_fails,
                   last_ok, last_fail, is_tier1
              FROM source_health
             ORDER BY
               CASE status
                 WHEN 'down'     THEN 0
                 WHEN 'degraded' THEN 1
                 WHEN 'unknown'  THEN 2
                 ELSE                 3
               END,
               consecutive_fails DESC,
               source_key
            """
        )
        items = [
            {
                **dict(r),
                "last_ok": str(r["last_ok"]) if r["last_ok"] else None,
                "last_fail": str(r["last_fail"]) if r["last_fail"] else None,
            }
            for r in rows
        ]
        return ok(items, count=len(items))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8090)

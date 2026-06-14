"""Cardeep live API (F2 skeleton -> F6 full).

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
tables with 500 k+ rows — for wallapop 576 k listings a SELECT COUNT(*)
costs ~40 ms extra per request and is not worth it.
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
#   CARDEEP_API_KEY not set in environment  ->  public mode; all callers pass (no change
#                                               to existing behaviour — all existing tests
#                                               pass without providing a key).
#   CARDEEP_API_KEY set in environment      ->  protected mode; callers must send the
#                                               'X-API-Key' header with the correct value.
#                                               Missing or wrong key -> HTTP 401.
#
# Applied via Depends(require_api_key) on data endpoints only (entities / platforms / geo /
# vehicles). NOT applied to /health so that liveness probes and monitoring always reach it.
# ---------------------------------------------------------------------------

def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """FastAPI dependency: enforce the API key when CARDEEP_API_KEY is set in the
    environment. No-op (public) when the env var is absent so all existing callers and
    tests continue to work without any modification."""
    configured_key = os.environ.get("CARDEEP_API_KEY")
    if configured_key is None:
        # Public mode — key not configured; grant access unconditionally.
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


app = FastAPI(title="Cardeep API", version="0.1.0", lifespan=lifespan)


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
    2. Compute the canonical_ulid using the latest VAM-verified v_canonical view,
       falling back to the entity's own ulid for non-clustered / particular entities.
    3. Collect ALL entities whose canonical (via the same COALESCE logic) equals
       that canonical_ulid — those form the complete cluster.

    Returns ClusterInfo or None if *cdp_code* does not exist.
    """
    # Step 1 — resolve the input entity
    entity_row = await conn.fetchrow(
        """
        SELECT e.entity_ulid,
               COALESCE(vc.canonical_ulid, e.entity_ulid)    AS canonical_ulid,
               COALESCE(vc.canonical_cdp_code, e.cdp_code)   AS canonical_cdp_code
          FROM entity e
          LEFT JOIN v_canonical vc ON vc.entity_ulid = e.entity_ulid
         WHERE e.cdp_code = $1
        """,
        cdp_code,
    )
    if entity_row is None:
        return None

    canonical_ulid: str = entity_row["canonical_ulid"]
    canonical_cdp_code: str = entity_row["canonical_cdp_code"]

    # Step 2 — collect all members of the cluster
    member_rows = await conn.fetch(
        """
        SELECT e.entity_ulid,
               e.cdp_code
          FROM entity e
          LEFT JOIN v_canonical vc ON vc.entity_ulid = e.entity_ulid
         WHERE COALESCE(vc.canonical_ulid, e.entity_ulid) = $1
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


@app.get("/health")
async def health() -> JSONResponse:
    async with app.state.pool.acquire() as c:
        counts = {
            "entities": await c.fetchval("SELECT count(*) FROM entity"),
            "vehicles_available": await c.fetchval("SELECT count(*) FROM vehicle WHERE status='available'"),
            "events": await c.fetchval("SELECT count(*) FROM vehicle_event"),
            "provinces": await c.fetchval("SELECT count(*) FROM geo_province"),
            "municipalities": await c.fetchval("SELECT count(*) FROM geo_municipality"),
        }
    return ok({"status": "live", "counts": counts})


@app.get("/entities/{cdp_code}/canonical")
async def get_entity_canonical(cdp_code: str, _: None = Depends(require_api_key)) -> JSONResponse:
    """Resolve *cdp_code* to its canonical and expose the full cluster.

    Response fields
    ---------------
    input_cdp_code    — the code requested by the caller
    canonical_cdp_code — the authoritative code for the physical dealer
    is_canonical      — True when input == canonical (this entity IS the representative)
    members           — list of all cdp_codes in the cluster (canonical included)
    n_members         — len(members); 1 for singletons
    """
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
    """Return the CANONICAL entity for *cdp_code* with aggregated cluster inventory.

    Changes vs pre-B1.5
    --------------------
    - Resolves *cdp_code* to its canonical; serves the canonical entity row.
    - available_inventory  — sum of available stock across ALL cluster members.
    - canonical_cdp_code   — the canonical identifier.
    - n_aliases            — cluster members excluding the canonical (duplicates collapsed).
    - queried_cdp_code     — the original code the caller sent.
    """
    async with app.state.pool.acquire() as c:
        cluster = await resolve_cluster(c, cdp_code)
        if cluster is None:
            return err(f"entity {cdp_code} not found")

        # Serve the canonical entity row
        row = await c.fetchrow(
            "SELECT * FROM entity WHERE entity_ulid = $1",
            cluster.canonical_ulid,
        )
        # Aggregate available inventory across the full cluster
        n_available = await c.fetchval(
            "SELECT count(*) FROM vehicle "
            "WHERE entity_ulid = ANY($1::text[]) AND status = 'available'",
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


@app.get("/entities/{cdp_code}/inventory")
async def get_inventory(
    cdp_code: str,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Return available stock for ALL cluster members, deduplicated by vehicle_ulid.

    Changes vs pre-B1.5
    --------------------
    Resolves *cdp_code* to its cluster and returns vehicles across all member entities,
    deduped by vehicle_ulid, ordered by first_seen DESC.

    Pagination (B3.1)
    -----------------
    Accepts ``page`` and ``size`` query params.  Returns ``has_more`` in meta.
    DISTINCT ON + ORDER requires a subquery to apply LIMIT/OFFSET after dedup.
    """
    offset = (page - 1) * size
    async with app.state.pool.acquire() as c:
        cluster = await resolve_cluster(c, cdp_code)
        if cluster is None:
            return err(f"entity {cdp_code} not found")

        rows = await c.fetch(
            """
            SELECT vehicle_ulid, deep_link, title, make, model, year, km, price, currency,
                   fuel, transmission, photo_url, status, first_seen, last_seen
              FROM (
                    SELECT DISTINCT ON (vehicle_ulid)
                           vehicle_ulid, deep_link, title, make, model, year, km, price,
                           currency, fuel, transmission, photo_url, status, first_seen, last_seen
                      FROM vehicle
                     WHERE entity_ulid = ANY($1::text[]) AND status = 'available'
                     ORDER BY vehicle_ulid, first_seen DESC
              ) deduped
             ORDER BY first_seen DESC, vehicle_ulid
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


@app.get("/entities/{cdp_code}/delta")
async def get_delta(
    cdp_code: str,
    since: str | None = None,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Return vehicle events for *cdp_code*.

    Pagination (B3.1)
    -----------------
    When ``since`` is provided the window can be very large (all events from a
    stale timestamp).  Both the ``since``-filtered and the unfiltered paths are
    now paginated via ``page``/``size``.  The old hard-coded ``LIMIT 500`` is
    replaced by the configurable ``size`` (max 200) so callers control depth.
    """
    offset = (page - 1) * size
    # Parse ``since`` to a timezone-aware datetime so asyncpg receives the
    # correct Python type (it rejects raw strings for timestamptz columns).
    since_dt: datetime | None = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError:
            return err(f"invalid since format '{since}'; use ISO-8601 (e.g. 2024-01-01T00:00:00Z)", status=400)
    async with app.state.pool.acquire() as c:
        eulid = await c.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", cdp_code)
        if eulid is None:
            return err(f"entity {cdp_code} not found")
        if since_dt is not None:
            rows = await c.fetch(
                "SELECT event_type, old_value, new_value, observed_at FROM vehicle_event "
                "WHERE entity_ulid=$1 AND observed_at >= $2 "
                "ORDER BY observed_at DESC, event_type LIMIT $3 OFFSET $4",
                eulid, since_dt, size, offset,
            )
        else:
            rows = await c.fetch(
                "SELECT event_type, old_value, new_value, observed_at FROM vehicle_event "
                "WHERE entity_ulid=$1 ORDER BY observed_at DESC, event_type LIMIT $2 OFFSET $3",
                eulid, size, offset,
            )
        items = [{**dict(r), "observed_at": str(r["observed_at"])} for r in rows]
        return ok(
            items,
            page=page,
            size=size,
            returned=len(items),
            has_more=len(items) == size,
        )


@app.get("/geo/{province_code}/entities")
async def entities_by_province(
    province_code: str,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """List entities for a province.

    Pagination (B3.1)
    -----------------
    Madrid (province_code='28') has 49 661 entities — an unbounded response
    was a P0 hazard.  Now paginated via ``page``/``size``.
    """
    offset = (page - 1) * size
    async with app.state.pool.acquire() as c:
        rows = await c.fetch(
            "SELECT cdp_code, kind, trade_name, legal_name, municipality_code, is_tier1, status "
            "FROM entity WHERE province_code=$1 ORDER BY trade_name, cdp_code LIMIT $2 OFFSET $3",
            province_code, size, offset,
        )
        return ok(
            [dict(r) for r in rows],
            page=page,
            size=size,
            returned=len(rows),
            has_more=len(rows) == size,
            province=province_code,
        )


@app.get("/geo/{province_code}/tree")
async def province_inventory_tree(province_code: str, _: None = Depends(require_api_key)) -> JSONResponse:
    """Province inventory grouped pais -> PROVINCIA -> COMARCA -> ciudad, with a
    clean count tree and zero NULL-geo noise (only municipality-resolved entities,
    inner-joined through the comarca layer)."""
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
        # province-only entities (have province, no municipality) reported separately,
        # never mixed into the comarca tree as noise.
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
    """National geo-completeness report: how many entities/vehicles carry the full
    pais+PROVINCIA+COMARCA+ciudad grid vs partial, every number from a live query."""
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


@app.get("/platforms/{cdp_code}/inventory")
async def platform_inventory(
    cdp_code: str,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=50, ge=1, le=200, description="Items per page (1-200)"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Cars linked to a platform via platform_listing, each WITH its selling-dealer
    attribution (the dual-membership proof: platform edge + singular dealer owner).

    Pagination (B3.1)
    -----------------
    Wallapop has 576 213 active listings — returning all in one request was a P0
    hazard.  Now paginated via ``page``/``size`` (default 50, max 200).
    """
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
    """The platforms a car is listed on (its platform_listing edges), plus the car's
    singular owning dealer — proving ownership and membership are distinct axes."""
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
        vehicle = {"vehicle_ulid": vrow["vehicle_ulid"], "make": vrow["make"],
                   "model": vrow["model"], "year": vrow["year"], "deep_link": vrow["deep_link"],
                   "owning_dealer": {"cdp_code": vrow["dealer_cdp_code"],
                                     "name": vrow["dealer_name"], "kind": vrow["dealer_kind"]}}
        return ok({"vehicle": vehicle, "platforms": platforms}, count=len(platforms))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8090)

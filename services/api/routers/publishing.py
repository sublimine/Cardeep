"""/publishing/* -- Frente A of pilar 05-multiposting (plans/cardeep-omni/05-multiposting.md).

Read-only "estado de publicacion" surface: for a dealer, where is their inventory
cross-listed, at what price, and with what anomalies -- built entirely from the
existing inbound edge (platform_listing, migration 0009) plus the dealer's own
census (vehicle/servable_vehicle) and the published market_stat run (01-market-
intelligence F1/F2). Zero credentials, zero outbound write -- ownership/scope per
00-MASTER.md and the carta's F1 (this file) covers criteria Sec.4.1-4.4 only:
Frente B (publish_job/AS24/feeds, F4/F5) is explicitly out of scope and gated.

Follows the exact pattern of platforms.py: require_api_key, ok/err envelope,
page_slice over a LIMIT size+1 overfetch, cache+rate-limit on the heavier endpoint.

REAL FINDING (F0, scripts/f0_publishing_census.py): platforms.py:49-50 hard-gates
`entity.kind == 'plataforma'`, which 400s on 96,941 real platform_listing edges
whose target is kind in {oem_vo_portal, cadena, rent_a_car_vo, importador} --
OEM certified-used portals, retail chains and rent-a-car de-fleeting channels that
legitimately re-list a dealer's car under their own brand. From the DEALER's point
of view ("where is MY car cross-posted") that census taxonomy is irrelevant -- the
edge itself is the operative fact. This router does NOT replicate that kind-gate;
every platform_listing edge is served regardless of the target entity's `kind`.
Declared here as a finding for platforms.py's owner, not silently fixed there (out
of this pilar's F0-F2 scope, and platforms.py is shared infrastructure other
pilares' tests already cover).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from services.api.cache import cache_set, try_cache_get
from services.api.deps import err, ok, page_slice, require_api_key
from services.api.ratelimit import RATE_DEFAULT, RATE_EXPENSIVE, limiter

router = APIRouter()

# ---------------------------------------------------------------------------
# Constants (05-multiposting.md carta S4.1/S4.2/S4.4 -- product thresholds live
# here, named, never inline; mirrors the local-constant pattern already used by
# services/api/routers/market.py's M2_BELOW_MARKET_CUT/M2_ABOVE_MARKET_CUT --
# no repo-wide "registro unico de umbrales" file exists yet (00-MASTER.md C-12
# names it as a future extension of pipeline/market/cohort.py; not built by any
# pilar so far), so this follows the same precedent instead of inventing a
# second convention).
# ---------------------------------------------------------------------------

# S4.1 coverage semaphore bands.
COVERAGE_GREEN_MIN: float = 0.80
COVERAGE_AMBER_MIN: float = 0.40

# S4.2 "precio distinto" badge: divergence must clear BOTH a relative floor (ignore
# rounding) and an absolute floor (ignore cent-level noise on cheap cars).
PRICE_DIVERGENCE_REL: float = 0.02   # 2% of the dealer's own price
PRICE_DIVERGENCE_ABS_EUR: float = 200.0

# S4.4 "anuncio viejo" badge: reuses 01-market-intelligence's published M3 metric
# (median days_to_listing_removal for make+model+year-band+fuel+province, see
# pipeline/market/metrics_f2.py) rather than deriving a second, independent
# cohort computation with a km-band as the carta originally sketched -- 00-MASTER
# C-1/C-12 prohibit a second median-by-cohort implementation, and M3 is already
# live, tested and published (see 05-multiposting.md S4.4 amendment, F0). The
# carta's own n-threshold for this badge (30) is stricter than cohort.py's
# MIN_COHORT_N (8) used when M3 was computed -- applied here as an additional
# local filter on top of M3's own `n`, not a re-derivation.
FRESCURA_MIN_N: int = 30


def _coverage_band(pct: float) -> str:
    if pct >= COVERAGE_GREEN_MIN:
        return "verde"
    if pct >= COVERAGE_AMBER_MIN:
        return "ambar"
    return "rojo"


def _price_divergence(dealer_price: float | None, platform_price: float | None) -> dict[str, Any] | None:
    """S4.2: signed delta + a hard boolean flag. None when either price is missing
    (never fabricate a divergence from a half-known pair)."""
    if dealer_price is None or platform_price is None:
        return None
    delta = platform_price - dealer_price
    threshold = max(PRICE_DIVERGENCE_REL * dealer_price, PRICE_DIVERGENCE_ABS_EUR)
    return {"delta": delta, "flag": abs(delta) > threshold}


def _classify_anomaly(vehicle_status: str, listing_status: str) -> str | None:
    """S4.3: the two hard anomaly states, pure functions of two already-verified
    columns (vehicle.status, platform_listing.status) -- zero heuristic, per the
    carta's own wording ("consultas directas sobre columnas verificadas; cero
    heuristica"). Extracted as a standalone function so it is unit-testable
    without depending on live data happening to contain a positive example today
    (05-multiposting-f1 report: the live corpus currently has ZERO
    sold_still_listed rows -- verified live, the harvester transitions a
    vehicle's platform_listing edges to 'removed' in the same pass it marks the
    vehicle 'gone', so the anomaly type is real but not currently observed; this
    function's correctness is proven by the unit tests, not by a live instance).
    """
    if vehicle_status == "gone" and listing_status == "listed":
        return "sold_still_listed"
    if vehicle_status == "available" and listing_status == "removed":
        return "available_removed"
    return None


async def _resolve_dealer(conn, cdp_code: str):
    return await conn.fetchrow(
        "SELECT entity_ulid, trade_name, kind, province_code FROM entity WHERE cdp_code=$1",
        cdp_code,
    )


# ---------------------------------------------------------------------------
# GET /publishing/{cdp_code}/coverage -- S4.1 semaphore per platform
# ---------------------------------------------------------------------------

@router.get("/publishing/{cdp_code}/coverage")
@limiter.limit(RATE_EXPENSIVE)
async def publishing_coverage(cdp_code: str, request: Request, _: None = Depends(require_api_key)) -> JSONResponse:
    """Per-platform coverage semaphore for one dealer (carta S4.1, S6.1).

    coverage(D,P) = count(listed AND available cars of D on P) / count(available cars of D).
    Only platforms with >=1 edge are returned (a portal the dealer has never touched
    carries no information -- showing a 0%-everywhere row for all 43 platforms would
    be noise, not signal).
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        drow = await _resolve_dealer(c, cdp_code)
        if drow is None:
            return err(f"dealer {cdp_code} not found")

        total_available = await c.fetchval(
            "SELECT count(*) FROM servable_vehicle WHERE entity_ulid=$1", drow["entity_ulid"]
        )

        rows = await c.fetch(
            """SELECT p.cdp_code, p.trade_name, p.kind,
                      count(DISTINCT pl.vehicle_ulid) AS n_listed
                 FROM platform_listing pl
                 JOIN servable_vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
                 JOIN entity p ON p.entity_ulid = pl.platform_entity_ulid
                WHERE v.entity_ulid = $1 AND pl.status = 'listed'
                GROUP BY p.cdp_code, p.trade_name, p.kind
                ORDER BY n_listed DESC""",
            drow["entity_ulid"],
        )

        platforms = []
        for r in rows:
            pct = (r["n_listed"] / total_available) if total_available else 0.0
            platforms.append({
                "cdp_code": r["cdp_code"],
                "trade_name": r["trade_name"],
                "kind": r["kind"],
                "n_listed": r["n_listed"],
                "coverage_pct": pct,
                "band": _coverage_band(pct),
            })

        response = ok(
            {
                "dealer": {"cdp_code": cdp_code, "trade_name": drow["trade_name"]},
                "total_available": total_available,
                "platforms": platforms,
            },
            n_platforms=len(platforms),
        )
    return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /publishing/{cdp_code}/matrix -- S4.1-S4.4 fused per-vehicle row (S6.2)
# ---------------------------------------------------------------------------

_VEHICLE_PAGE_SQL = """
    SELECT v.vehicle_ulid, v.deep_link, v.title, v.make, v.model, v.year, v.km,
           v.price, v.currency, v.fuel, v.transmission, v.photo_url,
           v.status, v.first_seen, v.last_seen
      FROM vehicle v
      LEFT JOIN servable_vehicle sv ON sv.vehicle_ulid = v.vehicle_ulid
     WHERE v.entity_ulid = $1
       AND (
             sv.vehicle_ulid IS NOT NULL
          OR (v.status = 'gone' AND EXISTS (
                SELECT 1 FROM platform_listing pl
                 WHERE pl.vehicle_ulid = v.vehicle_ulid AND pl.status = 'listed'))
           )
     ORDER BY v.last_seen DESC, v.vehicle_ulid
     LIMIT $2 OFFSET $3
"""


async def _fetch_latest_m3_run(conn) -> str | None:
    return await conn.fetchval(
        "SELECT run_id FROM market_stat_run WHERE published ORDER BY run_at DESC LIMIT 1"
    )


async def _fetch_m3_lookup(conn, run_id: str | None, segments: list[tuple]) -> dict[tuple, float]:
    """Batch-fetch M3 (median days_to_listing_removal) for the exact
    (make, model, year, fuel, province_code) combinations on the current page.

    Returns {} when there is no published run or no segment clears FRESCURA_MIN_N --
    callers must treat a missing key as "not computable", never as zero days.
    """
    if run_id is None or not segments:
        return {}
    makes = [s[0] for s in segments]
    models = [s[1] for s in segments]
    years = [s[2] for s in segments]
    fuels = [s[3] for s in segments]
    provinces = [s[4] for s in segments]
    rows = await conn.fetch(
        """SELECT make, model, year, fuel, province_code, value_num
             FROM market_stat
            WHERE run_id = $1 AND metric_id = 'M3' AND n >= $2
              AND (make, model, year, fuel, province_code) = ANY(
                    SELECT unnest($3::text[]), unnest($4::text[]), unnest($5::int[]),
                           unnest($6::text[]), unnest($7::text[])
                  )""",
        run_id, FRESCURA_MIN_N, makes, models, years, fuels, provinces,
    )
    return {(r["make"], r["model"], r["year"], r["fuel"], r["province_code"]): float(r["value_num"]) for r in rows}


@router.get("/publishing/{cdp_code}/matrix")
@limiter.limit(RATE_EXPENSIVE)
async def publishing_matrix(
    cdp_code: str,
    request: Request,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """One row per vehicle (available, OR gone-with-a-still-listed-edge for the
    'vendido pero sigue publicado' anomaly), each carrying its known platform
    edges with divergence/anomaly/frescura already computed (carta S4.1-S4.4,
    S6.2). A platform the vehicle has NO edge on is simply absent from its
    `platforms` array -- the frontend renders "no publicado" for any platform in
    /publishing/{cdp}/coverage's list that a given row's array does not contain.
    """
    async with request.app.state.pool.acquire() as c:
        drow = await _resolve_dealer(c, cdp_code)
        if drow is None:
            return err(f"dealer {cdp_code} not found")

        offset = (page - 1) * size
        vrows = await c.fetch(_VEHICLE_PAGE_SQL, drow["entity_ulid"], size + 1, offset)
        vrows, has_more = page_slice(vrows, size)

        if not vrows:
            response = ok([], page=page, size=size, returned=0, has_more=False,
                           dealer={"cdp_code": cdp_code, "trade_name": drow["trade_name"]})
            return response

        ulids = [r["vehicle_ulid"] for r in vrows]
        edge_rows = await c.fetch(
            """SELECT pl.vehicle_ulid, p.cdp_code AS platform_cdp_code, p.trade_name AS platform_name,
                      pl.listing_ref, pl.listing_url, pl.platform_price, pl.status AS listing_status,
                      pl.first_seen, pl.last_seen, pl.removed_at
                 FROM platform_listing pl
                 JOIN entity p ON p.entity_ulid = pl.platform_entity_ulid
                WHERE pl.vehicle_ulid = ANY($1::text[])
                ORDER BY pl.vehicle_ulid, pl.first_seen DESC""",
            ulids,
        )
        edges_by_vehicle: dict[str, list] = {}
        for e in edge_rows:
            edges_by_vehicle.setdefault(e["vehicle_ulid"], []).append(e)

        run_id = await _fetch_latest_m3_run(c)
        segments = sorted({
            (r["make"], r["model"], r["year"], r["fuel"], drow["province_code"])
            for r in vrows
            if r["make"] and r["model"] and r["year"] and r["fuel"] and drow["province_code"]
        })
        m3_lookup = await _fetch_m3_lookup(c, run_id, segments)

        items = []
        for v in vrows:
            v_price = float(v["price"]) if v["price"] is not None else None
            segment_key = (v["make"], v["model"], v["year"], v["fuel"], drow["province_code"])
            median_days = m3_lookup.get(segment_key)

            platforms = []
            for e in edges_by_vehicle.get(v["vehicle_ulid"], []):
                platform_price = float(e["platform_price"]) if e["platform_price"] is not None else None
                divergence = _price_divergence(v_price, platform_price)

                anomaly = _classify_anomaly(v["status"], e["listing_status"])

                old_listing = None
                if e["listing_status"] == "listed" and median_days is not None:
                    days_up = (e["last_seen"] - e["first_seen"]).total_seconds() / 86400.0
                    old_listing = days_up > median_days

                platforms.append({
                    "cdp_code": e["platform_cdp_code"],
                    "trade_name": e["platform_name"],
                    "listing_ref": e["listing_ref"],
                    "listing_url": e["listing_url"],
                    "platform_price": platform_price,
                    "status": e["listing_status"],
                    "first_seen": str(e["first_seen"]),
                    "last_seen": str(e["last_seen"]),
                    "removed_at": str(e["removed_at"]) if e["removed_at"] else None,
                    "divergence": divergence,
                    "anomaly": anomaly,
                    "old_listing": old_listing,
                })

            items.append({
                "vehicle_ulid": v["vehicle_ulid"],
                "deep_link": v["deep_link"],
                "title": v["title"],
                "make": v["make"],
                "model": v["model"],
                "year": v["year"],
                "km": v["km"],
                "price": v_price,
                "currency": v["currency"],
                "fuel": v["fuel"],
                "transmission": v["transmission"],
                "photo_url": v["photo_url"],
                "status": v["status"],
                "first_seen": str(v["first_seen"]),
                "last_seen": str(v["last_seen"]),
                "platforms": platforms,
            })

        return ok(
            items,
            page=page, size=size, returned=len(items), has_more=has_more,
            dealer={"cdp_code": cdp_code, "trade_name": drow["trade_name"]},
            frescura_run_id=run_id,
        )

"""/market/* — market-intelligence endpoints (pilar 01-market-intelligence, F3-F5).

Ownership: 00-MASTER.md resolution C-1 assigns this file and the ``/market/*``
namespace to pilar 01 exclusively. Pilar 09 (trading-terminal) owns a SEPARATE
``services/api/routers/terminal.py`` with ``/terminal/*`` — never this file. This
is ALSO the shared comparables engine pilar 03 (K9/K10/K11) and 07 (C2) are
expected to consume rather than re-derive (00-MASTER.md §98) — one implementation.

Scope built so far: M1/M3/M4/M5/M7/M9/M10 (F3, served from ``market_stat``), M8
(F4, served from ``dgt_corroboration``), and M2 (F5, price-position — computed
live against the latest published M1 row, never precomputed/stored per-vehicle:
storing a ratio for millions of vehicles that only changes when a NEW market_stat
run publishes would be pure staleness risk for zero benefit over a cheap live
lookup+division).

DECLARED GAP (not hidden): M6 (value curve by age cohort) is named in the carta's
router design (§5) but was never assigned a construction phase in §9's F0-F5 list
(F1=M1 only, F2=M3/M4/M5/M7/M9/M10 explicitly, F7=M6 LONGITUDINAL only — the
cross-sectional Fase-1 of M6 has no owning phase). Rather than fabricate M6 data to
fill the router's advertised shape, this endpoint simply omits M6 from the served
metric set until a future block computes it. The frontend spec (§6 item 5, "¿Cómo
pierde valor?") is therefore NOT servable from this router yet — declared here, not
silently dropped.

Every response carries ``run_id``, the run's ``computed_at``/``window_description``,
and each metric's own ``n`` + window — the carta's transversal rule ("todo widget
muestra n, ventana y timestamp del run"). A segment that never cleared
MIN_COHORT_N is simply ABSENT from the response body, never a fabricated zero.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from services.api.cache import cache_set, try_cache_get
from services.api.deps import err, ok, require_api_key
from services.api.search_parse import QueryParser
from services.api.ratelimit import RATE_DEFAULT, RATE_EXPENSIVE, limiter

router = APIRouter()

# Metrics served by /market/segments/.../stats (M2/M8 have their own dedicated
# endpoints below; M6 is a declared gap — see module docstring).
_SERVED_METRICS: tuple[str, ...] = ("M1", "M3", "M4", "M5", "M7", "M9", "M10")

# M2 price-position bands (carta §4 M2 row). [ASUMIDO -> re-verified in F5 against
# the REAL distribution of price/p50 ratios across 1,183,432 live canonical
# vehicles: p25=0.898, p50=1.000, p75=1.127 (01-market-intelligence-f5.md has the
# full percentile table). These cuts land close to the natural IQR split and are
# KEPT, not silently changed — a METHODOLOGY recalibration is explicitly reserved
# by the project's own model-routing doctrine for a caro-model adversarial gate
# (Fable 5/Opus), which this execution context could not invoke as a literal
# separate model call; the full analysis needed for that gate is written up in
# the F5 report so the decision can be made quickly, not re-derived from scratch.
M2_BELOW_MARKET_CUT: float = 0.92
M2_ABOVE_MARKET_CUT: float = 1.08


def _price_position_band(ratio: float) -> str:
    if ratio < M2_BELOW_MARKET_CUT:
        return "below_market"
    if ratio > M2_ABOVE_MARKET_CUT:
        return "above_market"
    return "at_market"


async def _latest_published_run(conn) -> dict[str, Any] | None:
    row = await conn.fetchrow(
        "SELECT run_id, run_at, methodology_version, window_description, metrics_computed "
        "FROM market_stat_run WHERE published = TRUE ORDER BY run_at DESC LIMIT 1"
    )
    return dict(row) if row is not None else None


def _row_payload(r: dict[str, Any]) -> dict[str, Any]:
    """Shape one market_stat row for the API — omits NULL distribution/scalar fields
    instead of serializing them as null noise (M1/M10 use p25/p50/p75; M3/M4/M5/M7/M9
    use value_num/value_extra — a row never has both shapes populated)."""
    payload: dict[str, Any] = {"n": r["n"]}
    if r["p25"] is not None:
        payload["p25"] = float(r["p25"])
    if r["p50"] is not None:
        payload["p50"] = float(r["p50"])
    if r["p75"] is not None:
        payload["p75"] = float(r["p75"])
    if r["value_num"] is not None:
        payload["value"] = float(r["value_num"])
    if r["value_extra"] is not None:
        payload["detail"] = r["value_extra"]
    return payload


# ---------------------------------------------------------------------------
# GET /market/segments/{make}/{model}/stats — M1/M3/M4/M7/M9/M10 for one segment
# ---------------------------------------------------------------------------

@router.get("/market/segments/{make}/{model}/stats")
@limiter.limit(RATE_DEFAULT)
async def segment_stats(
    make: str,
    model: str,
    request: Request,
    year: int = Query(..., description="Anchor year of the +/-1 sliding band (e.g. 2024)"),
    fuel: str = Query(..., description="Fuel type, exact match (e.g. 'Gasolina', 'Diesel')"),
    province: str | None = Query(default=None, description="2-char province code; omitted = national only"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """M1 (price p25/p50/p75), M3 (days-to-retirada), M4 (MDS), M7 (momentum),
    M9 (seller pressure), M10 (platform-count distribution) for one segment.

    Segment resolution honesty (carta §6 item 1): when ``province`` is given, the
    provincial row is served if it cleared MIN_COHORT_N; otherwise this endpoint
    falls back to the national row and sets ``fallback_to_national: true`` on that
    metric so the frontend can render the honest "aún no hay muestra suficiente en
    tu provincia" copy instead of silently swapping numbers. A metric absent from
    BOTH scopes is simply not a key in ``metrics`` — never a fabricated value.
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        run = await _latest_published_run(c)
        if run is None:
            return err("no published market_stat run yet", status=503)

        rows = await c.fetch(
            """
            SELECT metric_id, province_code, n, p25, p50, p75, value_num, value_extra
              FROM market_stat
             WHERE run_id = $1 AND make = $2 AND model = $3 AND year = $4 AND fuel = $5
               AND metric_id = ANY($6::text[])
               AND (province_code = $7 OR province_code IS NULL)
            """,
            run["run_id"], make, model, year, fuel, list(_SERVED_METRICS), province,
        )
        if not rows:
            return err(
                f"no market data for {make} {model} (year={year}, fuel={fuel}) — "
                f"either the segment does not exist or every cohort is below the "
                f"minimum sample size (n>=8)",
                status=404,
            )

        by_metric_scope: dict[str, dict[str, dict]] = {}
        for r in rows:
            scope = "prov" if r["province_code"] is not None else "nat"
            by_metric_scope.setdefault(r["metric_id"], {})[scope] = dict(r)

        metrics: dict[str, Any] = {}
        for metric_id, scopes in by_metric_scope.items():
            wanted_scope = "prov" if (province is not None and "prov" in scopes) else "nat"
            if wanted_scope not in scopes:
                wanted_scope = "nat" if "nat" in scopes else "prov"
            chosen = scopes[wanted_scope]
            payload = _row_payload(chosen)
            payload["scope"] = wanted_scope
            payload["fallback_to_national"] = (province is not None and wanted_scope == "nat")
            metrics[metric_id] = payload

        response = ok(
            {
                "make": make, "model": model, "year": year, "fuel": fuel,
                "province_requested": province,
                "metrics": metrics,
            },
            run_id=run["run_id"],
            run_at=str(run["run_at"]),
            methodology_version=run["methodology_version"],
            window_description=run["window_description"],
        )
        return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /market/provinces/demand — M5 provincial absorption ranking
# ---------------------------------------------------------------------------

@router.get("/market/provinces/demand")
@limiter.limit(RATE_EXPENSIVE)
async def provinces_demand(
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """M5 ranking: absorption rate (GONE/available in the run's window) per province.

    No make/model dimension (carta §4 M5 row: national demand map, not a segment
    filter) — every province that cleared MIN_COHORT_N on the available side in the
    latest published run, ordered by absorption rate descending.
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        run = await _latest_published_run(c)
        if run is None:
            return err("no published market_stat run yet", status=503)

        rows = await c.fetch(
            """
            SELECT province_code, n, value_num, value_extra
              FROM market_stat
             WHERE run_id = $1 AND metric_id = 'M5'
             ORDER BY value_num DESC NULLS LAST
            """,
            run["run_id"],
        )
        items = [
            {
                "province_code": r["province_code"],
                "n_available": r["n"],
                "absorption_rate": float(r["value_num"]) if r["value_num"] is not None else None,
                "detail": r["value_extra"],
            }
            for r in rows
        ]
        response = ok(
            items,
            run_id=run["run_id"],
            run_at=str(run["run_at"]),
            window_description=run["window_description"],
            count=len(items),
        )
        return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /market/dgt-corroboration — M8 (F4): DGT-vs-GONE cohort corroboration
# ---------------------------------------------------------------------------

async def _latest_corroboration_run(conn) -> dict[str, Any] | None:
    row = await conn.fetchrow(
        "SELECT run_id, run_at, month, methodology_version, notes "
        "FROM dgt_corroboration_run ORDER BY run_at DESC LIMIT 1"
    )
    return dict(row) if row is not None else None


@router.get("/market/dgt-corroboration")
@limiter.limit(RATE_DEFAULT)
async def dgt_corroboration(
    request: Request,
    province: str | None = Query(default=None, description="2-char province code; omitted = national rows"),
    make: str | None = Query(default=None, description="Make, case-insensitive"),
    model: str | None = Query(default=None, description="Model, case-insensitive; omitted = make-level rows only"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """M8: what fraction of Cardeep's GONE signal is corroborated against the DGT's
    official monthly transfer registry, per (province+make[+model]) cohort.

    Published as a DATA-QUALITY metric (carta §4 M8 row) — a low ratio is not hidden,
    it is the honest measurement of how much of the "listing removed" proxy actually
    lines up with an official ownership-transfer record for that cohort+month. No
    per-VIN join is possible (DGT restricts the chassis number since 2025-02-01);
    this is COHORT-level corroboration only, never a per-unit "this exact car sold"
    claim (carta §3.2 declared limit).
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        run = await _latest_corroboration_run(c)
        if run is None:
            return err("no dgt_corroboration run yet", status=503)

        make_norm = make.strip().upper() if make else None
        model_norm = model.strip().upper() if model else None

        rows = await c.fetch(
            """
            SELECT province_code, make, model, gone_count, dgt_count, ratio
              FROM dgt_corroboration
             WHERE run_id = $1
               AND (province_code = $2 OR $2 IS NULL)
               AND (make = $3 OR $3 IS NULL)
               AND (model IS NOT DISTINCT FROM $4)
             ORDER BY gone_count DESC
             LIMIT 200
            """,
            run["run_id"], province, make_norm, model_norm,
        )
        items = [
            {
                "province_code": r["province_code"],
                "make": r["make"],
                "model": r["model"],
                "gone_count": r["gone_count"],
                "dgt_count": r["dgt_count"],
                "ratio": float(r["ratio"]) if r["ratio"] is not None else None,
            }
            for r in rows
        ]
        response = ok(
            items,
            run_id=run["run_id"],
            run_at=str(run["run_at"]),
            month=run["month"],
            methodology_version=run["methodology_version"],
            notes=run["notes"],
            count=len(items),
        )
        return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /market/price-position/{vehicle_ulid} — M2 (F5)
# ---------------------------------------------------------------------------

class PricePositionOutcome:
    """Result of ``compute_price_position`` — status/data/meta, NOT a JSONResponse, so
    it is reusable outside a route handler (03-garage-fleet F3/F4: dealer_ops.py's
    price-override endpoint and the "Mercado" screen both need this exact computation,
    00-MASTER.md C-1: "un solo cálculo... prohibido un tercer cálculo independiente")."""

    __slots__ = ("ok", "status", "error", "data", "meta")

    def __init__(self, *, ok: bool, status: int = 200, error: str | None = None,
                 data: dict[str, Any] | None = None, meta: dict[str, Any] | None = None) -> None:
        self.ok = ok
        self.status = status
        self.error = error
        self.data = data
        self.meta = meta or {}


async def compute_price_position(conn, vehicle_ulid: str) -> PricePositionOutcome:
    """M2 core computation — extracted from the route below so it has exactly ONE
    body, called both by ``GET /market/price-position/{ulid}`` and by any other
    pilar that needs "is this price below/at/above its segment's market" (03-K9).
    Behaviour is IDENTICAL to the original inline route (see git history) — every
    branch below maps 1:1 to what used to be a direct ``return err(...)``/``return
    ok(...)`` in the handler; ``tests/test_market_router_m2.py`` pins this contract.
    """
    vrow = await conn.fetchrow(
        """
        SELECT v.vehicle_ulid, v.make, v.model, v.year, v.fuel, v.price,
               e.province_code
          FROM vehicle v
          JOIN entity e ON e.entity_ulid = v.entity_ulid
         WHERE v.vehicle_ulid = $1
        """,
        vehicle_ulid,
    )
    if vrow is None:
        return PricePositionOutcome(ok=False, status=404, error=f"vehicle {vehicle_ulid} not found")

    if vrow["price"] is None:
        return PricePositionOutcome(
            ok=True,
            data={"vehicle_ulid": vehicle_ulid, "position": None, "reason": "vehicle has no price"},
        )
    if any(vrow[f] is None for f in ("make", "model", "year", "fuel", "province_code")):
        return PricePositionOutcome(
            ok=True,
            data={"vehicle_ulid": vehicle_ulid, "position": None,
                  "reason": "vehicle is missing make/model/year/fuel/province — cannot resolve a segment"},
        )

    run = await _latest_published_run(conn)
    if run is None:
        return PricePositionOutcome(ok=False, status=503, error="no published market_stat run yet")

    m1_rows = await conn.fetch(
        """
        SELECT province_code, p50, n
          FROM market_stat
         WHERE run_id = $1 AND metric_id = 'M1' AND make = $2 AND model = $3
           AND year = $4 AND fuel = $5 AND (province_code = $6 OR province_code IS NULL)
        """,
        run["run_id"], vrow["make"], vrow["model"], vrow["year"], vrow["fuel"], vrow["province_code"],
    )
    if not m1_rows:
        return PricePositionOutcome(
            ok=True,
            data={"vehicle_ulid": vehicle_ulid, "position": None,
                  "reason": "no M1 data for this segment (n<8 even nationally, or segment never computed)"},
            meta={"run_id": run["run_id"]},
        )

    prov_row = next((r for r in m1_rows if r["province_code"] is not None), None)
    chosen = prov_row if prov_row is not None else next(r for r in m1_rows if r["province_code"] is None)
    scope = "prov" if chosen is prov_row else "nat"

    p50 = float(chosen["p50"])
    price = float(vrow["price"])
    ratio = price / p50 if p50 > 0 else None
    if ratio is None:
        return PricePositionOutcome(
            ok=True,
            data={"vehicle_ulid": vehicle_ulid, "position": None, "reason": "segment p50 is zero"},
            meta={"run_id": run["run_id"]},
        )

    return PricePositionOutcome(
        ok=True,
        data={
            "vehicle_ulid": vehicle_ulid,
            "price": price,
            "segment": {
                "make": vrow["make"], "model": vrow["model"], "year": vrow["year"],
                "fuel": vrow["fuel"], "province_code": vrow["province_code"],
            },
            "position": {
                "ratio": ratio,
                "band": _price_position_band(ratio),
                "cuts": {"below_market_lt": M2_BELOW_MARKET_CUT, "above_market_gt": M2_ABOVE_MARKET_CUT},
                "segment_p50": p50,
                "segment_n": chosen["n"],
                "scope": scope,
                "fallback_to_national": scope == "nat",
            },
        },
        meta={"run_id": run["run_id"], "run_at": str(run["run_at"])},
    )


@router.get("/market/price-position/{vehicle_ulid}")
@limiter.limit(RATE_DEFAULT)
async def price_position(
    vehicle_ulid: str,
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """M2: is THIS specific listing priced below/at/above its segment's market
    (M1's p50), and by how much. This is the shared comparables engine 03
    (garage-fleet K9) and 07 (marketing C2) are meant to consume rather than
    re-derive (00-MASTER.md §98) — one implementation, used by every consumer.

    Computed LIVE against the latest published M1 row for this vehicle's own
    segment (make+model+its own year as the +/-1 band anchor+fuel+province, with
    the same national fallback as ``/market/segments/.../stats``) — never
    precomputed/stored per-vehicle.

    Cuts (<0.92 / 0.92-1.08 / >1.08) are PUBLISHED in the response, not a black
    box (carta §4 M2 row, explicit contrast with CarGurus' undisclosed thresholds).

    Honest degradation, never a fabricated ratio:
      - vehicle_ulid not found -> 404.
      - vehicle exists but has no price, or make/model/year/fuel/province
        incomplete, or its segment never cleared MIN_COHORT_N even nationally in
        the latest published run -> 200 with ``position: null`` and a ``reason``.
    """
    async with request.app.state.pool.acquire() as c:
        result = await compute_price_position(c, vehicle_ulid)
    if not result.ok:
        return err(result.error or "unknown error", status=result.status)
    return ok(result.data, **result.meta)


# ---------------------------------------------------------------------------
# Landing showcase — a public, rotating slice of the live census
# ---------------------------------------------------------------------------

# Rows pulled before diversification. Comfortably more than any `limit` so that
# capping each make still leaves enough distinct cars to fill the strip.
_SHOWCASE_POOL = 400

# Page-level sample rate. 0.4% of the available table is ~10k rows — plenty to
# fill the pool, and it reads a fraction of the pages instead of scanning 2.5M
# (measured: 8.9ms). ORDER BY last_seen was the obvious alternative and was
# rejected: no index covers it, so it degrades to a full scan plus a sort.
_SHOWCASE_SAMPLE_PCT = 0.4

_SHOWCASE_SQL = f"""
WITH sample AS (
    SELECT vehicle_ulid, make, model, year, km, price, currency, fuel,
           photo_url, entity_ulid, first_seen
      FROM vehicle TABLESAMPLE SYSTEM ({_SHOWCASE_SAMPLE_PCT})
     WHERE status = 'available'
       AND price > 0
       AND photo_url <> ''
       AND year IS NOT NULL
       AND km IS NOT NULL
       AND make <> ''
       AND model <> ''
     LIMIT {_SHOWCASE_POOL}
)
SELECT s.vehicle_ulid,
       s.make,
       s.model,
       s.year,
       s.km,
       round(s.price)::int AS price,
       s.currency,
       s.fuel,
       s.photo_url,
       gp.name AS province,
       GREATEST(0, EXTRACT(DAY FROM now() - s.first_seen)::int) AS days_listed
  FROM sample s
  LEFT JOIN entity e ON e.entity_ulid = s.entity_ulid
  LEFT JOIN geo_province gp ON gp.code = e.province_code
"""


# Marques written in capitals because they ARE initialisms or stylised that way.
# An explicit list, because the obvious shortcut — "four letters and uppercase" —
# also catches AUDI and FORD, which are words.
_ACRONYM_MAKES = frozenset({
    "BMW", "MG", "DS", "SEAT", "DAF", "MAN", "DR", "SWM", "BYD", "GMC", "RAM",
    "KGM", "DFSK", "XEV", "SYM", "KTM", "NIO", "LEVC", "SsangYong".upper(),
    "MINI", "SRT", "TVR", "BAC", "AC",
})


def _display_make(make: str) -> str:
    """Title-case a marque unless it is a genuine initialism."""
    key = make.strip().upper()
    if key in _ACRONYM_MAKES:
        return key
    return " ".join(w[:1].upper() + w[1:].lower() if w.isalpha() else w for w in make.split())


def _display_fuel(fuel: str | None) -> str | None:
    """Keep the fuel only when the source spelled out a word."""
    value = (fuel or "").strip()
    return value if len(value) > 2 else None


@router.get("/market/showcase")
@limiter.limit(RATE_DEFAULT)
async def showcase(
    request: Request,
    limit: int = Query(default=12, ge=1, le=24),
    per_make: int = Query(default=2, ge=1, le=6),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """A handful of REAL, currently-listed vehicles, for the public landing.

    Why this exists: the landing needs to show the market it claims to index.
    Every other vehicle route is either per-``vehicle_ulid`` or gated behind a
    dealer membership (``/deals/vehicle-search``), so an anonymous visitor had
    no way to see a single real car — leaving invented ones as the only way to
    fill a marketplace strip. This serves the census instead.

    Deliberately NOT cached. The query costs ~9ms and the whole point of the
    surface is that it rotates: two visits land on two different slices of the
    same live index. Rate limiting, not caching, is what bounds the load.

    Scope kept narrow on purpose: vehicle attributes plus the province name.
    No dealer identity and no ``deep_link`` — the landing's call to action
    belongs to our own marketplace, and source links are a competitive signal
    that has no business on an unauthenticated page.
    """
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(_SHOWCASE_SQL)
        picked = _diversify(rows, limit, per_make)

        # The valuation seal. Measured at 21-80ms per vehicle against the latest
        # published market_stat run, so a dozen of them is a fraction of a second
        # — cheap enough to answer live and far cheaper than storing a ratio for
        # millions of rows that only changes when a new run publishes.
        for item in picked:
            outcome = await compute_price_position(c, item["id"])
            # A run can answer successfully and still have no position: the
            # segment exists but its cohort never cleared the minimum. Reaching
            # into it blind is what made limit=14 a 500 while limit=12 passed by
            # luck — every card in that dozen happened to have one.
            position = (outcome.data or {}).get("position") if outcome.ok else None
            item["band"] = position.get("band") if isinstance(position, dict) else None

    if not picked:
        return err("no listed vehicle matched the showcase filters", status=503)

    return ok(picked, returned=len(picked), pool=len(rows), sample_pct=_SHOWCASE_SAMPLE_PCT)


# ---------------------------------------------------------------------------
# Live result count — what the submit button promises
# ---------------------------------------------------------------------------

_COUNT_SQL = """
SELECT coalesce(sum(n), 0)::bigint AS n
  FROM search_cube
 WHERE ($1::text IS NULL OR make = $1)
   AND ($2::text IS NULL OR model = $2)
   AND ($8::text IS NULL OR submodel = $8)
   AND ($3::text IS NULL OR province_code = $3)
   AND ($4::int  IS NULL OR (year IS NOT NULL AND year >= $4))
   AND ($5::int  IS NULL OR (year IS NOT NULL AND year <= $5))
   AND ($6::int  IS NULL OR (km_bucket >= 0 AND km_bucket >= $6))
   AND ($7::int  IS NULL OR (km_bucket >= 0 AND km_bucket <= $7))
   -- Colour is known for 11% of the index. Filtering on it therefore EXCLUDES the
   -- unlabelled majority, which is correct — a car whose colour nobody published
   -- cannot be shown as matching "rojo" — and is why `unknown_color_excluded`
   -- ships with the answer instead of the shortfall going unmentioned.
   AND ($9::text  IS NULL OR color = $9)
   AND ($10::text IS NULL OR body_type = $10)
   AND ($11::bool IS NULL OR is_family = $11)
   AND ($12::text IS NULL OR fuel = $12)
   -- Seats are known for 69.5% of the index. `seats = 0` is "not labelled", so a
   -- seat filter excludes it — a car whose capacity nobody published cannot be
   -- shown as matching "7 plazas".
   AND ($13::int  IS NULL OR (seats > 0 AND seats >= $13))
   -- Price bounds arrive in EUROS and are converted here, so the caller never has
   -- to mirror the grain. Bucket i covers [i×1.000, (i+1)×1.000): "under 20.000"
   -- is therefore every bucket up to 19.
   AND ($14::int  IS NULL OR (price_bucket >= 0 AND price_bucket >= ($14 / 1000)))
   AND ($15::int  IS NULL OR (price_bucket >= 0 AND price_bucket <= (($15 - 1) / 1000)))
"""

# Cars whose kilometres the source never published. They are excluded the moment a
# kilometre bound is set — a car whose mileage is unknown cannot be shown as
# matching "under 50.000 km" — and the number is RETURNED rather than silently
# dropped, so the interface can say how many it had to set aside instead of
# pretending they never existed.
_UNKNOWN_KM_SQL = """
SELECT coalesce(sum(n), 0)::bigint AS n
  FROM search_cube
 WHERE km_bucket = -1
   AND ($1::text IS NULL OR make = $1)
   AND ($2::text IS NULL OR model = $2)
   AND ($6::text IS NULL OR submodel = $6)
   AND ($3::text IS NULL OR province_code = $3)
   AND ($4::int  IS NULL OR (year IS NOT NULL AND year >= $4))
   AND ($5::int  IS NULL OR (year IS NOT NULL AND year <= $5))
"""


# The parser's dictionaries ARE the census, so the instance is cached against the
# cube's own timestamp: a rebuild changes the vocabulary and must invalidate it.
# Loading them per request would put three DISTINCT queries in front of every
# keystroke.
_PARSER: tuple[Any, QueryParser] | None = None


async def _parser(conn) -> QueryParser:
    global _PARSER
    stamp = await conn.fetchval("SELECT computed_at FROM search_cube_meta")
    if _PARSER is None or _PARSER[0] != stamp:
        _PARSER = (stamp, await QueryParser.load(conn))
    return _PARSER[1]


@router.get("/search/parse")
@limiter.limit(RATE_DEFAULT)
async def search_parse(
    request: Request,
    q: str = Query(min_length=1, max_length=200),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Turn a written sentence into the filters it means.

    "BMW Serie 3 diésel por menos de 15.000 €" becomes make/model/fuel/price_max;
    "coche rojo grande de familia" becomes colour plus is_family, which is
    answerable because body type is labelled per MODEL (`model_attributes`) rather
    than hunted for in listing text where it appears in 2% of rows.

    Deterministic, no model call, ~0 ms after the first request. It resolves what
    it can and RETURNS what it could not in `unresolved` — the interface can then
    say which word it did not understand instead of quietly searching for
    something else. The owner's standing rule is that nothing random is ever
    shown; this is where that is enforced, because a widened query is how random
    results get in.
    """
    async with request.app.state.pool.acquire() as c:
        parsed = (await _parser(c)).parse(q)

        # The version is resolved AFTER the model, scoped to it, and against the
        # original sentence rather than what the parser has left. Loading all
        # 106.000 versions into the parser to do this in one pass would cost more
        # than the one indexed lookup this needs, and only ever for the queries
        # that named a model in the first place.
        if parsed.make and parsed.model and not parsed.submodel:
            from services.api.search_parse import norm as _norm

            text = _norm(q)
            # Fetched by POPULARITY, then evaluated longest-first.
            #
            # Ordering the query itself by length looked right and silently broke
            # the common case: Clase C has enough versions that its 400 longest are
            # all long, and "C 220 d" — seven characters, the single most listed
            # version of the model — never reached the matcher. What the query has
            # to bring back is what people type, which is the frequent ones; what
            # the matcher then wants is the most specific of those, which is the
            # longest, so "C 220 d Estate" wins over "C 220 d" when both fit.
            rows = await c.fetch(
                "SELECT submodel FROM search_submodel WHERE make = $1 AND model = $2 "
                "ORDER BY n DESC LIMIT 400",
                parsed.make, parsed.model)
            rows = sorted(rows, key=lambda r: -len(r["submodel"]))
            import re as _re

            for r in rows:
                token = _norm(r["submodel"])
                # Word boundaries, and never a single character.
                #
                # A plain substring test made "peugeot 2008" resolve to submodel
                # "2" — a real version name, matching inside the model's own
                # digits. The version then narrowed the search to something the
                # visitor never asked for, which is the quiet kind of wrong: the
                # page still works, it just answers a different question.
                if len(token) < 2:
                    continue
                if _re.search(rf"\b{_re.escape(token)}\b", text):
                    parsed.submodel = r["submodel"]
                    parsed.unresolved = [
                        w for w in parsed.unresolved if w not in token.split()
                    ]
                    break

    return ok(parsed.to_dict(), query=q)


@router.get("/search/makes")
@limiter.limit(RATE_DEFAULT)
async def search_makes(
    request: Request,
    min_n: int = Query(default=25, ge=1, le=10_000),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """The marque list for the picker, counted from the SAME table as the button.

    Why not `mv_market_make_model`, which already answers this: the roll-up
    excludes listings with no model, so it reported Mercedes-Benz as 159.133 while
    `/search/count` — which counts every available car — answered 183.837 for the
    same selection. Two different numbers for one marque on one screen, twenty
    thousand apart, is the kind of detail that makes a visitor stop believing the
    rest of the page. One source, one number.
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        # The cube is already keyed by the canonical marque (resolved at build
        # time), so this is a plain roll-up: one row per brand, and the value
        # returned is the same string the count groups by. An earlier version
        # grouped by the census spelling and joined only for the label, which put
        # three identically-labelled "Mercedes-Benz" rows in the picker — 115.360,
        # 882 and 39 — with no way for a visitor to know which one to click.
        # `is_listable` is now HONOURED, which it was not before.
        #
        # The flag existed, the registry set it correctly, and this query ignored
        # it — so a picker whose whole job is choosing a CAR was offering Yamaha,
        # Ducati, Benimar and Hymer alongside Peugeot. They are real vehicles and
        # real rows; they are simply not what this control is for. They remain
        # searchable by name and countable; they just stop being suggested.
        #
        # Marques with no registry row at all keep appearing: an unrecognised
        # spelling with real stock behind it is a curation gap, and hiding it would
        # hide the gap rather than the noise.
        rows = await c.fetch(
            """
            SELECT s.make, coalesce(mc.slug, '') AS canon_slug, s.n
              FROM (SELECT make, sum(n)::int AS n
                      FROM search_cube
                     WHERE make <> ''
                     GROUP BY make
                    HAVING sum(n) >= $1) s
              LEFT JOIN make_canon mc ON mc.norm_key = make_norm(s.make)
             WHERE mc.slug IS NULL OR mc.is_listable
             ORDER BY s.n DESC
            """, min_n)

    items = [
        {
            "make": r["make"],
            "display": r["make"],
            "slug": r["canon_slug"] or _slugify_make(r["make"]),
            "n": r["n"],
        }
        for r in rows
    ]
    return cache_set(request, ok(items, returned=len(items)))


@router.get("/search/models")
@limiter.limit(RATE_DEFAULT)
async def search_models(
    request: Request,
    make: str = Query(min_length=1, max_length=80),
    min_n: int = Query(default=1, ge=1, le=10_000),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Models filed under a marque, from the cube, with their real counts.

    Listings whose model the source never published are excluded from the LIST —
    "" is not a model anyone can pick — but they remain inside the marque's own
    total, which is why the sum of the models can be smaller than the number on the
    marque. That gap is real and belongs to the data, not to the query.
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT model, sum(n)::int AS n
              FROM search_cube
             WHERE make = $1 AND model <> ''
             GROUP BY model
            HAVING sum(n) >= $2
             ORDER BY 2 DESC
             LIMIT 600
            """, make, min_n)

    return cache_set(
        request,
        ok([{"model": r["model"], "n": r["n"]} for r in rows], returned=len(rows)),
    )


@router.get("/search/provinces")
@limiter.limit(RATE_DEFAULT)
async def search_provinces(
    request: Request,
    make: str | None = Query(default=None),
    model: str | None = Query(default=None),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """The 52 provinces with how many cars each holds, from the cube.

    Counted, and counted CONDITIONALLY: pick a marque and the list re-counts for
    that marque. A province offering "Toda España" numbers while a make is already
    chosen would be telling the visitor about stock the search will not return.

    Provinces with nothing matching are omitted rather than rendered as "(0)" —
    an option that leads nowhere is noise, and the count is what makes that
    decidable instead of guessed.
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT gp.code, gp.name, sum(s.n)::int AS n
              FROM search_cube s
              JOIN geo_province gp ON gp.code = s.province_code
                                  AND gp.country_code = 'ES'
             WHERE ($1::text IS NULL OR s.make = $1)
               AND ($2::text IS NULL OR s.model = $2)
             GROUP BY gp.code, gp.name
             ORDER BY gp.name
            """, make, model)

    return cache_set(
        request,
        ok([{"code": r["code"], "name": r["name"], "n": r["n"]} for r in rows],
           returned=len(rows)),
    )


@router.get("/search/submodels")
@limiter.limit(RATE_DEFAULT)
async def search_submodels(
    request: Request,
    make: str = Query(min_length=1, max_length=80),
    model: str = Query(min_length=1, max_length=120),
    limit: int = Query(default=40, ge=1, le=200),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """The third level of the picker: versions filed under one model.

    Clicking Mercedes-Benz should not stop at Clase C — the buyer who knows they
    want a C 63 AMG and the buyer who only knows they want a Clase C are different
    people, and the control has to serve both without making either scroll past
    the other. This is the level that serves the first, while the roll-up the
    interface puts above it serves the second.

    The versions are the connectors' own `version` field, back-filled into
    `vehicle.trim`, so they read the way the market writes them ("C 220 d",
    "C 200 d Estate") rather than the way a parser guessed. Coverage is 44.3% of
    available cars: a model with no versions on record simply offers none, which
    is why the roll-up is always present and always first.
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT submodel, n
              FROM search_submodel
             WHERE make = $1 AND model = $2
             ORDER BY n DESC
             LIMIT $3
            """, make, model, limit)
        # What the cap leaves out, said out loud. A list that silently stops at
        # twenty reads as "these are all of them"; the tail of a popular model is
        # long and someone hunting a rare version deserves to know it exists rather
        # than concluding the index does not have it.
        tail = await c.fetchrow(
            """
            SELECT count(*)::int AS families, coalesce(sum(n), 0)::int AS cars
              FROM (SELECT submodel, n FROM search_submodel
                     WHERE make = $1 AND model = $2
                     ORDER BY n DESC OFFSET $3) t
            """, make, model, limit)

    return cache_set(
        request,
        ok(
            [{"submodel": r["submodel"], "n": r["n"]} for r in rows],
            returned=len(rows),
            hidden_families=tail["families"],
            hidden_cars=tail["cars"],
        ),
    )


def _slugify_make(make: str) -> str:
    """Lowercase, alphanumeric-only — the same shape the logo lookup expects."""
    return "".join(ch for ch in make.lower() if ch.isalnum())


@router.get("/search/count")
@limiter.limit(RATE_DEFAULT)
async def search_count(
    request: Request,
    make: str | None = Query(default=None),
    model: str | None = Query(default=None),
    submodel: str | None = Query(default=None, max_length=120),
    color: str | None = Query(default=None, max_length=20),
    body_type: str | None = Query(default=None, max_length=20),
    is_family: bool | None = Query(default=None),
    fuel: str | None = Query(default=None, max_length=24),
    seats_min: int | None = Query(default=None, ge=1, le=9),
    price_min: int | None = Query(default=None, ge=0, le=10_000_000),
    price_max: int | None = Query(default=None, ge=1, le=10_000_000),
    province: str | None = Query(default=None, max_length=8),
    year_min: int | None = Query(default=None, ge=1900, le=2100),
    year_max: int | None = Query(default=None, ge=1900, le=2100),
    # 0..50 since migration 0102 moved the grain to a uniform 5.000 km.
    km_min_bucket: int | None = Query(default=None, ge=0, le=50),
    km_max_bucket: int | None = Query(default=None, ge=0, le=50),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """How many cars match this filter combination, exactly, as of a stated moment.

    Served from `search_cube` (migration 0100), not from `vehicle`: the same
    question against the source table measures 600-2700 ms, which a control that
    updates while the user is still choosing cannot spend.

    The count is EXACT, not estimated. That is possible because the cube's
    kilometre buckets are keyed to the exact option values the interface offers,
    so every filter combination the UI can express lands on a cube boundary. The
    planner's own row estimates were considered and rejected — measured 9-17x
    low, which is not a number anyone should be shown.

    `as_of` and `age_seconds` ship with every response. The cube is a snapshot of
    a census that gains and loses roughly two thousand cars an hour; a count
    presented as live would be wrong within the minute and dishonest immediately.
    """
    if year_min is not None and year_max is not None and year_min > year_max:
        return err("year_min cannot exceed year_max", status=400)
    if km_min_bucket is not None and km_max_bucket is not None and km_min_bucket > km_max_bucket:
        return err("km_min_bucket cannot exceed km_max_bucket", status=400)

    cached = try_cache_get(request)
    if cached is not None:
        return cached

    args = (make, model, province, year_min, year_max)
    async with request.app.state.pool.acquire() as c:
        meta = await c.fetchrow("SELECT computed_at, vehicles FROM search_cube_meta")
        if meta is None:
            return err("search_cube has never been built", status=503)
        # The unfiltered total is the one query that has to scan the whole cube
        # (measured 602 ms against 43-60 ms for any filtered combination), and it
        # is also the one answer that never depends on user input. It was
        # materialised at build time; read it instead of recomputing it.
        no_filters = not any(
            v is not None for v in (make, model, submodel, color, body_type, is_family,
                                    fuel, seats_min, price_min, price_max,
                                    province, year_min, year_max,
                                    km_min_bucket, km_max_bucket))
        n = (
            meta["vehicles"]
            if no_filters
            else await c.fetchval(_COUNT_SQL, *args, km_min_bucket, km_max_bucket,
                                  submodel, color, body_type, is_family,
                                  fuel, seats_min, price_min, price_max)
        )
        unknown_km = (
            await c.fetchval(_UNKNOWN_KM_SQL, *args, submodel)
            if (km_min_bucket is not None or km_max_bucket is not None)
            else 0
        )
        # How much stock a colour filter had to set aside for want of a colour.
        # Reported, never hidden: 89% of the index has no published colour, and a
        # visitor filtering by one deserves to know the search just got that much
        # narrower for a reason that is not about the cars.
        unknown_color = (
            await c.fetchval(
                "SELECT coalesce(sum(n),0)::bigint FROM search_cube WHERE color = '' "
                "AND ($1::text IS NULL OR make = $1) AND ($2::text IS NULL OR model = $2) "
                "AND ($3::text IS NULL OR province_code = $3)",
                make, model, province)
            if color is not None
            else 0
        )

    age = (datetime.now(timezone.utc) - meta["computed_at"]).total_seconds()
    payload = {
        "count": int(n),
        "exact": True,
        "unknown_km_excluded": int(unknown_km),
        "unknown_color_excluded": int(unknown_color),
        "as_of": meta["computed_at"].isoformat(),
        "age_seconds": int(age),
    }
    return cache_set(request, ok(payload, total_indexed=int(meta["vehicles"])))


# ---------------------------------------------------------------------------
# Landing opportunities — the same strip, but earned instead of sampled
# ---------------------------------------------------------------------------

# Ranked rows pulled before diversification. The cap exists so one marque having a
# very good week cannot monopolise the strip.
_OPPORTUNITY_POOL = 300

# Credibility bounds, all measured against the live deal-score run (2026-08-03).
# See the WHERE clause below for why each exists.
_PCT_MIN = 12      # under this the "opportunity" is noise, not a signal
_PCT_MAX = 35      # over this it is almost always broken data, not a bargain
_MIN_COHORT = 30   # a median over fewer comparables is not a market price
_MAX_KM = 200_000  # the cohort does not control for mileage; the tail must go

# `savings_eur` is the house's own measure — the gap between a car's asking price
# and the median of its cohort — and `band` is the house's own verdict on that gap.
# Neither is invented here; both are read from the latest published deal-score run.
#
# servable_vehicle, not vehicle: the run is a snapshot, and between runs a car can
# sell or get price-trap quarantined. The view re-checks both live, so the strip can
# never advertise something that is no longer there.
_OPPORTUNITY_SQL = f"""
WITH latest AS (
    -- PUBLISHED runs only.
    --
    -- `arbitrage_run.published` defaults to false and the scoring job never sets
    -- it: a run has to clear its own dual-path cross-check (SQL against Python,
    -- twenty cohorts, 0.5% tolerance) before anyone should quote it. Taking the
    -- most recent run regardless — which this query did at first — meant a public
    -- page could have shown verdicts from a run that failed its own audit. The
    -- gate exists; it just was not being honoured here.
    SELECT run_id FROM arbitrage_run
     WHERE published
     ORDER BY run_at DESC LIMIT 1
)
SELECT ds.vehicle_ulid,
       ds.band,
       round(ds.savings_eur)::int              AS savings_eur,
       round(ds.cohort_median_price)::int      AS cohort_median_price,
       ds.cohort_n,
       v.make, v.model, v.year, v.km,
       round(v.price)::int                     AS price,
       v.currency, v.fuel, v.photo_url,
       gp.name                                 AS province,
       GREATEST(0, EXTRACT(DAY FROM now() - v.first_seen)::int) AS days_listed
  FROM deal_score ds
  JOIN latest l           ON l.run_id = ds.run_id
  JOIN servable_vehicle v ON v.vehicle_ulid = ds.vehicle_ulid
  LEFT JOIN entity e      ON e.entity_ulid = v.entity_ulid
  LEFT JOIN geo_province gp ON gp.code = e.province_code
 WHERE v.photo_url <> ''
   AND v.price > 0
   AND v.year IS NOT NULL
   AND v.km IS NOT NULL
   AND ds.savings_eur > 0
   -- CREDIBILITY BAND. Ranking by absolute savings alone puts the broken data at
   -- the very top: the first pass of this query offered a 2023 Range Rover at
   -- 23.500 € (81% under its cohort) and a 2024 Dodge Challenger at 30.000 € (69%).
   -- Those are not bargains, they are data errors, deposit-only prices, or wrecks
   -- — and 47 rows in the current run claim savings of 100% or more of the cohort
   -- median, which is arithmetically impossible for an honest listing. The measured
   -- mass of real discounts sits at 20-30%, so anything past {_PCT_MAX}% is
   -- discarded rather than shown. A public strip that leads with the census's worst
   -- rows would destroy the exact credibility it exists to build.
   AND ds.savings_eur BETWEEN ds.cohort_median_price * {_PCT_MIN / 100} AND ds.cohort_median_price * {_PCT_MAX / 100}
   -- The cohort has to be big enough for its median to mean something.
   AND ds.cohort_n >= {_MIN_COHORT}
   -- The cohort is make+model+year and does NOT control for mileage, so a
   -- worn-out example reads as a discount purely by being worn out. Excluding the
   -- high-km tail keeps the claim to cars where the gap is about the price.
   AND v.km <= {_MAX_KM}
 ORDER BY (ds.band = 'chollo_fuerte') DESC, ds.savings_eur DESC
 LIMIT {_OPPORTUNITY_POOL}
"""

_BAND_LABEL = {"chollo_fuerte": "Chollo", "bajo_mercado": "Bajo mercado"}


@router.get("/market/opportunities")
@limiter.limit(RATE_DEFAULT)
async def opportunities(
    request: Request,
    limit: int = Query(default=10, ge=1, le=24),
    per_make: int = Query(default=1, ge=1, le=4),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """The landing strip, ranked by the house's own verdict instead of sampled.

    What this replaces: ``/market/showcase`` draws with ``TABLESAMPLE SYSTEM`` — a
    genuinely random slice of the census. That was the right call when the only
    goal was proving the index is real, and the wrong one for a strip that claims
    to show opportunities: a random car is not an opportunity, and presenting it
    as one is a claim the data does not support.

    Every row here cleared ``deal_score``: its price sits far enough below the
    median of its own cohort (same make, model and year, minimum cohort size) for
    the arbitrage run to have banded it. ``savings_eur`` is that gap in euros.
    The strip therefore shows what the product actually sells — knowing which car
    is priced wrong — instead of shuffling the shelf.

    ``as_of`` is served with every response, because a deal-score run is a
    snapshot and the honest thing is to say how old it is rather than let a
    visitor assume it is live.
    """
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(_OPPORTUNITY_SQL)
        computed_at = await c.fetchval(
            "SELECT run_at FROM arbitrage_run WHERE published ORDER BY run_at DESC LIMIT 1")

    if not rows:
        # No published run, or none of its cars is still servable. The strip renders
        # nothing rather than falling back to a random sample — the fallback that
        # existed before and was the reason this endpoint was written.
        return err("no published deal-score run is currently servable", status=503)

    picked = _diversify(rows, limit, per_make)

    # _diversify only knows the columns the showcase needs; the verdict fields are
    # re-attached here from the source rows.
    by_id = {r["vehicle_ulid"]: r for r in rows}
    for item in picked:
        src = by_id[item["id"]]
        item["band"] = src["band"]
        item["band_label"] = _BAND_LABEL.get(src["band"], src["band"])
        item["savings_eur"] = src["savings_eur"]
        # The percentage is what makes the euro figure legible: 3.000 € off a
        # 12.000 € cohort median is a very different claim from 3.000 € off 90.000 €.
        item["savings_pct"] = (
            round(100 * src["savings_eur"] / src["cohort_median_price"])
            if src["cohort_median_price"] else None
        )
        item["cohort_n"] = src["cohort_n"]
        # Carried on every row, not just in `meta`, so the strip cannot render a
        # verdict without also being able to say when it was reached. A deal-score
        # run is a snapshot; a snapshot presented as live is a lie of omission.
        item["as_of"] = computed_at.isoformat() if computed_at else None

    return ok(
        picked,
        returned=len(picked),
        pool=len(rows),
        as_of=computed_at.isoformat() if computed_at else None,
    )


def _diversify(rows, limit: int, per_make: int) -> list[dict[str, Any]]:
    """Cap each make so a market this size does not render as twelve Renaults."""
    seen: dict[str, int] = {}
    picked: list[dict[str, Any]] = []
    for r in rows:
        make = (r["make"] or "").strip()
        if seen.get(make.lower(), 0) >= per_make:
            continue
        seen[make.lower()] = seen.get(make.lower(), 0) + 1
        picked.append(
            {
                "id": r["vehicle_ulid"],
                # Sources disagree on case for the same marque ("VOLKSWAGEN" and
                # "Volkswagen" both occur). Normalising the presentation is not
                # rewriting the datum — the row still says what it said.
                "make": _display_make(make),
                "model": (r["model"] or "").strip(),
                "year": r["year"],
                "km": r["km"],
                "price": r["price"],
                "currency": (r["currency"] or "EUR").strip(),
                # Some feeds carry a one-letter fuel code ("D") instead of a
                # word. A card cannot render that meaningfully, so it is omitted
                # rather than guessed at.
                "fuel": _display_fuel(r["fuel"]),
                "photo": r["photo_url"],
                "province": r["province"],
                "days_listed": r["days_listed"],
            }
        )
        if len(picked) >= limit:
            break

    return picked

# ---------------------------------------------------------------------------
# The marque universe, as the census actually holds it
# ---------------------------------------------------------------------------

# A make needs this many live listings to be offered as a filter. The view holds
# 3,501 distinct `make_raw` values; the overwhelming majority are single-listing
# typos and junk, and a picker that offers them is not more complete, only worse.
_MAKE_MIN_LISTINGS = 25

# Source strings that are not marques at all. Kept explicit rather than filtered
# by heuristic, so every exclusion is a decision someone can read and reverse.
_NOT_A_MAKE = {
    "OTROS",       # literally "others" — no marque to recover
    "OTRO",
    "DEFAULT",     # a scraper placeholder that reached the field
    "MICROCAR AIXAM LIGIER CHATENET",  # four marques in one string, none resolvable
    "COCHES",
    "VARIOS",
}

# Same marque, different spellings across sources — including outright typos the
# feeds carry ("WOLKSWAGEN") and sub-brands that belong to their parent for the
# purposes of a filter ("MERCEDES-AMG").
_MAKE_ALIASES: dict[str, str] = {
    "MERCEDES": "Mercedes-Benz",
    "MERCEDES BENZ": "Mercedes-Benz",
    "MERCEDES-BENZ": "Mercedes-Benz",
    "MERCEDES AMG": "Mercedes-Benz",
    "MERCEDES-AMG": "Mercedes-Benz",
    "WOLKSWAGEN": "Volkswagen",
    "VOLKSWAGEN": "Volkswagen",
    "VW": "Volkswagen",
    "LAND": "Land Rover",
    "LAND ROVER": "Land Rover",
    "LAND-ROVER": "Land Rover",
    "LANDROVER": "Land Rover",
    "RANGE ROVER": "Land Rover",
    "KGM": "KGM",
    "KGM / SSANGYONG": "KGM",
    "KGM/SSANGYONG": "KGM",
    "SSANGYONG KGM": "KGM",
    "SUZUKI MOTOS": "Suzuki",
    "CORVETTE": "Chevrolet",
    "DR AUTOMOBILES": "DR",
    "CITROEN": "Citroën",
    "CITROËN": "Citroën",
    "SKODA": "Škoda",
    "KIA": "Kia",
    # Model names that reached the make column. These are real listings — a Golf
    # is a Volkswagen — so they fold into the marque instead of being discarded.
    # Verified against the view: "ASTRA" carries models like `opel`, `cdti` and
    # `Opel astra 2014`, which is a mis-filed Opel and nothing else.
    "GOLF": "Volkswagen",
    "IBIZA": "SEAT",
    "ASTRA": "Opel",
    "LYNK": "Lynk & Co",
    # Two more the census carries mangled: a doubled prefix, and a keyboard-mash
    # that reached the field. Verified against the view before deciding which is
    # recoverable and which is not.
    # Five spellings of one micro-EV marque, models 1/3/3 Max/6/T01 across 116
    # live listings. An earlier pass had it down as junk to discard — it is not:
    # discarding it would drop real inventory, the same mistake GOLF and IBIZA
    # taught. The most frequent spelling wins as the display name; confirming the
    # manufacturer's official styling is a separate, unfinished job.
    "YOOUDOO": "Yooudooo",
    "YOOUDOOO": "Yooudooo",
    "YOOUDOOO 6": "Yooudooo",
    "YOOUDOO 6": "Yooudooo",
    "YOOUDOO 3MAX": "Yooudooo",
    "LYNK & CO": "Lynk & Co",
    "SSANGYONG": "SsangYong",
    "MINI": "MINI",
    "ŠKODA": "Škoda",
}


def _canonical_make(raw: str) -> str | None:
    """Canonical display name for a census `make`, or None when it is not a marque."""
    key = " ".join((raw or "").strip().upper().split())
    if not key or key in _NOT_A_MAKE:
        return None
    if key in _MAKE_ALIASES:
        return _MAKE_ALIASES[key]
    return _display_make(key)


def _slug(name: str) -> str:
    """Asset-friendly key: lowercase, accents folded, punctuation dropped."""
    import unicodedata

    folded = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return "".join(ch for ch in folded if ch.isalnum())


@router.get("/market/makes")
@limiter.limit(RATE_DEFAULT)
async def market_makes(request: Request, _: None = Depends(require_api_key)) -> JSONResponse:
    """Every marque the census actually lists, with its live count.

    Served from `mv_market_make_model` (migration 0097), not from the vehicle
    table: the raw aggregation measured 5.0s, which is not a number a dropdown
    can spend. Here it is a scan of a few thousand rows.

    Spellings are canonicalised on the way out, never in storage — the view keeps
    what the source said. `computed_at` travels with the payload so the caller
    can show how fresh the roll-up is instead of implying it is live.
    """
    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            "SELECT make_raw, sum(n)::bigint AS n, max(computed_at) AS computed_at "
            "FROM mv_market_make_model GROUP BY make_raw"
        )

    merged: dict[str, dict[str, Any]] = {}
    computed_at = None
    for r in rows:
        computed_at = computed_at or r["computed_at"]
        name = _canonical_make(r["make_raw"])
        if name is None:
            continue
        slot = merged.setdefault(name, {"make": name, "slug": _slug(name), "n": 0})
        slot["n"] += int(r["n"])

    makes = sorted(
        (m for m in merged.values() if m["n"] >= _MAKE_MIN_LISTINGS),
        key=lambda m: -m["n"],
    )
    return ok(
        makes,
        returned=len(makes),
        min_listings=_MAKE_MIN_LISTINGS,
        computed_at=str(computed_at) if computed_at else None,
    )


@router.get("/market/models")
@limiter.limit(RATE_DEFAULT)
async def market_models(
    request: Request,
    make: str = Query(..., min_length=1, max_length=64),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """The models the census lists for one marque, most-listed first.

    The argument is a canonical name, so every raw spelling that folds into it is
    resolved first — asking for "Mercedes-Benz" must also reach the rows filed
    under "MERCEDES BENZ".
    """
    async with request.app.state.pool.acquire() as c:
        raws = await c.fetch("SELECT DISTINCT make_raw FROM mv_market_make_model")
        wanted = [r["make_raw"] for r in raws if _canonical_make(r["make_raw"]) == make]
        if not wanted:
            return err(f"no listed vehicle under make {make!r}", status=404)

        rows = await c.fetch(
            "SELECT model, sum(n)::bigint AS n FROM mv_market_make_model "
            "WHERE make_raw = ANY($1::text[]) GROUP BY model ORDER BY n DESC LIMIT 400",
            wanted,
        )

    models = [{"model": r["model"], "n": int(r["n"])} for r in rows if int(r["n"]) >= 3]
    return ok(models, returned=len(models), make=make)


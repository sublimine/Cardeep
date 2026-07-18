"""/terminal/* — trading-terminal endpoints (pilar 09-trading-terminal, F2).

Ownership: 00-MASTER.md resolution C-1 assigns ``services/api/routers/market.py`` and the
``/market/*`` namespace to pilar 01-market-intelligence exclusively. This file is 09's OWN,
SEPARATE router (namespace ``/terminal/*``, coherent with the frontend route ``/terminal``) —
never touches market.py. Reads market_symbol/market_bucket_daily (migrations/0086), tables that
are genuinely distinct from 01's market_stat/market_stat_run (different cohort key: make+model
+province, no fuel/year axis — carta 09 §4 C1).

C7 (deal-rating) DELIBERATELY DELEGATES to market.py's ``compute_price_position`` (M2) instead of
building a second, independent price-position engine. AMENDMENT to the carta's F0-authored §4 C7
text (which specified a from-scratch price~km regression): by the time this router was built,
01's M2 was already real, live, and serves exactly "is this listing priced below/at/above its
segment" — the same question C7 asks. Building a second comparable engine for the same vehicle
would be exactly the "tres implementaciones de mediana-por-cohorte... el mismo coche etiquetado
distinto en dos pantallas" anti-pattern 00-MASTER.md C-1/C-12 warn against (§5.2 risk register).
This is a real, declared engineering decision, not a shortcut: C7's endpoint below is a thin
symbol-scoped wrapper over M2, never a re-derivation.

C5's "venta probable (inferida)" (Fase 4, market_sale_inference, pipeline/terminal/infer_sales.py)
CONSUMES v_vehicle_lifetime per 00-MASTER.md C-9 — NOT the carta's original vehicle_cluster
heuristic. VERIFIED LIVE this session (not assumed): v_vehicle_lifetime is currently EMPTY (0
edges survive the resolver even after 04-arbitrage-F6's vin_ref remediation, migration 0083 — see
migrations/0090's header for the exact measurement). The sale-inference endpoint below therefore
degrades its badge to "sin verificar" whenever no V4 audit is <=30d fresh — no audit has been run
yet in this execution (declared, not hidden).
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any, Literal

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from services.api.cache import cache_set, try_cache_get
from services.api.deps import err, ok, require_api_key
from services.api.ratelimit import RATE_DEFAULT, RATE_EXPENSIVE, limiter
from services.api.routers.market import compute_price_position

router = APIRouter()

# C2 (09-trading-terminal.md §4) — mirrored here as a read-time re-statement for the "muestra
# insuficiente" messaging; the authoritative enforcement happens at write time in
# pipeline/terminal/compute_buckets.py (a row that fails the bar is never written).
MIN_ACTIVE_C2 = 30
MIN_EVENTS_C2 = 5

# C6 (price-pressure) window — 09-trading-terminal.md §4 row C6: "% de anuncios activos con >=1
# PRICE_CHANGE a la baja en 30d". PRESSURE_WINDOW_DAYS is evaluated against the CORPUS's own most
# recent observed_at (see _corpus_now below), not wall-clock now — the corpus is a frozen/batch
# snapshot (00-marketplace-engine C-8), so "last 30 days" must be relative to the data's own
# timeline or every window would spuriously read as empty during an engine outage.
PRESSURE_WINDOW_DAYS = 30
PRESSURE_ALERT_THRESHOLD_PCT = 25.0  # >25% => "mercado bajo presión" (carta §4 C6)

# C8 dealer-concentration + activity window (30d, same corpus-relative "now").
DEALER_ACTIVITY_WINDOW_DAYS = 30
TOP_N_CONCENTRATION = 5

RangeLabel = Literal["1M", "3M", "6M", "1Y", "ALL"]
_RANGE_DAYS: dict[str, int] = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365}

METHODOLOGY_VERSION = "v1"


def _parse_symbol_key(symbol_key: str) -> tuple[str, str, str | None]:
    """'{MAKE}|{MODEL}|{PROVINCE-or-NAT}' -> (make, model, province_code|None)."""
    parts = symbol_key.split("|")
    if len(parts) != 3:
        raise ValueError(f"malformed symbol_key: {symbol_key!r}")
    make, model, prov = parts
    return make, model, (None if prov == "NAT" else prov)


async def _corpus_now(conn) -> Any:
    """The corpus's own most recent observed_at — see PRESSURE_WINDOW_DAYS docstring for why
    this replaces wall-clock now() throughout this router's rolling-window computations."""
    return await conn.fetchval("SELECT max(observed_at) FROM vehicle_event")


# ---------------------------------------------------------------------------
# GET /terminal/symbols — C1 search (dealer natural-language query resolved against
# market_symbol; the frontend layers catalog.ts fuzzy-matching on top per carta §6).
# ---------------------------------------------------------------------------

@router.get("/terminal/symbols")
@limiter.limit(RATE_DEFAULT)
async def search_symbols(
    request: Request,
    q: str = Query(..., min_length=1, description="Free-text make/model fragment, case-insensitive"),
    province: str | None = Query(default=None, description="2-char province code filter; omitted = all scopes"),
    limit: int = Query(default=20, ge=1, le=100),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT symbol_key, make, model, province_code, level, first_bucket, last_bucket
              FROM market_symbol
             WHERE is_active
               AND (make || ' ' || model) ILIKE '%' || $1 || '%'
               AND ($2::varchar IS NULL OR province_code = $2)
             ORDER BY last_bucket DESC, make, model
             LIMIT $3
            """,
            q, province, limit,
        )
        items = [
            {
                "symbol_key": r["symbol_key"], "make": r["make"], "model": r["model"],
                "province_code": r["province_code"], "level": r["level"],
                "first_bucket": str(r["first_bucket"]), "last_bucket": str(r["last_bucket"]),
            }
            for r in rows
        ]
        response = ok(items, count=len(items))
        return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /terminal/screener — Fase 3b: TradingView-style screener, technical (Δ%, DOM) +
# fundamental-censal (stock, dealers, concentration) columns COMBINED in one table row
# (carta §6, item "Screener"). Sourced from each symbol's LATEST market_bucket_daily row
# (cheap, precomputed) — no live per-row computation, unlike /stats (which is one symbol
# at a time and can afford a live join).
# ---------------------------------------------------------------------------

@router.get("/terminal/screener")
@limiter.limit(RATE_EXPENSIVE)
async def screener(
    request: Request,
    province: str | None = Query(default=None),
    make: str | None = Query(default=None),
    sort: Literal["active_count", "new_count", "gone_count", "dom_p50_days"] = Query(default="active_count"),
    limit: int = Query(default=50, ge=1, le=200),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            f"""
            WITH latest AS (
                SELECT DISTINCT ON (symbol_key) symbol_key, bucket_date, active_count,
                       median_price, new_count, gone_count, price_change_down_count,
                       price_change_up_count, dom_p50_days
                  FROM market_bucket_daily
                 ORDER BY symbol_key, bucket_date DESC
            )
            SELECT ms.symbol_key, ms.make, ms.model, ms.province_code, l.bucket_date,
                   l.active_count, l.median_price, l.new_count, l.gone_count,
                   l.price_change_down_count, l.price_change_up_count, l.dom_p50_days
              FROM latest l
              JOIN market_symbol ms ON ms.symbol_key = l.symbol_key
             WHERE ms.is_active
               AND ($1::varchar IS NULL OR ms.province_code = $1)
               AND ($2::text IS NULL OR ms.make ILIKE $2)
             ORDER BY l.{sort} DESC NULLS LAST
             LIMIT $3
            """,
            province, make, limit,
        )
        items = [
            {
                "symbol_key": r["symbol_key"], "make": r["make"], "model": r["model"],
                "province_code": r["province_code"], "bucket_date": str(r["bucket_date"]),
                "active_count": r["active_count"],
                "median_price": float(r["median_price"]) if r["median_price"] is not None else None,
                "new_count": r["new_count"], "gone_count": r["gone_count"],
                "price_change_down_count": r["price_change_down_count"],
                "price_change_up_count": r["price_change_up_count"],
                "dom_p50_days": float(r["dom_p50_days"]) if r["dom_p50_days"] is not None else None,
            }
            for r in rows
        ]
        response = ok(items, count=len(items), sort=sort)
        return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /terminal/{symbol_key}/ohlc — C3 (weekly candles honest on real bucket days only)
# ---------------------------------------------------------------------------

def _iso_week_key(d: date) -> tuple[int, int]:
    iso = d.isocalendar()
    return (iso[0], iso[1])


def _rows_to_bars(rows: list[dict], *, daily: bool) -> list[dict[str, Any]]:
    """rows: ordered by bucket_date ASC, each with bucket_date/median_price/new_count.

    daily=True: one Bar per real bucket_date (O=H=L=C=median_price — an honest single-
    observation snapshot, never fabricated intraday spread).
    daily=False: one Bar per ISO week that contains >=1 real bucket_date (carta §4 C3: "O =
    mediana del primer día con dato, H = max de medianas diarias, L = min, C = mediana del
    último día"). A week with no real bucket_date simply has no bar — no interpolation.
    """
    # asyncpg returns NUMERIC columns as Decimal — JSONResponse's default encoder cannot
    # serialize Decimal (a real bug this session's own E2E curl check caught: GET .../ohlc
    # 500'd with "Object of type Decimal is not JSON serializable"). Cast to float at this one
    # normalization boundary rather than scattering casts through every call site.
    if daily:
        return [
            {
                "time": str(r["bucket_date"]), "open": float(r["median_price"]), "high": float(r["median_price"]),
                "low": float(r["median_price"]), "close": float(r["median_price"]), "volume": r["new_count"],
            }
            for r in rows
            if r["median_price"] is not None
        ]
    weeks: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for r in rows:
        if r["median_price"] is None:
            continue
        weeks[_iso_week_key(r["bucket_date"])].append(r)
    bars = []
    for _wk, wrows in sorted(weeks.items()):
        wrows_sorted = sorted(wrows, key=lambda r: r["bucket_date"])
        prices = [float(r["median_price"]) for r in wrows_sorted]
        bars.append({
            "time": str(wrows_sorted[0]["bucket_date"]),
            "open": prices[0], "high": max(prices), "low": min(prices), "close": prices[-1],
            "volume": sum(r["new_count"] for r in wrows_sorted),
        })
    return bars


@router.get("/terminal/{symbol_key}/ohlc")
@limiter.limit(RATE_DEFAULT)
async def symbol_ohlc(
    symbol_key: str,
    request: Request,
    range: RangeLabel = Query(default="ALL"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """C3: weekly OHLC bars from real bucket days only (range<=30d ('1M') serves DAILY bars
    per the carta's own spec: 'o día para rangos ≤ 30d con velas de línea'). Gaps in the
    corpus (the 00-marketplace-engine outage, see migrations/0086 header) render as MISSING
    bars — never an interpolated flat line."""
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    try:
        _parse_symbol_key(symbol_key)
    except ValueError as e:
        return err(str(e), status=400)

    async with request.app.state.pool.acquire() as c:
        exists = await c.fetchval("SELECT 1 FROM market_symbol WHERE symbol_key = $1", symbol_key)
        if not exists:
            return err(f"symbol {symbol_key} not found", status=404)

        rows = await c.fetch(
            """
            SELECT bucket_date, median_price, new_count
              FROM market_bucket_daily
             WHERE symbol_key = $1
             ORDER BY bucket_date ASC
            """,
            symbol_key,
        )
        all_rows = [dict(r) for r in rows]
        if range != "ALL" and all_rows:
            cutoff = all_rows[-1]["bucket_date"] - timedelta(days=_RANGE_DAYS[range])
            all_rows = [r for r in all_rows if r["bucket_date"] > cutoff]

        bars = _rows_to_bars(all_rows, daily=(range == "1M"))
        response = ok(
            bars,
            symbol_key=symbol_key, range=range, granularity=("daily" if range == "1M" else "weekly"),
            bucket_count=len(all_rows), bar_count=len(bars),
        )
        return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /terminal/{symbol_key}/stats — C5 (volume/rotation), C6 (price pressure),
# C8 (censal fundamental) — computed LIVE (never precomputed per-symbol), mirroring
# market.py's M2 "computed live against the latest published row" pattern: these are
# cheap live lookups+aggregates, not a stale nightly figure.
# ---------------------------------------------------------------------------

@router.get("/terminal/{symbol_key}/stats")
@limiter.limit(RATE_EXPENSIVE)
async def symbol_stats(
    symbol_key: str,
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    try:
        make, model, province = _parse_symbol_key(symbol_key)
    except ValueError as e:
        return err(str(e), status=400)

    async with request.app.state.pool.acquire() as c:
        sym = await c.fetchrow("SELECT symbol_key FROM market_symbol WHERE symbol_key = $1", symbol_key)
        if sym is None:
            return err(f"symbol {symbol_key} not found", status=404)

        now = await _corpus_now(c)
        if now is None:
            return err("no vehicle_event data in corpus", status=503)
        pressure_since = now - timedelta(days=PRESSURE_WINDOW_DAYS)
        activity_since = now - timedelta(days=DEALER_ACTIVITY_WINDOW_DAYS)

        # Fixed 3-parameter scheme throughout this endpoint ($1=make, $2=model,
        # $3=province-or-NULL — "($3::varchar IS NULL OR e.province_code = $3)" scopes to
        # national when province is None, exactly like /terminal/symbols above) so date
        # params always land at a STABLE, predictable position instead of a computed index.
        base_params: list[Any] = [make, model, province]
        prov_filter = "($3::varchar IS NULL OR e.province_code = $3)"

        # C5/C8 — live census over CURRENTLY available inventory for this symbol.
        census = await c.fetchrow(
            f"""
            SELECT
                count(*) FILTER (WHERE v.status = 'available') AS active_count,
                count(DISTINCT v.entity_ulid) FILTER (WHERE v.status = 'available') AS n_dealers,
                count(DISTINCT v.entity_ulid) FILTER (
                    WHERE v.status = 'available'
                      AND EXISTS (SELECT 1 FROM platform_listing pl WHERE pl.vehicle_ulid = v.vehicle_ulid)
                ) AS n_dealers_on_platform
              FROM vehicle v
              JOIN entity e ON e.entity_ulid = v.entity_ulid
             WHERE v.make = $1 AND v.model = $2 AND {prov_filter}
            """,
            *base_params,
        )
        if census["active_count"] < MIN_ACTIVE_C2:
            return ok(
                {
                    "symbol_key": symbol_key, "insufficient_sample": True,
                    "active_count": census["active_count"], "min_required": MIN_ACTIVE_C2,
                    "reason": f"muestra insuficiente: {census['active_count']} activos (mínimo {MIN_ACTIVE_C2})",
                },
                corpus_now=str(now),
            )

        # Top-5 dealer concentration (C8).
        top5 = await c.fetch(
            f"""
            SELECT v.entity_ulid, count(*) AS n
              FROM vehicle v JOIN entity e ON e.entity_ulid = v.entity_ulid
             WHERE v.make = $1 AND v.model = $2 AND {prov_filter} AND v.status = 'available'
             GROUP BY v.entity_ulid ORDER BY n DESC LIMIT {TOP_N_CONCENTRATION}
            """,
            *base_params,
        )
        top5_stock = sum(r["n"] for r in top5)
        concentration_pct = (100.0 * top5_stock / census["active_count"]) if census["active_count"] else None

        # Sample of real active listings for this symbol (carta §6: "cada cifra clicable ->
        # drill-down a la lista real de dealers/anuncios, deep-link, mandato del proyecto").
        # A small honest sample, not a full paginated browse — this endpoint's job is the
        # census panel, not a listing search surface.
        sample = await c.fetch(
            f"""
            SELECT v.vehicle_ulid, v.year, v.km, v.price, v.deep_link, e.cdp_code
              FROM vehicle v JOIN entity e ON e.entity_ulid = v.entity_ulid
             WHERE v.make = $1 AND v.model = $2 AND {prov_filter} AND v.status = 'available'
             ORDER BY v.last_seen DESC LIMIT 8
            """,
            *base_params,
        )

        # C6 — price-pressure: % of active listings with >=1 PRICE_CHANGE-down in the window.
        pressure = await c.fetchrow(
            f"""
            WITH active AS (
                SELECT v.vehicle_ulid FROM vehicle v JOIN entity e ON e.entity_ulid = v.entity_ulid
                 WHERE v.make = $1 AND v.model = $2 AND {prov_filter} AND v.status = 'available'
            )
            SELECT count(*) AS n_active,
                   count(*) FILTER (
                       WHERE EXISTS (
                           SELECT 1 FROM vehicle_event ev
                            WHERE ev.vehicle_ulid = active.vehicle_ulid
                              AND ev.event_type = 'PRICE_CHANGE'
                              AND ev.observed_at > $4
                              AND (ev.new_value->>'price')::numeric < (ev.old_value->>'price')::numeric
                       )
                   ) AS n_with_price_cut
              FROM active
            """,
            *base_params, pressure_since,
        )
        pressure_pct = (
            100.0 * pressure["n_with_price_cut"] / pressure["n_active"]
            if pressure["n_active"] else None
        )

        # C5 — new/gone counts + DOM p50 from the latest computed bucket (F1 aggregation).
        latest_bucket = await c.fetchrow(
            """
            SELECT bucket_date, new_count, gone_count, dom_p50_days, computed_at
              FROM market_bucket_daily WHERE symbol_key = $1
             ORDER BY bucket_date DESC LIMIT 1
            """,
            symbol_key,
        )

        # Dealer altas in the 30d activity window (C8). "Bajas" (a dealer whose entire
        # stock of this symbol went to zero) is declared, not built here — it requires a
        # per-dealer as-of-window stock reconstruction beyond F2's live-snapshot scope;
        # left as a Fase-4-adjacent gap, not silently faked as a zero.
        altas = await c.fetchval(
            f"""
            SELECT count(DISTINCT v.entity_ulid) FROM vehicle v JOIN entity e ON e.entity_ulid = v.entity_ulid
              JOIN vehicle_event ev ON ev.vehicle_ulid = v.vehicle_ulid
             WHERE v.make = $1 AND v.model = $2 AND {prov_filter}
               AND ev.event_type = 'NEW' AND ev.observed_at > $4
            """,
            *base_params, activity_since,
        )

        response = ok(
            {
                "symbol_key": symbol_key, "insufficient_sample": False,
                "active_count": census["active_count"],
                "n_dealers": census["n_dealers"],
                "n_dealers_on_platform": census["n_dealers_on_platform"],
                "top5_stock": top5_stock, "concentration_top5_pct": concentration_pct,
                "price_pressure": {
                    "n_active": pressure["n_active"], "n_with_price_cut": pressure["n_with_price_cut"],
                    "pct": pressure_pct, "window_days": PRESSURE_WINDOW_DAYS,
                    "alert": (pressure_pct is not None and pressure_pct > PRESSURE_ALERT_THRESHOLD_PCT),
                },
                "dealers_new_30d": altas,
                "latest_bucket": (
                    {
                        "bucket_date": str(latest_bucket["bucket_date"]),
                        "new_count": latest_bucket["new_count"], "gone_count": latest_bucket["gone_count"],
                        "dom_p50_days": (float(latest_bucket["dom_p50_days"]) if latest_bucket["dom_p50_days"] is not None else None),
                        "computed_at": str(latest_bucket["computed_at"]),
                    }
                    if latest_bucket is not None else None
                ),
                "sample_vehicles": [
                    {
                        "vehicle_ulid": r["vehicle_ulid"], "year": r["year"], "km": r["km"],
                        "price": float(r["price"]) if r["price"] is not None else None,
                        "deep_link": r["deep_link"], "cdp_code": r["cdp_code"],
                    }
                    for r in sample
                ],
            },
            corpus_now=str(now),
        )
        return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /terminal/{symbol_key}/rating/{vehicle_ulid} — C7 (deal-rating), delegates to M2.
# See module docstring for the amendment rationale.
# ---------------------------------------------------------------------------

@router.get("/terminal/{symbol_key}/rating/{vehicle_ulid}")
@limiter.limit(RATE_DEFAULT)
async def symbol_rating(
    symbol_key: str,
    vehicle_ulid: str,
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    try:
        _parse_symbol_key(symbol_key)
    except ValueError as e:
        return err(str(e), status=400)

    async with request.app.state.pool.acquire() as c:
        result = await compute_price_position(c, vehicle_ulid)
    if not result.ok:
        return err(result.error or "unknown error", status=result.status)
    payload = dict(result.data)
    payload["symbol_key"] = symbol_key
    return ok(payload, **result.meta)


# ---------------------------------------------------------------------------
# GET /terminal/{symbol_key}/sale-inference — C5 (Fase 4): "venta probable" summary.
# V4 audit-freshness gate: the badge degrades to "sin_verificar" automatically whenever no
# audited row is <=30d fresh — a stale/absent audit is NEVER silently presented as verified.
# ---------------------------------------------------------------------------

V4_AUDIT_FRESHNESS_DAYS = 30


@router.get("/terminal/{symbol_key}/sale-inference")
@limiter.limit(RATE_DEFAULT)
async def symbol_sale_inference(
    symbol_key: str,
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    try:
        _parse_symbol_key(symbol_key)
    except ValueError as e:
        return err(str(e), status=400)

    async with request.app.state.pool.acquire() as c:
        exists = await c.fetchval("SELECT 1 FROM market_symbol WHERE symbol_key = $1", symbol_key)
        if not exists:
            return err(f"symbol {symbol_key} not found", status=404)

        counts = await c.fetch(
            """
            SELECT inference, count(*) AS n, avg(confidence) AS avg_confidence
              FROM market_sale_inference WHERE symbol_key = $1
             GROUP BY inference
            """,
            symbol_key,
        )
        by_inference = {
            r["inference"]: {"n": r["n"], "avg_confidence": float(r["avg_confidence"])}
            for r in counts
        }

        # V4 freshness: most recent audit across ALL of market_sale_inference (global gate —
        # the carta's own audit cadence is a periodic sample, not a per-symbol sweep). Computed
        # in Python (not a second SQL round-trip) — simple datetime arithmetic, no need for a
        # database expression.
        latest_audit_at = await c.fetchval("SELECT max(audited_at) FROM market_sale_inference WHERE audited = TRUE")
        audit_fresh = (
            latest_audit_at is not None
            and (datetime.now(timezone.utc) - latest_audit_at) < timedelta(days=V4_AUDIT_FRESHNESS_DAYS)
        )
        false_positive_rate = None
        if audit_fresh:
            audited_stats = await c.fetchrow(
                "SELECT count(*) AS n_audited, "
                "count(*) FILTER (WHERE audit_result = 'still_listed_elsewhere') AS n_false_positive "
                "FROM market_sale_inference WHERE audited = TRUE"
            )
            if audited_stats["n_audited"]:
                false_positive_rate = 100.0 * audited_stats["n_false_positive"] / audited_stats["n_audited"]

        response = ok({
            "symbol_key": symbol_key,
            "probable_sale": by_inference.get("probable_sale", {"n": 0, "avg_confidence": None}),
            "relisted": by_inference.get("relisted", {"n": 0, "avg_confidence": None}),
            "delisted": by_inference.get("delisted", {"n": 0, "avg_confidence": None}),
            "badge": "verificado" if audit_fresh else "sin_verificar",
            "false_positive_rate_pct": false_positive_rate,
            "latest_audit_at": str(latest_audit_at) if latest_audit_at else None,
            "audit_freshness_days": V4_AUDIT_FRESHNESS_DAYS,
        })
        return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /terminal/news — C10 (Fase 5): real sector news, anchored to the chart's timestamp
# (Bloomberg GIP pattern, carta §2.1). ONLY V5-fresh-verified items are served — an item whose
# verified_at is stale (or NULL, e.g. never verified) is NEVER returned, per C10's own gate:
# "cero fabricación, cero atribución no verificada."
# ---------------------------------------------------------------------------

V5_FRESHNESS_DAYS = 30


@router.get("/terminal/news")
@limiter.limit(RATE_DEFAULT)
async def news(
    request: Request,
    symbol_key: str | None = Query(default=None, description="Filter to items tagged with this symbol; omitted = all"),
    limit: int = Query(default=20, ge=1, le=100),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        rows = await c.fetch(
            """
            SELECT news_ulid, source_name, source_url, title, published_at, verified_at, symbol_keys
              FROM sector_news
             WHERE verified_at IS NOT NULL
               AND verified_at > now() - ($1 || ' days')::interval
               AND ($2::text IS NULL OR $2 = ANY(symbol_keys))
             ORDER BY published_at DESC NULLS LAST
             LIMIT $3
            """,
            str(V5_FRESHNESS_DAYS), symbol_key, limit,
        )
        items = [
            {
                "news_ulid": r["news_ulid"], "source_name": r["source_name"], "source_url": r["source_url"],
                "title": r["title"], "published_at": str(r["published_at"]) if r["published_at"] else None,
                "verified_at": str(r["verified_at"]), "symbol_keys": r["symbol_keys"],
            }
            for r in rows
        ]
        response = ok(items, count=len(items), freshness_days=V5_FRESHNESS_DAYS)
        return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /terminal/methodology — V7 (09-trading-terminal.md §7, row V7): every formula lives
# versioned and dated, linked from the UI's "cómo se calcula esto".
# ---------------------------------------------------------------------------

@router.get("/terminal/methodology")
@limiter.limit(RATE_DEFAULT)
async def methodology(request: Request, _: None = Depends(require_api_key)) -> JSONResponse:
    return ok({
        "methodology_version": METHODOLOGY_VERSION,
        "doc": "docs/architecture/09-TERMINAL-METHODOLOGY.md",
        "c1_symbol": "make + model + province_code (NULL = national roll-up)",
        "c2_min_sample": {"min_active": MIN_ACTIVE_C2, "min_events": MIN_EVENTS_C2},
        "c3_bar": "median (p50) of asking price, AS-OF each real bucket day; weekly OHLC "
                  "except range=1M which serves daily bars. Rótulo obligatorio: 'precio de "
                  "anuncio (mediana)', nunca 'precio' a secas.",
        "c4_outlier_exclusion": {
            "rule": "excluded iff BOTH price AND km deviate > sigma_threshold from the "
                    "symbol's own bucket-day population mean (population stddev)",
            "sigma_threshold": 2.6,
            "source": "Manheim 'Summary Methodology for Manheim Used Vehicle Value Index' "
                       "(site.manheim.com), verified live 2026-07-18: 'Outliers are defined "
                       "as those where both price and mileage are outside of 2.6 standard "
                       "deviations.'",
        },
        "c5_rotation": "new/gone counts + DOM p50 from the latest F1 bucket. 'Venta probable "
                       "(inferida)' served by /terminal/{symbol}/sale-inference (Fase 4, "
                       "pipeline/terminal/infer_sales.py) — consumes v_vehicle_lifetime per "
                       "00-MASTER.md C-9; badge is 'sin_verificar' until a V4 audit is <=30d "
                       "fresh (none has run yet, declared not hidden).",
        "c6_price_pressure": {
            "window_days": PRESSURE_WINDOW_DAYS, "alert_threshold_pct": PRESSURE_ALERT_THRESHOLD_PCT,
            "rule": "% of currently-active listings with >=1 PRICE_CHANGE-down in the window, "
                    "evaluated against the corpus's own max(observed_at), not wall-clock now.",
        },
        "c7_deal_rating": "delegates to market.py's compute_price_position (01-market-"
                          "intelligence M2) — a deliberate amendment, see terminal.py module "
                          "docstring: avoids a second independent price-position engine for "
                          "the same vehicle (00-MASTER.md C-1/C-12).",
        "c8_censal": "n_dealers, active_count, top5 concentration, dealers_new_30d — all live "
                     "SQL over vehicle+entity+platform_listing, never precomputed.",
        "c10_news": {
            "sources": ["ANFAC (anfac.com/feed/)", "Faconauto (faconauto.com/feed/)", "GANVAM (ganvam.es/feed/)"],
            "rule": "cero titular sin source_url verificable; V5 re-fetches each item's OWN "
                    "permalink and requires the title to still appear live. verified_at older "
                    "than V5_FRESHNESS_DAYS -> the item is never served, not shown stale.",
            "freshness_days": V5_FRESHNESS_DAYS,
            "classification": "deterministic keyword match against active market_symbol makes — "
                               "no LLM in this pipeline (§8 doctrine: cero LLM en el camino "
                               "crítico del dato).",
        },
        "disclaimers": [
            "Indexa ANUNCIOS, no ventas confirmadas — declarado en el producto, no solo en doc interna.",
            "Sin capa de validación humana sobre el índice (a diferencia de KBB/Edmunds).",
        ],
    })

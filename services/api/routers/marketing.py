"""/entities/{cdp}/listing-audit, /channel-radar, /feed/{target} and /vehicles/{ulid}/
adcopy -- pilar 07-marketing (plans/cardeep-omni/07-marketing.md).

Ownership: this is a NEW router (00-MASTER.md S5.1 file-ownership table has no prior
claimant on ``services/api/routers/marketing.py`` or these paths) -- zero collision
with market.py (01, ``/market/*``), publishing.py (05, ``/publishing/*``) or
arbitrage.py (04, ``/arbitrage/*``).

Cross-pilar reuse (00-MASTER.md C-1/C-12 "un solo calculo"): price-position (C2) is
NEVER re-derived here -- ``compute_price_position`` is imported directly from
market.py, the exact function 03-garage-fleet's ``dealer_ops.py`` already imports for
the same reason. Coverage/divergence classification (C3/C4) reuse the pure functions
already extracted by 05-multiposting's publishing.py (``_coverage_band``,
``_price_divergence``) -- the SAME pattern ``tests/test_api_publishing.py`` itself
already uses (importing those underscore-prefixed helpers across a module boundary is
established precedent in this codebase, not a private API violation).
"""
from __future__ import annotations

import hashlib
from typing import Any

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from pipeline.ids import ulid
from pipeline.marketing.feeds import TARGETS, DealerFeedInput, FeedTarget, VehicleFeedInput, generate_feed
from services.api.cache import cache_set, try_cache_get
from services.api.deps import err, ok, page_slice, require_api_key, resolve_cluster
from services.api.ratelimit import RATE_DEFAULT, RATE_EXPENSIVE, limiter
from services.api.routers.market import compute_price_position

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /entities/{cdp_code}/listing-audit -- C1 (F1)
# ---------------------------------------------------------------------------

_LISTING_AUDIT_SQL = """
    SELECT v.vehicle_ulid, v.deep_link, v.title, v.make, v.model, v.year, v.price,
           v.currency, v.photo_url, la.score, la.checks, la.computed_at
      FROM v_latest_listing_audit la
      JOIN vehicle v ON v.vehicle_ulid = la.vehicle_ulid
     WHERE v.entity_ulid = ANY($1::text[]) AND v.status = 'available'
     ORDER BY la.score ASC, v.vehicle_ulid
     LIMIT $2 OFFSET $3
"""


@router.get("/entities/{cdp_code}/listing-audit")
@limiter.limit(RATE_EXPENSIVE)
async def listing_audit(
    cdp_code: str,
    request: Request,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    include_price_position: bool = Query(
        default=False,
        description="F2 (C2): attach M2 price-position per row via market.py's "
        "compute_price_position (01-market-intelligence's single canonical "
        "implementation, never re-derived here). Opt-in because it costs one extra "
        "sequential DB round-trip PER ROW on this page (bounded by `size`, never the "
        "whole fleet) — off by default so a plain page load stays cheap; the frontend "
        "requests it only where the grounding is actually shown (carta S6 Bloque 1/4).",
    ),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """C1 — "Arregla estos primero" (carta S6 Bloque 1): the dealer's own vehicles,
    worst score first, each with its 11-check breakdown already computed by
    scripts/run_listing_audit.py (never recomputed here — this endpoint ONLY reads
    ``v_latest_listing_audit``, the persisted evidence, per carta S4 C1: "El score se
    persiste con la lista de checks fallados, nunca solo el agregado").

    A vehicle with NO row yet in ``listing_audit`` (audit job has not reached it) is
    simply absent from this list — never a fabricated score. ``meta.audited_count``
    vs ``meta.total_available`` lets the frontend show honest audit coverage.

    F2 (C2): when ``include_price_position=true``, each item also carries
    ``price_position`` — the EXACT same M2 computation 03-garage-fleet's K9 badge and
    dealer_ops.py's price-override consume (00-MASTER.md: "un solo cálculo... 07-C2").
    Never null-padded: a vehicle whose segment lacks comparables gets
    ``price_position: {"position": null, "reason": "..."}, exactly like the
    ``/market/price-position/{ulid}`` endpoint returns directly.
    """
    cached = try_cache_get(request)
    if cached is not None:
        return cached

    async with request.app.state.pool.acquire() as c:
        cluster = await resolve_cluster(c, cdp_code)
        if cluster is None:
            return err(f"dealer {cdp_code} not found", status=404)

        total_available = await c.fetchval(
            "SELECT count(*) FROM vehicle WHERE entity_ulid = ANY($1::text[]) AND status = 'available'",
            cluster.member_ulids,
        )
        latest_run = await c.fetchrow(
            """SELECT lar.run_ulid, lar.finished_at
                 FROM listing_audit la
                 JOIN listing_audit_run lar ON lar.run_ulid = la.run_ulid
                 JOIN vehicle v ON v.vehicle_ulid = la.vehicle_ulid
                WHERE v.entity_ulid = ANY($1::text[])
                ORDER BY la.computed_at DESC LIMIT 1""",
            cluster.member_ulids,
        )
        audited_count = await c.fetchval(
            """SELECT count(*) FROM v_latest_listing_audit la
                 JOIN vehicle v ON v.vehicle_ulid = la.vehicle_ulid
                WHERE v.entity_ulid = ANY($1::text[]) AND v.status = 'available'""",
            cluster.member_ulids,
        )

        offset = (page - 1) * size
        rows = await c.fetch(_LISTING_AUDIT_SQL, cluster.member_ulids, size + 1, offset)
        rows, has_more = page_slice(rows, size)

        items = [
            {
                "vehicle_ulid": r["vehicle_ulid"],
                "deep_link": r["deep_link"],
                "title": r["title"],
                "make": r["make"],
                "model": r["model"],
                "year": r["year"],
                "price": float(r["price"]) if r["price"] is not None else None,
                "currency": r["currency"],
                "photo_url": r["photo_url"],
                "score": r["score"],
                "checks": r["checks"],
                "computed_at": str(r["computed_at"]),
            }
            for r in rows
        ]

        if include_price_position:
            # Sequential on the SAME connection (asyncpg connections are not safe for
            # concurrent overlapping queries) — bounded by `size` (<=200), never the
            # whole fleet. One canonical function, no second formula.
            for item in items:
                outcome = await compute_price_position(c, item["vehicle_ulid"])
                item["price_position"] = outcome.data if outcome.ok else {"position": None, "reason": outcome.error}

        response = ok(
            items,
            page=page, size=size, returned=len(items), has_more=has_more,
            dealer={"cdp_code": cluster.canonical_cdp_code},
            total_available=total_available,
            audited_count=audited_count,
            latest_run_id=latest_run["run_ulid"] if latest_run else None,
            latest_run_finished_at=str(latest_run["finished_at"]) if latest_run and latest_run["finished_at"] else None,
            price_position_included=include_price_position,
        )
    # Deliberately NOT cached when include_price_position=true: compute_price_position
    # reads the LATEST published market_stat run live (market.py's own contract), and
    # caching a per-vehicle price-position snapshot here would silently go stale
    # against that run without the TTL logic knowing to invalidate on a new publish.
    if include_price_position:
        return response
    return cache_set(request, response)


# ---------------------------------------------------------------------------
# GET /entities/{cdp_code}/feed/{target} -- C6 (F3)
# ---------------------------------------------------------------------------


# Every available vehicle, regardless of listing_audit status — the feed must serve
# the FULL inventory, not just already-audited rows. Photo dimensions (needed to
# validate the image_link field) are fetched separately from v_latest_listing_audit
# (_fetch_photo_dims_by_vehicle below) rather than joined here, since a vehicle may
# have no audit row at all yet (in which case its photo is simply "not measured",
# same honest default as c8 itself).
_FEED_VEHICLE_ROWS_SQL = """
    SELECT v.vehicle_ulid, v.deep_link, v.title, v.make, v.model, v.year, v.km,
           v.price, v.currency, v.fuel, v.transmission, v.photo_url, v.vin_ref
      FROM vehicle v
     WHERE v.entity_ulid = ANY($1::text[]) AND v.status = 'available'
     ORDER BY v.vehicle_ulid
"""


async def _fetch_photo_dims_by_vehicle(conn, ulids: list[str]) -> dict[str, tuple[int | None, int | None]]:
    """Reuses the SAME photo-dimension measurements c8 already persisted (F1) —
    the feed's image-size validity check is not a second measurement pass, it is the
    SAME data (00-MASTER.md C-1: one calculation)."""
    if not ulids:
        return {}
    rows = await conn.fetch(
        "SELECT vehicle_ulid, checks FROM v_latest_listing_audit WHERE vehicle_ulid = ANY($1::text[])",
        ulids,
    )
    out: dict[str, tuple[int | None, int | None]] = {}
    for r in rows:
        checks = r["checks"]
        c8 = next((c for c in checks if c.get("check_id") == "c8"), None)
        if c8 is None:
            continue
        ev = c8.get("evidence", {})
        out[r["vehicle_ulid"]] = (ev.get("width"), ev.get("height"))
    return out


@router.get("/entities/{cdp_code}/feed/{target}")
@limiter.limit(RATE_EXPENSIVE)
async def feed_export(
    cdp_code: str,
    request: Request,
    target: str = Path(..., description=f"one of {TARGETS}"),
    _: None = Depends(require_api_key),
):
    """C6 — feed compliant con el spec de la plataforma destino (carta S6 Bloque 3:
    "Cardeep genera el fichero; la campaña la creas y pagas tu en tu cuenta de Google/
    Meta"). Generated LIVE on every request from ``vehicle``+``entity`` (deterministic
    templates, pipeline/marketing/feeds.py, zero LLM per carta S8) — the file itself is
    never stored (doctrine of capacity, cf. capacity_ledger/0033_evict.sql); only the
    metadata (item/valid counts, invalid_report, content_hash) is persisted to
    ``feed_export`` for traceability.

    A <100% valid feed is still downloadable — WITH the failure report attached in
    ``meta.invalid_report`` (carta S4 C6: "sin maquillaje"), never silently dropped.
    """
    if target not in TARGETS:
        return err(f"unknown feed target '{target}', must be one of {TARGETS}", status=422)

    async with request.app.state.pool.acquire() as c:
        cluster = await resolve_cluster(c, cdp_code)
        if cluster is None:
            return err(f"dealer {cdp_code} not found", status=404)

        drow = await c.fetchrow(
            """SELECT e.trade_name, e.address, e.postcode,
                      gm.name AS municipality_name, gp.name AS province_name
                 FROM entity e
                 LEFT JOIN geo_municipality gm ON gm.code = e.municipality_code
                 LEFT JOIN geo_province gp ON gp.code = e.province_code
                WHERE e.entity_ulid = $1""",
            cluster.canonical_ulid,
        )
        dealer = DealerFeedInput(
            cdp_code=cluster.canonical_cdp_code,
            trade_name=drow["trade_name"] if drow else None,
            address=drow["address"] if drow else None,
            postcode=drow["postcode"] if drow else None,
            municipality_name=drow["municipality_name"] if drow else None,
            province_name=drow["province_name"] if drow else None,
        )

        vrows = await c.fetch(_FEED_VEHICLE_ROWS_SQL, cluster.member_ulids)
        ulids = [r["vehicle_ulid"] for r in vrows]
        photo_dims = await _fetch_photo_dims_by_vehicle(c, ulids)

        vehicles = [
            VehicleFeedInput(
                vehicle_ulid=r["vehicle_ulid"], deep_link=r["deep_link"], title=r["title"],
                make=r["make"], model=r["model"], year=r["year"], km=r["km"],
                price=float(r["price"]) if r["price"] is not None else None,
                currency=r["currency"], fuel=r["fuel"], transmission=r["transmission"],
                photo_url=r["photo_url"],
                photo_width=photo_dims.get(r["vehicle_ulid"], (None, None))[0],
                photo_height=photo_dims.get(r["vehicle_ulid"], (None, None))[1],
                vin_ref=r["vin_ref"],
            )
            for r in vrows
        ]

        result = generate_feed(target, vehicles, dealer)  # type: ignore[arg-type]
        content_hash = hashlib.sha256(result.content.encode("utf-8")).hexdigest()

        export_ulid_val = ulid()
        await c.execute(
            """INSERT INTO feed_export
                   (export_ulid, entity_ulid, target, item_count, valid_count, invalid_report, content_hash)
               VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7)""",
            export_ulid_val, cluster.canonical_ulid, target,
            result.item_count, result.valid_count,
            [dict(r) for r in result.invalid_report], content_hash,
        )

    filename_ext = "jsonld" if target == "schema_org_jsonld" else "csv"
    headers = {
        "Content-Disposition": f'attachment; filename="{cdp_code}_{target}.{filename_ext}"',
        "X-Feed-Export-Id": export_ulid_val,
        "X-Feed-Item-Count": str(result.item_count),
        "X-Feed-Valid-Count": str(result.valid_count),
        "X-Feed-Content-Hash": content_hash,
    }
    return PlainTextResponse(content=result.content, media_type=result.content_type, headers=headers)


@router.get("/entities/{cdp_code}/feed/{target}/report")
@limiter.limit(RATE_DEFAULT)
async def feed_export_report(
    cdp_code: str,
    request: Request,
    target: str = Path(..., description=f"one of {TARGETS}"),
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """The JSON companion to the download above (carta S6 Bloque 3: "lista de coches
    excluidos y por qué campo exacto") — a client that wants the failure report WITHOUT
    downloading the whole feed file reads the latest feed_export row instead of
    re-generating."""
    async with request.app.state.pool.acquire() as c:
        cluster = await resolve_cluster(c, cdp_code)
        if cluster is None:
            return err(f"dealer {cdp_code} not found", status=404)

        row = await c.fetchrow(
            """SELECT export_ulid, item_count, valid_count, invalid_report, content_hash, created_at
                 FROM feed_export
                WHERE entity_ulid = $1 AND target = $2
                ORDER BY created_at DESC LIMIT 1""",
            cluster.canonical_ulid, target,
        )
        if row is None:
            return err(f"no feed export exists yet for {cdp_code}/{target} — request the CSV/JSON-LD first", status=404)

        return ok({
            "export_ulid": row["export_ulid"],
            "item_count": row["item_count"],
            "valid_count": row["valid_count"],
            "valid_pct": (row["valid_count"] / row["item_count"] * 100.0) if row["item_count"] else 0.0,
            "invalid_report": row["invalid_report"],
            "content_hash": row["content_hash"],
            "created_at": str(row["created_at"]),
        })

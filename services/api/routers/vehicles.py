"""/vehicles/{ulid} — vehicle detail, history, and platform listing endpoints.

SU-D2 additions:
  - /vehicles/{ulid}: RATE_DEFAULT; not cached (vehicle state changes after
    each harvest run — price, km, status).
  - /vehicles/{ulid}/history: RATE_DEFAULT; not cached (event stream appends
    on every harvest; consumers expect fresh data).

02-history-reports F2 addition:
  - /vehicles/{ulid}/lifetime: "Vida en mercado" — the verified lifetime chain
    (F1's v_vehicle_lifetime, gated vam_verified=TRUE) plus the C1-C10
    aggregates (plans/cardeep-omni/02-history-reports.md §4), computed by the
    pure functions in services/api/lifetime_aggregates.py. RATE_DEFAULT; not
    cached (see F2 close-out note: cache is a decision for measured latency,
    not assumed up front).
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from services.api.deps import err, ok, page_slice, require_api_key
from services.api.lifetime_aggregates import (
    compute_chain,
    compute_episode,
    compute_semaforo,
    freshness_label,
)
from services.api.ratelimit import RATE_DEFAULT, limiter

router = APIRouter()


# ---------------------------------------------------------------------------
# GAP 2 new: /vehicles/{ulid} detail + /vehicles/{ulid}/history
# ---------------------------------------------------------------------------

@router.get("/vehicles/{vehicle_ulid}/history")
@limiter.limit(RATE_DEFAULT)
async def vehicle_history(
    vehicle_ulid: str,
    request: Request,
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
    async with request.app.state.pool.acquire() as c:
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
            size + 1,
            offset,
        )
        rows, has_more = page_slice(rows, size)
        items = [{**dict(r), "observed_at": str(r["observed_at"])} for r in rows]
        return ok(
            items,
            page=page,
            size=size,
            returned=len(items),
            has_more=has_more,
            vehicle_ulid=vehicle_ulid,
        )


@router.get("/vehicles/{vehicle_ulid}")
@limiter.limit(RATE_DEFAULT)
async def vehicle_detail(
    vehicle_ulid: str,
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """GAP-2: Full detail for a single vehicle.

    If *vehicle_ulid* is a non-canonical alias (per v_canonical_vehicle),
    the canonical_vehicle_ulid is exposed so callers can redirect.
    Returns 404 with coherent message when the ulid does not exist at all.
    """
    async with request.app.state.pool.acquire() as c:
        row = await c.fetchrow(
            """
            SELECT v.vehicle_ulid, v.make, v.model, v.year, v.km, v.price, v.currency,
                   v.photo_url, v.deep_link, v.title, v.fuel, v.transmission,
                   v.vin_ref, v.status, v.first_seen, v.last_seen,
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
# 02-history-reports F2: GET /vehicles/{ulid}/lifetime — "Vida en mercado"
# ---------------------------------------------------------------------------

# Walks v_vehicle_lifetime (the served, vam_verified=TRUE-only overlay from
# pipeline/identity/link_lifetimes.py) outward from vehicle_ulid in both
# directions. v_vehicle_lifetime is EMPTY whenever no lifetime_link_run has
# been vam_verified=TRUE yet — this query then returns 0 rows, and the
# handler below degrades honestly to a single-episode, chain_verified=False
# response (§12: a section renders only if it has >=1 real datum).
#
# A depth guard (50) is defense-in-depth against any future data anomaly; the
# resolver's temporal-ordering guard (link_lifetimes.py's _within_window,
# strict >) makes a cycle impossible by construction today.
_CHAIN_SQL = """
    WITH RECURSIVE fwd AS (
        SELECT vehicle_ulid_from, vehicle_ulid_to, match_signal, match_probability, evidence, 1 AS depth
          FROM v_vehicle_lifetime WHERE vehicle_ulid_from = $1
        UNION ALL
        SELECT vl.vehicle_ulid_from, vl.vehicle_ulid_to, vl.match_signal, vl.match_probability, vl.evidence, fwd.depth + 1
          FROM v_vehicle_lifetime vl JOIN fwd ON vl.vehicle_ulid_from = fwd.vehicle_ulid_to
         WHERE fwd.depth < 50
    ),
    bwd AS (
        SELECT vehicle_ulid_from, vehicle_ulid_to, match_signal, match_probability, evidence, 1 AS depth
          FROM v_vehicle_lifetime WHERE vehicle_ulid_to = $1
        UNION ALL
        SELECT vl.vehicle_ulid_from, vl.vehicle_ulid_to, vl.match_signal, vl.match_probability, vl.evidence, bwd.depth + 1
          FROM v_vehicle_lifetime vl JOIN bwd ON vl.vehicle_ulid_to = bwd.vehicle_ulid_from
         WHERE bwd.depth < 50
    )
    SELECT DISTINCT vehicle_ulid_from, vehicle_ulid_to, match_signal, match_probability, evidence
      FROM (
          SELECT vehicle_ulid_from, vehicle_ulid_to, match_signal, match_probability, evidence FROM fwd
          UNION
          SELECT vehicle_ulid_from, vehicle_ulid_to, match_signal, match_probability, evidence FROM bwd
      ) x
"""


def _chain_node_ulids(vehicle_ulid: str, edges: list[dict]) -> list[str]:
    """Order the chain's vehicle_ulids from earliest episode to latest.

    The resolver (link_lifetimes.py) only ever creates a linear chain — each
    vehicle_ulid has at most one incoming and one outgoing edge per verified
    run — so a simple walk from the node with no predecessor is sufficient
    (no general graph traversal needed).
    """
    nodes = {vehicle_ulid}
    succ: dict[str, str] = {}
    pred: dict[str, str] = {}
    for e in edges:
        nodes.add(e["vehicle_ulid_from"])
        nodes.add(e["vehicle_ulid_to"])
        succ[e["vehicle_ulid_from"]] = e["vehicle_ulid_to"]
        pred[e["vehicle_ulid_to"]] = e["vehicle_ulid_from"]

    start = next((n for n in nodes if n not in pred), vehicle_ulid)
    ordered = [start]
    cur = start
    seen = {start}
    while cur in succ and succ[cur] not in seen:
        cur = succ[cur]
        ordered.append(cur)
        seen.add(cur)
    return ordered


@router.get("/vehicles/{vehicle_ulid}/lifetime")
@limiter.limit(RATE_DEFAULT)
async def vehicle_lifetime(
    vehicle_ulid: str,
    request: Request,
    _: None = Depends(require_api_key),
) -> JSONResponse:
    """Vida en mercado: the verified lifetime chain for one physical car plus
    the C1-C10 aggregates (plans/cardeep-omni/02-history-reports.md §4).

    Honest degradation, not an error, when there is no verified chain (no F1
    run has been vam_verified=TRUE yet, or this specific vehicle has no
    candidate link): the response still carries the vehicle's OWN episode
    metrics (C1/C3/C4/C8a/C10 — these never depend on cross-episode linking),
    with ``chain_verified: false`` and the chain-only fields (C2/C6/C7/C8b)
    absent rather than fabricated (§12).
    """
    async with request.app.state.pool.acquire() as c:
        exists = await c.fetchval("SELECT 1 FROM vehicle WHERE vehicle_ulid = $1", vehicle_ulid)
        if exists is None:
            return err(f"vehicle {vehicle_ulid} not found")

        edge_rows = await c.fetch(_CHAIN_SQL, vehicle_ulid)
        edges = [dict(r) for r in edge_rows]

        node_ulids = _chain_node_ulids(vehicle_ulid, edges)

        vehicle_rows = await c.fetch(
            """
            SELECT vehicle_ulid, entity_ulid, make, model, year, km, price,
                   status, first_seen, last_seen
              FROM vehicle
             WHERE vehicle_ulid = ANY($1::text[])
            """,
            node_ulids,
        )
        vehicles_by_ulid = {r["vehicle_ulid"]: dict(r) for r in vehicle_rows}

        event_rows = await c.fetch(
            """
            SELECT vehicle_ulid, event_type, old_value, new_value, observed_at
              FROM vehicle_event
             WHERE vehicle_ulid = ANY($1::text[])
             ORDER BY vehicle_ulid, observed_at ASC
            """,
            node_ulids,
        )
        events_by_ulid: dict[str, list[dict]] = defaultdict(list)
        for r in event_rows:
            events_by_ulid[r["vehicle_ulid"]].append(dict(r))

        dealer_ulids = list({v["entity_ulid"] for v in vehicles_by_ulid.values()})
        entity_rows = await c.fetch(
            "SELECT entity_ulid, cdp_code, trade_name, kind FROM entity WHERE entity_ulid = ANY($1::text[])",
            dealer_ulids,
        )
        entities_by_ulid = {r["entity_ulid"]: dict(r) for r in entity_rows}

        now = datetime.now(timezone.utc)
        episodes = []
        for ulid in node_ulids:
            v = vehicles_by_ulid.get(ulid)
            if v is None:
                # A chain member vanished (evicted/deleted since the F1 run wrote
                # this edge — PG MVCC doctrine allows DELETE of stale rows).
                # Skip it honestly rather than crash; the chain degrades to its
                # remaining real members.
                continue
            ep = compute_episode(v, events_by_ulid.get(ulid, []), now)
            dealer = entities_by_ulid.get(v["entity_ulid"])
            ep.update({
                "make": v["make"], "model": v["model"], "year": v["year"],
                "price": float(v["price"]) if v["price"] is not None else None,
                "km": v["km"], "status": v["status"],
                "first_seen": str(v["first_seen"]), "last_seen": str(v["last_seen"]),
                "dealer_cdp_code": dealer["cdp_code"] if dealer else None,
                "dealer_name": dealer["trade_name"] if dealer else None,
            })
            episodes.append(ep)

        # C8b: inter-episode km retreat — F1 already evaluated this per edge
        # (evidence.km_retreat_flagged) when it built the chain; reuse it rather
        # than recomputing, so the linker and the alert can never diverge.
        c8b_km_retreats = [
            {
                "vehicle_ulid_from": e["vehicle_ulid_from"],
                "vehicle_ulid_to": e["vehicle_ulid_to"],
                **e["evidence"],
            }
            for e in edges
            if e["evidence"].get("km_retreat_flagged")
        ]

        chain = compute_chain(episodes, edges)
        chain["c8b_km_retreats"] = c8b_km_retreats
        current_episode = next(
            (e for e in episodes if e["vehicle_ulid"] == vehicle_ulid),
            episodes[0] if episodes else None,
        )
        semaforo = (
            compute_semaforo(current_episode, chain)
            if current_episode is not None
            else {"label": "sin_senales", "triggers": []}
        )
        freshness = (
            freshness_label(vehicles_by_ulid[vehicle_ulid]["last_seen"], now)
            if vehicle_ulid in vehicles_by_ulid
            else None
        )

        links = [
            {
                "vehicle_ulid_from": e["vehicle_ulid_from"],
                "vehicle_ulid_to": e["vehicle_ulid_to"],
                "match_signal": e["match_signal"],
                "match_probability": e["match_probability"],
                "evidence": e["evidence"],
            }
            for e in edges
        ]

        return ok(
            {
                "vehicle_ulid": vehicle_ulid,
                "chain_verified": chain["chain_verified"],
                "episodes": episodes,
                "links": links,
                "aggregates": chain,
                "semaforo": semaforo,
                "freshness": freshness,
            },
            count=len(episodes),
        )

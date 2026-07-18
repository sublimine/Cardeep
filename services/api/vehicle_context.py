"""services/api/vehicle_context.py — 06-unified-crm-chat F5: the shared "chip de
mercado" computation (carta §4: "días en mercado, historial de precio").

Reused by ``crm_deals.py`` and ``crm_inbox.py`` so the Inbox/Deals/Kanban chip and
``GET /vehicles/{ulid}`` (``services/api/routers/vehicles.py``) NEVER diverge
(00-MASTER.md C-1, "un solo cálculo"): ``days_in_stock`` here is byte-identical to
``now() - vehicle.first_seen`` and price history reads the SAME ``vehicle_event`` rows
``/vehicles/{ulid}/history`` serves — this module does not re-derive either value from
a second source of truth. ``tests/test_vehicle_context.py``'s divergence test calls
BOTH this module and the ``/vehicles/{ulid}`` route independently and asserts they
agree, per carta §7's protocol.

Two entry points:
  * ``compute_vehicle_context`` — full detail (price history included), for single-
    resource views (a deal's detail modal, an open conversation thread).
  * ``batch_vehicle_summaries`` — ONE query for N vehicles (no price history), for
    list views (the deals list, the Kanban board, the inbox list) so rendering a page
    of cards never N+1-queries the census.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _days_in_stock(first_seen: datetime, now: datetime) -> int:
    return (now - first_seen).days


async def compute_vehicle_context(conn, vehicle_ulid: str) -> dict[str, Any] | None:
    """Full "chip de mercado" for one vehicle: days in stock, current price, full
    PRICE_CHANGE history, and whether it is still listed (status != 'gone' — carta §5
    F5 test negativo: "vehículo GONE del censo -> el chip lo dice, no muestra datos
    stale como vivos"). Returns None if the vehicle_ulid does not exist at all.
    """
    vrow = await conn.fetchrow(
        "SELECT vehicle_ulid, make, model, year, price, status, first_seen, last_seen "
        "FROM vehicle WHERE vehicle_ulid = $1",
        vehicle_ulid,
    )
    if vrow is None:
        return None

    event_rows = await conn.fetch(
        """
        SELECT new_value, observed_at FROM vehicle_event
         WHERE vehicle_ulid = $1 AND event_type = 'PRICE_CHANGE'
         ORDER BY observed_at ASC
        """,
        vehicle_ulid,
    )
    price_history: list[dict[str, Any]] = []
    for r in event_rows:
        new_val = r["new_value"]
        price = new_val.get("price") if isinstance(new_val, dict) else None
        if price is not None:
            price_history.append({"price": float(price), "observedAt": r["observed_at"].isoformat()})

    now = datetime.now(timezone.utc)
    return {
        "vehicleUlid": vrow["vehicle_ulid"],
        "make": vrow["make"], "model": vrow["model"], "year": vrow["year"],
        "price": float(vrow["price"]) if vrow["price"] is not None else None,
        "status": vrow["status"],
        "stillListed": vrow["status"] != "gone",
        "daysInStock": _days_in_stock(vrow["first_seen"], now),
        "firstSeen": vrow["first_seen"].isoformat(),
        "priceHistory": price_history,
    }


async def batch_vehicle_summaries(conn, vehicle_ulids: list[str]) -> dict[str, dict[str, Any]]:
    """Same fields as ``compute_vehicle_context`` MINUS ``priceHistory``, for N vehicles
    in a single query — list views must never N+1 into the census per card."""
    if not vehicle_ulids:
        return {}
    rows = await conn.fetch(
        "SELECT vehicle_ulid, make, model, year, price, status, first_seen "
        "FROM vehicle WHERE vehicle_ulid = ANY($1::text[])",
        list(set(vehicle_ulids)),
    )
    now = datetime.now(timezone.utc)
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        out[r["vehicle_ulid"]] = {
            "vehicleUlid": r["vehicle_ulid"],
            "make": r["make"], "model": r["model"], "year": r["year"],
            "price": float(r["price"]) if r["price"] is not None else None,
            "status": r["status"],
            "stillListed": r["status"] != "gone",
            "daysInStock": _days_in_stock(r["first_seen"], now),
            "firstSeen": r["first_seen"].isoformat(),
        }
    return out

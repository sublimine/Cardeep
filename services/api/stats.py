"""Single source of truth for the GET /stats product counts.

Both the live handler (services/api/routers/ops.py) and the off-request refresh job
(scripts/refresh_product_stats.py -> product_stats table) call compute_counts, so the cached row is
byte-identical to a live computation. No FastAPI imports here, so the scheduler/script can import it cheaply.
"""
from __future__ import annotations

from typing import Any

# Order/keys mirror the GET /stats `counts` envelope exactly. The two heavy ones (dealers,
# vehicles_unique_available) are COUNT(DISTINCT)/JOIN over millions of rows — that is why /stats is
# precomputed into product_stats off the request path.
_QUERIES: dict[str, str] = {
    "dealers": """
        SELECT count(DISTINCT vdr.resolved_cdp_code)
          FROM v_dealer_resolved vdr
          JOIN entity e ON e.entity_ulid = vdr.entity_ulid
         WHERE e.kind <> 'particular'
    """,
    "vehicles_unique_available": """
        SELECT count(*)
          FROM v_canonical_vehicle vc
          JOIN servable_vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
         WHERE vc.vehicle_ulid = vc.canonical_vehicle_ulid
           AND v.status = 'available'
    """,
    "events": "SELECT count(*) FROM vehicle_event",
    "provinces": "SELECT count(*) FROM geo_province",
    "municipalities": "SELECT count(*) FROM geo_municipality",
}

STAT_KEYS: tuple[str, ...] = tuple(_QUERIES)


async def compute_counts(conn: Any) -> dict[str, int]:
    """Compute the 5 product counts live from base tables/views (the slow but exact path)."""
    out: dict[str, int] = {}
    for key, sql in _QUERIES.items():
        out[key] = await conn.fetchval(sql)
    return out

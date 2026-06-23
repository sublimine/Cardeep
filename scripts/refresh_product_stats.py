"""Refresh the product_stats single-row cache that backs a fast GET /stats.

Computes the exact product counts (services.api.stats.compute_counts — the same queries the API uses)
and UPSERTs the single row. Designed to run OFF the request path: invoked on a cadence by the harvest
scheduler, and runnable by hand. Idempotent (UPSERT id=1). Reads CARDEEP_DSN.

Usage: python -m scripts.refresh_product_stats
"""
from __future__ import annotations

import asyncio
import os

import asyncpg

from services.api.stats import compute_counts

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")


async def refresh(dsn: str = DSN) -> dict[str, int]:
    """Compute the counts and UPSERT product_stats(id=1). Returns the counts written."""
    conn = await asyncpg.connect(dsn)
    try:
        counts = await compute_counts(conn)
        await conn.execute(
            """
            INSERT INTO product_stats
                (id, dealers, vehicles_unique_available, events, provinces, municipalities, computed_at)
            VALUES (1, $1, $2, $3, $4, $5, now())
            ON CONFLICT (id) DO UPDATE SET
                dealers = EXCLUDED.dealers,
                vehicles_unique_available = EXCLUDED.vehicles_unique_available,
                events = EXCLUDED.events,
                provinces = EXCLUDED.provinces,
                municipalities = EXCLUDED.municipalities,
                computed_at = now()
            """,
            counts["dealers"],
            counts["vehicles_unique_available"],
            counts["events"],
            counts["provinces"],
            counts["municipalities"],
        )
        return counts
    finally:
        await conn.close()


def main() -> None:
    counts = asyncio.run(refresh())
    print("product_stats refreshed:", counts)


if __name__ == "__main__":
    main()

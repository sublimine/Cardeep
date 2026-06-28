"""Refresh the product_stats cache that backs a fast GET /stats — ONE ROW PER country.

Computes the exact product counts (services.api.stats.compute_counts — the same queries the API uses)
for EVERY country present in ``entity`` and UPSERTs one product_stats row per country. Designed to run
OFF the request path: invoked on a cadence by the harvest scheduler, and runnable by hand. Idempotent
(UPSERT on country_code). Reads CARDEEP_DSN.

ES byte-identical: with ES the only tenant (entity non-ES = 0 today), this writes exactly the ES row —
the same counts as the historical single-row refresh, now addressed by country_code='ES' (0066).

Usage: python -m scripts.refresh_product_stats
"""
from __future__ import annotations

import asyncio
import os

import asyncpg

from services.api.stats import DEFAULT_COUNTRY, compute_counts

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

_UPSERT = """
    INSERT INTO product_stats
        (country_code, dealers, vehicles_unique_available, events, provinces, municipalities, computed_at)
    VALUES ($1, $2, $3, $4, $5, $6, now())
    ON CONFLICT (country_code) DO UPDATE SET
        dealers = EXCLUDED.dealers,
        vehicles_unique_available = EXCLUDED.vehicles_unique_available,
        events = EXCLUDED.events,
        provinces = EXCLUDED.provinces,
        municipalities = EXCLUDED.municipalities,
        computed_at = now()
"""


async def _distinct_countries(conn: asyncpg.Connection) -> list[str]:
    """Every country to refresh: the distinct ``entity.country_code`` values, or ``[DEFAULT_COUNTRY]``
    when the census is empty (so the ES row is always refreshed — byte-identical to the single-tenant
    past)."""
    rows = await conn.fetch(
        "SELECT DISTINCT country_code FROM entity WHERE country_code IS NOT NULL ORDER BY country_code")
    return [r["country_code"] for r in rows] or [DEFAULT_COUNTRY]


async def refresh_with_conn(conn: asyncpg.Connection) -> dict[str, dict[str, int]]:
    """Compute + UPSERT one product_stats row per country present in ``entity``, on the CALLER's
    connection (so tests can run it inside a rolled-back transaction). Returns ``{country: counts}``."""
    out: dict[str, dict[str, int]] = {}
    for cc in await _distinct_countries(conn):
        counts = await compute_counts(conn, cc)
        await conn.execute(
            _UPSERT, cc, counts["dealers"], counts["vehicles_unique_available"],
            counts["events"], counts["provinces"], counts["municipalities"])
        out[cc] = counts
    return out


async def refresh(dsn: str = DSN) -> dict[str, dict[str, int]]:
    """Open a connection and refresh every country's product_stats row. Returns ``{country: counts}``."""
    conn = await asyncpg.connect(dsn)
    try:
        return await refresh_with_conn(conn)
    finally:
        await conn.close()


def main() -> None:
    counts = asyncio.run(refresh())
    print("product_stats refreshed:", counts)


if __name__ == "__main__":
    main()

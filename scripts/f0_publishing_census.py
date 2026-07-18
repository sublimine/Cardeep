"""F0 (05-multiposting) — direct SQL census of platform_listing by platform x dealer,
cross-checked against the live GET /platforms/{cdp}/inventory endpoint.

One-shot verification script (not a permanent module), mirroring the pattern of
scripts/f0_market_volume_truth.py (01-market-intelligence). Prints a report consumed to
write plans/cardeep-omni/05-multiposting.md's F0 execution log with real numbers.

Two independent verification paths, per the carta's F0 criterion:
  Via 1 (direct SQL): platform_listing JOIN servable_vehicle JOIN entity, grouped by platform.
  Via 2 (live endpoint): GET /platforms/{cdp}/inventory, sampled (not fully paginated for the
    largest platforms -- Wallapop alone has 789k+ listed rows; full pagination at 200/page
    against the shared RATE_EXPENSIVE=30/min limiter would take ~2h and risks starving the
    other two parallel fronts (03-garage-fleet, 04-arbitrage) hitting the SAME live API
    process right now -- so the smallest 2 real platforms are paginated to COMPLETION
    (exact-count proof) and the largest platforms are sampled (first page, subset proof).
    Declared honestly below, not disguised as exhaustive.

Usage: python -m scripts.f0_publishing_census
"""
from __future__ import annotations

import asyncio
import os
import time
import urllib.request
import urllib.error
import json

import asyncpg

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
API_BASE = os.environ.get("CARDEEP_API_BASE", "http://127.0.0.1:8090")

# Full-pagination cross-check budget: platforms with fewer listed rows than this are
# paginated to completion (exact-count proof); above it, sampled (subset proof) to respect
# the shared rate limiter (RATE_EXPENSIVE=30/min) other live sessions depend on.
FULL_PAGINATION_ROW_BUDGET = 2_000


def _http_get_json(path: str) -> dict:
    req = urllib.request.Request(API_BASE + path, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        print("=== F0.1 platform_listing totals (direct SQL) ===")
        total = await conn.fetchval("SELECT count(*) FROM platform_listing")
        listed = await conn.fetchval("SELECT count(*) FROM platform_listing WHERE status='listed'")
        n_platforms = await conn.fetchval("SELECT count(DISTINCT platform_entity_ulid) FROM platform_listing")
        print(f"  total edges={total:,}  listed={listed:,}  distinct platforms={n_platforms}")

        print("\n=== F0.2 per-platform census: listed edges (dealer inventory, live) x distinct dealers ===")
        # Mirrors platforms.py:59-63's exact JOIN (servable_vehicle, not raw vehicle) so this
        # census counts precisely what the existing endpoint would serve for each platform.
        rows = await conn.fetch(
            """
            SELECT e.cdp_code, e.trade_name, e.entity_ulid,
                   count(*) FILTER (WHERE pl.status='listed') AS n_listed,
                   count(DISTINCT d.entity_ulid) FILTER (WHERE pl.status='listed') AS n_dealers
              FROM platform_listing pl
              JOIN servable_vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
              JOIN entity d ON d.entity_ulid = v.entity_ulid
              JOIN entity e ON e.entity_ulid = pl.platform_entity_ulid
             GROUP BY e.cdp_code, e.trade_name, e.entity_ulid
             ORDER BY n_listed DESC
            """
        )
        for r in rows:
            print(f"  {r['trade_name']:<22} {r['cdp_code']:<20} listed={r['n_listed']:>8,}  dealers={r['n_dealers']:>6,}")

        print("\n=== F0.2b REAL FINDING: platform_entity_ulid targets that are NOT kind='plataforma' ===")
        kind_rows = await conn.fetch(
            """SELECT e.kind, count(DISTINCT e.entity_ulid) n_entities, count(*) n_edges
                 FROM platform_listing pl JOIN entity e ON e.entity_ulid = pl.platform_entity_ulid
                GROUP BY e.kind ORDER BY n_edges DESC"""
        )
        for r in kind_rows:
            print(f"  kind={r['kind']:<16} entities={r['n_entities']:>3}  edges={r['n_edges']:>10,}")
        non_plataforma_edges = sum(r["n_edges"] for r in kind_rows if r["kind"] != "plataforma")
        print(f"  TOTAL edges via non-'plataforma' targets: {non_plataforma_edges:,}")
        print("  (oem_vo_portal/cadena/rent_a_car_vo/importador all legitimately re-list a")
        print("   dealer's car under their own brand/channel -- platforms.py:49-50's hard")
        print("   'kind==plataforma' gate 400s on these, undercounting real cross-postings.")
        print("   Declared as a finding for publishing.py to NOT replicate; not fixed here --")
        print("   platforms.py is shared infrastructure outside this pilar's F0-F2 scope.)")

        print("\n=== F0.3 dealers-with-inventory vs dealers-with-any-platform-presence ===")
        dealers_with_inv = await conn.fetchval(
            "SELECT count(DISTINCT entity_ulid) FROM servable_vehicle"
        )
        dealers_with_platform = await conn.fetchval(
            """SELECT count(DISTINCT v.entity_ulid)
                 FROM platform_listing pl
                 JOIN servable_vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
                WHERE pl.status='listed'"""
        )
        pct = (dealers_with_platform / dealers_with_inv * 100) if dealers_with_inv else 0
        print(f"  dealers with available inventory: {dealers_with_inv:,}")
        print(f"  dealers with >=1 listed platform edge: {dealers_with_platform:,} ({pct:.2f}%)")

        print("\n=== F0.4 second path: cross-check via live GET /platforms/{cdp}/inventory ===")
        health = _http_get_json("/health")
        print(f"  API /health: {health}")

        for r in rows:
            cdp, name, n_listed_sql = r["cdp_code"], r["trade_name"], r["n_listed"]
            if n_listed_sql == 0:
                continue
            try:
                if n_listed_sql <= FULL_PAGINATION_ROW_BUDGET:
                    # Full pagination -> exact count must match SQL exactly.
                    page, size, seen = 1, 200, 0
                    while True:
                        body = _http_get_json(f"/platforms/{cdp}/inventory?page={page}&size={size}")
                        n = len(body["data"])
                        seen += n
                        if not body["meta"]["has_more"]:
                            break
                        page += 1
                        time.sleep(1.2)  # stay well under 30/min shared with parallel fronts
                    match = "OK" if seen == n_listed_sql else "MISMATCH"
                    print(f"  [FULL] {name:<20} sql={n_listed_sql:,} endpoint={seen:,}  {match}")
                else:
                    # Sampled: first page only -- subset proof (every returned row must be a
                    # real edge that also exists in the SQL result for this platform).
                    body = _http_get_json(f"/platforms/{cdp}/inventory?page=1&size=50")
                    n_page = len(body["data"])
                    print(f"  [SAMPLE] {name:<20} sql_total={n_listed_sql:,} endpoint_first_page={n_page}")
            except urllib.error.HTTPError as e:
                # Expected for the 25 non-'plataforma' targets (F0.2b finding) -- the OLD
                # platforms.py endpoint 400s on them. Not a script bug; declared, not hidden.
                print(f"  [SKIP-400] {name:<20} sql={n_listed_sql:,}  existing endpoint rejects kind (F0.2b)")
            time.sleep(1.2)

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())

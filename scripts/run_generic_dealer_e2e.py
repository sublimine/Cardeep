"""B5.7 E2E test — scrape + ingest 10-15 SCHEMA_ORG dealer sites.

Reads the probe report (docs/recon/B5_7_probe.json), picks up to --limit
SCHEMA_ORG leads, harvests their vehicle pages, ingests into DB and prints
the VAM verdict per dealer.

Usage:
    python scripts/run_generic_dealer_e2e.py \\
        [--probe docs/recon/B5_7_probe.json] \\
        [--limit 15] \\
        [--workers 4] \\
        [--dsn postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep]

PEP8, type hints.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import asyncpg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.platform.generic_dealer_site import (
    harvest_dealer_site,
    ingest_generic_dealer_vehicles,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def _load_schema_org_probes(probe_file: str, limit: int) -> list[dict]:
    path = Path(probe_file)
    if not path.exists():
        raise FileNotFoundError(f"Probe file not found: {probe_file}")
    results = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if obj.get("label") == "SCHEMA_ORG" and obj.get("vehicle_urls_found", 0) > 0:
                results.append(obj)
            if len(results) >= limit:
                break
    return results


def _harvest_one(probe: dict, max_pages: int) -> tuple[dict, list]:
    """Synchronous harvest for one dealer (runs in thread pool)."""
    entity_ulid = probe["entity_ulid"]
    website = probe["website"]
    logger.info("Harvesting %s …", website)
    vehicles = harvest_dealer_site(entity_ulid, website, max_pages=max_pages)
    logger.info("  -> %d vehicles from %s", len(vehicles), website)
    return probe, vehicles


async def _ingest_all(dsn: str, harvests: list[tuple[dict, list]]) -> list[dict]:
    """Ingest all harvested vehicles and collect VAM results."""
    conn = await asyncpg.connect(dsn=dsn)
    results = []
    try:
        for probe, vehicles in harvests:
            result = await ingest_generic_dealer_vehicles(
                conn, probe["entity_ulid"], vehicles
            )
            result["website"] = probe["website"]
            result["vehicle_urls_in_sitemap"] = probe["vehicle_urls_found"]
            result["schema_fields"] = probe["schema_fields_found"]
            results.append(result)
            logger.info("  [%s] ingested=%d skipped=%d available_db=%d verdict=%s",
                        probe["website"][:40], result["ingested"],
                        result["skipped"], result["available_in_db"], result["verdict"])
    finally:
        await conn.close()
    return results


def _print_results(results: list[dict]) -> None:
    print("\n" + "=" * 80)
    print("B5.7 E2E TEST — Resultados por dealer")
    print("=" * 80)
    total_ingested = 0
    total_trustworthy = 0
    print(f"{'Website':<40} {'Sitemap':>7} {'New':>5} {'Skip':>5} {'DB':>6} {'VAM':<12}")
    print("-" * 80)
    for r in results:
        site = r["website"][:39]
        urls = r.get("vehicle_urls_in_sitemap", "?")
        ingested = r.get("ingested", 0)
        skipped = r.get("skipped", 0)
        db_avail = r.get("available_in_db", 0)
        verdict = r.get("verdict", "?")
        print(f"{site:<40} {str(urls):>7} {ingested:>5} {skipped:>5} {db_avail:>6} {verdict:<12}")
        total_ingested += ingested
        if verdict == "TRUSTWORTHY":
            total_trustworthy += 1
    print("-" * 80)
    print(f"{'TOTAL':<40} {'':>7} {total_ingested:>5}")
    print(f"\nVAM TRUSTWORTHY: {total_trustworthy}/{len(results)} dealers")
    print("=" * 80 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="E2E test: generic dealer site scraper")
    parser.add_argument("--probe", default="docs/recon/B5_7_probe.json",
                        help="Path to probe JSON-lines from probe_dealer_sites.py")
    parser.add_argument("--limit", type=int, default=15,
                        help="Max SCHEMA_ORG dealers to test (default: 15)")
    parser.add_argument("--max-pages", type=int, default=200,
                        help="Max vehicle pages to harvest per dealer (default: 200)")
    parser.add_argument("--workers", type=int, default=4,
                        help="Parallel harvest threads (default: 4)")
    parser.add_argument("--dsn",
                        default="postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep",
                        help="DB connection string")
    args = parser.parse_args()

    logger.info("Loading SCHEMA_ORG probes from %s (limit=%d)…", args.probe, args.limit)
    probes = _load_schema_org_probes(args.probe, args.limit)
    logger.info("Found %d SCHEMA_ORG dealers to test", len(probes))

    if not probes:
        logger.error("No SCHEMA_ORG probes found — run probe_dealer_sites.py first")
        sys.exit(1)

    # Harvest in thread pool (blocking IO)
    t0 = time.monotonic()
    harvests: list[tuple[dict, list]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(_harvest_one, p, args.max_pages) for p in probes]
        for fut in futures:
            try:
                harvests.append(fut.result())
            except Exception as exc:
                logger.error("harvest error: %s", exc)

    # Ingest
    logger.info("Ingesting %d dealers into DB…", len(harvests))
    results = asyncio.run(_ingest_all(args.dsn, harvests))

    _print_results(results)

    # Write E2E report
    report_path = Path("docs/recon/B5_7_e2e_results.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logger.info("E2E report written to %s", report_path)
    logger.info("Total elapsed: %.1fs", time.monotonic() - t0)


if __name__ == "__main__":
    main()

"""B5.7 probe — classify Overture leads by web-scrape viability.

Samples up to --sample (default 80) dealer leads from the DB that have
own-site websites (non-platform URLs).  For each lead, calls probe_single()
and writes a JSON-lines report + a summary table.

Usage:
    python scripts/probe_dealer_sites.py [--sample 80] [--workers 8] [--out docs/recon/B5_7_probe.json]

Output:
    docs/recon/B5_7_probe.json   — JSON-lines, one object per lead
    stdout                       — summary table + projection

PEP8, type hints, no external deps beyond the project virtualenv.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

import asyncpg

# Allow running from repo root without install
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.platform.generic_dealer_site import probe_single, SiteProbe

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# Platforms and OEM portals to exclude from "own site" classification
_EXCLUDE_PATTERNS = [
    "milanuncios", "wallapop", "coches.net", "coches.com", "autocasion",
    "autoscout24", "motor.es", "facebook.com", "instagram.com",
    "mercedes-benz.com", "peugeot.es", "nissan.es", "seat.es", "toyota.es",
    "bmw.es", "renault.es", "volkswagen.es", "ford.es", "opel.es",
    "hyundai.com", "kia.com", "volvo.es", "audi.es", "citroen.es",
    "red.nissan.es", "redcomercial.", "youtube.", "wordpress.com",
    "negocio.site", "sociosg.com", "paa.ge", "bit.ly", "honda.es",
    "subaru.es", "dhl.com", "mitsubishi", "redconcesionarios", "redsuzuki",
    "jaguar.es", "landrover.es", "jimdo.com", "wix.com", "weebly.com",
    "blogspot.com", "lexus.es", "fiat.es", "cepsa.es", "repsol.com",
    "michelin.es", "pirelli.com", "goodyear.es", "bridgestone.es",
    "continental.es", "firestone.es", "vulco.es", "midas.es",
    "motorflash.com", "inventario.pro", "motoraddress.com",
    "twsm.es", "dmsplus.es",
]


def _is_own_site(website: str) -> bool:
    w = website.lower()
    return not any(p in w for p in _EXCLUDE_PATTERNS)


async def _fetch_sample(dsn: str, limit: int) -> list[dict]:
    """Query DB for Overture leads with own-site websites."""
    conn = await asyncpg.connect(dsn=dsn)
    try:
        rows = await conn.fetch(
            """
            SELECT entity_ulid, legal_name, trade_name, website, kind, province_code
            FROM entity
            WHERE first_discovered_source LIKE '%overture%'
              AND website IS NOT NULL
              AND website != ''
              AND kind IN ('compraventa', 'desguace', 'concesionario_oficial')
            ORDER BY province_code, entity_ulid
            """,
        )
    finally:
        await conn.close()

    results = []
    for r in rows:
        w = r["website"]
        if w and _is_own_site(w):
            results.append(dict(r))
        if len(results) >= limit:
            break
    return results


def _run_probes(leads: list[dict], workers: int) -> list[SiteProbe]:
    """Probe all leads in a thread pool (probe_single is sync/blocking)."""
    probes: list[SiteProbe] = []

    def _probe(lead: dict) -> SiteProbe:
        return probe_single(lead["entity_ulid"], lead["website"])

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_probe, lead): lead for lead in leads}
        done = 0
        for fut in as_completed(futures):
            done += 1
            try:
                p = fut.result()
                probes.append(p)
                logger.info("[%d/%d] %s -> %s (urls=%d fields=%d)",
                            done, len(leads), p.website, p.label,
                            p.vehicle_urls_found, p.schema_fields_found)
            except Exception as exc:  # noqa: BLE001
                lead = futures[fut]
                logger.error("probe failed %s: %s", lead["website"], exc)
                probes.append(SiteProbe(
                    entity_ulid=lead["entity_ulid"],
                    website=lead["website"],
                    base_url=lead["website"],
                    label="MUERTO",
                    error=str(exc),
                ))
    return probes


def _summary(probes: list[SiteProbe], total_own_site_leads: int) -> dict:
    """Compute classification rates + projection."""
    from collections import Counter
    labels = Counter(p.label for p in probes)
    n = len(probes)

    def pct(k: str) -> float:
        return round(100.0 * labels[k] / n, 1) if n else 0.0

    # Projection: apply sample rates to total own-site leads
    proj_schema = round(total_own_site_leads * labels["SCHEMA_ORG"] / n) if n else 0
    proj_sitemap = round(total_own_site_leads * labels["SITEMAP_SOLO"] / n) if n else 0
    proj_sin_sitemap = round(total_own_site_leads * labels["SIN_SITEMAP"] / n) if n else 0
    proj_dead = round(total_own_site_leads * labels["MUERTO"] / n) if n else 0

    # Avg vehicles per SCHEMA_ORG probe
    schema_probes = [p for p in probes if p.label == "SCHEMA_ORG"]
    avg_vehicle_urls = (
        sum(p.vehicle_urls_found for p in schema_probes) / len(schema_probes)
        if schema_probes else 0
    )

    return {
        "sample_size": n,
        "total_own_site_leads": total_own_site_leads,
        "counts": dict(labels),
        "rates": {
            "SCHEMA_ORG": pct("SCHEMA_ORG"),
            "SITEMAP_SOLO": pct("SITEMAP_SOLO"),
            "SIN_SITEMAP": pct("SIN_SITEMAP"),
            "MUERTO": pct("MUERTO"),
        },
        "projection": {
            "SCHEMA_ORG_leads": proj_schema,
            "SITEMAP_SOLO_leads": proj_sitemap,
            "SIN_SITEMAP_leads": proj_sin_sitemap,
            "MUERTO_leads": proj_dead,
            "avg_vehicle_urls_per_schema_org_site": round(avg_vehicle_urls, 1),
        },
    }


def _print_summary(s: dict) -> None:
    n = s["sample_size"]
    total = s["total_own_site_leads"]
    rates = s["rates"]
    proj = s["projection"]

    print("\n" + "=" * 70)
    print(f"B5.7 PROBE — Clasificación de {n} leads (de {total} webs propias Overture)")
    print("=" * 70)
    print(f"{'Clase':<18} {'Muestra':>8} {'%':>7} {'Proyección ~14k leads':>22}")
    print("-" * 58)
    for label in ("SCHEMA_ORG", "SITEMAP_SOLO", "SIN_SITEMAP", "MUERTO"):
        count = s["counts"].get(label, 0)
        rate = rates.get(label, 0.0)
        proj_n = proj.get(f"{label}_leads", 0)
        print(f"{label:<18} {count:>8} {rate:>6.1f}%  ~{proj_n:>8}")
    print("-" * 58)
    print(f"{'TOTAL':<18} {n:>8} {'100%':>7}")
    print()
    print(f"Schema.org sites: avg {proj['avg_vehicle_urls_per_schema_org_site']:.0f} URLs de vehículo por sitemap")
    proj_vehicles = round(proj["SCHEMA_ORG_leads"] * proj["avg_vehicle_urls_per_schema_org_site"])
    print(f"Proyección coches extraíbles con sitemap+schema.org: ~{proj_vehicles:,}")
    gap = total - proj["SCHEMA_ORG_leads"]
    print(f"Gap restante (SITEMAP_SOLO+SIN_SITEMAP+MUERTO): ~{gap:,} leads necesitan otra vía")
    print("=" * 70 + "\n")


async def _count_own_site_leads(dsn: str) -> int:
    conn = await asyncpg.connect(dsn=dsn)
    try:
        rows = await conn.fetch(
            """
            SELECT website FROM entity
            WHERE first_discovered_source LIKE '%overture%'
              AND website IS NOT NULL AND website != ''
              AND kind IN ('compraventa', 'desguace', 'concesionario_oficial')
            """
        )
        return sum(1 for r in rows if _is_own_site(r["website"]))
    finally:
        await conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe Overture dealer websites")
    parser.add_argument("--sample", type=int, default=80,
                        help="Number of leads to probe (default: 80)")
    parser.add_argument("--workers", type=int, default=6,
                        help="Parallel probe threads (default: 6)")
    parser.add_argument("--out", default="docs/recon/B5_7_probe.json",
                        help="Output JSON-lines file path")
    parser.add_argument("--dsn",
                        default="postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep",
                        help="DB connection string")
    args = parser.parse_args()

    t0 = time.monotonic()

    logger.info("Counting total own-site Overture leads…")
    total_own = asyncio.run(_count_own_site_leads(args.dsn))
    logger.info("Total own-site leads in DB: %d", total_own)

    logger.info("Fetching %d-lead sample from DB…", args.sample)
    leads = asyncio.run(_fetch_sample(args.dsn, args.sample))
    logger.info("Sample fetched: %d leads", len(leads))

    logger.info("Probing %d sites with %d workers…", len(leads), args.workers)
    probes = _run_probes(leads, args.workers)

    # Write JSON-lines
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for p in probes:
            f.write(json.dumps(asdict(p), ensure_ascii=False) + "\n")
    logger.info("Results written to %s", out_path)

    s = _summary(probes, total_own)
    _print_summary(s)

    # Also write summary alongside
    summary_path = out_path.with_suffix(".summary.json")
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)
    logger.info("Summary written to %s", summary_path)

    elapsed = time.monotonic() - t0
    logger.info("Done in %.1fs", elapsed)


if __name__ == "__main__":
    main()

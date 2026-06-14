"""B4.1 — Geo probe: quantify how much of the municipality gap is recoverable via fuzzy match.

STANDALONE diagnostic — reads from cardeep-pg and external APIs; NEVER writes to any table.
Classifies each owner sampled from milanuncios + wallapop into exactly one bucket:
  NO_CITY          — city payload is empty/None -> source wall, cannot fix without re-design
  EXACT            — geo.municipality_code(prov, city) resolves today (current exact match works)
  FUZZY_RECOVERABLE — exact fails but rapidfuzz.process.extractOne >=88 within province succeeds
  LATLON_ONLY      — exact+fuzzy both fail, but item has lat/lon available
  NO_GEO           — nothing resolves

Run:
    cd C:\\Users\\elias\\projects\\cardeep
    python -m scripts.recon.b4_geo_probe        (or python scripts/recon/b4_geo_probe.py)

Requires: rapidfuzz (pip install rapidfuzz) — MIT, €0.
Does NOT write to entity, vehicle, platform_listing, vehicle_event or any other table.
Does NOT commit.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from typing import Iterator

import asyncpg
from curl_cffi import requests as cffi_requests
from rapidfuzz import process as rf_process, fuzz as rf_fuzz

# ---------------------------------------------------------------------------
# Path bootstrap (works whether run as script or module)
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from pipeline.engine.governor import governor  # noqa: E402
from pipeline.geo import GeoResolver, _norm  # noqa: E402
from pipeline.platform.milanuncios_wholesale import (  # noqa: E402
    ENDPOINT as MN_ENDPOINT,
    PAGE_SIZE as MN_PAGE_SIZE,
    MilanunciosFetcher,
    parse_ad_dealer,
    parse_ad_particular,
    _prov2 as mn_prov2,
    _demojibake,
)
from pipeline.platform.wallapop_wholesale import (  # noqa: E402
    SEARCH_ENDPOINT as WP_SEARCH_ENDPOINT,
    USER_ENDPOINT as WP_USER_ENDPOINT,
    CATEGORY_CARS as WP_CATEGORY,
    WallapopFetcher,
    parse_seller,
    parse_item_vehicle,
    _prov_from_cp,
    _GEO_GRID,
    _KEYWORDS as WP_KEYWORDS,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DSN = os.environ.get(
    "CARDEEP_DSN",
    "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep",
)
FUZZY_THRESHOLD = 88          # rapidfuzz score_cutoff for FUZZY_RECOVERABLE bucket
IMPERSONATE = "chrome131"
TIMEOUT = 40

# Milanuncios sample: provinces 42 (Soria, small) and 28 (Madrid, dense with variants)
MN_PROVINCES = (42, 28)
MN_MAX_PAGES_PER_PROVINCE = 3    # max 3 pages × 100 ads = 300 ads per province

# Wallapop sample: 2 keywords × 2 centroids (Madrid + Barcelona) = ~320 items max
WP_SAMPLE_KEYWORDS = WP_KEYWORDS[:2]          # "toyota", "bmw" — enough for the probe
WP_SAMPLE_GRID = _GEO_GRID[:2]               # Madrid + Barcelona centroids
WP_MAX_PAGES_PER_QUERY = 4                   # ~40 items/page × 4 = ~160 items per (kw, centroid)

# ---------------------------------------------------------------------------
# Bucket constants
# ---------------------------------------------------------------------------
NO_CITY = "NO_CITY"
EXACT = "EXACT"
FUZZY_RECOVERABLE = "FUZZY_RECOVERABLE"
LATLON_ONLY = "LATLON_ONLY"
NO_GEO = "NO_GEO"
BUCKETS = (NO_CITY, EXACT, FUZZY_RECOVERABLE, LATLON_ONLY, NO_GEO)


@dataclass
class OwnerSample:
    """Minimal owner record extracted from a single ad/item for bucket classification."""
    source: str            # "milanuncios" | "wallapop"
    kind: str              # "compraventa" | "particular"
    province_code: str | None
    city: str | None       # raw city from payload (after demojibake for MN)
    lat: float | None = None
    lon: float | None = None


@dataclass
class BucketResult:
    bucket: str
    fuzzy_match: str | None = None    # INE municipality name matched by fuzzy
    fuzzy_score: float | None = None  # rapidfuzz score


@dataclass
class ProbeStats:
    source: str
    total: int = 0
    by_bucket: dict = field(default_factory=lambda: {b: 0 for b in BUCKETS})
    fuzzy_examples: list = field(default_factory=list)   # list of dict for report

    def record(self, owner: OwnerSample, result: BucketResult) -> None:
        self.total += 1
        self.by_bucket[result.bucket] += 1
        if result.bucket == FUZZY_RECOVERABLE and len(self.fuzzy_examples) < 50:
            self.fuzzy_examples.append({
                "city_payload": owner.city,
                "province_code": owner.province_code,
                "muni_ine": result.fuzzy_match,
                "score": round(result.fuzzy_score or 0, 1),
                "kind": owner.kind,
            })


# ---------------------------------------------------------------------------
# Fuzzy municipality index (built from GeoResolver internal state)
# ---------------------------------------------------------------------------

def build_fuzzy_index(geo: GeoResolver) -> dict[str, list[str]]:
    """Build prov_code -> [list of unique normalized municipality names] for fuzzy search.

    We pull the keys from geo._muni (prov -> {norm_key: code5}). The keys are already
    normalized (_norm applied). We de-duplicate by taking the unique set of keys per prov.
    rapidfuzz will score our query_norm against these keys and return the closest match.
    """
    index: dict[str, list[str]] = {}
    for prov, name_to_code in geo._muni.items():
        index[prov] = list(name_to_code.keys())
    return index


def classify_owner(
    owner: OwnerSample,
    geo: GeoResolver,
    fuzzy_index: dict[str, list[str]],
) -> BucketResult:
    """Classify one owner into exactly one bucket."""
    # 1) Province sanity — if no province, only LATLON or NO_GEO remain.
    if not owner.province_code:
        if owner.lat is not None and owner.lon is not None:
            return BucketResult(LATLON_ONLY)
        return BucketResult(NO_GEO)

    # 2) NO_CITY — empty city payload -> source wall
    if not owner.city or not owner.city.strip():
        if owner.lat is not None and owner.lon is not None:
            return BucketResult(LATLON_ONLY)
        return BucketResult(NO_CITY)

    # 3) EXACT — does the current GeoResolver resolve it?
    if geo.municipality_code(owner.province_code, owner.city) is not None:
        return BucketResult(EXACT)

    # 4) FUZZY — try rapidfuzz within the province.
    # Guard: filter out candidates that are too short to be a real municipality match.
    # The GeoResolver index contains normalized fragments like 'la', 'las', 'los', 'el'
    # (articles stripped from bilingual names like "Poble Sec / la Pobla"). These short
    # tokens produce false-positive WRatio scores against any city starting with 'La...'
    # or 'Las...'. We exclude candidates whose character length < max(4, len(city_norm)//2).
    city_norm = _norm(owner.city)
    min_cand_len = max(4, len(city_norm) // 2)
    candidates = [
        c for c in (fuzzy_index.get(owner.province_code, []))
        if len(c) >= min_cand_len
    ]
    if candidates and city_norm:
        hit = rf_process.extractOne(
            city_norm,
            candidates,
            scorer=rf_fuzz.WRatio,
            processor=None,          # already normalized
            score_cutoff=FUZZY_THRESHOLD,
        )
        if hit is not None:
            matched_key, score, _ = hit
            # Recover a human-friendly INE name from the key (best-effort: use the key itself
            # since it is already the normalized form; the report shows city_payload -> key).
            return BucketResult(FUZZY_RECOVERABLE, fuzzy_match=matched_key, fuzzy_score=score)

    # 5) LATLON_ONLY
    if owner.lat is not None and owner.lon is not None:
        return BucketResult(LATLON_ONLY)

    # 6) NO_GEO
    return BucketResult(NO_GEO)


# ---------------------------------------------------------------------------
# Milanuncios sampling
# ---------------------------------------------------------------------------

async def sample_milanuncios(
    geo: GeoResolver,
    fuzzy_index: dict[str, list[str]],
) -> ProbeStats:
    """Fetch MN_PROVINCES × MN_MAX_PAGES_PER_PROVINCE pages, classify owners."""
    stats = ProbeStats(source="milanuncios")
    fetcher = MilanunciosFetcher(pool_size=1)
    gov = governor()
    gf = gov.wrap_fetch_text(fetcher.fetch_page)

    seen_authors: set[str] = set()
    print("[MN] starting milanuncios sample...")

    for prov_int in MN_PROVINCES:
        prov_code = f"{prov_int:02d}"
        print(f"  [MN] province={prov_int} ({prov_code})...")
        for page_idx in range(MN_MAX_PAGES_PER_PROVINCE):
            offset = page_idx * MN_PAGE_SIZE
            try:
                # Acquire token from the governor before fetching
                await gov.acquire("searchapi.gw.milanuncios.com")
                slot = await fetcher._free.get()
                try:
                    data = await asyncio.to_thread(
                        fetcher.fetch_page,
                        MN_ENDPOINT,
                        offset=offset,
                        limit=MN_PAGE_SIZE,
                        province=prov_int,
                        slot=slot,
                    )
                finally:
                    fetcher._free.put_nowait(slot)
            except Exception as exc:
                print(f"  [MN] WARN province={prov_int} offset={offset}: {exc}")
                break

            ads = data.get("ads") or []
            if not ads:
                print(f"  [MN] province={prov_int} empty at offset={offset}, stopping")
                break

            for ad in ads:
                # Try dealer path first, then particular
                d = parse_ad_dealer(ad)
                if d is not None:
                    author_key = f"pro:{d.author_id}"
                    if author_key in seen_authors:
                        continue
                    seen_authors.add(author_key)
                    owner = OwnerSample(
                        source="milanuncios",
                        kind="compraventa",
                        province_code=d.province_code,
                        city=d.city,
                    )
                else:
                    p = parse_ad_particular(ad)
                    if p is None:
                        continue
                    author_key = f"prv:{p.author_id}"
                    if author_key in seen_authors:
                        continue
                    seen_authors.add(author_key)
                    owner = OwnerSample(
                        source="milanuncios",
                        kind="particular",
                        province_code=p.province_code,
                        city=p.city,
                    )

                result = classify_owner(owner, geo, fuzzy_index)
                stats.record(owner, result)

            print(f"    offset={offset}: {len(ads)} ads, owners so far={stats.total}")

    return stats


# ---------------------------------------------------------------------------
# Wallapop sampling
# ---------------------------------------------------------------------------

def _wp_search_params(keyword: str, lat: str, lon: str, next_page: str | None = None) -> dict:
    p: dict = {
        "keywords": keyword,
        "source": "deep_link",
        "category_id": WP_CATEGORY,
        "search_id": str(uuid.uuid4()),
        "latitude": lat,
        "longitude": lon,
        "order_by": "most_relevance",
        "section_type": "organic_search_results",
    }
    if next_page:
        p["next_page"] = next_page
    return p


async def sample_wallapop(
    geo: GeoResolver,
    fuzzy_index: dict[str, list[str]],
) -> ProbeStats:
    """Fetch a bounded sample from wallapop and classify owner geo."""
    stats = ProbeStats(source="wallapop")
    fetcher = WallapopFetcher(pool_size=1)
    gov = governor()
    gf = gov.wrap_fetch_text(fetcher.fetch_get)

    seen_item_ids: set[str] = set()
    # seller cache: user_id -> SellerRef|None (avoids duplicate user lookups)
    seller_cache: dict[str, object] = {}

    print("[WP] starting wallapop sample...")

    for lat, lon in WP_SAMPLE_GRID:
        for keyword in WP_SAMPLE_KEYWORDS:
            print(f"  [WP] keyword={keyword!r} centroid=({lat},{lon})...")
            next_page_token: str | None = None
            for page_idx in range(WP_MAX_PAGES_PER_QUERY):
                params = _wp_search_params(keyword, lat, lon, next_page_token)
                try:
                    await gov.acquire("api.wallapop.com")
                    slot = await fetcher._free.get()
                    try:
                        data = await asyncio.to_thread(
                            fetcher.fetch_get,
                            WP_SEARCH_ENDPOINT,
                            params=params,
                            slot=slot,
                        )
                    finally:
                        fetcher._free.put_nowait(slot)
                except Exception as exc:
                    print(f"  [WP] WARN kw={keyword!r} page={page_idx}: {exc}")
                    break

                # The wallapop API response changed: items moved from top-level
                # search_objects to data.section.items. Support both for resilience.
                search_objs = data.get("search_objects") or []
                if not search_objs:
                    section = (data.get("data") or {}).get("section") or {}
                    search_objs = section.get("items") or []
                meta = data.get("meta") or {}
                next_page_token = meta.get("next_page")

                if not search_objs:
                    break

                for item in search_objs:
                    item_id = str(item.get("id") or "")
                    if not item_id or item_id in seen_item_ids:
                        continue
                    seen_item_ids.add(item_id)

                    if str(item.get("category_id") or "") not in ("100", ""):
                        continue

                    v = parse_item_vehicle(item)
                    if not v.deep_link:
                        continue

                    user_id = str(item.get("user_id") or "")
                    if not user_id:
                        continue

                    # Fetch seller if not cached
                    if user_id not in seller_cache:
                        try:
                            await gov.acquire("api.wallapop.com")
                            slot = await fetcher._free.get()
                            try:
                                user_data = await asyncio.to_thread(
                                    fetcher.fetch_get,
                                    f"{WP_USER_ENDPOINT}/{user_id}",
                                    slot=slot,
                                )
                            finally:
                                fetcher._free.put_nowait(slot)
                            seller_cache[user_id] = parse_seller(user_id, user_data)
                        except Exception:
                            seller_cache[user_id] = None

                    seller = seller_cache[user_id]
                    if seller is None:
                        continue

                    # Derive province from seller zip -> item region -> item lat/lon path
                    prov = _prov_from_cp(seller.zip)
                    city: str | None = None

                    if prov:
                        # Seller's registered zip -> province; city = seller city or item city
                        city = seller.city or v.item_city
                    else:
                        # Try item region2 as province name
                        prov = geo.province_code(v.item_region)
                        if prov:
                            city = v.item_city or seller.city
                        else:
                            # Global city uniqueness path
                            gp, _gm = geo.resolve_city_global(v.item_city)
                            if gp:
                                prov = gp
                                city = v.item_city
                            # else prov stays None; LATLON or NO_GEO

                    kind = "compraventa" if seller.is_professional else "particular"
                    owner = OwnerSample(
                        source="wallapop",
                        kind=kind,
                        province_code=prov,
                        city=city,
                        lat=v.item_lat,
                        lon=v.item_lon,
                    )
                    result = classify_owner(owner, geo, fuzzy_index)
                    stats.record(owner, result)

                print(f"    page={page_idx} items={len(search_objs)} classified={stats.total} next={'yes' if next_page_token else 'no'}")
                if not next_page_token:
                    break

    return stats


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def pct(n: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{100 * n / total:.1f}%"


def build_report(mn: ProbeStats, wp: ProbeStats) -> str:
    combined_total = mn.total + wp.total
    combined_buckets: dict[str, int] = {b: mn.by_bucket[b] + wp.by_bucket[b] for b in BUCKETS}

    # % gap is total - EXACT (owners that currently lack municipality_code)
    mn_gap = mn.total - mn.by_bucket[EXACT]
    wp_gap = wp.total - wp.by_bucket[EXACT]
    comb_gap = combined_total - combined_buckets[EXACT]

    lines: list[str] = []
    lines.append("# B4_GEO_PROBE — Informe empírico de geocoding (B4.1)")
    lines.append("")
    lines.append(f"> Generado: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    lines.append(f"> Command: `PYTHONIOENCODING=utf-8 python scripts/recon/b4_geo_probe.py`")
    lines.append("")
    lines.append("## 1. Muestra recogida")
    lines.append("")
    lines.append(f"| Fuente | Owners únicos muestreados |")
    lines.append(f"|--------|--------------------------|")
    lines.append(f"| milanuncios | {mn.total} |")
    lines.append(f"| wallapop | {wp.total} |")
    lines.append(f"| **TOTAL** | **{combined_total}** |")
    lines.append("")
    lines.append("## 2. Tasas por bucket — milanuncios")
    lines.append("")
    lines.append(_bucket_table(mn))
    lines.append("")
    lines.append("### Gap milanuncios (owners sin municipio_code hoy)")
    lines.append("")
    if mn_gap > 0:
        lines.append(f"Del gap de {mn_gap} ({pct(mn_gap, mn.total)} del total MN):")
        lines.append(f"  - NO_CITY (muro de fuente): {mn.by_bucket[NO_CITY]} ({pct(mn.by_bucket[NO_CITY], mn_gap)} del gap)")
        lines.append(f"  - FUZZY_RECOVERABLE: {mn.by_bucket[FUZZY_RECOVERABLE]} ({pct(mn.by_bucket[FUZZY_RECOVERABLE], mn_gap)} del gap)")
        lines.append(f"  - LATLON_ONLY: {mn.by_bucket[LATLON_ONLY]} ({pct(mn.by_bucket[LATLON_ONLY], mn_gap)} del gap)")
        lines.append(f"  - NO_GEO: {mn.by_bucket[NO_GEO]} ({pct(mn.by_bucket[NO_GEO], mn_gap)} del gap)")
    lines.append("")
    lines.append("## 3. Tasas por bucket — wallapop")
    lines.append("")
    lines.append(_bucket_table(wp))
    lines.append("")
    lines.append("### Gap wallapop")
    lines.append("")
    if wp_gap > 0:
        lines.append(f"Del gap de {wp_gap} ({pct(wp_gap, wp.total)} del total WP):")
        lines.append(f"  - NO_CITY (muro de fuente): {wp.by_bucket[NO_CITY]} ({pct(wp.by_bucket[NO_CITY], wp_gap)} del gap)")
        lines.append(f"  - FUZZY_RECOVERABLE: {wp.by_bucket[FUZZY_RECOVERABLE]} ({pct(wp.by_bucket[FUZZY_RECOVERABLE], wp_gap)} del gap)")
        lines.append(f"  - LATLON_ONLY: {wp.by_bucket[LATLON_ONLY]} ({pct(wp.by_bucket[LATLON_ONLY], wp_gap)} del gap)")
        lines.append(f"  - NO_GEO: {wp.by_bucket[NO_GEO]} ({pct(wp.by_bucket[NO_GEO], wp_gap)} del gap)")
    lines.append("")
    lines.append("## 4. Tasas AGREGADAS (milanuncios + wallapop)")
    lines.append("")
    lines.append(_bucket_table_raw(combined_buckets, combined_total))
    lines.append("")
    lines.append(f"**Gap agregado** (sin municipio hoy): {comb_gap} ({pct(comb_gap, combined_total)})")
    if comb_gap > 0:
        lines.append(f"  - Recuperable por fuzzy: {combined_buckets[FUZZY_RECOVERABLE]} ({pct(combined_buckets[FUZZY_RECOVERABLE], comb_gap)} del gap)")
        lines.append(f"  - Muro de fuente (NO_CITY): {combined_buckets[NO_CITY]} ({pct(combined_buckets[NO_CITY], comb_gap)} del gap)")
        lines.append(f"  - Solo lat/lon: {combined_buckets[LATLON_ONLY]} ({pct(combined_buckets[LATLON_ONLY], comb_gap)} del gap)")
        lines.append(f"  - Sin nada (NO_GEO): {combined_buckets[NO_GEO]} ({pct(combined_buckets[NO_GEO], comb_gap)} del gap)")
    lines.append("")
    lines.append("## 5. Ejemplos FUZZY_RECOVERABLE (validación manual)")
    lines.append("")
    lines.append("Los siguientes `city_payload` fallaron el match exacto actual pero son capturados")
    lines.append("por rapidfuzz ≥88 dentro de la provincia. Confirman que el fuzzy NO inventa:")
    lines.append("")
    all_fuzzy = mn.fuzzy_examples + wp.fuzzy_examples
    if all_fuzzy:
        lines.append("| # | Fuente | Prov | city_payload (raw) | municipio_INE_key (fuzzy) | score |")
        lines.append("|---|--------|------|---------------------|--------------------------|-------|")
        for i, ex in enumerate(all_fuzzy[:30], 1):
            src = "MN" if i <= len(mn.fuzzy_examples) else "WP"
            lines.append(
                f"| {i} | {src} | {ex['province_code']} | {ex['city_payload']} "
                f"| {ex['muni_ine']} | {ex['score']} |"
            )
    else:
        lines.append("_(ningún ejemplo FUZZY_RECOVERABLE encontrado en la muestra)_")
    lines.append("")
    lines.append("## 6. Interpretación y decisión B4.2")
    lines.append("")
    lines.append("- **FUZZY_RECOVERABLE** = gap cerrable implementando B4.2 (GeoResolver fuzzy).")
    lines.append("- **NO_CITY** = muro real de fuente (city ausente en el payload). No se resuelve sin B4.4 (persistir locality crudo) + re-scrape o cambio de estrategia.")
    lines.append("- **LATLON_ONLY** = cerrable por B4.3 (reverse-geocode con centroides INE).")
    lines.append("- **NO_GEO** = residual duro: sin ciudad, sin coordenadas, sin CP. Suelo declarado.")
    lines.append("")
    lines.append("---")
    lines.append("_Probe standalone — cero escrituras a producción. Solo lectura de DB + fetch de muestra acotada._")
    return "\n".join(lines)


def _bucket_table(stats: ProbeStats) -> str:
    rows = []
    rows.append("| Bucket | Count | % total | % gap |")
    rows.append("|--------|-------|---------|-------|")
    gap = stats.total - stats.by_bucket[EXACT]
    for b in BUCKETS:
        n = stats.by_bucket[b]
        pct_total = pct(n, stats.total)
        pct_g = pct(n, gap) if b != EXACT else "—"
        rows.append(f"| {b} | {n} | {pct_total} | {pct_g} |")
    rows.append(f"| **TOTAL** | {stats.total} | 100% | — |")
    return "\n".join(rows)


def _bucket_table_raw(by_bucket: dict[str, int], total: int) -> str:
    gap = total - by_bucket.get(EXACT, 0)
    rows = []
    rows.append("| Bucket | Count | % total | % gap |")
    rows.append("|--------|-------|---------|-------|")
    for b in BUCKETS:
        n = by_bucket.get(b, 0)
        pct_total = pct(n, total)
        pct_g = pct(n, gap) if b != EXACT else "—"
        rows.append(f"| {b} | {n} | {pct_total} | {pct_g} |")
    rows.append(f"| **TOTAL** | {total} | 100% | — |")
    return "\n".join(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    print("=" * 60)
    print("B4.1 — Geo probe (read-only, no DB writes)")
    print("=" * 60)
    print(f"DSN: {DSN}")
    print(f"rapidfuzz threshold: {FUZZY_THRESHOLD}")
    print()

    # Connect to cardeep-pg and load the GeoResolver
    print("[DB] connecting to cardeep-pg...")
    conn: asyncpg.Connection = await asyncpg.connect(DSN)
    try:
        print("[DB] loading GeoResolver...")
        geo = await GeoResolver.load(conn)
        print(f"[DB] loaded {sum(len(v) for v in geo._muni.values())} muni keys across {len(geo._muni)} provinces")
    finally:
        await conn.close()

    # Build fuzzy index from the GeoResolver internals
    print("[FUZZY] building province-indexed fuzzy candidates...")
    fuzzy_index = build_fuzzy_index(geo)
    total_candidates = sum(len(v) for v in fuzzy_index.values())
    print(f"[FUZZY] {total_candidates} candidates across {len(fuzzy_index)} provinces")
    print()

    # Sample milanuncios
    mn_stats: ProbeStats | None = None
    try:
        mn_stats = await sample_milanuncios(geo, fuzzy_index)
        print(f"\n[MN] done: {mn_stats.total} owners, buckets: {mn_stats.by_bucket}")
    except Exception as exc:
        print(f"\n[MN] ERROR: {exc} — continuing with wallapop only")
        mn_stats = ProbeStats(source="milanuncios")

    print()

    # Sample wallapop
    wp_stats: ProbeStats | None = None
    try:
        wp_stats = await sample_wallapop(geo, fuzzy_index)
        print(f"\n[WP] done: {wp_stats.total} owners, buckets: {wp_stats.by_bucket}")
    except Exception as exc:
        print(f"\n[WP] ERROR: {exc} — continuing without wallapop")
        wp_stats = ProbeStats(source="wallapop")

    print()

    # Generate and persist report
    report_md = build_report(mn_stats, wp_stats)
    report_path = os.path.join(_REPO_ROOT, "docs", "recon", "B4_GEO_PROBE.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(report_md)
    print(f"[REPORT] written to {report_path}")
    print()

    # Print summary to stdout
    print("=" * 60)
    print("RESUMEN EJECUTIVO")
    print("=" * 60)
    combined_total = mn_stats.total + wp_stats.total
    combined_buckets = {b: mn_stats.by_bucket[b] + wp_stats.by_bucket[b] for b in BUCKETS}
    comb_gap = combined_total - combined_buckets[EXACT]
    print(f"Total owners muestreados: {combined_total} (MN={mn_stats.total}, WP={wp_stats.total})")
    print()
    for b in BUCKETS:
        n = combined_buckets[b]
        print(f"  {b:22s}: {n:5d}  ({pct(n, combined_total)} total, {pct(n, comb_gap) if b != EXACT else '—':>7} del gap)")
    print()
    print(f"Gap total (sin municipio hoy): {comb_gap} ({pct(comb_gap, combined_total)})")
    if comb_gap > 0:
        fr = combined_buckets[FUZZY_RECOVERABLE]
        nc = combined_buckets[NO_CITY]
        print(f"  → Recuperable por fuzzy B4.2: {fr} ({pct(fr, comb_gap)} del gap)")
        print(f"  → Muro de fuente (NO_CITY):   {nc} ({pct(nc, comb_gap)} del gap)")
    print()
    print(f"Ejemplos FUZZY_RECOVERABLE: {len(mn_stats.fuzzy_examples + wp_stats.fuzzy_examples)}")
    if mn_stats.fuzzy_examples or wp_stats.fuzzy_examples:
        print("  (primeros 10 — ver B4_GEO_PROBE.md para la lista completa)")
        for ex in (mn_stats.fuzzy_examples + wp_stats.fuzzy_examples)[:10]:
            print(f"    '{ex['city_payload']}' → '{ex['muni_ine']}' (score={ex['score']}, prov={ex['province_code']})")


if __name__ == "__main__":
    asyncio.run(main())

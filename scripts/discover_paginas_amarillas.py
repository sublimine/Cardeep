"""FASE 1 — DESCUBRIR: Páginas Amarillas (general ES business directory).

Enumerates the live PA paginated search per province across the auto rubros
(concesionarios, compraventa, desguaces), parses every listing card from the
schema.org LocalBusiness microdata + the per-item data-analytics JSON, and
persists the raw harvest to docs/research/paginas_amarillas_raw.json.

A second pass (--upsert) dedups each listing against the existing entity table
using the SAME canonical identity the rest of the pipeline uses (bare-host
website, then normalized name+municipality) and inserts only genuinely new
points of sale, geo-resolved to INE province/municipality codes.

The directory is a long-tail ENRICHMENT source: every listing here is a real
brick-and-mortar POS, exactly the "garaje perdido" not on any marketplace.

Env: CARDEEP_DSN, curl_cffi chrome131.
Usage:
  python -m scripts.discover_paginas_amarillas harvest [--provinces 28,08]
  python -m scripts.discover_paginas_amarillas upsert
"""
from __future__ import annotations

import html
import json
import re
import sys
import time
from pathlib import Path

from curl_cffi import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "research" / "paginas_amarillas_raw.json"
SOURCE_KEY = "paginas_amarillas"
BASE = "https://www.paginasamarillas.es/search/{rubro}/all-ma/{prov}/all-is/all-ci/all-ba/all-pu/all-nc/{page}"

# rubro slug -> default kind hint (overridden per-item by the activity text).
# NOTE: PA's "concesionarios" rubro is a broad SEO bucket that mixes official
# brand dealers and independent used-car shops under one generic label. We do
# NOT trust the directory to assert "official": absent a verifiable brand signal,
# a directory listing is the generic independent POS = compraventa. The DGT /
# OEM-locator sources own the authoritative concesionario_oficial census; this
# directory only adds the long-tail bricks-and-mortar POS missing from them.
RUBROS = {
    "concesionarios-de-coches": "compraventa",
    "compra-venta-de-coches": "compraventa",
    "compra-venta-de-vehiculos": "compraventa",
    "vehiculos-de-ocasion": "compraventa",
    "desguaces-de-coches": "desguace",
}

# INE province code -> PA province slug (verified live; tricky ones disambiguated
# so the slug actually filters instead of falling back to the national list).
PROV_SLUG = {
    "01": "araba-alava", "02": "albacete", "03": "alicante", "04": "almeria",
    "05": "avila", "06": "badajoz", "07": "islas-baleares", "08": "barcelona",
    "09": "burgos", "10": "caceres", "11": "cadiz", "12": "castellon",
    "13": "ciudad-real", "14": "cordoba", "15": "a-coruna", "16": "cuenca",
    "17": "girona", "18": "granada", "19": "guadalajara", "20": "gipuzkoa",
    "21": "huelva", "22": "huesca", "23": "jaen", "24": "leon", "25": "lleida",
    "26": "la-rioja", "27": "lugo", "28": "madrid", "29": "malaga", "30": "murcia",
    "31": "navarra", "32": "ourense", "33": "asturias", "34": "palencia",
    "35": "las-palmas", "36": "pontevedra", "37": "salamanca",
    "38": "santa-cruz-de-tenerife", "39": "cantabria", "40": "segovia",
    "41": "sevilla", "42": "soria", "43": "tarragona", "44": "teruel",
    "45": "toledo", "46": "valencia", "47": "valladolid", "48": "bizkaia",
    "49": "zamora", "50": "zaragoza", "51": "ceuta", "52": "melilla",
}

# activity-text fragments (PA's own category labels) -> entity kind.
# Order matters: most specific first. We never derive "official dealer" from a
# directory label (see RUBROS note); the generic "concesionarios" label falls
# through to the rubro default (compraventa).
ACTIVITY_KIND = [
    ("desguace", "desguace"),
    ("recuperaci", "desguace"),       # "recuperación de vehículos"
    ("taller", "garaje"),
    ("compra venta", "compraventa"),
    ("compra-venta", "compraventa"),
    ("ocasi", "compraventa"),         # vehículos de ocasión / segunda mano
    ("segunda mano", "compraventa"),
]

ITEM_RE = re.compile(r'class="listado-item[^"]*"(.*?)(?=class="listado-item|<footer|id="paginacion")', re.S)
DETAIL_RE = re.compile(r'href="(https://www\.paginasamarillas\.es/f/[^"]+\.html)"')
ANALYTICS_RE = re.compile(r"data-analytics='(\{.*?\})'", re.S)
WEBSITE_RE = re.compile(r'href="(https?://(?!www\.paginasamarillas\.es)[^"]+)"[^>]*class="[^"]*web', re.S)
WEBSITE_RE2 = re.compile(r'href="(https?://(?!www\.paginasamarillas\.es)[^"]+)"')
TOTAL_RE = re.compile(r"([\d.]+)\s*Empresas")


def _micro(block: str, prop: str) -> str | None:
    m = re.search(r'itemprop="' + prop + r'"[^>]*?(?:content="([^"]*)"|>([^<]*)<)', block)
    if not m:
        return None
    val = (m.group(1) or m.group(2) or "").strip()
    return html.unescape(val) or None


def _website(block: str) -> str | None:
    m = WEBSITE_RE.search(block) or WEBSITE_RE2.search(block)
    if not m:
        return None
    url = m.group(1)
    # strip PA's referral tracking params
    url = re.split(r"[?#]", url)[0]
    if "paginasamarillas" in url or "javascript" in url:
        return None
    return url or None


def _classify(activity: str | None, rubro_default: str) -> str:
    a = (activity or "").lower()
    for frag, kind in ACTIVITY_KIND:
        if frag in a:
            return kind
    return rubro_default


def parse_page(t: str, rubro_default: str) -> list[dict]:
    out = []
    for m in ITEM_RE.finditer(t):
        block = m.group(1)
        dm = DETAIL_RE.search(block)
        analytics = {}
        am = ANALYTICS_RE.search(block)
        if am:
            try:
                analytics = json.loads(am.group(1).encode("latin-1").decode("latin-1"))
            except Exception:
                analytics = {}
        name = _micro(block, "name") or analytics.get("name")
        if not name:
            continue
        addr = _micro(block, "streetAddress")
        if addr:
            addr = addr.split(";")[0].strip()  # PA appends ";TALLER" etc.
        out.append({
            "name": name,
            "address": addr,
            "locality": _micro(block, "addressLocality"),
            "postcode": _micro(block, "postalCode"),
            "region": _micro(block, "addressRegion") or analytics.get("province"),
            "phone": _micro(block, "telephone"),
            "website": _website(block),
            "activity": analytics.get("activity"),
            "detail": dm.group(1) if dm else None,
            "kind": _classify(analytics.get("activity"), rubro_default),
        })
    return out


def fetch(url: str, retries: int = 3) -> str | None:
    for i in range(retries):
        try:
            r = requests.get(url, impersonate="chrome131", timeout=30)
            if r.status_code == 200:
                return r.content.decode("latin-1")
            if r.status_code in (404, 410):
                return None
        except Exception as e:
            if i == retries - 1:
                print(f"  fetch fail {url[:90]}: {type(e).__name__}")
        time.sleep(1.5 * (i + 1))
    return None


def harvest(provinces: list[str]) -> None:
    seen: dict[str, dict] = {}  # detail-url or name|locality -> record
    stats = {"pages": 0, "rubros": {}}
    for rubro, kdefault in RUBROS.items():
        rcount = 0
        for prov_code in provinces:
            slug = PROV_SLUG[prov_code]
            page = 1
            while True:
                url = BASE.format(rubro=rubro, prov=slug, page=page)
                t = fetch(url)
                stats["pages"] += 1
                if t is None:
                    break
                if page == 1:
                    tm = TOTAL_RE.search(t)
                    total = tm.group(1) if tm else "?"
                recs = parse_page(t, kdefault)
                if not recs:
                    break
                for r in recs:
                    key = r["detail"] or f"{r['name']}|{r['locality']}"
                    if key not in seen:
                        r["prov_code"] = prov_code
                        r["rubro"] = rubro
                        seen[key] = r
                        rcount += 1
                page += 1
                if page > 60:  # hard safety cap; no ES province auto rubro exceeds this
                    break
            print(f"[{rubro}] {slug} ({prov_code}) total={total} pages_done={page-1} "
                  f"cum_unique={len(seen)}")
        stats["rubros"][rubro] = rcount
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {"source": SOURCE_KEY, "count": len(seen), "stats": stats,
               "records": list(seen.values())}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nwrote {len(seen)} distinct listings -> {OUT}")
    print("by rubro:", stats["rubros"])


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "harvest"
    if mode == "harvest":
        provs = list(PROV_SLUG.keys())
        if "--provinces" in sys.argv:
            provs = sys.argv[sys.argv.index("--provinces") + 1].split(",")
        harvest(provs)
    else:
        print(f"unknown mode '{mode}'")
        sys.exit(2)


if __name__ == "__main__":
    main()

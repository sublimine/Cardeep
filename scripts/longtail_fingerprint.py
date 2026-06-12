"""Long-tail CMS/DMS family fingerprinter for Cardeep own-site dealers.

Reads the distinct own-site domain list (docs/_longtail_probe_list.json), fetches
each homepage with a Chrome TLS fingerprint (curl_cffi, no proxy/browser), and
CLASSIFIES it by the website PLATFORM family — the CMS (WordPress + automotive
plugin), a Spanish DMS/dealer-site vendor (Motorflash, Tecnom/Quintegia, Sumauto,
Wikicoches, ...), a generic site builder (Wix, Squarespace, Webflow, Shopify), or
generic/custom. The family is the harvest multiplier: ONE recipe per family drains
many dealers, because dealers on the same platform expose inventory the same way.

Output: docs/_longtail_fingerprints.json (one record per domain, with the matched
family, the evidence signals, and any inventory-listing path candidates seen).

This is read-only market research over PUBLIC homepages. No DB writes here.

Run: python scripts/longtail_fingerprint.py
"""
from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path

from curl_cffi import requests as cffi_requests

ROOT = Path(__file__).resolve().parent.parent
PROBE_LIST = ROOT / "docs" / "_longtail_probe_list.json"
OUT = ROOT / "docs" / "_longtail_fingerprints.json"

_IMPERSONATE = "chrome131"
_TIMEOUT = 25
_CONCURRENCY = 20

# ---------------------------------------------------------------------------
# Family signatures. Each family is a set of regexes/substrings tested against
# the lowercased homepage HTML (and, where noted, response headers). Ordered:
# the FIRST family that matches wins for the primary label, but ALL matches are
# recorded so multi-signal sites (e.g. WordPress + Motorflash iframe) are visible.
# Signatures are intentionally specific to avoid false positives.
# ---------------------------------------------------------------------------

# Known Spanish automotive DMS / dealer-website vendors (the real multiplier).
# Each maps a vendor to the host/asset fingerprints its sites embed.
DMS_VENDORS = {
    # Motorflash: huge ES dealer-stock vendor; stock embedded via motorflash widgets/iframes.
    "motorflash": [r"motorflash", r"mf-widget", r"motorflash\.com"],
    # Sumauto / Hexagon (coches.net group white-label dealer sites).
    "sumauto": [r"sumauto", r"hexagoncuratedcars"],
    # Wikicoches / Wide dealer-site builder.
    "wikicoches": [r"wikicoches"],
    # Tecnom (DMS, often Quintegia ecosystem) dealer sites.
    "tecnom": [r"tecnom", r"\.tecnom\."],
    # Quintegia / DealerBest dealer-site platform.
    "quintegia": [r"quintegia", r"dealerbest"],
    # Ridemovi / Ridecar stock widgets.
    "ridecar": [r"ridecar", r"ridemovi"],
    # Reefer/Retail vendors and generic "stock" iframes from known hosts.
    "automanager": [r"automanager", r"carsales-cdn"],
    # Cardoo / Carsync / Stockspark (Infomedia) embedded stock.
    "stockspark": [r"stockspark", r"infomedia"],
    # Pixelware / Tot-Net automotive.
    "totnet": [r"tot-net", r"totnet"],
    # GestionMax / Cymed automotive DMS.
    "gestionmax": [r"gestionmax", r"cymed"],
    # Epyme / Audatex stock feeds.
    "audatex": [r"audatex"],
    # Coches.com / Cargest white-label.
    "cargest": [r"cargest"],
    # Wayboo / Wayni automotive sites.
    "wayboo": [r"wayboo"],
}

# Generic site builders / SaaS website platforms.
BUILDERS = {
    "wix": [r"wix\.com", r"_wixcssistemplate", r"static\.parastorage\.com", r"x-wix-"],
    "squarespace": [r"squarespace", r"static1\.squarespace\.com"],
    "webflow": [r"webflow", r"assets\.website-files\.com", r"\.webflow\.io"],
    "shopify": [r"cdn\.shopify\.com", r"shopify"],
    "godaddy_websites": [r"img1\.wsimg\.com", r"websitebuilder"],
    "jimdo": [r"jimdo", r"jimstatic"],
    "weebly": [r"weebly", r"editmysite"],
    "duda": [r"\.dudamobile\.com", r"dudaone", r"irp\.cdn-website\.com"],
}

# CMS engines.
CMS = {
    "wordpress": [r"wp-content", r"wp-includes", r"wp-json"],
    "joomla": [r"/components/com_", r"joomla", r"/media/jui/"],
    "drupal": [r"sites/default/files", r"drupal-settings-json", r"drupal\.js"],
    "prestashop": [r"prestashop", r"/themes/[^/]+/assets"],
}

# WordPress automotive plugins (secondary signal — tells us the LISTING recipe seed).
WP_AUTO_PLUGINS = {
    "motors_plugin": [r"stm_motors", r"motors-", r"plugins/motors"],
    "car_dealer_wp": [r"car-dealer", r"wpcardealer", r"vehicle-listings"],
    "wp_auto_listing": [r"automotive-", r"wp-cars", r"car-listing"],
}

# Inventory-listing URL hints to look for in homepage anchors (recipe seed).
INVENTORY_HINTS = [
    "vehiculos", "vehicles", "coches", "stock", "ocasion", "ocasió", "seminuevos",
    "segunda-mano", "kilometro-0", "km0", "vo", "nuestro-stock", "inventory",
    "vehiculos-ocasion", "coches-ocasion", "catalogo",
]


def _match_any(patterns, hay) -> list[str]:
    hits = []
    for p in patterns:
        if re.search(p, hay):
            hits.append(p)
    return hits


def classify(html: str, headers: dict) -> dict:
    """Return {family, subfamily, signals[], inventory_paths[]} for one homepage."""
    h = html.lower()
    hdr = " ".join(f"{k}:{v}".lower() for k, v in (headers or {}).items())
    signals = []

    # generator meta (strong CMS hint)
    gen = None
    m = re.search(r'<meta[^>]+name=["\']generator["\'][^>]*content=["\']([^"\']+)["\']', h)
    if m:
        gen = m.group(1).strip()
        signals.append(f"generator:{gen[:40]}")

    matched = {}  # family -> list of evidence

    # 1) DMS vendors (highest value — the multiplier families)
    for vendor, pats in DMS_VENDORS.items():
        hits = _match_any(pats, h) or _match_any(pats, hdr)
        if hits:
            matched.setdefault("dms", []).append((vendor, hits))

    # 2) site builders
    for b, pats in BUILDERS.items():
        hits = _match_any(pats, h) or _match_any(pats, hdr)
        if hits:
            matched.setdefault("builder", []).append((b, hits))

    # 3) CMS
    for c, pats in CMS.items():
        hits = _match_any(pats, h)
        if hits:
            matched.setdefault("cms", []).append((c, hits))

    # 4) WP automotive plugins (only meaningful if WP present)
    wp_plugins = []
    if any(c == "wordpress" for c, _ in matched.get("cms", [])):
        for pl, pats in WP_AUTO_PLUGINS.items():
            hits = _match_any(pats, h)
            if hits:
                wp_plugins.append(pl)

    # inventory listing path candidates from homepage anchors
    inv_paths = []
    for a in re.findall(r'href=["\']([^"\']+)["\']', h):
        al = a.lower()
        for hint in INVENTORY_HINTS:
            if hint in al and not al.startswith("http") or (hint in al and "://" in al):
                # keep relative or same-site listing paths
                inv_paths.append(a)
                break
    # dedup, cap
    seen = set()
    inv_paths = [p for p in inv_paths if not (p in seen or seen.add(p))][:8]

    # Decide PRIMARY family with precedence: DMS vendor > builder > CMS > generic.
    if "dms" in matched:
        vendor, ev = matched["dms"][0]
        family, sub = "dms", vendor
    elif "builder" in matched:
        b, ev = matched["builder"][0]
        family, sub = "builder", b
    elif "cms" in matched:
        c, ev = matched["cms"][0]
        family, sub = "cms", c
        if c == "wordpress" and wp_plugins:
            sub = "wordpress+" + "+".join(wp_plugins)
    else:
        family, sub = "generic", (gen.split()[0].lower() if gen else "custom")

    for grp, items in matched.items():
        for name, ev in items:
            signals.append(f"{grp}:{name}({len(ev)})")
    if wp_plugins:
        signals.append("wp_plugins:" + ",".join(wp_plugins))

    return {
        "family": family,
        "subfamily": sub,
        "generator": gen,
        "signals": signals,
        "wp_plugins": wp_plugins,
        "inventory_paths": inv_paths,
        "all_matches": {k: [n for n, _ in v] for k, v in matched.items()},
    }


def fetch(domain: str, website: str) -> dict:
    """Fetch a homepage; try the recorded website first, then https://domain."""
    candidates = []
    w = (website or "").strip()
    if w:
        if not w.startswith("http"):
            w = "https://" + w
        candidates.append(w)
    candidates.append(f"https://www.{domain}")
    candidates.append(f"https://{domain}")
    last_err = None
    for url in candidates:
        try:
            resp = cffi_requests.get(url, impersonate=_IMPERSONATE, timeout=_TIMEOUT,
                                     allow_redirects=True)
            if resp.status_code == 200 and resp.text:
                return {"ok": True, "url": url, "final_url": str(resp.url),
                        "status": resp.status_code, "html": resp.text,
                        "headers": dict(resp.headers)}
            last_err = f"HTTP {resp.status_code}"
        except Exception as e:  # noqa: BLE001 — any transport error -> try next candidate
            last_err = type(e).__name__ + ": " + str(e)[:80]
    return {"ok": False, "error": last_err}


async def probe_one(sem: asyncio.Semaphore, rec: dict) -> dict:
    async with sem:
        res = await asyncio.to_thread(fetch, rec["domain"], rec.get("website"))
    out = {"domain": rec["domain"], "name": rec.get("name"),
           "website": rec.get("website")}
    if not res.get("ok"):
        out.update({"reachable": False, "error": res.get("error"),
                    "family": "unreachable", "subfamily": None})
        return out
    cls = classify(res["html"], res.get("headers", {}))
    out.update({"reachable": True, "final_url": res.get("final_url"),
                "html_len": len(res["html"]), **cls})
    return out


async def main() -> None:
    records = json.loads(PROBE_LIST.read_text(encoding="utf-8"))
    print(f"[fingerprint] probing {len(records)} distinct own-site domains "
          f"(concurrency={_CONCURRENCY})")
    sem = asyncio.Semaphore(_CONCURRENCY)
    results = []
    done = 0
    tasks = [probe_one(sem, r) for r in records]
    for fut in asyncio.as_completed(tasks):
        r = await fut
        results.append(r)
        done += 1
        if done % 25 == 0:
            print(f"[fingerprint] {done}/{len(records)} probed")
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[fingerprint] wrote {OUT} ({len(results)} records)")


if __name__ == "__main__":
    asyncio.run(main())

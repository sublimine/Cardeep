"""Refinement pass over the long-tail fingerprints.

Two jobs the first pass left open:
  1) RE-PROBE the unreachable domains with verify=False + a real browser header
     set, to recover the 403 / CertificateVerifyError / SSLError / timeout sites
     (a 26% gap that would bias the family map if left as "unreachable").
  2) RE-CLASSIFY every reachable homepage with the EXPANDED signature set that
     the first pass discovered empirically — most importantly inventario.pro
     (a confirmed ES dealer-stock vendor whose sites share the /coches/<make>/<id>
     template) plus ueni, and framework labels (next.js/astro/nuxt) for the
     "generic" bucket so the head of the long tail is named, not lumped.

Reads docs/_longtail_fingerprints.json + docs/_longtail_probe_list.json, writes
docs/_longtail_fingerprints.json in place (refined) and prints the new ranking.
Read-only over public homepages; no DB writes.

Run: python scripts/longtail_refine.py
"""
from __future__ import annotations

import asyncio
import json
import re
from collections import Counter
from pathlib import Path

from curl_cffi import requests as cffi_requests

ROOT = Path(__file__).resolve().parent.parent
FP = ROOT / "docs" / "_longtail_fingerprints.json"
PROBE = ROOT / "docs" / "_longtail_probe_list.json"

_IMPERSONATE = "chrome131"
_TIMEOUT = 25
_CONCURRENCY = 16

_BROWSER_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
              "image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

# Expanded DMS vendors (inventario.pro is the empirically-confirmed new family).
DMS_VENDORS = {
    "inventario_pro": [r"inventario\.pro"],
    "motorflash": [r"motorflash", r"mf-widget"],
    "sumauto": [r"sumauto", r"hexagoncuratedcars"],
    "wikicoches": [r"wikicoches"],
    "tecnom": [r"\btecnom\b"],
    "quintegia": [r"quintegia", r"dealerbest"],
    "ridecar": [r"ridecar", r"ridemovi"],
    "automanager": [r"automanager", r"carsales-cdn"],
    "stockspark": [r"stockspark"],
    "cargest": [r"cargest"],
    "wayboo": [r"wayboo"],
}

BUILDERS = {
    "wix": [r"wix\.com", r"static\.parastorage\.com", r"x-wix-"],
    "squarespace": [r"squarespace", r"static1\.squarespace\.com"],
    "webflow": [r"\.webflow\.io", r"assets\.website-files\.com"],
    "shopify": [r"cdn\.shopify\.com"],
    "godaddy_websites": [r"img1\.wsimg\.com"],
    "jimdo": [r"jimdo", r"jimstatic"],
    "weebly": [r"weebly", r"editmysite"],
    "duda": [r"\.dudamobile\.com", r"irp\.cdn-website\.com"],
    "ueni": [r"ueni", r"ueniweb"],
    "basekit": [r"basekit"],
}

CMS = {
    "wordpress": [r"wp-content", r"wp-includes", r"wp-json"],
    "joomla": [r"/components/com_", r"/media/jui/"],
    "drupal": [r"sites/default/files", r"drupal-settings-json"],
    "prestashop": [r"prestashop", r"/themes/[^/]+/assets"],
}

# JS frameworks — turns "generic/custom" into a named (probably custom-DMS) bucket.
FRAMEWORKS = {
    "nextjs": [r"__next_data__", r"/_next/static"],
    "nuxt": [r"__nuxt__", r"/_nuxt/"],
    "astro": [r"astro-island", r"data-astro"],
    "angular": [r"ng-version"],
}

WP_AUTO_PLUGINS = {
    "motors_plugin": [r"stm_motors", r"plugins/motors"],
    "car_dealer_wp": [r"car-dealer", r"wpcardealer"],
    "wp_auto_listing": [r"automotive-", r"wp-cars", r"car-listing"],
}

INVENTORY_HINTS = ["vehiculos", "vehicles", "coches", "stock", "ocasion", "seminuevos",
                   "segunda-mano", "km0", "kilometro-0", "inventario", "catalogo"]


def _hits(pats, hay):
    return [p for p in pats if re.search(p, hay)]


def classify(html: str, headers: dict) -> dict:
    h = html.lower()
    hdr = " ".join(f"{k}:{v}".lower() for k, v in (headers or {}).items())
    signals = []
    gen = None
    m = re.search(r'<meta[^>]+name=["\']generator["\'][^>]*content=["\']([^"\']+)["\']', h)
    if m:
        gen = m.group(1).strip()

    matched = {}
    for v, p in DMS_VENDORS.items():
        if _hits(p, h) or _hits(p, hdr):
            matched.setdefault("dms", []).append(v)
    for b, p in BUILDERS.items():
        if _hits(p, h) or _hits(p, hdr):
            matched.setdefault("builder", []).append(b)
    for c, p in CMS.items():
        if _hits(p, h):
            matched.setdefault("cms", []).append(c)
    for fw, p in FRAMEWORKS.items():
        if _hits(p, h):
            matched.setdefault("framework", []).append(fw)

    wp_plugins = []
    if "wordpress" in matched.get("cms", []):
        for pl, p in WP_AUTO_PLUGINS.items():
            if _hits(p, h):
                wp_plugins.append(pl)

    inv = []
    for a in re.findall(r'href=["\']([^"\']+)["\']', h):
        al = a.lower()
        if any(hint in al for hint in INVENTORY_HINTS):
            inv.append(a)
    seen = set()
    inv = [x for x in inv if not (x in seen or seen.add(x))][:8]

    # precedence: DMS vendor > builder > CMS > framework > generic
    if "dms" in matched:
        family, sub = "dms", matched["dms"][0]
    elif "builder" in matched:
        family, sub = "builder", matched["builder"][0]
    elif "cms" in matched:
        sub = matched["cms"][0]
        if sub == "wordpress" and wp_plugins:
            sub = "wordpress+" + "+".join(wp_plugins)
        family = "cms"
    elif "framework" in matched:
        family, sub = "framework", matched["framework"][0]
    else:
        family, sub = "generic", (gen.split()[0].lower() if gen else "custom")

    for grp, names in matched.items():
        signals.append(f"{grp}:{','.join(names)}")
    if gen:
        signals.append(f"generator:{gen[:40]}")

    return {"family": family, "subfamily": sub, "generator": gen, "signals": signals,
            "wp_plugins": wp_plugins, "inventory_paths": inv,
            "all_matches": {k: v for k, v in matched.items()}}


def fetch(domain: str, website: str) -> dict:
    cands = []
    w = (website or "").strip()
    if w:
        if not w.startswith("http"):
            w = "https://" + w
        cands.append(w)
    cands += [f"https://www.{domain}", f"https://{domain}", f"http://www.{domain}"]
    last = None
    for url in cands:
        try:
            resp = cffi_requests.get(url, impersonate=_IMPERSONATE, timeout=_TIMEOUT,
                                     headers=_BROWSER_HEADERS, allow_redirects=True,
                                     verify=False)
            if resp.status_code == 200 and resp.text:
                return {"ok": True, "final_url": str(resp.url), "html": resp.text,
                        "headers": dict(resp.headers)}
            last = f"HTTP {resp.status_code}"
        except Exception as e:  # noqa: BLE001
            last = type(e).__name__
    return {"ok": False, "error": last}


async def reprobe(sem, rec):
    async with sem:
        res = await asyncio.to_thread(fetch, rec["domain"], rec.get("website"))
    out = {"domain": rec["domain"], "name": rec.get("name"), "website": rec.get("website")}
    if not res.get("ok"):
        out.update({"reachable": False, "error": res.get("error"),
                    "family": "unreachable", "subfamily": None})
        return out
    out.update({"reachable": True, "final_url": res.get("final_url"),
                "html_len": len(res["html"]), **classify(res["html"], res.get("headers", {}))})
    return out


async def main():
    recs = json.loads(FP.read_text(encoding="utf-8"))
    probe = {r["domain"]: r for r in json.loads(PROBE.read_text(encoding="utf-8"))}
    by_dom = {r["domain"]: r for r in recs}

    # 1) re-probe unreachables with verify=False + browser headers
    unreachable = [probe[d] for d, r in by_dom.items()
                   if not r.get("reachable") and d in probe]
    print(f"[refine] re-probing {len(unreachable)} unreachable domains (verify=off)")
    sem = asyncio.Semaphore(_CONCURRENCY)
    recovered = 0
    for fut in asyncio.as_completed([reprobe(sem, r) for r in unreachable]):
        r = await fut
        by_dom[r["domain"]] = r
        if r.get("reachable"):
            recovered += 1
    print(f"[refine] recovered {recovered}/{len(unreachable)} previously-unreachable")

    # 2) re-classify the ALREADY-reachable ones with the expanded signatures by
    #    refetching them (cheap, and guarantees inventario.pro/ueni/framework hits).
    reach = [probe[d] for d, r in by_dom.items()
             if r.get("reachable") and d in probe and r.get("subfamily")
             in ("custom", "wordpress") or (r.get("family") in ("generic", "cms")
             and d in probe and r.get("reachable"))]
    # simpler: re-classify ALL currently-reachable with expanded set
    reach = [probe[d] for d, r in by_dom.items() if r.get("reachable") and d in probe]
    print(f"[refine] re-classifying {len(reach)} reachable domains (expanded signatures)")
    for fut in asyncio.as_completed([reprobe(sem, r) for r in reach]):
        r = await fut
        if r.get("reachable"):
            by_dom[r["domain"]] = r

    out = list(by_dom.values())
    FP.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    fam = Counter(r.get("family") for r in out)
    sub = Counter(f"{r.get('family')}/{r.get('subfamily')}" for r in out)
    print("\n--- REFINED family ranking ---")
    for f, c in fam.most_common():
        print(f"  {c:5}  {f}")
    print("\n--- REFINED subfamily ranking (top 25) ---")
    for s, c in sub.most_common(25):
        print(f"  {c:5}  {s}")


if __name__ == "__main__":
    asyncio.run(main())

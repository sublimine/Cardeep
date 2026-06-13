"""Geographic sweep — candidate collector + dedup + own-site probe + upsert.

FRONT discover_geographic: find the "garaje perdido" — small local car-selling
businesses (concesionario, compraventa, venta de coches ocasion, desguace) that
are NOT on the big marketplaces and NOT yet in the entity census, by harvesting
the own-site domains surfaced through per-province web/places search.

Pipeline per candidate domain:
  1. dedup against the live DB (bare host, then normalized name+municipality),
  2. probe the own-site (curl_cffi chrome131) for reachability + a parseable
     vehicle-listing surface (price tokens / detail anchors),
  3. resolve geo to INE province/municipality,
  4. upsert entity (correct kind) + entity_source idempotently,
  5. record whether the own-site is harvestable (>= price-token threshold).

Read-only web research; the only writes are entity/entity_source upserts gated
on genuine novelty. Every count is later re-derived from the DB itself (VAM).
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

import asyncpg
from curl_cffi import requests as cffi_requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.geo import GeoResolver  # noqa: E402
from pipeline.ids import ulid  # noqa: E402
from services.api.codes import cdp_code  # noqa: E402

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "docs" / "research" / "geographic"
SOURCE_KEY = "geo_sweep"
IMPERSONATE = "chrome131"
TIMEOUT = 25
MIN_PRICE_TOKENS = 3  # harvestable own-site threshold

# Ranked inventory-listing slugs (reused from probe_generic_custom — the bespoke
# long-tail converges on these). First 200 with >=3 price tokens => harvestable.
SLUGS = [
    "/coches", "/vehiculos", "/coches-ocasion", "/vehiculos-ocasion",
    "/ocasion", "/stock", "/catalogo", "/seminuevos", "/km0",
    "/coches-segunda-mano", "/nuestro-stock", "/vehiculos-de-ocasion",
    "/inventario", "/listado", "/turismos", "/coches-de-ocasion",
    "/vo", "/segunda-mano", "/coches/usados/", "/usados",
]
PRICE_RE = re.compile(r"\d[\d.\s]{2,}\s*(?:€|&euro;|EUR)", re.I)
EURO_NUM_RE = re.compile(r"(\d{1,3}(?:[.\s]\d{3})+)\s*(?:€|&euro;)")


def _norm(t: str | None) -> str:
    if not t:
        return ""
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", t.lower())


def _host(w: str | None) -> str:
    if not w:
        return ""
    w = w.lower().strip()
    w = re.sub(r"^https?://", "", w)
    w = re.sub(r"^www\.", "", w)
    return w.split("/")[0].split("?")[0].split("#")[0].rstrip(".")


def _sniff(html: str) -> dict:
    prices = PRICE_RE.findall(html)
    euro_nums = EURO_NUM_RE.findall(html)
    return {
        "html_len": len(html),
        "price_tokens": len(prices),
        "euro_thousands": len(euro_nums),
    }


def probe_site(domain: str) -> dict:
    """Reachability + best listing surface for an own-site. Pure read."""
    sess = cffi_requests.Session(impersonate=IMPERSONATE)
    out = {"domain": domain, "reachable": False, "harvestable": False,
           "best_price_tokens": 0, "best_slug": None, "final_home": None}
    home_html = None
    for base in (f"https://www.{domain}", f"https://{domain}"):
        try:
            r = sess.get(base, impersonate=IMPERSONATE, timeout=TIMEOUT, allow_redirects=True)
            if r.status_code == 200 and len(r.text) > 800:
                out["reachable"] = True
                out["final_home"] = str(r.url)
                home_html = r.text
                break
        except Exception as e:  # noqa: BLE001
            out["error"] = f"{type(e).__name__}"
    if not out["reachable"]:
        return out
    # home itself may be the listing (mono-page dealers)
    hs = _sniff(home_html)
    best = hs["price_tokens"]
    best_slug = "/" if best >= MIN_PRICE_TOKENS else None
    m = re.match(r"(https?://[^/]+)", out["final_home"])
    root = m.group(1) if m else f"https://{domain}"
    for slug in SLUGS:
        try:
            r = sess.get(root + slug, impersonate=IMPERSONATE, timeout=TIMEOUT, allow_redirects=True)
            if r.status_code == 200 and len(r.text) > 4000:
                s = _sniff(r.text)
                tok = max(s["price_tokens"], s["euro_thousands"])
                if tok > best:
                    best, best_slug = tok, slug
                    if best >= 12:  # plenty — stop early
                        break
        except Exception:  # noqa: BLE001
            continue
    out["best_price_tokens"] = best
    out["best_slug"] = best_slug
    out["harvestable"] = best >= MIN_PRICE_TOKENS
    return out


async def upsert_entity(conn: asyncpg.Connection, geo: GeoResolver, c: dict) -> dict:
    """Upsert one candidate. Returns {status, cdp_code, was_new}."""
    prov = geo.province_code(c.get("province"))
    muni = geo.municipality_code(prov, c.get("municipality"))
    if not prov and c.get("municipality"):
        prov, muni = geo.resolve_city_global(c["municipality"])
    if not prov:
        return {"status": "no_province", "cdp_code": None, "was_new": False}
    domain = _host(c.get("website")) or None
    name = c.get("name")
    if not domain and not (name and (muni or prov)):
        return {"status": "no_identity", "cdp_code": None, "was_new": False}
    code = cdp_code(province_code=prov, domain=domain, name=name,
                    municipality_code=muni, address=c.get("address"))
    eulid = ulid()
    row = await conn.fetchrow(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, municipality_code, address, website, is_tier1, status,
               first_discovered_source, last_seen)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,false,'active',$10, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()
           RETURNING (xmax = 0) AS inserted""",
        eulid, code, c["kind"], name, name, prov, muni,
        c.get("address"), (f"https://{domain}" if domain else None), SOURCE_KEY)
    real_ulid = await conn.fetchval("SELECT entity_ulid FROM entity WHERE cdp_code=$1", code)
    await conn.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        real_ulid, SOURCE_KEY, c.get("source_ref") or domain or name)
    return {"status": "upserted", "cdp_code": code, "was_new": bool(row["inserted"])}


async def process(candidates_path: str) -> None:
    cands = json.loads(Path(candidates_path).read_text(encoding="utf-8"))
    idx = json.loads((OUT_DIR / "_dedup_index.json").read_text(encoding="utf-8"))
    db_hosts = set(idx["hosts"])
    db_namemuni = set(idx["namemuni"])

    conn = await asyncpg.connect(DSN)
    geo = await GeoResolver.load(conn)
    results = []
    seen_hosts: set[str] = set()
    try:
        for c in cands:
            host = _host(c.get("website"))
            rec = {**c, "host": host}
            # DEDUP 1: bare host already in DB or already processed this run
            if host and (host in db_hosts or host in seen_hosts):
                rec["dedup"] = "host_known"
                results.append(rec)
                continue
            # DEDUP 2: normalized name + municipality (when geo resolvable)
            prov = geo.province_code(c.get("province"))
            muni = geo.municipality_code(prov, c.get("municipality"))
            nm = _norm(c.get("name"))
            if nm and muni and f"{nm}|{muni}" in db_namemuni:
                rec["dedup"] = "namemuni_known"
                results.append(rec)
                continue
            # genuinely new -> probe own-site if it has a website
            if host:
                seen_hosts.add(host)
                probe = probe_site(host)
                rec["probe"] = probe
            up = await upsert_entity(conn, geo, c)
            rec["upsert"] = up
            rec["dedup"] = "new"
            results.append(rec)
            print(f"[{up['status']:>10}] new={up['was_new']} "
                  f"harvest={rec.get('probe', {}).get('harvestable')} {c.get('name')} <{host}>")
    finally:
        await conn.close()
    out_path = OUT_DIR / (Path(candidates_path).stem + "_processed.json")
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    new = sum(1 for r in results if r.get("upsert", {}).get("was_new"))
    harv = sum(1 for r in results if r.get("probe", {}).get("harvestable"))
    print(f"[geo_sweep] processed={len(results)} new_entities={new} harvestable_ownsite={harv}")
    print(f"[geo_sweep] -> {out_path}")


if __name__ == "__main__":
    asyncio.run(process(sys.argv[1]))

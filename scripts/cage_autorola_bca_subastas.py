"""Cage the FREE-STEALTH ES auction lots from Autorola + BCA Espana into the subastas group.

This overturns the prior "GATED, no public lot data layer" verdict on Autorola/BCA: the prior probe
used a NON-JS curl_cffi fetch, which cannot boot the Angular/JS SPAs. Driven through a JS-executing
STEALTH BROWSER (Playwright/camoufox class), BOTH platforms expose full per-lot ES car stock with NO
login:

  * Autorola (www.autorola.es)  - the SPA fetches a public REST data layer
      GET https://old.autorola.es/rest/vehiclesearchenrollment/result?locale=es_ES&offset&limit[&auctionId]
    returning groups[].vehicleDTOS[] with vehicleDTO{headline,details,countryCode,localizedMileage,
    presentationYear,pictureUrl} + auctionId/auctionTitle (the sale event) + firstReg + sortableMileage.
    Per-lot countryCode='ES' is the ES filter. Anonymous: loginRequired=True / price=None (bid gated),
    but the VEHICLE itself (make/model/version/year/km/location/photo) is fully public.
  * BCA Espana (es.bca-europe.com) - the SPA fetches (behind a Cloudflare JS challenge the browser
    passes; a plain curl_cffi gets a 403 'Just a moment...'):
      POST https://es.bca-europe.com/buyer/facetedsearch/GetViewModel?q=&bq=salecountry_exact:ES
    returning VehicleResults[] with IsUserAnonymous=true, CanViewPricing=false, TotalVehicles=1926.
    Each lot: Make/Model/Derivative, VehicleInfoHeadline/Column1-3 (reg date, mileage, doors, fuel,
    transmission, power), SaleLocation, SaleInformation (lot ref), ImageUrl (grp=public). Price gated.

Both are caged with the EXACT dual-membership ontology the Ayvens connector uses
(pipeline.platform.group_subastas_wholesale):
  platform (Autorola / BCA Espana) -> entity kind='plataforma' (+ platform_meta)        [PLATFORM]
  each SALE EVENT (the ES auction)  -> entity kind='subasta' (national, province NULL)   [SELLER]
  each LOT (car)                    -> vehicle OWNED BY its sale event                    [CAR]
  the lot ON the platform           -> platform_listing edge                             [EDGE]
defense_tier: Autorola t1_soft (cookie-gated SPA, no hard WAF) / BCA t2_js_challenge (Cloudflare).
source_group=official_registry (nearest enum for the auction group). price=NULL (bid gated, honest).

The HARVEST itself runs through the stealth browser (the only free way past the SPA bootstrap + the
BCA Cloudflare challenge); this script INGESTS the already-harvested public slices (JSON captured from
the live browser network) and cages them idempotently. Denominators recorded honestly:
Autorola ES (the 2 opened ES sale events drained) / BCA ES TotalVehicles=1926 (50-lot public slice).

Run: python scripts/cage_autorola_bca_subastas.py --bca <bca.json> --autorola <a1.json> [<a2.json> ...]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

import psycopg2
import psycopg2.extras


def _load_json(fn):
    """Load a JSON file, tolerating a double-encoded JSON-string wrapper (browser evaluate dumps)."""
    d = json.load(open(fn, encoding="utf-8"))
    if isinstance(d, str):
        d = json.loads(d)
    return d

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.ids import ulid  # noqa: E402
from services.api.codes import cdp_code, _base32  # noqa: E402

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
NATIONAL = "00"

# ---------------------------------------------------------------------------
# Platform identities
# ---------------------------------------------------------------------------

PLATFORMS = {
    "autorola": {
        "domain": "autorola.es",
        "website": "autorola.es",
        "legal_name": "Autorola Espana (Autorola Group remarketing auctions)",
        "trade_name": "Autorola",
        "source_key": "group_subastas_autorola",
        "defense_tier": "t1_soft",      # cookie-gated Angular SPA + per-request anon JWT; no hard WAF.
        "family": "autorola",
        "data_surface": "internal_api",
        "surface_intent": "spa_rest_vehiclesearch",
        "endpoint": "GET https://old.autorola.es/rest/vehiclesearchenrollment/result",
        "host": "old.autorola.es",
        "sale_label": "Autorola subasta",
    },
    "bca": {
        "domain": "es.bca-europe.com",
        "website": "es.bca-europe.com",
        "legal_name": "BCA Espana (British Car Auctions Espana, B2B VO remarketing)",
        "trade_name": "BCA Espana",
        "source_key": "group_subastas_bca",
        "defense_tier": "t2_js_challenge",  # Cloudflare JS challenge fronts the faceted-search API.
        "family": "bca_europe",
        "data_surface": "internal_api",
        "surface_intent": "spa_facetedsearch_viewmodel",
        "endpoint": "POST https://es.bca-europe.com/buyer/facetedsearch/GetViewModel",
        "host": "es.bca-europe.com",
        "sale_label": "BCA Espana subasta",
    },
}


def platform_cdp_code(domain: str) -> str:
    key = f"domain:{domain}"
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return f"CDP-ES-{NATIONAL}-{_base32(digest)}"


# ---------------------------------------------------------------------------
# Field helpers
# ---------------------------------------------------------------------------


def _to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _km_range(km):
    if km is None:
        return None
    return km if 0 <= km <= 5_000_000 else None


def _year_ok(y):
    return y if (y is not None and 1900 <= y <= 2100) else None


_FUEL = {"gasolina": "Gasolina", "petrol": "Gasolina", "diesel": "Diesel",
         "diésel": "Diesel", "diesél": "Diesel", "electrico": "Electrico",
         "eléctrico": "Electrico", "hibrido": "Hibrido", "híbrido": "Hibrido"}
_TRANS = {"manual": "Manual", "automatic": "Automatico", "automatico": "Automatico",
          "automático": "Automatico", "auto": "Automatico", "secuencial": "Automatico"}


def _norm_fuel(s):
    if not isinstance(s, str):
        return None
    return _FUEL.get(s.strip().lower(), s.strip()) or None


def _norm_trans(s):
    if not isinstance(s, str):
        return None
    return _TRANS.get(s.strip().lower(), s.strip()) or None


# ---------------------------------------------------------------------------
# Parsers: platform JSON slice -> normalized cage rows
# ---------------------------------------------------------------------------


def parse_autorola(files: list[str]) -> tuple[dict, list[dict]]:
    """Return (sales_by_id, lots). ES filter = vehicleDTO.countryCode == 'ES'. Dedup on enrollId."""
    sales: dict[str, dict] = {}
    lots: dict[str, dict] = {}
    for fn in files:
        d = _load_json(fn)
        for g in d.get("groups", []):
            for v in g.get("vehicleDTOS", []):
                vd = v.get("vehicleDTO") or {}
                if (vd.get("countryCode") or "").upper() != "ES":
                    continue
                enroll = str(v.get("enrollId") or "")
                auc_id = str(v.get("auctionId") or "")
                if not enroll or not auc_id:
                    continue
                auc_title = (v.get("auctionTitle") or "").strip() or f"auction {auc_id}"
                sales.setdefault(auc_id, {"sale_id": auc_id, "name": auc_title})
                headline = (vd.get("headline") or "").strip()
                details = (vd.get("details") or "").strip()
                # details: "1.0 Tsi Dsg Style Xm, Gasolina, 85 kW, 116 CV, Auto 7marchas, 5puertas"
                parts = [p.strip() for p in details.split(",")]
                version = parts[0] if parts else None
                fuel = next((p for p in parts if p.lower() in _FUEL), None)
                trans = next((p for p in parts
                              if any(t in p.lower() for t in ("manual", "auto", "secuencial"))), None)
                make = (v.get("vehicleDTO", {}).get("headline") or "").split(" ")[0] or None
                model = headline[len(make):].strip() if (make and headline.startswith(make)) else None
                # year from presentationYear "12/2024" or firstReg ISO
                py = vd.get("presentationYear") or ""
                ym = re.search(r"(\d{4})", py) or re.search(r"(\d{4})", v.get("firstReg") or "")
                year = _year_ok(int(ym.group(1))) if ym else None
                kmm = re.search(r"([\d.]+)", (vd.get("localizedMileage") or "").replace(".", ""))
                km = _km_range(_to_int(v.get("sortableMileage")) or
                               (_to_int(kmm.group(1)) if kmm else None))
                lots[enroll] = {
                    "platform": "autorola",
                    "sale_id": auc_id,
                    "listing_ref": enroll,
                    "deep_link": f"https://www.autorola.es/vehicles/{enroll}",
                    "title": headline or None,
                    "make": make,
                    "model": model,
                    "year": year,
                    "km": km,
                    "price": None,           # loginRequired=True -> bid gated -> NULL (honest).
                    "fuel": _norm_fuel(fuel),
                    "transmission": _norm_trans(trans.split(" ")[0] if trans else None),
                    "photo_url": vd.get("pictureUrl") or None,
                }
    return sales, list(lots.values())


# BCA VehicleType values kept as "car" stock. CrossCountryVehicle (4x4/SUV) is a car;
# Motorcycle and LightCommercialVehicle (vans) are the noise the contract drops.
_BCA_CAR_TYPES = {"car", "crosscountryvehicle"}


def parse_bca(files: list[str]) -> tuple[dict, list[dict]]:
    """Return (sales_by_id, lots), filtered to cars only.

    The SALE EVENT is the BCA SaleId/SaleName (lot owned by it). Prefers the clean
    structured fields (VehicleType, Mileage, FuelType, RegistrationDate, SaleId/SaleName)
    from the live faceted-search slice, falling back to the legacy VehicleInfoColumn parse.
    """
    sales: dict[str, dict] = {}
    lots: dict[str, dict] = {}
    for fn in files:
        d = _load_json(fn)
        rows = d.get("rows") or d.get("VehicleResults") or []
        for v in rows:
            vid = str(v.get("id") or v.get("VehicleId") or "")
            if not vid:
                continue
            # vehicleType=car filter: drop the moto + van noise, keep cars + 4x4.
            vtype = (v.get("VehicleType") or v.get("vehicleType") or "").strip().lower()
            if vtype and vtype not in _BCA_CAR_TYPES:
                continue
            make = v.get("make") or v.get("Make")
            model = v.get("model") or v.get("Model")
            deriv = v.get("deriv") or v.get("Derivative")
            headline = v.get("headline") or v.get("VehicleInfoHeadline") or ""
            c1 = v.get("c1") or v.get("VehicleInfoColumn1") or ""
            c2 = v.get("c2") or v.get("VehicleInfoColumn2") or ""
            c3 = v.get("c3") or v.get("VehicleInfoColumn3") or ""
            sale_info = v.get("sale") or v.get("SaleInformation") or ""
            loc = v.get("loc") or v.get("SaleLocation") or ""
            img = v.get("img") or v.get("ImageUrl") or ""
            # sale event: prefer the structured SaleId/SaleName; else parse SaleInformation.
            sale_name = (v.get("SaleName") or "").strip() or None
            if not sale_name:
                seg = [s.strip() for s in sale_info.split(",")]
                if len(seg) >= 2:
                    sale_name = seg[1]
            sale_name = sale_name or (loc or "BCA Espana subasta")
            structured_sale_id = (v.get("SaleId") or "").strip()
            sale_id = (structured_sale_id[:16] if structured_sale_id
                       else hashlib.sha256((sale_name + "|" + (loc or "")).encode("utf-8")).hexdigest()[:16])
            sales.setdefault(sale_id, {"sale_id": sale_id, "name": sale_name[:120]})
            # year: prefer RegistrationDate ISO; else headline "..., 2021" or c1 date.
            reg_date = v.get("RegistrationDate") or ""
            ym = (re.search(r"(\d{4})", reg_date) or re.search(r",\s*(\d{4})\s*$", headline)
                  or re.search(r"/(\d{4})", c1))
            year = _year_ok(int(ym.group(1))) if ym else None
            # km: prefer structured Mileage; else c1 "... Kilometraje".
            km = _km_range(_to_int(v.get("Mileage")))
            if km is None:
                kmm = re.search(r"([\d.]+)\s*Kil", c1)
                km = _km_range(_to_int(kmm.group(1).replace(".", "")) if kmm else None)
            # fuel: prefer structured FuelType; else scan c3.
            fuel = v.get("FuelType") or next(
                (w for w in re.split(r"[@\s]+", c3) if w.lower() in _FUEL), None)
            trans = next((w for w in re.split(r"[@\s]+", c3)
                          if w.lower() in ("manual", "automatico", "automático", "auto")), None)
            img_url = ("https:" + img) if img.startswith("//") else (img or None)
            lots[vid] = {
                "platform": "bca",
                "sale_id": sale_id,
                "listing_ref": v.get("reg") or v.get("RegistrationNumber") or vid,
                "deep_link": f"https://es.bca-europe.com/vehicle/{vid}",
                "title": (headline.split(",")[0].strip() or
                          " ".join(x for x in (make, model) if x)) or None,
                "make": make,
                "model": (model or "") + ((" " + deriv) if deriv else "") or None,
                "year": year,
                "km": km,
                "price": None,           # CanViewPricing=false -> bid gated -> NULL (honest).
                "fuel": _norm_fuel(fuel),
                "transmission": _norm_trans(trans),
                "photo_url": img_url,
            }
    return sales, list(lots.values())


# ---------------------------------------------------------------------------
# DB cage (dual-membership, idempotent ON CONFLICT) - mirrors group_subastas_wholesale
# ---------------------------------------------------------------------------


def ensure_platform(cur, p: dict) -> str:
    code = platform_cdp_code(p["domain"])
    cur.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, website, is_tier1, status, kind_source,
               defense_tier, source_group, role, first_discovered_source, last_seen)
           VALUES (%s,%s,'plataforma',%s,%s,NULL,%s,FALSE,'active','platform_label',
               %s::defense_tier,'official_registry'::source_group,'platform'::entity_role,%s, now())
           ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
               defense_tier = EXCLUDED.defense_tier, role = EXCLUDED.role,
               legal_name = EXCLUDED.legal_name, kind = EXCLUDED.kind""",
        (ulid(), code, p["legal_name"], p["trade_name"], p["website"],
         p["defense_tier"], p["source_key"]))
    cur.execute("SELECT entity_ulid FROM entity WHERE cdp_code=%s", (code,))
    eulid = cur.fetchone()[0]
    cur.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES (%s,%s,%s) "
        "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
        (eulid, p["source_key"], p["domain"]))
    cur.execute(
        """INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
               requires_creds, is_platform_like, family)
           VALUES (%s,%s,%s::jsonb,FALSE,FALSE,%s)
           ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
               surface_detail = EXCLUDED.surface_detail, family = EXCLUDED.family""",
        (eulid, p["data_surface"],
         json.dumps({"endpoint": p["endpoint"], "host": p["host"],
                     "country": "es", "surface_intent": p["surface_intent"],
                     "engine": "stealth_browser_js_spa", "price_gate": "bid_login_gated"}),
         p["family"]))
    return eulid


def sale_cdp(p: dict, sale: dict) -> str:
    name = f"{p['sale_label']} {sale['name']}"
    return cdp_code(province_code=NATIONAL, domain=None, name=name,
                    address=f"{p['family']}sale:{sale['sale_id']}")


def cage(cur, p: dict, platform_ulid: str, sales: dict, lots: list[dict]) -> dict:
    src = p["source_key"]
    # sale-event sellers (kind=subasta, national)
    sale_to_cdp = {sid: sale_cdp(p, s) for sid, s in sales.items()}
    for sid, s in sales.items():
        code = sale_to_cdp[sid]
        cur.execute(
            """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
                   province_code, is_tier1, status, kind_source, sells_cars,
                   source_group, role, first_discovered_source, last_seen)
               VALUES (%s,%s,'subasta',%s,%s,NULL,FALSE,'active','platform_label',TRUE,
                   'official_registry'::source_group,'registry'::entity_role,%s, now())
               ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now()""",
            (ulid(), code, f"{p['sale_label']} {s['name']}"[:200],
             f"{p['sale_label']} {s['name']}"[:200], src))
        cur.execute(
            "INSERT INTO entity_source (entity_ulid, source_key, source_ref) "
            "SELECT entity_ulid,%s,%s FROM entity WHERE cdp_code=%s "
            "ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()",
            (src, str(sid), code))
    cur.execute("SELECT cdp_code, entity_ulid FROM entity WHERE cdp_code = ANY(%s)",
                (list(sale_to_cdp.values()),))
    cdp_to_ulid = dict(cur.fetchall())

    new_vehicles = 0
    new_edges = 0
    new_events = 0
    for lot in lots:
        sale_ulid = cdp_to_ulid[sale_to_cdp[lot["sale_id"]]]
        v_ulid = ulid()
        cur.execute(
            """INSERT INTO vehicle (vehicle_ulid, entity_ulid, deep_link, title, make, model,
                   year, km, price, fuel, transmission, photo_url, status, first_seen, last_seen)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NULL,%s,%s,%s,'available', now(), now())
               ON CONFLICT (entity_ulid, deep_link) DO UPDATE SET last_seen = now(),
                   status='available'
               RETURNING (xmax = 0) AS inserted, vehicle_ulid""",
            (v_ulid, sale_ulid, lot["deep_link"], lot["title"], lot["make"], lot["model"],
             lot["year"], lot["km"], lot["fuel"], lot["transmission"], lot["photo_url"]))
        inserted, real_vulid = cur.fetchone()
        if inserted:
            new_vehicles += 1
        cur.execute(
            """INSERT INTO platform_listing (vehicle_ulid, platform_entity_ulid, listing_url,
                   listing_ref, platform_price, status, first_seen, last_seen)
               VALUES (%s,%s,%s,%s,NULL,'listed', now(), now())
               ON CONFLICT (vehicle_ulid, platform_entity_ulid)
                 DO UPDATE SET last_seen = now(), status='listed', listing_ref = EXCLUDED.listing_ref
               RETURNING (xmax = 0) AS inserted""",
            (real_vulid, platform_ulid, lot["deep_link"], lot["listing_ref"]))
        if cur.fetchone()[0]:
            new_edges += 1
        if inserted:
            cur.execute(
                """INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type,
                       old_value, new_value)
                   VALUES (%s,%s,%s,'NEW',NULL,%s::jsonb)""",
                (ulid(), real_vulid, sale_ulid,
                 json.dumps({"make": lot["make"], "model": lot["model"], "year": lot["year"],
                             "km": lot["km"], "platform": p["trade_name"]})))
            new_events += 1
    return {"sales": len(sales), "lots": len(lots),
            "new_vehicles": new_vehicles, "new_edges": new_edges, "new_events": new_events}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--autorola", nargs="*", default=[])
    ap.add_argument("--bca", nargs="*", default=[])
    args = ap.parse_args()

    conn = psycopg2.connect(DSN)
    conn.autocommit = False
    cur = conn.cursor()
    report = {}
    try:
        if args.autorola:
            p = PLATFORMS["autorola"]
            pulid = ensure_platform(cur, p)
            sales, lots = parse_autorola(args.autorola)
            report["autorola"] = cage(cur, p, pulid, sales, lots)
            report["autorola"]["platform_cdp"] = platform_cdp_code(p["domain"])
        if args.bca:
            p = PLATFORMS["bca"]
            pulid = ensure_platform(cur, p)
            sales, lots = parse_bca(args.bca)
            report["bca"] = cage(cur, p, pulid, sales, lots)
            report["bca"]["platform_cdp"] = platform_cdp_code(p["domain"])
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

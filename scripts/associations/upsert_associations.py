"""FASE 1 — DESCUBRIR (upsert pass): official Spanish dealer/sector ASSOCIATIONS.

Sources mined for this front (discover_associations):
  - AEDRA  (Asociacion Espanola del Desguace y Reciclaje del Automovil) -> desguace
  - ACEVAS (Concesionarios VW/Audi/Skoda)                              -> concesionario_oficial
  - AECS   (Concesionarios Stellantis)                                 -> concesionario_oficial

Dedup ladder against the LIVE entity table (identical to paginas_amarillas /
associations DedupIndex): bare-host website -> normalized name+municipality ->
name+province. Inserts ONLY genuinely-new points of sale; attaches the association
as a corroborating entity_source on dupes.

source_group='association', kind_source='legal_census'.

Usage:
  python scripts/associations/upsert_associations.py            # dry-run
  python scripts/associations/upsert_associations.py --commit   # write
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

import psycopg2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))

from dedup_upsert import DedupIndex, GeoResolver, bare_host, cdp_code, ulid  # noqa: E402
from geo_from_address import resolve as geo_resolve  # noqa: E402

ROOT = Path(HERE).resolve().parent.parent
RES = ROOT / "docs" / "research" / "associations"
REPORT = RES / "upsert_report.json"
DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")


def load_records():
    """Normalize the three source files into a common record shape."""
    recs = []
    # AEDRA -> desguace
    aedra = json.loads((RES / "aedra_members.json").read_text(encoding="utf-8"))
    for m in aedra:
        recs.append({
            "source_key": "aedra",
            "source_ref": f"https://aedra.org/asociados/{m['slug']}/",
            "kind": "desguace",
            "name": m["name"],
            "website": m.get("website"),
            "phone": m.get("phone"),
            "address": m.get("address_raw"),
            "province_hint": None,
        })
    # ACEVAS -> concesionario_oficial
    acevas = json.loads((RES / "acevas_members.json").read_text(encoding="utf-8"))
    for m in acevas:
        recs.append({
            "source_key": "acevas",
            "source_ref": "https://www.acevas.com/concesionarios/",
            "kind": "concesionario_oficial",
            "name": m["name"],
            "website": m.get("website"),
            "phone": m.get("phone"),
            "email": m.get("email"),
            "address": m.get("address_raw"),
            "postcode": m.get("zip"),
            "province_hint": m.get("province"),
        })
    # AECS -> concesionario_oficial
    aecs = json.loads((RES / "aecs_members.json").read_text(encoding="utf-8"))
    for m in aecs:
        recs.append({
            "source_key": "aecs",
            "source_ref": "https://asociacionstellantis.com/directorio-asociados/",
            "kind": "concesionario_oficial",
            "name": m["name"],
            "website": m.get("website"),
            "address": None,
            "province_hint": m.get("province"),
        })
    return recs


def insert_new(cur, *, code, kind, name, prov, muni, address, postcode, phone,
               email, website, source_key, source_ref):
    eulid = ulid()
    cur.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, municipality_code, address, postcode, phone, email, website,
               website_waf, is_tier1, status, first_discovered_source, kind_source,
               source_group, sells_cars)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'none',FALSE,'unverified',%s,
                   'legal_census','association',TRUE)""",
        (eulid, code, kind, name, name, prov, muni, address, postcode, phone, email,
         website, source_key))
    cur.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) "
        "VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", (eulid, source_key, source_ref))
    return eulid


def run(commit: bool):
    records = load_records()
    print(f"loaded {len(records)} association records "
          f"(aedra+acevas+aecs)")
    conn = psycopg2.connect(DSN)
    idx = DedupIndex.load(conn)
    geo = GeoResolver(conn)
    print(f"dedup index: {len(idx.by_host)} hosts, {len(idx.by_name_muni)} name+muni keys")

    stats = Counter()
    new_by_kind = Counter()
    dup_by_reason = Counter()
    new_with_site = 0
    new_examples = []
    cur = conn.cursor()

    for r in records:
        name = r["name"]
        website = r.get("website")
        prov, muni, pc = geo_resolve(geo, r.get("address") or "", r.get("province_hint"))
        postcode = r.get("postcode") or pc
        existing, reason = idx.match(name=name, website=website,
                                     municipality_code=muni, province_code=prov)
        if existing:
            stats["dup"] += 1
            dup_by_reason[(reason or "?").split(":")[0]] += 1
            cur.execute(
                "INSERT INTO entity_source (entity_ulid, source_key, source_ref) "
                "SELECT entity_ulid, %s, %s FROM entity WHERE cdp_code=%s "
                "ON CONFLICT DO NOTHING", (r["source_key"], r["source_ref"], existing))
            continue
        if not prov:
            stats["skip_no_province"] += 1
            continue
        host = bare_host(website)
        code = cdp_code(province_code=prov, domain=host, name=name,
                        municipality_code=muni, address=r.get("address"))
        cur.execute("SELECT 1 FROM entity WHERE cdp_code=%s", (code,))
        if cur.fetchone():
            stats["dup_cdp"] += 1
            idx.register(cdp=code, name=name, website=website,
                         municipality_code=muni, province_code=prov)
            cur.execute(
                "INSERT INTO entity_source (entity_ulid, source_key, source_ref) "
                "SELECT entity_ulid, %s, %s FROM entity WHERE cdp_code=%s "
                "ON CONFLICT DO NOTHING", (r["source_key"], r["source_ref"], code))
            continue
        stats["new"] += 1
        new_by_kind[r["kind"]] += 1
        if website:
            new_with_site += 1
        if len(new_examples) < 40:
            new_examples.append({"name": name, "kind": r["kind"], "source": r["source_key"],
                                 "prov": prov, "muni": muni, "website": website})
        insert_new(cur, code=code, kind=r["kind"], name=name, prov=prov, muni=muni,
                   address=r.get("address"), postcode=postcode, phone=r.get("phone"),
                   email=r.get("email"), website=website,
                   source_key=r["source_key"], source_ref=r["source_ref"])
        idx.register(cdp=code, name=name, website=website,
                     municipality_code=muni, province_code=prov)

    if commit:
        conn.commit()
        print("COMMITTED")
    else:
        conn.rollback()
        print("DRY-RUN (no writes)")

    print(f"new={stats['new']} dup={stats['dup']} dup_cdp={stats['dup_cdp']} "
          f"skip_no_province={stats['skip_no_province']}")
    print(f"new by kind: {dict(new_by_kind)}")
    print(f"dup by reason: {dict(dup_by_reason)}")
    print(f"new entities carrying own-site website: {new_with_site}")

    report = {
        "front": "discover_associations",
        "committed": commit,
        "sources": ["aedra", "acevas", "aecs"],
        "records_in": len(records),
        "stats": dict(stats),
        "new_by_kind": dict(new_by_kind),
        "dup_by_reason": dict(dup_by_reason),
        "new_with_site": new_with_site,
        "examples": new_examples,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    cur.close()
    conn.close()
    return report


if __name__ == "__main__":
    run("--commit" in sys.argv)

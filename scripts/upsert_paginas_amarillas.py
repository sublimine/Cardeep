"""FASE 1 — DESCUBRIR (upsert pass): Páginas Amarillas directory listings.

Reads docs/research/paginas_amarillas_raw.json, dedups every listing against the
LIVE entity table with the mandated identity ladder (bare-host website ->
normalized name+municipality -> name+province), and inserts ONLY genuinely new
points of sale. Geo-resolved to INE codes; source_group='directory'.

Reuses the battle-tested DedupIndex / GeoResolver / bare_host / normalize_name /
ulid / cdp_code helpers from the associations front so dedup behaviour is
identical across discovery fronts (no second architecture).

Env: CARDEEP_DSN.
Usage:
  python -m scripts.upsert_paginas_amarillas            # dry-run (no writes)
  python -m scripts.upsert_paginas_amarillas --commit   # write new POS
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

import psycopg2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.associations.dedup_upsert import (  # noqa: E402
    DedupIndex, GeoResolver, bare_host, cdp_code, ulid,
)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "docs" / "research" / "paginas_amarillas_raw.json"
REPORT = ROOT / "docs" / "research" / "paginas_amarillas_upsert_report.json"
DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
SOURCE_KEY = "paginas_amarillas"


def _insert_new(cur, *, code, kind, name, prov, muni, address, postcode, phone,
                website, source_ref) -> None:
    eulid = ulid()
    cur.execute(
        """INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
               province_code, municipality_code, address, postcode, phone, website,
               website_waf, is_tier1, status, first_discovered_source, kind_source,
               source_group, role, sells_cars)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'none',FALSE,'unverified',%s,
                   'classifier','directory','standalone_pos',TRUE)""",
        (eulid, code, kind, name, name, prov, muni, address, postcode, phone,
         website, SOURCE_KEY))
    cur.execute(
        "INSERT INTO entity_source (entity_ulid, source_key, source_ref) "
        "VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", (eulid, SOURCE_KEY, source_ref))


def run(commit: bool) -> None:
    payload = json.loads(RAW.read_text(encoding="utf-8"))
    records = payload["records"]
    print(f"loaded {len(records)} raw listings from {RAW.name}")

    conn = psycopg2.connect(DSN)
    idx = DedupIndex.load(conn)
    geo = GeoResolver(conn)
    print(f"dedup index: {len(idx.by_host)} hosts, {len(idx.by_name_muni)} name+muni keys")

    stats = Counter()
    kind_new = Counter()
    sites_new = 0
    cur = conn.cursor()
    new_examples = []
    for r in records:
        name = r["name"]
        website = r.get("website")
        prov = r.get("prov_code") or geo.province(r.get("region"))
        muni = geo.municipality(r.get("locality"), prov) if prov else None
        existing, reason = idx.match(name=name, website=website,
                                     municipality_code=muni, province_code=prov)
        if existing:
            stats["dup"] += 1
            if commit:
                cur.execute(
                    "INSERT INTO entity_source (entity_ulid, source_key, source_ref) "
                    "SELECT entity_ulid, %s, %s FROM entity WHERE cdp_code=%s "
                    "ON CONFLICT DO NOTHING",
                    (SOURCE_KEY, r.get("detail") or name, existing))
            continue
        if not prov:
            stats["skip_no_province"] += 1
            continue
        host = bare_host(website)
        code = cdp_code(province_code=prov, domain=host, name=name,
                        municipality_code=muni, address=r.get("address"))
        # same canonical key already minted this run / pre-existing row?
        cur.execute("SELECT 1 FROM entity WHERE cdp_code=%s", (code,))
        if cur.fetchone():
            stats["dup_cdp"] += 1
            idx.register(cdp=code, name=name, website=website,
                         municipality_code=muni, province_code=prov)
            continue
        stats["new"] += 1
        kind_new[r["kind"]] += 1
        if website:
            sites_new += 1
        if len(new_examples) < 25:
            new_examples.append({"name": name, "kind": r["kind"], "muni": muni,
                                 "prov": prov, "website": website})
        if commit:
            _insert_new(cur, code=code, kind=r["kind"], name=name, prov=prov, muni=muni,
                        address=r.get("address"), postcode=r.get("postcode"),
                        phone=r.get("phone"), website=website,
                        source_ref=r.get("detail") or name)
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
    print(f"new by kind: {dict(kind_new)}")
    print(f"new entities carrying own-site website: {sites_new}")

    report = {"source": SOURCE_KEY, "committed": commit, "stats": dict(stats),
              "new_by_kind": dict(kind_new), "new_with_site": sites_new,
              "examples": new_examples}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    cur.close()
    conn.close()


if __name__ == "__main__":
    run("--commit" in sys.argv)

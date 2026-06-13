"""DB-grounded final tally for the 'unreachable' stealth re-test.

Reads the stealth probe result (docs/_unreachable_stealth_result.json) and the LIVE
DB, and prints the authoritative buckets with every number sourced from the DB:
  (a) recovered-free  -> domains that served own-site stock under camoufox, now caged
  (b) genuinely dead  -> dns_dead (NXDOMAIN) + hard_wall (challenge never clears)
  (c) no_listing      -> resolves & renders but no own-site car inventory surface

Caged = the domain's owning entity carries an entity_source row for FAMILY_KEY AND
has >=1 own-site vehicle (no platform_listing edge) in the live DB.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter

import psycopg2

DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
FAMILY_KEY = "family_unreachable"


def _bare(host: str) -> str:
    return re.sub(r"^www\.", "", re.sub(r"^https?://", "", (host or "").lower())).split("/")[0]


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    res = json.load(open("docs/_unreachable_stealth_result.json", encoding="utf-8"))
    buckets = Counter(r["bucket"] for r in res)
    print(f"stealth result: {len(res)} domains -> {dict(buckets)}")

    conn = psycopg2.connect(DSN)
    cur = conn.cursor()

    # Family membership + own-site vehicle count, straight from the live DB.
    cur.execute("""
        SELECT count(DISTINCT es.entity_ulid)
          FROM entity_source es WHERE es.source_key = %s""", (FAMILY_KEY,))
    members = cur.fetchone()[0]
    cur.execute("""
        SELECT count(*) FROM vehicle v
         WHERE v.entity_ulid IN (SELECT entity_ulid FROM entity_source WHERE source_key=%s)
           AND NOT EXISTS (SELECT 1 FROM platform_listing pl
                            WHERE pl.vehicle_ulid = v.vehicle_ulid)""", (FAMILY_KEY,))
    own_site_cars = cur.fetchone()[0]
    print(f"DB: family_unreachable members={members}, own-site (no-edge) cars={own_site_cars}")

    # Per recovered domain: is it caged (member + >=1 own-site car)?
    recovered = [r for r in res if r["bucket"] == "recovered"]
    print(f"\nRECOVERED-FREE domains ({len(recovered)}):")
    caged = 0
    for r in recovered:
        bare = _bare(r.get("host") or r["domain"])
        cur.execute("""
            SELECT e.entity_ulid, e.cdp_code,
                   EXISTS (SELECT 1 FROM entity_source es
                            WHERE es.entity_ulid=e.entity_ulid AND es.source_key=%s) AS is_member,
                   (SELECT count(*) FROM vehicle v
                     WHERE v.entity_ulid=e.entity_ulid
                       AND NOT EXISTS (SELECT 1 FROM platform_listing pl
                                        WHERE pl.vehicle_ulid=v.vehicle_ulid)) AS own_cars
              FROM entity e
             WHERE e.website IS NOT NULL AND e.website<>''
               AND lower(regexp_replace(regexp_replace(e.website,'^https?://',''),'^www\\.','')) LIKE %s
             ORDER BY e.last_seen DESC LIMIT 1""", (FAMILY_KEY, bare + "%"))
        row = cur.fetchone()
        if row:
            eulid, cdp, is_member, own_cars = row
            cage_ok = bool(is_member) and own_cars > 0
            caged += 1 if cage_ok else 0
            print(f"  {r['domain']:30s} cdp={cdp} member={is_member} "
                  f"own_cars={own_cars} CAGED={cage_ok} "
                  f"(stealth: {r.get('best_path')} dlinks={r.get('dlinks')} "
                  f"prices={r.get('prices')} status={r.get('status')})")
        else:
            print(f"  {r['domain']:30s} NO DB ENTITY by website host (cannot cage)")

    dns_dead = [r for r in res if r["bucket"] == "dns_dead"]
    hard_wall = [r for r in res if r["bucket"] == "hard_wall"]
    no_listing = [r for r in res if r["bucket"] == "no_listing"]
    print(f"\n=== FINAL BUCKETS (n={len(res)}) ===")
    print(f"  (a) recovered-free          : {len(recovered)}  (caged in DB: {caged})")
    print(f"  (b) genuinely dead — dns    : {len(dns_dead)}  (NXDOMAIN)")
    print(f"  (b) genuinely dead — wall   : {len(hard_wall)}  (challenge/SSL/HTTP-err never clears in stealth)")
    print(f"      genuinely dead TOTAL    : {len(dns_dead)+len(hard_wall)}")
    print(f"  (c) resolves, no own listing: {len(no_listing)}")
    conn.close()


if __name__ == "__main__":
    main()

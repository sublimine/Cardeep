"""One-off repair: canonicalize coches.com vehicle deep_links and merge the duplicates a
deep_link-format drift created.

ROOT CAUSE. The original per-PDP coches.com slice stored each car's deep_link as the full
SEO-slug sitemap <loc> (e.g. .../ocasion-citroen-c3-aircross-...htm?id=ELkOhfGqQBfk). The
upgraded SRP-per-make connector first rebuilt the link from the make slug
(.../mercedes.htm?id=...) because the SRP card does NOT ship the SEO slug. Same physical car
(same dealer, same visibleId), DIFFERENT deep_link -> the (entity_ulid, deep_link) idempotency
key split it into two vehicle rows. The connector is now fixed to emit a CANONICAL, slug-free
link keyed only on visibleId (.../coches-ocasion.htm?id={visibleId}) — identical from any
surface. This script brings the EXISTING rows onto that same canonical key and collapses the
duplicates so re-runs are truly idempotent.

SAFETY (verified before writing): coches.com vehicles are isolated — 0 of them carry an edge
to any other platform, and every vehicle_event on them is type NEW. So canonicalizing +
merging within the coches.com set touches no other platform's data. The only FKs to
vehicle.vehicle_ulid are platform_listing and vehicle_event; both are repointed before any
delete. Idempotent: a second run finds every deep_link already canonical and 0 duplicates.

Identity of a coches.com car = (owning dealer entity_ulid, vin_ref==visibleId). Survivor =
the oldest (first_seen) vehicle in each identity group; redundant rows fold into it.
"""
from __future__ import annotations

import asyncio
import os

import asyncpg

DSN = os.environ.get("CARDEEP_DSN",
                     "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
_SRP_ALL = "https://www.coches.com/coches-segunda-mano/coches-ocasion.htm"


def canonical(vin_ref: str) -> str:
    return f"{_SRP_ALL}?id={vin_ref}" if vin_ref else _SRP_ALL


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        platform_ulid = await conn.fetchval(
            "SELECT entity_ulid FROM entity WHERE kind='plataforma' AND website='coches.com'")
        if not platform_ulid:
            print("coches.com platform entity not found; nothing to do.")
            return

        # All coches.com-linked vehicles with their identity (dealer, vin_ref) + first_seen.
        rows = await conn.fetch(
            """SELECT v.vehicle_ulid, v.entity_ulid, v.vin_ref, v.deep_link, v.first_seen
                 FROM platform_listing pl
                 JOIN vehicle v ON v.vehicle_ulid = pl.vehicle_ulid
                WHERE pl.platform_entity_ulid = $1""",
            platform_ulid)
        print(f"coches.com vehicles: {len(rows)}")

        # Group by identity (entity_ulid, vin_ref). Survivor = oldest first_seen (stable).
        groups: dict[tuple[str, str], list] = {}
        for r in rows:
            key = (r["entity_ulid"], r["vin_ref"] or "")
            groups.setdefault(key, []).append(r)

        survivors: list[tuple[str, str]] = []   # (survivor_ulid, canonical_link)
        merges: list[tuple[str, str]] = []      # (loser_ulid, survivor_ulid)
        dup_groups = 0
        for (entity_ulid, vin_ref), members in groups.items():
            members.sort(key=lambda m: (m["first_seen"] or m["vehicle_ulid"]))
            survivor = members[0]
            survivors.append((survivor["vehicle_ulid"], canonical(vin_ref)))
            if len(members) > 1:
                dup_groups += 1
                for loser in members[1:]:
                    merges.append((loser["vehicle_ulid"], survivor["vehicle_ulid"]))

        print(f"identity groups: {len(groups)} | duplicate groups: {dup_groups} | "
              f"vehicles to merge away: {len(merges)}")

        async with conn.transaction():
            # 1) Repoint events from losers to survivors, then delete loser edges/vehicles.
            #    Edges: the survivor already owns the coches.com edge, so a loser's edge would
            #    collide on (vehicle_ulid, platform_entity_ulid) if repointed -> delete losers'
            #    edges outright (the survivor's edge is the kept one). Other-platform edges do
            #    not exist on these vehicles (verified), so no edge is lost.
            for loser_ulid, survivor_ulid in merges:
                await conn.execute(
                    "UPDATE vehicle_event SET vehicle_ulid=$2 WHERE vehicle_ulid=$1",
                    loser_ulid, survivor_ulid)
                await conn.execute(
                    "DELETE FROM platform_listing WHERE vehicle_ulid=$1", loser_ulid)
                await conn.execute(
                    "DELETE FROM vehicle WHERE vehicle_ulid=$1", loser_ulid)

            # 2) Canonicalize every survivor's deep_link AND its kept edge's listing_url, so the
            #    (entity_ulid, deep_link) key and the platform_listing.listing_url converge on the
            #    same canonical form a fresh connector run would write (true idempotency).
            for survivor_ulid, link in survivors:
                await conn.execute(
                    "UPDATE vehicle SET deep_link=$2 WHERE vehicle_ulid=$1",
                    survivor_ulid, link)
                await conn.execute(
                    "UPDATE platform_listing SET listing_url=$2 "
                    "WHERE vehicle_ulid=$1 AND platform_entity_ulid=$3",
                    survivor_ulid, link, platform_ulid)

        # Post-checks.
        tot = await conn.fetchval(
            "SELECT count(*) FROM platform_listing WHERE platform_entity_ulid=$1", platform_ulid)
        noncanon = await conn.fetchval(
            """SELECT count(*) FROM platform_listing pl JOIN vehicle v ON v.vehicle_ulid=pl.vehicle_ulid
               WHERE pl.platform_entity_ulid=$1
                 AND v.deep_link <> 'https://www.coches.com/coches-segunda-mano/coches-ocasion.htm?id=' || v.vin_ref""",
            platform_ulid)
        dups = await conn.fetchval(
            """SELECT count(*) FROM (
                 SELECT v.entity_ulid, v.vin_ref FROM platform_listing pl
                 JOIN vehicle v ON v.vehicle_ulid=pl.vehicle_ulid
                 WHERE pl.platform_entity_ulid=$1
                 GROUP BY v.entity_ulid, v.vin_ref HAVING count(*)>1) t""",
            platform_ulid)
        print(f"DONE: coches.com edges={tot} | non-canonical deep_links={noncanon} | "
              f"remaining duplicate identities={dups}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())

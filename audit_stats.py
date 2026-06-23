import asyncio, asyncpg
DSN="postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
async def main():
    c=await asyncpg.connect(DSN)
    dealers=await c.fetchval("""SELECT count(DISTINCT vdr.resolved_cdp_code) FROM v_dealer_resolved vdr JOIN entity e ON e.entity_ulid=vdr.entity_ulid WHERE e.kind<>'particular'""")
    veh=await c.fetchval("""SELECT count(*) FROM v_canonical_vehicle vc JOIN servable_vehicle v ON v.vehicle_ulid=vc.vehicle_ulid WHERE vc.vehicle_ulid=vc.canonical_vehicle_ulid AND v.status='available'""")
    muni=await c.fetchval("SELECT count(*) FROM geo_municipality")
    prov=await c.fetchval("SELECT count(*) FROM geo_province")
    print("LIVE dealers:",dealers,"| FALLBACK 61729 | drift:",dealers-61729)
    print("LIVE vehicles_unique_available:",veh,"| FALLBACK 1704968 | drift:",veh-1704968)
    print("LIVE municipalities:",muni,"| FALLBACK 8132 | drift:",muni-8132)
    print("LIVE provinces:",prov,"| FALLBACK 52")
    await c.close()
asyncio.run(main())

import asyncio, asyncpg
DSN="postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
async def main():
    c=await asyncpg.connect(DSN)
    kinds=await c.fetch("SELECT DISTINCT kind FROM servable_entity WHERE status='active' AND kind<>'particular' ORDER BY kind")
    print("DISTINCT served kinds (non-particular,active):", [r['kind'] for r in kinds])
    # geo_province count
    pc=await c.fetchval("SELECT count(*) FROM geo_province")
    print("geo_province count:", pc)
    # Does NO_DENOM verdict ever appear in venta/desguace live?
    nd=await c.fetch("SELECT segment, count(*) FROM v_province_seal WHERE verdict='NO_DENOM' GROUP BY segment")
    print("NO_DENOM rows:", [dict(r) for r in nd])
    # max coverage_pct venta
    mx=await c.fetchrow("SELECT max(coverage_pct) mx, min(coverage_pct) mn FROM v_province_seal WHERE segment='venta'")
    print("venta coverage_pct range:", dict(mx))
    # how many entities total have '_' placeholder name nationwide
    junk=await c.fetchval("SELECT count(*) FROM servable_entity WHERE status='active' AND kind<>'particular' AND (trade_name='_' OR legal_name='_')")
    print("nationwide '_' placeholder names:", junk)
    await c.close()
asyncio.run(main())

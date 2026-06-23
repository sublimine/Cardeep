import asyncio, asyncpg, json
DSN="postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
async def main():
    c=await asyncpg.connect(DSN)
    # 1) venta national from view
    row=await c.fetchrow("""
        SELECT sum(numerator) num, sum(denominator) den, count(*) np,
               count(*) FILTER (WHERE verdict='SELLADO') sellado,
               count(*) FILTER (WHERE verdict='PARCIAL') parcial,
               count(*) FILTER (WHERE verdict='GAP') gap
        FROM v_province_seal WHERE segment='venta'""")
    print("DB v_province_seal venta national:", dict(row))
    # 2) sample provinces 03,29 numerator/verdict
    for code in ('03','28','29'):
        r=await c.fetchrow("SELECT province_code,numerator,denominator,coverage_pct,verdict FROM v_province_seal WHERE segment='venta' AND province_code=$1",code)
        print("DB venta",code,":",dict(r) if r else None)
    await c.close()
asyncio.run(main())

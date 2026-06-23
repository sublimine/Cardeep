import asyncio, asyncpg, json
DSN="postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
async def main():
    c=await asyncpg.connect(DSN)
    # Replicate exact API query for province 28, page1 size60
    rows=await c.fetch("""
        SELECT * FROM (
            SELECT DISTINCT ON (vdr.resolved_cdp_code)
                   vdr.resolved_cdp_code AS cdp_code,
                   se.kind, se.trade_name, se.legal_name, se.municipality_code,
                   se.is_tier1, se.status
              FROM servable_entity se
              JOIN v_dealer_resolved vdr ON vdr.entity_ulid = se.entity_ulid
             WHERE se.province_code = $1 AND se.status='active' AND se.kind <> 'particular'
             ORDER BY vdr.resolved_cdp_code, se.trade_name NULLS LAST, se.cdp_code
        ) q ORDER BY q.trade_name NULLS LAST, q.cdp_code LIMIT 60 OFFSET 0""", '28')
    print("DB replicate first cdp:", rows[0]['cdp_code'], "trade:", repr(rows[0]['trade_name']))
    # Total distinct canonical dealers in Madrid (the true count behind has_more)
    total=await c.fetchval("""
        SELECT count(*) FROM (
          SELECT DISTINCT vdr.resolved_cdp_code
          FROM servable_entity se JOIN v_dealer_resolved vdr ON vdr.entity_ulid=se.entity_ulid
          WHERE se.province_code=$1 AND se.status='active' AND se.kind<>'particular') t""",'28')
    print("DB total canonical dealers Madrid(28):", total)
    # How many have junk/placeholder names "_"
    junk=await c.fetchval("SELECT count(*) FROM servable_entity WHERE province_code='28' AND status='active' AND kind<>'particular' AND (trade_name='_' OR legal_name='_')")
    print("Madrid entities with '_' name:", junk)
    # municipality_code null among Madrid dealers
    nullmuni=await c.fetchval("SELECT count(*) FROM servable_entity WHERE province_code='28' AND status='active' AND kind<>'particular' AND municipality_code IS NULL")
    print("Madrid dealers with NULL municipality_code:", nullmuni)
    await c.close()
asyncio.run(main())

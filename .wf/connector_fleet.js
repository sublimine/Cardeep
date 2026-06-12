export const meta = {
  name: 'cardeep-connector-fleet',
  description: 'Wire 4 more verified-free Tier-1 giants as platform connectors in parallel (wallapop, autocasion, coches.com, motor.es), harvest a substantial chunk each, into the live DB',
  whenToUse: 'Scale CARDEEP inventory across multiple giants at once following the proven coches.net connector pattern',
  phases: [
    { title: 'Wire', detail: 'one builder per giant, follows the coches.net template, harvests + verifies (parallel)' },
    { title: 'Synthesis', detail: 'roll up the multi-platform live state' },
  ],
}

const TEMPLATE = [
  'Build a CARDEEP platform connector that wires ONE verified-free Tier-1 giant into the LIVE pipeline, EXACTLY mirroring',
  'the proven template C:\\Users\\elias\\projects\\cardeep\\pipeline\\platform\\coches_net_wholesale.py (read it first — copy its',
  'structure: ensure the platform entity kind=plataforma with defense_tier/source_group/role=platform + platform_meta;',
  'per-car cage = upsert SELLING DEALER entity (kind=compraventa, kind_source=platform_label, sells_cars=TRUE, geo-resolved)',
  '+ upsert vehicle OWNED BY dealer (vehicle.entity_ulid=dealer) + INSERT platform_listing edge + emit delta NEW events',
  '+ capture price-drop history if present + save versioned recipe + record a VAM verification_verdict; idempotent ON CONFLICT;',
  'every fetch through governor().wrap_fetch_text for its host; is_open breaker gate + record_run + auto_repair on failure).',
  'Work ONLY in C:\\Users\\elias\\projects\\cardeep — NEVER write to any cardex/CARDEX path. Use absolute paths.',
  'READ: the connector template (coches_net_wholesale.py), your platform recipe (docs/architecture/tier1_recipes/<p>.md),',
  'pipeline/engine/{fetch,governor}.py, pipeline/ops/health.py, pipeline/geo.py, pipeline/geocode.py, services/api/codes.py,',
  'pipeline/ids.py, migrations/0006+0009+0016 (the live schema: entity_kind enum, platform_listing, defense_tier/source_group/role).',
  'ENV: python C:/Users/elias/AppData/Local/Programs/Python/Python311/python ; curl_cffi installed ; DB cardeep-pg :5433',
  'postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep. Preserve live data (only ADD). Build pipeline/platform/<p>_wholesale.py',
  'with a --pages/--limit CLI; harvest a BOUNDED but substantial chunk (~3000-5000 real cars) for this run (the full run is the',
  'same command with more pages); inspect the REAL response for field names, do not assume. VERIFY E2E by querying the DB yourself:',
  'platform entity created, platform_listing rows, dealers discovered, delta events, VAM verdict, data only grew; then a curl to',
  '/platforms/<cdp>/inventory showing real cars with dealer attribution (start/stop uvicorn :8090). Do NOT git commit.',
  'REPORT verified numbers (platform cdp, dealers, cars, platform_listing, VAM) + confirm zero cardex writes.',
].join(' ')

const STR = { type: 'string' }
const CONN_SCHEMA = {
  type: 'object',
  required: ['platform', 'built', 'platform_cdp', 'cars_caged', 'vam'],
  properties: {
    platform: STR,
    built: { type: 'boolean' },
    platform_cdp: STR,
    dealers_discovered: { type: 'number' },
    cars_caged: { type: 'number' },
    platform_listings: { type: 'number' },
    delta_events: { type: 'number' },
    vam: STR,
    file: STR,
    issue: STR,
  },
}
const SYN_SCHEMA = { type: 'object', required: ['summary'], properties: { totals: { type: 'array', items: STR }, summary: STR } }

const TARGETS = [
  { key: 'wallapop', recipe: 'wallapop.md', host: 'api.wallapop.com', group: 'marketplace_generalist', tier: 't1_soft',
    note: 'GET api.wallapop.com/api/v3/search/section (verified free, 200, real cars). Geo lat/long honored; pagination = meta.next_page JWT replayed as ?next_page=; 40 items/page. PRO-dealer via GET /api/v3/users/{id} (type professional/normal + web_slug). To sweep broad inventory iterate keywords or geo grid; for this chunk a few keyword/geo pages = ~3-5k cars is fine. is_tier1=TRUE.' },
  { key: 'autocasion', recipe: 'autocasion.md', host: 'gql.autocasion.com', group: 'marketplace_motor', tier: 't1_soft',
    note: 'GraphQL gql.autocasion.com/graphql (open introspection). Enumerate ad ids from SSR results pages www.autocasion.com/coches-ocasion?page=N (regex ref(\\d+)), hydrate via gql ad(adId:N){...}, dealer via PDP JSON-LD AutoDealer. Total ~115k. Harvest ~3-5k for this chunk. is_tier1=TRUE.' },
  { key: 'coches_com', recipe: 'coches_com.md', host: 'www.coches.com', group: 'marketplace_motor', tier: 't1_soft',
    note: 'Sitemap sitemap/coches/Todo-VO-{0..3}.xml -> 92,259 PDP URLs (CORRECTED real count, not 200k). Fetch PDP, decode r.content (not r.text), regex __NEXT_DATA__, props.pageProps.data.classified -> vehicle + classified.dealer. Harvest ~3-5k PDPs for this chunk. is_tier1=TRUE (Imperva). family note: independent.' },
  { key: 'motor_es', recipe: 'motor_es.md', host: 'www.motor.es', group: 'marketplace_motor', tier: 't1_soft',
    note: 'Read the recipe motor_es.md for the verified free path (Cloudflare-passing curl). Find the listing->PDP path or internal API; pull real cars + dealer. ~51k total; harvest ~3-5k for this chunk. is_tier1=TRUE.' },
]

phase('Wire')
log('Connector fleet: wiring ' + TARGETS.length + ' giants in parallel (different hosts, no rate collision)')
const conns = await parallel(TARGETS.map(t => () =>
  agent(TEMPLATE +
    '\n\nYOUR GIANT: ' + t.key + ' · recipe docs/architecture/tier1_recipes/' + t.recipe + ' · host ' + t.host +
    ' · classify the platform entity defense_tier=' + t.tier + ', source_group=' + t.group + ', role=platform.' +
    '\nRECIPE NOTE: ' + t.note +
    '\nBuild C:\\Users\\elias\\projects\\cardeep\\pipeline\\platform\\' + t.key + '_wholesale.py.',
    { label: 'wire:' + t.key, phase: 'Wire', schema: CONN_SCHEMA, agentType: 'general-purpose' })))
const ok = conns.filter(Boolean)
const wired = ok.filter(c => c.built && c.cars_caged > 0)
log('Wired live: ' + wired.map(c => c.platform + '(' + c.cars_caged + ')').join(', '))

phase('Synthesis')
const rows = ok.map(c => c.platform + ': ' + (c.built ? c.cars_caged + ' cars, ' + c.dealers_discovered + ' dealers, VAM ' + c.vam : 'FAILED: ' + (c.issue || '?'))).join('\n')
const syn = await agent(
  'Summarize the CARDEEP connector-fleet result. Per-connector:\n' + rows +
  '\n\nQuery the live DB yourself for the grand totals (SELECT count from entity, vehicle, platform_listing, distinct plataforma entities) and write a short rollup to C:\\Users\\elias\\projects\\cardeep\\docs\\architecture\\tier1_recipes\\CONNECTORS_STATUS.md (which giants are wired, cars each, what remains). Return {totals, summary}.',
  { label: 'synthesis:connectors', phase: 'Synthesis', agentType: 'general-purpose', schema: SYN_SCHEMA })

return { connectors: ok, wired_count: wired.length, synthesis: syn }

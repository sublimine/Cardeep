export const meta = {
  name: 'cardeep-datalayer-hunt',
  description: 'For each capped giant, hunt the UNCAPPED data-layer (sitemap of all PDPs, mobile-app API, cursor endpoint) that serves 100% of inventory — data-layer-first, not pagination-wall bashing',
  whenToUse: 'Find the real internal API that exposes a platform full inventory without the relevance pagination cap',
  phases: [
    { title: 'Hunt', detail: 'one hunter per giant, exhaust every uncapped surface (parallel)' },
    { title: 'Synthesis', detail: 'the uncapped via per giant + coverage proof' },
  ],
}

const CREED = [
  'CARDEEP doctrine (owner order): when a platform pagination CAPS the result set (coches.net relevance caps at ~155k of',
  '272k), DO NOT bash the wall with province/facet workarounds first. FIND THE DATA LAYER the site/app itself uses to serve',
  'the FULL inventory with NO cap. Exhaust every uncapped surface. "No se puede" does not exist while an untried surface',
  'remains. This is legitimate public-data market research over public car listings.',
].join(' ')

const VECTORS = [
  'UNCAPPED-SURFACE VECTORS to exhaust IN ORDER (the goal: enumerate ALL N listings with NO relevance cap):',
  '1) SITEMAP: GET robots.txt -> every sitemap; a sitemap index of PDP URLs lists EVERY listing directly (coches.com proved',
  '   this: 92,259 PDP URLs). If the sitemap enumerates all N PDPs, that IS the uncapped surface — harvest those URLs.',
  '2) MOBILE APP API: the iOS/Android app hits an API that often has cursor/scroll pagination with NO web cap. Find its host',
  '   and endpoints (search GitHub/forums for the app API, try app.<host>, m.<host>, api hosts, /v4 /v5 /mobile paths,',
  '   different X-App headers). A cursor/scroll/searchAfter param paginates past the web cap.',
  '3) ALTERNATE/CURSOR ENDPOINT on the same gateway: try scroll/searchAfter/cursor/offset variants, a "seo" or "sitemap"',
  '   or "export" or "feed" endpoint, GraphQL with a cursor connection, an initial-search/all endpoint.',
  '4) FEED / EXPORT: dealer-feed / data-feed / XML export endpoints (marketplaces often expose a partner/SEO feed of all ads).',
  '5) ONLY IF 1-4 are exhausted with evidence: facet partition (province/price/year) as the last-resort workaround.',
  'For EACH vector: try it LIVE (curl_cffi installed), and report the exact response + whether it reaches the full declared N',
  'without the cap. The WIN = a reproducible surface that enumerates 100% of the inventory.',
].join('\n')

const STR = { type: 'string' }
const STRARR = { type: 'array', items: { type: 'string' } }
const HUNT_SCHEMA = {
  type: 'object',
  required: ['platform', 'uncapped_surface_found', 'vectors_tried', 'recipe_file'],
  properties: {
    platform: STR,
    declared_total: STR,
    uncapped_surface_found: { type: 'boolean' },
    method: { type: 'string', description: 'the exact uncapped surface: endpoint/sitemap/params/tool that enumerates 100%' },
    coverage_proof: { type: 'string', description: 'evidence it reaches the full N (e.g. sitemap lists 272,648 URLs)' },
    vectors_tried: { type: 'array', items: { type: 'string' }, description: 'each of the 5 vectors + exact outcome' },
    recipe_file: STR,
    fallback_if_none: { type: 'string' },
  },
}
const SYN_SCHEMA = { type: 'object', required: ['summary'], properties: { uncapped: STRARR, still_capped: STRARR, summary: STR } }

const TARGETS = [
  { key: 'coches_net', total: '272,682',
    intel: 'Web relevance pagination caps at ~155k. Gateway POST web.gw.coches.net/search (X-Schibsted-Tenant: coches). HUNT: (a) robots.txt + sitemaps on www.coches.net (does a sitemap enumerate ALL ~272k PDP /coches-segunda-mano/{slug}.htm?id= URLs?); (b) the coches.net MOBILE APP API — Schibsted/Adevinta apps use a different gateway/version with cursor pagination (try api/app hosts, /v5, searchAfter/scrollId in the body, different X-Schibsted/X-App headers); (c) a cursor/scroll variant on web.gw.coches.net. Find the surface that yields all 272k.' },
  { key: 'wallapop', total: '~750,000',
    intel: 'api.wallapop.com/api/v3/search/section is keyword/geo-scoped (40/page, next_page JWT) — NOT a flat catalog, so keyword-sweep is slow/partial. HUNT the uncapped surface: (a) wallapop SITEMAP (sitemap of all item /item/{slug} URLs?); (b) the wallapop MOBILE app API — it has a richer search (try api.wallapop.com/api/v3/general/search with proper signing, /api/v3/cars, mapbox/geo-tile enumeration, or a category browse with cursor); (c) a geo-tile sweep that covers Spain with no overlap. Find the surface enumerating the full ~750k.' },
  { key: 'autocasion', total: '115,179',
    intel: 'GraphQL gql.autocasion.com/graphql (open introspection). The search resolver returns ad ids; does it cap? HUNT: (a) sitemap of all PDP /coches-segunda-mano/{slug}-ref{ID} URLs (enumerate all 115k refs directly); (b) the GraphQL search with a cursor/offset that reaches all 115k (introspect the schema for a cursor connection / total); (c) confirm no relevance cap. Find the surface for 100%.' },
]

phase('Hunt')
log('Data-layer hunt: ' + TARGETS.length + ' giants, exhaust uncapped surfaces (parallel)')
const hunts = await parallel(TARGETS.map(t => () =>
  agent(CREED + '\n\n' + VECTORS +
    '\n\nYOUR GIANT: ' + t.key + ' (declared ' + t.total + ' cars).\nINTEL: ' + t.intel +
    '\n\nWork ONLY in C:\\Users\\elias\\projects\\cardeep — NEVER write to any cardex/CARDEX path. FIRST load web tools via ToolSearch select:WebSearch,WebFetch. Probe LIVE with curl_cffi (project python C:/Users/elias/AppData/Local/Programs/Python/Python311/python). Write the uncapped-surface recipe (or the per-vector dead-log) to the ABSOLUTE path C:\\Users\\elias\\projects\\cardeep\\docs\\architecture\\tier1_recipes\\' + t.key + '_datalayer.md. Do the work in your turn — RUN the probes, do not defer. Return the structured result.',
    { label: 'hunt:' + t.key, phase: 'Hunt', schema: HUNT_SCHEMA, agentType: 'general-purpose' })))
const ok = hunts.filter(Boolean)
const found = ok.filter(h => h.uncapped_surface_found)
log('Uncapped surface FOUND: ' + (found.map(h => h.platform).join(', ') || 'none — facet fallback'))

phase('Synthesis')
const rows = ok.map(h => h.platform + ': ' + (h.uncapped_surface_found ? 'UNCAPPED via ' + (h.method || '').slice(0, 90) : 'still capped -> ' + (h.fallback_if_none || '').slice(0, 60))).join('\n')
const syn = await agent(
  'Synthesize the CARDEEP data-layer hunt into C:\\Users\\elias\\projects\\cardeep\\docs\\architecture\\tier1_recipes\\DATALAYER_STATUS.md: per giant, the uncapped surface that enumerates 100% (or the honest residual). Results:\n' + rows +
  '\n\nReturn {uncapped, still_capped, summary}.',
  { label: 'synthesis:datalayer', phase: 'Synthesis', agentType: 'general-purpose', schema: SYN_SCHEMA })

return { hunts: ok, found_count: found.length, synthesis: syn }

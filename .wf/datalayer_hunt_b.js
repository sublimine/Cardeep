export const meta = {
  name: 'cardeep-datalayer-hunt-b',
  description: 'Data-layer hunt for the REMAINING Tier-1 giants (milanuncios, spoticar, motor.es, coches.com): the uncapped surface (sitemap/mobile-API/cursor) that serves 100%',
  whenToUse: 'Cover the rest of the Tier-1 universe data-layer-first',
  phases: [{ title: 'Hunt', detail: 'one hunter per remaining giant (parallel)' }, { title: 'Synthesis', detail: 'rollup' }],
}

const CREED = [
  'CARDEEP doctrine (owner order): find the DATA LAYER the site/app uses to serve the FULL inventory with NO pagination cap.',
  'Exhaust every uncapped surface BEFORE any province/facet workaround. Legitimate public-data market research.',
].join(' ')
const VECTORS = [
  'UNCAPPED-SURFACE VECTORS in order: 1) SITEMAP (robots.txt -> sitemap index of ALL PDP URLs = the full enumeration).',
  '2) MOBILE APP API (cursor/scroll, no web cap; try api/app/m hosts, /v4 /v5, X-App headers, searchAfter/scrollId).',
  '3) ALTERNATE/CURSOR endpoint / GraphQL cursor connection / SEO/feed/export endpoint. 4) For browser-walled (camoufox)',
  'platforms, the in-browser XHR the SPA calls. 5) ONLY if all exhausted with evidence: facet partition. Probe LIVE with',
  'curl_cffi (and camoufox where the wall needs it). The WIN = a reproducible surface enumerating 100% of the declared N.',
].join('\n')

const STR = { type: 'string' }
const STRARR = { type: 'array', items: { type: 'string' } }
const HUNT_SCHEMA = {
  type: 'object', required: ['platform', 'uncapped_surface_found', 'vectors_tried', 'recipe_file'],
  properties: { platform: STR, declared_total: STR, uncapped_surface_found: { type: 'boolean' },
    method: STR, coverage_proof: STR, vectors_tried: STRARR, recipe_file: STR, fallback_if_none: STR },
}
const SYN_SCHEMA = { type: 'object', required: ['summary'], properties: { uncapped: STRARR, still_capped: STRARR, summary: STR } }

const TARGETS = [
  { key: 'milanuncios', total: '~667,000',
    intel: 'Adevinta, Imperva reese84 wall; camoufox warm-up mints the cookie. SRP is server-rendered (no clean API). HUNT: (a) SITEMAP — does milanuncios.com expose a sitemap of all /coches-...htm PDP URLs? (b) its MOBILE app API (Adevinta apps hit a gateway; try the same web.gw family with x-schibsted-tenant for milanuncios, or app hosts); (c) the in-page XHR the SPA calls after the camoufox warm-up (capture it). Find the surface for all ~667k.' },
  { key: 'spoticar', total: '~50,000',
    intel: 'Stellantis, AkamaiGHost 403 to curl. HUNT: (a) SITEMAP (does spoticar.es expose a PDP sitemap past Akamai? try via BotBrowser/camoufox); (b) the internal /api/count-published-vo + the listing API the SPA calls (capture XHR in a stealth browser); (c) the Woosmap stores API for dealers. Find the listing surface; use BotBrowser/Byparr/camoufox for the Akamai sensor — free, no residential IP.' },
  { key: 'motor_es', total: '~51,000',
    intel: 'Cloudflare-passing curl; /vercoche/ PDP robots-disallowed; sitemap_vo.xml has category URLs. HUNT: (a) a deeper sitemap that lists actual PDPs (not just categories); (b) the internal listing API the SPA/Next app calls (__NEXT_DATA__ or an XHR); (c) cursor pagination. Find the full ~51k surface.' },
  { key: 'coches_com', total: '92,259 (sitemap-verified)',
    intel: 'ALREADY has the uncapped surface: sitemap/coches/Todo-VO-{0..3}.xml = 92,259 PDP URLs (verified). The connector exists (coches_com_wholesale.py) but is SLOW (one HTML PDP per car). HUNT a FASTER surface: (a) is there a JSON/API behind the PDP (the __NEXT_DATA__ is already used — is there a bulk search API like coches.net?); (b) a mobile API; (c) can the PDP fetch be parallelized harder. Goal: same 92k but 10x faster.' },
]

phase('Hunt')
log('Data-layer hunt B: ' + TARGETS.length + ' remaining giants (parallel)')
const hunts = await parallel(TARGETS.map(t => () =>
  agent(CREED + '\n\n' + VECTORS + '\n\nYOUR GIANT: ' + t.key + ' (declared ' + t.total + ').\nINTEL: ' + t.intel +
    '\n\nWork ONLY in C:\\Users\\elias\\projects\\cardeep — NEVER write to any cardex/CARDEX path. FIRST load web tools via ToolSearch select:WebSearch,WebFetch. Probe LIVE (project python C:/Users/elias/AppData/Local/Programs/Python/Python311/python; curl_cffi + camoufox installable). Write to ABSOLUTE path C:\\Users\\elias\\projects\\cardeep\\docs\\architecture\\tier1_recipes\\' + t.key + '_datalayer.md. RUN the probes in your turn, do not defer. Return the structured result.',
    { label: 'hunt:' + t.key, phase: 'Hunt', schema: HUNT_SCHEMA, agentType: 'general-purpose' })))
const ok = hunts.filter(Boolean)
log('Uncapped found: ' + ok.filter(h => h.uncapped_surface_found).map(h => h.platform).join(', '))

phase('Synthesis')
const rows = ok.map(h => h.platform + ': ' + (h.uncapped_surface_found ? 'UNCAPPED ' + (h.method || '').slice(0, 80) : 'capped -> ' + (h.fallback_if_none || '').slice(0, 50))).join('\n')
const syn = await agent('Append the CARDEEP remaining-Tier-1 data-layer results to C:\\Users\\elias\\projects\\cardeep\\docs\\architecture\\tier1_recipes\\DATALAYER_STATUS.md. Results:\n' + rows + '\nReturn {uncapped, still_capped, summary}.',
  { label: 'synthesis:datalayer_b', phase: 'Synthesis', agentType: 'general-purpose', schema: SYN_SCHEMA })
return { hunts: ok, synthesis: syn }

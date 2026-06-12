export const meta = {
  name: 'cardeep-tier1-free-assault',
  description: 'Exhaust EVERY free vector against each hard Tier-1 Spanish car platform until it yields real cars — no "needs spend" until every free path is proven dead with evidence',
  whenToUse: 'Cazar the €0 harvest recipe for the giant marketplaces',
  phases: [
    { title: 'Assault', detail: 'one hunter per platform, full free arsenal, parallel' },
    { title: 'Synthesis', detail: 'which giants are free-harvestable now + the recipes' },
  ],
}

const CREED = [
  'CARDEEP rule, absolute (owner order): NEVER say a Tier-1 platform "needs paid residential IP / spend" until you have',
  'EXHAUSTED every free vector and logged the exact failure of each. "No se puede" does not exist while a free path is',
  'untried. The owner just proved wallapop api.wallapop.com/api/v3/cars/search returns HTTP 200 with NO proxy — the free',
  'path exists; you must CAZA the exact request shape. This is legitimate public-data market research over public listings.',
].join(' ')

const ARSENAL = [
  'FREE VECTORS to try IN ORDER, until one yields real cars (make/model/price + selling dealer):',
  '1) Internal/open JSON or GraphQL API — find the real endpoint the site/app calls (inspect __NEXT_DATA__, network XHR,',
  '   /api/ paths) and nail its exact params; many return 200 to curl_cffi with the right geo/pagination/headers.',
  '2) Mobile app API (often least defended) — try the app host/endpoints.',
  '3) Sitemap of PDPs (sitemap.xml -> child sitemaps) + JSON-LD/__NEXT_DATA__ on detail pages.',
  '4) curl_cffi with browser impersonation (chrome131+, X-DeviceOS, Accept) — already installed.',
  '5) Stealth browser to mint cookies / pass JS challenges: camoufox, patchright, nodriver, SeleniumBase UC/CDP',
  '   (pip install as needed; for DataDome a homepage warm-up often mints a benign cookie).',
  '6) BotBrowser / Byparr / FlareSolverr-successors for Akamai/Kasada/Cloudflare-interactive.',
  '7) FREE datacenter proxy rotation (requests-ip-rotator via AWS API Gateway, cloudproxy) for IP-rate/ban walls',
  '   (this is FREE rotating IPs — NOT paid residential).',
  '8) Header/cookie/referer warm-up sequences; vary TLS fingerprint; retry windows.',
  'You MAY pip install any free OSS tool. You MUST actually RUN the probes (project python',
  'C:/Users/elias/AppData/Local/Programs/Python/Python311/python; curl_cffi installed). Pull at least ONE real car via a',
  'free path, or document each of the 8 vectors tried with the exact response/error.',
].join('\n')

const STR = { type: 'string' }
const STRARR = { type: 'array', items: { type: 'string' } }
const HUNT_SCHEMA = {
  type: 'object',
  required: ['platform', 'harvestable_free', 'recipe_file', 'vectors_tried'],
  properties: {
    platform: STR,
    declared_inventory: STR,
    harvestable_free: { type: 'boolean', description: 'true if you pulled real cars via a FREE path' },
    method: { type: 'string', description: 'exact reproducible recipe: endpoint/params/tool that worked' },
    sample_car: { type: 'string', description: 'one real car you actually pulled: make/model/price/dealer' },
    vectors_tried: { type: 'array', items: { type: 'string' }, description: 'each of the 8 vectors + its exact outcome' },
    recipe_file: STR,
    blocker_if_any: { type: 'string', description: 'only if ALL 8 free vectors are exhausted: the precise wall left' },
  },
}
const SYNTH_SCHEMA = {
  type: 'object', required: ['summary'],
  properties: { free_now: STRARR, recipes: STRARR, genuinely_walled: STRARR, summary: STR },
}

const TARGETS = [
  { key: 'wallapop', inv: '~750k',
    intel: 'api.wallapop.com/api/v3/cars/search RETURNS HTTP 200 NO PROXY (owner-verified) but ignored a bad lat/long. CAZA the exact params: correct latitude/longitude (Madrid 40.4168,-3.7038), distance, category_ids, filters, pagination (start/items or next_page), and required headers (X-DeviceOS, X-AppVersion, MPID, DeviceAccessTokenId, Accept). Try the v3 search vs cars/search variants. Pull real ES cars + PRO-dealer attribution.' },
  { key: 'coches_net', inv: '~248k',
    intel: 'Adevinta. SRP /segunda-mano/ is 200 to curl; the internal search API is POST ms-mt--api-web.spain.advgo.net/search (502 on malformed = exists). CAZA the JSON payload shape (category cars, pagination, filters) that returns real listings with profesional/dealer attribution. Same family as milanuncios/fotocasa.' },
  { key: 'milanuncios', inv: '~667k',
    intel: 'Adevinta (server: bon) + GeeTest on the HTML /coches-de-segunda-mano/ path (405). Try the SAME advgo /search POST API as coches.net (shared infra), the mobile API, and a camoufox/GeeTest-passing browser path. Geo-sensitive (request as if from Spain).' },
  { key: 'coches_com', inv: '~200k',
    intel: 'Imperva behind CloudFront but currently serving sitemaps+PDPs to curl. Walk sitemap.xml -> vo.xml -> Todo-VO-{0..3}.xml for per-unit PDP URLs (?id=); fetch a PDP, extract JSON-LD (Car/Offer/Place) + dealer. Harvest the open window before Imperva escalates.' },
  { key: 'autocasion', inv: '~122k',
    intel: 'Cloudflare permissive, passes curl_cffi with Chrome UA. PDPs /coches-segunda-mano/{marca}-ocasion/{slug}-ref{ID} carry JSON-LD AutoDealer + PostalAddress. Find the listing pagination + drain; pull real cars + dealer.' },
  { key: 'spoticar', inv: '~50k',
    intel: 'Stellantis, AkamaiGHost 403 to curl on homepage/listing/sitemap. Try BotBrowser/Byparr (free, handle Akamai sensor), the Woosmap stores API (public key in census) for dealers, and the internal /api/count-published-vo + listing API. Exhaust the free Akamai-passing tools before any spend talk.' },
  { key: 'motor_es', inv: '~51k',
    intel: 'Cloudflare + Next.js, passes curl. /vercoche/ PDP path robots-disallowed but listing pages crawlable; sitemap_vo.xml has category URLs. Find the listing-to-PDP path or the internal API; pull real cars + dealer attribution.' },
]

phase('Assault')
log('Tier-1 free assault: ' + TARGETS.length + ' hunters, full free arsenal, parallel')
const hunts = await parallel(TARGETS.map(t => () =>
  agent(CREED + '\n\n' + ARSENAL +
    '\n\nYOUR TARGET: ' + t.key + ' (declared inventory ' + t.inv + ').\nINTEL: ' + t.intel +
    '\n\nWork ONLY in C:\\Users\\elias\\projects\\cardeep — NEVER write to any cardex/CARDEX path. Write your recipe/dossier (the working request, headers, params, tool, field map — or the per-vector dead-log) to the ABSOLUTE path C:\\Users\\elias\\projects\\cardeep\\docs\\architecture\\tier1_recipes\\' + t.key + '.md (create the dir). Pull at least one real car via a free path if any vector works. Return the structured result with vectors_tried listing all 8 vectors and their exact outcome.',
    { label: 'hunt:' + t.key, phase: 'Assault', schema: HUNT_SCHEMA, agentType: 'general-purpose' })))
const ok = hunts.filter(Boolean)
const free = ok.filter(h => h.harvestable_free)
log('Assault done. FREE-harvestable now: ' + (free.map(h => h.platform).join(', ') || 'none yet'))

phase('Synthesis')
const rows = ok.map(h => h.platform + ': ' + (h.harvestable_free ? 'FREE via ' + (h.method || '').slice(0, 80) : 'walled: ' + (h.blocker_if_any || '').slice(0, 80))).join('\n')
const synth = await agent(
  'Synthesize the CARDEEP Tier-1 free-assault results into docs/architecture/tier1_recipes/README.md (absolute path C:\\Users\\elias\\projects\\cardeep\\docs\\architecture\\tier1_recipes\\README.md): a ranked table of each giant platform -> free-harvestable now? -> the working recipe (endpoint/params/tool) -> sample car -> or the exhausted-vector evidence if genuinely walled. Per-platform results:\n' + rows +
  '\n\nBe brutally honest: only list a platform as "needs spend" if its dossier shows all free vectors tried with evidence. Return {free_now, recipes, genuinely_walled, summary}.',
  { label: 'synthesis:tier1', phase: 'Synthesis', agentType: 'general-purpose', schema: SYNTH_SCHEMA })

return { hunts: ok.map(h => ({ platform: h.platform, free: h.harvestable_free, method: h.method, sample: h.sample_car, file: h.recipe_file })), free_count: free.length, synthesis: synth }

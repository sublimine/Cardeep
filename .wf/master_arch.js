export const meta = {
  name: 'cardeep-master-architecture',
  description: 'Deepest CARDEEP architecture: parallel architect fleet per pillar + exhaustive Tier-1 census, synthesized into a master plan with adversarial review',
  whenToUse: 'Produce the institutional-grade architecture/plan/organization for CARDEEP before further code',
  phases: [
    { title: 'Recon', detail: 'exhaustive live Tier-1 census + entity ontology + arsenal-per-defense' },
    { title: 'Design', detail: 'one architect per pillar, deep, writes docs/architecture' },
    { title: 'Synthesis', detail: 'master architect consolidates into the master plan' },
    { title: 'Adversarial', detail: 'council stress-tests for gaps; gap-closer integrates' },
  ],
}

const MISSION = [
  'CARDEEP mission (owner exact intent): a LIVE, VERIFIED database holding, structured to the last atom,',
  '100% of Spain car points-of-sale, from the giant platform to the lost mountain garage:',
  'official dealerships, used-car traders (compraventas), garages, scrapyards (desguaces),',
  'rent-a-car selling ex-fleet, auctions, importers, AND the giant marketplaces themselves.',
  'For EACH entity: find it, extract ALL its stock, serve it in a live API with full delta',
  '(additions, removals, price changes, photo changes, complete history), recipe saved,',
  'ordered by country/province/comarca/city with a unique code per dealer. If a source fails,',
  'an alert fires with the EXACT origin, it self-repairs, and Cardeep never falls.',
  'Tier-1 (hard-defense platforms) separated ABSOLUTELY from the rest. Cheap/massive work uses',
  'local LLMs; expensive intelligence only decides. Everything to GitHub main, documented.',
].join(' ')

const CONTEXT = [
  'EXISTING REALITY (read these in repo C:/Users/elias/projects/cardeep before designing; build on what exists):',
  'docs/research/SOURCES_ES.md + SOURCES_ES_raw.json = a 56-agent live census of 181 Spanish sources',
  '(official registries, associations, OEM APIs, platforms, directories, scrapyards, OSS arsenal) = ground truth.',
  'docs/ARCHITECTURE.md, docs/ORQUESTACION.md, docs/workflows/README.md = current first-pass (to be SUPERSEDED).',
  'pipeline/ (deterministic Python: sources adapters, discover/scrape/recipe/ingest/verify, geocode),',
  'services/api (FastAPI+asyncpg), migrations/ (PG16), countries/ES/recipes/. Live DB ~12800 entities',
  '(desguace 1292, concesionario 1569, compraventa 2753, garaje 7200) + ~22k AS24 vehicles. PG16 cardeep-pg :5433.',
  'ARSENAL alive 2026 (from census): Scrapling, camoufox, curl_cffi, patchright, nodriver/zendriver, SeleniumBase,',
  'browserforge, Byparr, BotBrowser, is-antibot, browsers-benchmark. Current code WRONGLY used plain urllib;',
  'the redesign MUST use this arsenal and target DATA-LAYER surfaces (internal APIs, GraphQL, sitemaps), not HTML pagination.',
  'STANDARD: institutional-grade, deepest possible. Anti-hallucination: mark [VERIFIED] vs [ASSUMED]; no placeholders.',
  'Code/comments in English; prose may be Spanish or English.',
].join(' ')

const STR = { type: 'string' }
const STRARR = { type: 'array', items: { type: 'string' } }

const PILLAR_SCHEMA = {
  type: 'object',
  required: ['pillar', 'file_written', 'summary', 'key_decisions'],
  properties: {
    pillar: STR,
    file_written: STR,
    summary: STR,
    key_decisions: STRARR,
    open_questions: STRARR,
    dependencies: STRARR,
  },
}

const SYNTH_SCHEMA = {
  type: 'object',
  required: ['readme_path', 'master_plan_path', 'summary'],
  properties: {
    readme_path: STR,
    master_plan_path: STR,
    phase_count: { type: 'number' },
    contradictions_found: STRARR,
    summary: STR,
  },
}

const GAPS_SCHEMA = {
  type: 'object',
  required: ['gaps'],
  properties: { gaps: STRARR, severity: STR },
}

const CLOSER_SCHEMA = {
  type: 'object',
  required: ['gaps_closed'],
  properties: { gaps_closed: STRARR, gaps_deferred: STRARR, files_touched: STRARR },
}

const RECON = [
  { key: '00-TIER1-REGISTRY',
    p: 'YOUR PILLAR: the DEFINITIVE, EXHAUSTIVE registry of ALL Tier-1 car platforms/marketplaces serving Spain. The owner explicitly demanded the list of ALL Tier-1 of Spain before any attack. Do a LIVE sweep (WebSearch + fetch with a Chrome UA) to find EVERY one, not just the 18 in the census. Include the giants (coches.net, autoscout24.es, milanuncios, wallapop, autocasion, coches.com, motor.es), OEM used-car portals (Spoticar, Das WeltAuto/VW Approved, renew Renault/Dacia, MB Certified, Audi Selection, BMW Premium Selection, Toyota/Lexus, Hyundai Promise, Nissan Ocasion, Kia), multi-branch chains (Flexicar, OcasionPlus, Clicars, Autohero, Crestanevada, HR Motor, compramostucoche/AUTO1), B2B/auction (BCA, Autorola, Ayvens/Autobiz), and any niche/regional platform. For EACH: real inventory size verified on-site, owner/group, FULL defense stack (Cloudflare/Akamai/DataDome/PerimeterX/Imperva/GeeTest/none via headers+challenge), the DATA-LAYER surface (internal search API endpoint+params, GraphQL, sitemap of PDPs, __NEXT_DATA__), dealer-attribution model, and free-harvestable-now vs needs-residential-proxy. Rank by inventory. Mark Tier-1 vs OPEN. FIRST load web tools via ToolSearch with query select:WebSearch,WebFetch. Write the full registry to docs/architecture/00-TIER1-REGISTRY.md as a ranked table plus a per-platform attack dossier. Be exhaustive; confess suspected gaps.' },
  { key: '01-ENTITY-ONTOLOGY',
    p: 'YOUR PILLAR: the COMPLETE ontology/taxonomy of every kind of car point-of-sale in Spain. The owner caught that only concesionarios+compraventas is wrong. Define EVERY entity type with precise boundaries: concesionario_oficial, compraventa, garaje/taller-that-sells, desguace/CAT, plataforma (a first-class entity holding inventory), cadena, rent-a-car selling ex-fleet (OK Mobility, Centauro, Record, Goldcar), subasta/auction B2B, importador, OEM-VO-central-portal, and any others you justify. For each: definition, sub-types, which census sources discover it, its inventory model (where its car stock lives), and how it relates to platforms (the same car belongs to a platform AND its selling dealer). Design the IDENTITY and DEDUP model (cdp_code) that survives cross-source overlap and distinguishes physical branches. Write docs/architecture/01-ENTITY-ONTOLOGY.md. Load web tools via ToolSearch select:WebSearch,WebFetch if you must verify a type.' },
  { key: '02-SCRAPING-ENGINE',
    p: 'YOUR PILLAR: the elite scraping engine. The current code used plain urllib (an embarrassment); redesign around the real arsenal. Design a TIERED fetch engine: Tier-0 curl_cffi with browser JA3/JA4/TLS impersonation (current Chrome floor) for JSON/API/open-HTML; Tier-1 Scrapling StealthyFetcher / camoufox stealth browser for JS-rendered plus Cloudflare/Turnstile/DataDome; Tier-2 gated by owner spend residential proxies (Decodo) plus sensors (Hyper Solutions for Akamai, 2Captcha/Capsolver for DataDome) for the hardest (Akamai/PerimeterX). Per-source auto-routing via is-antibot fingerprinting grounded in browsers-benchmark data. Doctrine: ALWAYS target the DATA LAYER (internal API/GraphQL/sitemap), never fight HTML pagination; facet-partition plus stable-sort to beat pagination caps; session-level TLS coherence; current-Chrome impersonation (JA3/JA4 rot ~6 weeks, watch X25519MLKEM768). Specify a per-defense winning tool+config table (Cloudflare, DataDome, Akamai, PerimeterX, Imperva, GeeTest). Define the recipe system (versioned per source, self-healing selectors via Scrapling). Write docs/architecture/02-SCRAPING-ENGINE.md. Load web tools via ToolSearch select:WebSearch,WebFetch to verify current arsenal/JA3 facts.' },
]

const DESIGN = [
  { key: '03-DATA-MODEL',
    p: 'YOUR PILLAR: the canonical data model and storage architecture. Design the full PostgreSQL 16 schema: geo (country/province/comarca/municipality, INE), entity (all ontology kinds, cdp_code, defense/WAF, is_tier1, recipe_version, provenance, aliases), vehicle (full spec plus photo perceptual-hash for photo-delta plus VIN/ref plus deep_link), vehicle_event (append-only NEW/GONE/PRICE_CHANGE/PHOTO_CHANGE/KM_CHANGE, complete history), platform_inventory (a car belongs to a platform AND a dealer), verification_verdict, source_health plus alert. Doctrine: INSERT-new and close-gone, never UPDATE non-mutated rows; full history retention. Design partitioning/indexing for tens of millions of vehicles plus delta. Define the live API contract (per-entity inventory, per-platform inventory, delta-since, geo grid, search) with a consistent envelope. Write docs/architecture/03-DATA-MODEL.md with concrete DDL sketches.' },
  { key: '04-ORCHESTRATION',
    p: 'YOUR PILLAR: the orchestration/control plane. Design the permanent systems (S-DISCOVER, S-INVENTORY for platform-wholesale plus per-dealer, S-VERIFY/Inquisition, S-HEALTH, S-GEO, S-CODE) and the workflows that drive them. Define two planes: deterministic Python pipeline (cheap/massive, local LLM Ollama for classify/parse/dedup) vs intelligence plane (agent fleets for recipe-hunting hard platforms plus adversarial verification). Specify the job/queue model (Redis Streams transport, at-least-once, idempotent by cdp_code), worker fleet model plus safe parallelism (a rate-governor per source to avoid bans, the real bottleneck), anti-collision contract, cost-routing (local vs cloud, model tier per task), and the scheduler. Write docs/architecture/04-ORCHESTRATION.md.' },
  { key: '05-VERIFICATION-VAM',
    p: 'YOUR PILLAR: the verification architecture. Verify EVERYTHING, distrust every number, confirm by paths different from the one that produced it; better confess a gap than sell a lie. Design VAM (multi-path adversarial verification): quorum of 2 or more orthogonal paths, the rule that the actually-landed db count MUST agree (never mask ingestion loss), per-field live verification (price-trap, year-band), and the Inquisition as a SEPARATE adversarial verifier chain (one agent asserts, another refutes). Design capture-recapture (Chapman) to estimate the TRUE denominator of Spanish car POS by crossing orthogonal sources (Paginas Amarillas, registral CNAE, OSM/FSQ, DGT). Define the publish-gate (nothing TRUSTWORTHY means not served). Write docs/architecture/05-VERIFICATION-VAM.md.' },
  { key: '06-RESILIENCE-OPS',
    p: 'YOUR PILLAR: resilience and operations. The mandate: if one fails, an alert fires with the EXACT origin, it self-repairs, and Cardeep never falls. Design per-source health watchdog (consecutive-fail tracking, status), exact-origin alerting (source_key/entity/phase), RECIPE-DRIFT detection (a source whose extraction silently changed, fields go null, auto re-derive recipe), auto-repair loops (re-fingerprint defense, escalate tier, re-receta), circuit breakers, the ban/throttle response (backoff, rotate, quarantine), observability (metrics/dashboards), and graceful degradation. Write docs/architecture/06-RESILIENCE-OPS.md.' },
  { key: '07-COVERAGE-STRATEGY',
    p: 'YOUR PILLAR: the coverage strategy and executable roadmap to 100% of Spain. Design the A-to-Z phased plan with BINARY gates: how to close each segment (platforms wholesale first for max inventory; OEM networks via JSON APIs at zero cost; long-tail via OSM/FSQ/Overture/registries plus own-site harvest; desguaces via DGT) and each geography (province by province, sealing coverage). Define the denominator-closure method (capture-recapture), the cost gates (what needs owner spend: residential proxies for DataDome/PerimeterX/Akamai platforms), the ROI order (zero-cost open first, then gated), and the 100%-sealed definition plus honest KPIs per segment/province. Sequence realistically given source rate-limits (the true bottleneck). Write docs/architecture/07-COVERAGE-STRATEGY.md.' },
  { key: '08-REPO-ORGANIZATION',
    p: 'YOUR PILLAR: the repository and organization architecture. Organizacion impecable, separating ABSOLUTELY the Tier-1 from the other groups, with total logic and coherence. Design the full folder structure (engine/, platforms/_tier1/<name>/, sources/long_tail/, countries/ES/<province>/<comarca>/<city>/dealers/<cdp_code>/ with config/recipe/manifest/tombstone, services/api, migrations, docs/architecture, ops/, config/registries). Define the ABSOLUTE Tier-1 vs long-tail separation (separate code trees, recipes, raw stores, operation). Define naming conventions, the config-as-registry pattern (platforms_es.json drives harvesters), versioned vs gitignored, and the GitHub classification. Write docs/architecture/08-REPO-ORGANIZATION.md.' },
]

const DEEP = ' Design to EXTREME depth: concrete, rigorous, no placeholders. This is the deepest architecture the owner has ever seen. Write your doc, then return the structured summary.'

phase('Recon')
log('Recon: exhaustive Tier-1 census + entity ontology + arsenal-per-defense (parallel)')
const recon = await parallel(RECON.map(r => () =>
  agent(MISSION + '\n\n' + CONTEXT + '\n\n' + r.p + DEEP,
    { label: 'recon:' + r.key, phase: 'Recon', schema: PILLAR_SCHEMA, agentType: 'general-purpose' })))
const reconOk = recon.filter(Boolean)
log('Recon done: ' + reconOk.map(r => r.pillar).join(' | '))

phase('Design')
log('Design: architect fleet, one deep pillar each (parallel)')
const designIntro = '\n\nThe Recon phase wrote docs/architecture/00-TIER1-REGISTRY.md, 01-ENTITY-ONTOLOGY.md, 02-SCRAPING-ENGINE.md (read any relevant to your pillar).\n\n'
const design = await parallel(DESIGN.map(d => () =>
  agent(MISSION + '\n\n' + CONTEXT + designIntro + d.p + DEEP,
    { label: 'design:' + d.key, phase: 'Design', schema: PILLAR_SCHEMA, agentType: 'general-purpose' })))
const designOk = design.filter(Boolean)
log('Design done: ' + designOk.length + '/' + DESIGN.length + ' pillars')

phase('Synthesis')
const allPillars = reconOk.concat(designOk).map(p => p.pillar + ': ' + p.summary).join('\n')
const synth = await agent(
  MISSION + '\n\n' + CONTEXT + '\n\nAll architecture pillars are written under docs/architecture/ (00..08). Summaries:\n' + allPillars +
  '\n\nYOUR JOB (master architect): READ every docs/architecture/*.md, then synthesize TWO governing artifacts. 1) docs/architecture/README.md = the architecture overview: the system at a glance, how the pillars fit, the permanent systems, the two planes, the absolute Tier-1/long-tail separation, a single text diagram of the whole. 2) docs/MASTER_PLAN.md = the executable A-to-Z plan: phases with BINARY gates and acceptance criteria, the file/folder structure to build, the build sequence (dependencies), the cost gates, and the definition of 100% done. Reconcile contradictions between pillars and note them. This supersedes the first-pass docs. No placeholders. Return {readme_path, master_plan_path, phase_count, contradictions_found, summary}.',
  { label: 'synthesis:master', phase: 'Synthesis', agentType: 'general-purpose', schema: SYNTH_SCHEMA })

phase('Adversarial')
const LENSES = [
  'completeness: any segment, platform, entity-type, or failure-mode missing?',
  'feasibility and anti-detection realism: will the scraping engine actually beat these defenses in 2026, or is it wishful?',
  'coherence and scale: do pillars contradict; is the Tier-1/long-tail separation truly absolute; is the data model sound at tens-of-millions scale?',
]
const critiques = await parallel(LENSES.map(lens => () =>
  agent('Adversarially stress-test the CARDEEP master architecture for an owner who demands the deepest, most perfect plan ever. Read docs/architecture/*.md and docs/MASTER_PLAN.md. Lens: ' + lens + '. Find the REAL gaps, weak assumptions, missing pieces. Be ruthless. Return concrete actionable gaps.',
    { label: 'review:' + lens.slice(0, 16), phase: 'Adversarial', agentType: 'general-purpose', schema: GAPS_SCHEMA })))
const gaps = critiques.filter(Boolean).flatMap(c => c.gaps || [])
log('Adversarial review: ' + gaps.length + ' gaps found')

const closer = gaps.length ? await agent(
  'You are the master architect closing gaps the adversarial review found in the CARDEEP architecture. Gaps:\n' +
  gaps.map((g, i) => (i + 1) + '. ' + g).join('\n') +
  '\n\nFor each REAL gap, fix it by editing the relevant docs/architecture/*.md or docs/MASTER_PLAN.md (add the missing section/decision). Then append a "Gaps closed" section to docs/MASTER_PLAN.md listing what was addressed and what is deliberately deferred (with reason). Return {gaps_closed, gaps_deferred, files_touched}.',
  { label: 'closer:gaps', phase: 'Adversarial', agentType: 'general-purpose', schema: CLOSER_SCHEMA }) : null

return {
  pillars: reconOk.concat(designOk).map(p => ({ pillar: p.pillar, file: p.file_written, decisions: p.key_decisions })),
  synthesis: synth,
  adversarial_gaps: gaps,
  gaps_closed: closer ? closer.gaps_closed : [],
  gaps_deferred: closer ? closer.gaps_deferred : [],
}

export const meta = {
  name: 'cardeep-tooling-audit',
  description: 'Deep live audit of the best-in-class tool for every micro and macro task of CARDEEP scraping, researched across GitHub/forums/benchmarks, to build the greatest used-car scraping system ever',
  whenToUse: 'Choose the most modern, robust, bulletproof tool per task and document configs',
  phases: [
    { title: 'Audit', detail: 'one researcher per task-domain, live web/repo research (parallel)' },
    { title: 'Synthesis', detail: 'master bill-of-materials: chosen stack + config + rationale' },
    { title: 'Challenge', detail: 'adversarial: is any pick already obsolete or insufficient?' },
  ],
}

const BRIEF = [
  'CARDEEP wants to be the GREATEST second-hand vehicle scraping + indexing system ever built, for 100% of Spain',
  'car points-of-sale and the giant marketplaces, with full inventory + live delta + per-source recipe + verified API.',
  'You are a tooling researcher. For your assigned task-domain, audit the LIVE 2026 ecosystem and pick the MOST',
  'updated, modern, bulletproof, robust tool(s) — do NOT settle for the obvious/known one without proving it is still',
  'best. Research across MANY sources: GitHub (stars, last commit/release recency, open-issue health, maintenance),',
  'benchmarks, forums, Reddit, vendor docs. For EACH candidate: alive-or-dead (last release date), what it solves,',
  'strengths/weaknesses, and a concrete recommendation with integration notes + a sample CONFIG. Flag DEAD/abandoned',
  'tools explicitly (do not recommend corpses). End with: is CARDEEP current choice (if any) good enough, or what',
  'replaces it. Anti-hallucination: mark [VERIFIED] (you fetched the repo/page) vs [ASSUMED]; cite the source URL.',
  'FIRST load web tools via ToolSearch with query select:WebSearch,WebFetch. Write your audit to docs/architecture/tooling/<file>.',
].join(' ')

const STR = { type: 'string' }
const STRARR = { type: 'array', items: { type: 'string' } }
const AUDIT_SCHEMA = {
  type: 'object',
  required: ['domain', 'file_written', 'recommended', 'rationale'],
  properties: {
    domain: STR,
    file_written: STR,
    recommended: STRARR,
    rejected_or_dead: STRARR,
    rationale: STR,
    config_notes: STR,
  },
}
const BOM_SCHEMA = {
  type: 'object',
  required: ['bom_path', 'summary'],
  properties: { bom_path: STR, stack: STRARR, upgrades_vs_current: STRARR, summary: STR },
}
const CHALLENGE_SCHEMA = {
  type: 'object',
  required: ['obsolete_or_weak'],
  properties: { obsolete_or_weak: STRARR, better_alternatives: STRARR },
}

const DOMAINS = [
  { key: 'T01-tls-http', f: 'T01-tls-http-clients.md', t: 'No-browser HTTP clients with TLS/JA3/JA4 impersonation: curl_cffi vs primp vs rnet vs tls-client vs hrequests vs others. HTTP/2+3, Akamai/JA4 fingerprints, ML-KEM (X25519MLKEM768) support, current-Chrome floor, throughput.' },
  { key: 'T02-stealth-browser', f: 'T02-stealth-browsers.md', t: 'Stealth/undetected browsers: camoufox vs patchright vs nodriver vs zendriver vs SeleniumBase UC/CDP vs BotBrowser vs rebrowser-patches vs undetected variants. Anti-detect depth, benchmarks vs Cloudflare/DataDome/Akamai, maintenance.' },
  { key: 'T03-antibot-solving', f: 'T03-antibot-and-captcha.md', t: 'Anti-bot challenge solving + detection: FlareSolverr vs Byparr, Cloudflare Turnstile/DataDome/PerimeterX/GeeTest solvers, captcha services (2Captcha vs CapSolver vs Capmonster vs others), is-antibot detection libs. Success rates, cost.' },
  { key: 'T04-proxies', f: 'T04-proxy-fleet.md', t: 'Proxy providers + rotation for Spain residential/mobile: Decodo(Smartproxy) vs Oxylabs vs Bright Data vs IPRoyal vs Evomi vs others, pricing per GB, ES geo-targeting, session stickiness; rotation/management libs. (Owner gates spend — recommend best value.)' },
  { key: 'T05-fingerprint', f: 'T05-fingerprint-generation.md', t: 'Browser/header/TLS fingerprint generation + consistency: browserforge vs fakebrowser vs others; UA/sec-ch-ua/Accept coherence; JA3/JA4 rotation; canvas/WebGL/font spoof generators.' },
  { key: 'T06-framework', f: 'T06-scraping-framework.md', t: 'Scraping framework/orchestration: Scrapling vs Scrapy vs Crawlee-python vs Frontera vs custom asyncio. Self-healing selectors, async concurrency, retry/middleware, scale to millions.' },
  { key: 'T07-parsing', f: 'T07-parsing-extraction.md', t: 'HTML/JSON parsing + extraction: selectolax vs lxml vs parsel vs BeautifulSoup; JSON-LD extraction; regex-vs-LLM decision boundary; structured extraction with local LLM (outlines/instructor/lm-format-enforcer).' },
  { key: 'T08-local-llm', f: 'T08-local-llm.md', t: 'Local LLM for massive/cheap classify/parse/dedup: Ollama vs vLLM vs llama.cpp; best small models 2026 (qwen2.5/qwen3, llama3.x, gemma2/3, phi) for structured extraction on a CPU/modest-GPU; structured-output enforcement; throughput.' },
  { key: 'T09-dedup', f: 'T09-dedup-entity-resolution.md', t: 'Dedup / entity resolution for cross-source entities: Splink vs dedupe vs recordlinkage; fuzzy matching (rapidfuzz vs jellyfish); embedding-based (sentence-transformers/model2vec) blocking; address/name normalization.' },
  { key: 'T10-geo', f: 'T10-geocoding-address.md', t: 'Geocoding + address parsing for Spain: self-host Nominatim vs Pelias vs Photon; libpostal/pypostal for address parsing; province/municipality polygon point-in-polygon (shapely + INE/IGN boundaries); current nearest-neighbor — is it enough?' },
  { key: 'T11-image-hash', f: 'T11-perceptual-hash.md', t: 'Perceptual image hashing for photo-delta detection: imagehash (pHash/dHash/wHash) vs blockhash vs PDQ vs CLIP/embedding similarity. Robustness to re-encode/watermark/crop; speed at scale.' },
  { key: 'T12-queue-workers', f: 'T12-queue-and-workers.md', t: 'Job queue/transport + Python workers at scale: Redis Streams vs RabbitMQ vs NATS JetStream vs Kafka; worker libs arq vs dramatiq vs taskiq vs celery vs Temporal; at-least-once, idempotency, backpressure.' },
  { key: 'T13-datastore', f: 'T13-datastore.md', t: 'Datastore for tens of millions of vehicles + append-only delta + geo: PostgreSQL 16/17 + partitioning + pg_trgm + PostGIS + (TimescaleDB?) vs ClickHouse for the analytics/delta layer; hybrid OLTP+OLAP. Index/partition strategy.' },
  { key: 'T14-api', f: 'T14-api-framework.md', t: 'API framework: FastAPI vs Litestar vs Robyn vs Granian-served; async asyncpg/SQLAlchemy 2.0; pagination/caching; serving per-entity + per-platform inventory + delta at scale.' },
  { key: 'T15-orchestration', f: 'T15-durable-orchestration.md', t: 'Durable scheduling/orchestration of the permanent systems: APScheduler vs Temporal vs Prefect vs Dagster vs Windmill; crash-safe long-running jobs, retries, observability of the pipeline DAG.' },
  { key: 'T16-observability', f: 'T16-observability.md', t: 'Observability + alerting: OpenTelemetry + Prometheus + Grafana vs SigNoz vs VictoriaMetrics; structured logging (structlog/loguru); error tracking (Sentry/GlitchTip); the exact-origin alert channel.' },
]

const AUDIT_CLOSER = ' Be ruthless about recency: a tool not updated in 12+ months is suspect. Recommend the bulletproof modern pick + a fallback. Write your doc, then return the structured result.'

phase('Audit')
log('Tooling audit: ' + DOMAINS.length + ' researchers, live web/repo research (parallel)')
const audits = await parallel(DOMAINS.map(d => () =>
  agent(BRIEF + '\n\nYOUR TASK-DOMAIN: ' + d.t + '\nWrite to docs/architecture/tooling/' + d.f + '.' + AUDIT_CLOSER,
    { label: 'audit:' + d.key, phase: 'Audit', schema: AUDIT_SCHEMA, agentType: 'general-purpose' })))
const ok = audits.filter(Boolean)
log('Audited: ' + ok.map(a => a.domain).join(' | '))

phase('Synthesis')
const picks = ok.map(a => a.domain + ' -> ' + (a.recommended || []).join(', ')).join('\n')
const bom = await agent(
  BRIEF + '\n\nAll tool audits are written under docs/architecture/tooling/ (T01..T16). Picks:\n' + picks +
  '\n\nYOUR JOB (chief architect of the stack): READ every docs/architecture/tooling/*.md and synthesize docs/architecture/tooling/TOOLING.md = the master BILL OF MATERIALS: for EVERY micro and macro task of CARDEEP, the chosen tool with its version, why it beats alternatives, and a config snippet. Include a clear table (task -> tool -> version -> config -> rationale) and a section "Upgrades vs current code" (curl_cffi/scrapling already partially used; plain urllib must die). No placeholders. Return {bom_path, stack, upgrades_vs_current, summary}.',
  { label: 'synthesis:bom', phase: 'Synthesis', agentType: 'general-purpose', schema: BOM_SCHEMA })

phase('Challenge')
const chal = await agent(
  'Adversarially challenge the CARDEEP tooling bill-of-materials. Read docs/architecture/tooling/*.md and TOOLING.md. For an owner who demands the most modern bulletproof stack ever: which picks are already obsolete, insufficient at scale, unmaintained, or about to be superseded in 2026? What is the better alternative for each? Be specific and current.',
  { label: 'challenge:stack', phase: 'Challenge', agentType: 'general-purpose', schema: CHALLENGE_SCHEMA })

return {
  audits: ok.map(a => ({ domain: a.domain, file: a.file_written, recommended: a.recommended })),
  bom: bom,
  challenge: chal,
}

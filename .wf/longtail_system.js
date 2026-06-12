export const meta = {
  name: 'cardeep-longtail-system',
  description: 'The OTHER groups, each with its own system: OEM-VO portals as connectors + long-tail own-website inventory harvest by CMS family',
  whenToUse: 'Advance the non-Tier-1 groups (OEM, long-tail dealer own-sites, desguace networks) toward inventory',
  phases: [
    { title: 'Group', detail: 'one agent per group system (parallel)' },
    { title: 'Synthesis', detail: 'rollup of the demás-grupos progress' },
  ],
}

const BRIEF = [
  'CARDEEP — the OWNER demands ALL groups worked, not just Tier-1 marketplaces: "los demás con su sistema".',
  'Beyond the giant marketplaces, the inventory lives in: OEM certified-used portals (renew Renault/Dacia, Das WeltAuto VW,',
  'Spoticar Stellantis, MB Certified, etc.), and the LONG TAIL — each dealer/compraventa OWN WEBSITE. The long-tail is',
  'harvested by CMS FAMILY: group dealers by the platform their website runs (WordPress, a DMS vendor, a known dealer-site',
  'builder), then ONE recipe per family harvests many dealers. This is the multiplier. Legitimate public-data market research.',
  'The live DB has ~14k+ entities, many concesionario_oficial/compraventa with a website column populated.',
  'Mirror the proven connector pattern: pipeline/platform/coches_net_wholesale.py (platform-as-entity + dual-membership +',
  'batch ingest + governor + VAM) for the OEM portals; for long-tail use the per-dealer recipe model (pipeline/discover +',
  'pipeline/recipe + pipeline/ingest). Work ONLY in C:\\Users\\elias\\projects\\cardeep — NEVER write to any cardex/CARDEX path.',
  'project python C:/Users/elias/AppData/Local/Programs/Python/Python311/python; curl_cffi installed; DB cardeep-pg :5433.',
  'FIRST load web tools via ToolSearch select:WebSearch,WebFetch. RUN your probes/builds in your turn — do not defer.',
].join(' ')

const STR = { type: 'string' }
const STRARR = { type: 'array', items: { type: 'string' } }
const GROUP_SCHEMA = {
  type: 'object', required: ['group', 'built', 'summary'],
  properties: { group: STR, built: { type: 'boolean' }, surface: STR, entities_or_cars: { type: 'number' },
    method: STR, file: STR, vam: STR, summary: STR, issue: STR },
}
const SYN_SCHEMA = { type: 'object', required: ['summary'], properties: { progressed: STRARR, summary: STR } }

const GROUPS = [
  { key: 'oem_vo_renew', t: 'OEM-VO portal: renew (Renault/Dacia). es.renew.auto exposes raw Elasticsearch facet params (brand.label.raw=...) = clean faceted JSON, ~5,700 cars with strong per-dealer attribution. Build pipeline/platform/renew_wholesale.py mirroring coches_net (plataforma entity kind=oem_vo_portal, source_group=oem_vo_portal, defense_tier=t0/t1; per-car dealer + platform_listing + delta + VAM). Probe the JSON surface live, RUN a harvest of a substantial chunk, verify in DB.' },
  { key: 'oem_vo_dasweltauto', t: 'OEM-VO portal: Das WeltAuto (VW group, Motorflash-powered). Find its inventory surface (Motorflash API/JSON or per-province pages). Build pipeline/platform/dasweltauto_wholesale.py (kind=oem_vo_portal). Probe live, harvest a chunk, verify. If browser-walled, use the BFF/feature-app JSON the page calls.' },
  { key: 'longtail_classify', t: 'Long-tail CMS-family classification: query the live DB for entities WHERE website IS NOT NULL (concesionario_oficial + compraventa with own sites). Fetch a sample of their homepages (curl_cffi), CLASSIFY each by the website platform/CMS/DMS family (WordPress+plugin, a DMS vendor like Motorflash/Tecnom/Quintegia, a dealer-site builder, generic). Produce a ranked family report (which families cover the most dealers) + for the TOP family, identify the common inventory-listing pattern (the recipe seed). Write docs/architecture/longtail_families.md. This is the multiplier map for harvesting thousands of own-sites with few recipes.' },
  { key: 'longtail_recipe1', t: 'Long-tail family harvest PROOF: pick ONE concrete CMS/DMS family (e.g. Motorflash-powered dealer sites — many OEM Selection subsites use it; or a WordPress car-listing plugin). Build a family recipe + a connector pipeline/platform/family_<name>_wholesale.py that harvests the inventory of 2-3 real dealers of that family from their OWN websites into the DB (dealer entity already exists or upsert; vehicle owned by dealer; recipe saved; delta; VAM). Prove the multiplier: one recipe -> N dealers harvested. RUN it on real dealers, verify in DB.' },
]

phase('Group')
log('Demás-grupos systems: ' + GROUPS.length + ' fronts (OEM-VO portals + long-tail family) in parallel')
const res = await parallel(GROUPS.map(g => () =>
  agent(BRIEF + '\n\nYOUR FRONT: ' + g.t + '\nReturn the structured result; verify any number against the live DB yourself.',
    { label: 'group:' + g.key, phase: 'Group', schema: GROUP_SCHEMA, agentType: 'general-purpose' })))
const ok = res.filter(Boolean)
log('Fronts progressed: ' + ok.filter(r => r.built).map(r => r.group).join(', '))

phase('Synthesis')
const rows = ok.map(r => r.group + ': ' + (r.built ? (r.entities_or_cars || '?') + ' — ' + (r.method || '').slice(0, 70) : 'partial: ' + (r.issue || '?'))).join('\n')
const syn = await agent('Write the CARDEEP demás-grupos rollup to C:\\Users\\elias\\projects\\cardeep\\docs\\architecture\\GROUPS_STATUS.md. Results:\n' + rows + '\nReturn {progressed, summary}.',
  { label: 'synthesis:groups', phase: 'Synthesis', agentType: 'general-purpose', schema: SYN_SCHEMA })
return { fronts: ok, synthesis: syn }

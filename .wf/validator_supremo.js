export const meta = {
  name: 'cardeep-validator-supremo',
  description: 'Deepest possible verification/audit architecture for CARDEEP: parallel facet designers for denominator-proof, completion-proof, the Inquisition, lie/gap detection, and statistical rigor',
  whenToUse: 'Design the supreme multi-path validator so CARDEEP never validates a number it cannot prove',
  phases: [
    { title: 'Facets', detail: 'one architect per verification facet (parallel)' },
    { title: 'Protocols', detail: 'worked verification protocols for the owner two questions' },
    { title: 'Synthesis', detail: 'master validator spec + the Gestionador' },
    { title: 'MetaAudit', detail: 'can the validator itself be fooled? adversarial meta-review' },
  ],
}

const CREED = [
  'CARDEEP NEVER SELLS LIES. This is absolute. Before a single number is validated it must be proven',
  'by MULTIPLE INDEPENDENT PATHS, never by the path that produced it. If an agent says "500k entities exist',
  'in Spain", we must be able to PROVE or BOUND that. If it says "20k entities completed end-to-end", an',
  'INDEPENDENT validator must confirm it. Better to confess a gap than sell a lie. The validator detects',
  'inflated counts, silent caps, silently-dropped fields, staleness, fabrication, and coverage gaps, and a',
  'manager routes each detection to fix/research/quarantine/escalate. Verification is the heart of CARDEEP,',
  'not a feature.',
].join(' ')

const CONTEXT = [
  'CARDEEP = a live, verified DB of 100% of Spain car points-of-sale (dealers, compraventas, garages, desguaces,',
  'rent-a-car, auctions, importers) AND the giant marketplaces, each with full inventory + delta + recipe, served by an API.',
  'Repo C:/Users/elias/projects/cardeep. Existing: pipeline/verify.py (a first-pass VAM count-quorum), migrations',
  '(verification_verdict, source_health, alert tables), docs/research/SOURCES_ES.md (181-source census incl. INE DIRCE',
  'company counts by CNAE, DGT CAT registry, Paginas Amarillas rubric counts, OSM/FSQ/Overture). A master-architecture',
  'workflow is concurrently writing docs/architecture/00..08 incl. a light 05-VERIFICATION-VAM; YOUR work is the DEEP,',
  'authoritative validator that supersedes and expands it. Write to docs/architecture/verification/.',
  'Anti-hallucination: mark [VERIFIED] vs [ASSUMED]; no placeholders; concrete methods, formulas, thresholds.',
].join(' ')

const STR = { type: 'string' }
const STRARR = { type: 'array', items: { type: 'string' } }
const FACET_SCHEMA = {
  type: 'object',
  required: ['facet', 'file_written', 'summary', 'methods'],
  properties: {
    facet: STR,
    file_written: STR,
    summary: STR,
    methods: { type: 'array', items: { type: 'string' }, description: 'the concrete verification methods/formulas defined' },
    thresholds: STRARR,
    failure_modes_caught: STRARR,
  },
}
const SYNTH_SCHEMA = {
  type: 'object',
  required: ['spec_path', 'summary'],
  properties: { spec_path: STR, q500k_answer: STR, q20k_answer: STR, summary: STR },
}
const META_SCHEMA = {
  type: 'object',
  required: ['weaknesses'],
  properties: { weaknesses: STRARR, can_be_fooled_how: STRARR, fixes: STRARR },
}

const FACETS = [
  { key: 'V1-DENOMINATOR-PROOF',
    p: 'FACET: proving/bounding the TRUE denominator (how many car POS exist in Spain). Answer the owner question "an agent says 500k entities exist, how do you verify?". Design: (1) capture-recapture estimators (Lincoln-Petersen, Chapman bias-corrected, and multi-source / N-source log-linear models) over orthogonal source pairs (Paginas Amarillas rubrics, registral CNAE 45 via INE DIRCE, OSM/FSQ/Overture, DGT CAT) to estimate the universe with CONFIDENCE INTERVALS; (2) official anchors that bound it (INE DIRCE active-company counts per CNAE 4511/4520/4677, DGT CAT ~1300, etc.) as hard floors/ceilings; (3) overlap analysis to detect inflation; (4) the rule: NEVER claim a denominator we cannot bound with a stated CI; a bare "500k" with no recapture basis is REFUTED on sight. Give the exact formulas and a worked numeric example. Write docs/architecture/verification/V1-DENOMINATOR-PROOF.md.' },
  { key: 'V2-COMPLETION-PROOF',
    p: 'FACET: proving an entity (or "20k entities") is truly 100% completed end-to-end. Answer the owner question "an agent says 20k entities completed E2E, who validates it?". Design the per-entity COMPLETION GATE (binary, multi-path): discovered+geo+cdp_code -> inventory harvested COMPLETE (count reconciled by >=2 orthogonal paths: source-declared vs harvested-distinct vs db-landed, with the db-landed authority rule so ingestion loss never hides) -> recipe saved AND git-committed -> API actually serves it (live GET returns the inventory) -> delta verified (a second harvest produces correct events). Then the AGGREGATE proof for "20k done": acceptance sampling — blind re-scrape a statistically-sized random sample and field-compare to the stored data; only assert the 20k at the confidence the sample supports. Define the per-entity verdict ledger and the "completed" definition. Give sample-size math. Write docs/architecture/verification/V2-COMPLETION-PROOF.md.' },
  { key: 'V3-INQUISITION',
    p: 'FACET: the Inquisition — a SEPARATE adversarial verifier chain (never the path that produced the claim). Design: for every load-bearing claim, spawn N independent skeptics each prompted to REFUTE (default to refuted if not independently reproducible), with PERSPECTIVE-DIVERSE lenses (re-query, raw recount, batch hash, blind live re-fetch, cross-source corroboration) so redundancy is replaced by orthogonality; quorum rule (>=2 independent paths must agree, majority refute kills the claim); the assert-vs-refute protocol; how the Inquisition stays independent (different tools, different sources, no shared state with the producer). Write docs/architecture/verification/V3-INQUISITION.md.' },
  { key: 'V4-GESTIONADOR',
    p: 'FACET: the lie & gap detection manager (Gestionador). Design the automated DETECTORS: count-inflation (source-declared vs db-landed divergence beyond tolerance), silent-cap (top-N truncation not logged, pagination cap hit), silent-field-loss (null-rate spike vs recipe baseline), staleness (last_seen drift past TTL), fabrication signatures (impossible values, out-of-band years/prices, collapse of distinct rows to one code), coverage-gap (denominator estimate minus covered, per segment/province), price-trap (finance rate sold as price). Each detection becomes a managed item ROUTED to AUTO_FIX / RESEARCH / QUARANTINE / ESCALATE_GASTO / ESCALATE_OWNER, tracked to closure (nothing serves while quarantined). Define detector formulas + thresholds + the routing state machine. Write docs/architecture/verification/V4-GESTIONADOR.md.' },
  { key: 'V5-LEDGER-API',
    p: 'FACET: the verification data model, ledger, API and dashboards. Design the verification_verdict ledger schema (subject, claim, primary_path, verifier_paths JSON, independent_values JSON, divergence, verdict TRUSTWORTHY/REFUTED/UNVERIFIED/QUARANTINED, evidence, created_at) with DB-enforced quorum CHECK; the publish-gate (an entity/number is only served if its latest verdict is TRUSTWORTHY); the audit trail (immutable, append-only); the verification API/dashboard surface (per-segment/per-province coverage %, TRUSTWORTHY vs UNVERIFIED counts, open Gestionador items, denominator CI). Honest KPIs only. Write docs/architecture/verification/V5-LEDGER-API.md with DDL.' },
  { key: 'V6-STATISTICAL-RIGOR',
    p: 'FACET: statistical and sampling rigor underpinning every assertion. Design: acceptance sampling (AQL) for blind re-verification (given N entities and a target confidence/defect rate, the required sample size n and accept/reject criteria); confidence intervals for capture-recapture; how many of 20k to blind-recheck to assert correctness at 95%/99%; sequential sampling to stop early; how to size per-field verification samples; the difference between precision (no fabrication) and recall (no missing) and how each is measured. Give the formulas and tables. Write docs/architecture/verification/V6-STATISTICAL-RIGOR.md.' },
]

const DEEP = ' Design to EXTREME depth with concrete formulas, thresholds, and worked numeric examples. This is the deepest validator the owner has ever seen. Write your doc, then return the structured result.'

phase('Facets')
log('Validator facets: 6 architects in parallel (denominator, completion, inquisition, gestionador, ledger, statistics)')
const facets = await parallel(FACETS.map(f => () =>
  agent(CREED + '\n\n' + CONTEXT + '\n\n' + f.p + DEEP,
    { label: 'facet:' + f.key, phase: 'Facets', schema: FACET_SCHEMA, agentType: 'general-purpose' })))
const facetsOk = facets.filter(Boolean)
log('Facets done: ' + facetsOk.map(f => f.facet).join(' | '))

phase('Synthesis')
const facetSum = facetsOk.map(f => f.facet + ': ' + f.summary).join('\n')
const synth = await agent(
  CREED + '\n\n' + CONTEXT + '\n\nThe 6 verification facets are written under docs/architecture/verification/ (V1..V6). Summaries:\n' + facetSum +
  '\n\nYOUR JOB (chief auditor): READ every docs/architecture/verification/V*.md and synthesize docs/architecture/verification/VALIDATOR_SUPREMO.md = the single authoritative spec of CARDEEP supreme validator: how it all fits, the verification lifecycle of any claim, the Gestionador state machine, the publish-gate, and the honest-KPI dashboard. CRUCIALLY include two WORKED, STEP-BY-STEP PROTOCOLS answering the owner literal questions: (A) "An agent claims 500,000 entities/platforms exist in Spain — here is exactly, path by path, how we verify or refute it." (B) "An agent claims 20,000 entities are completed end-to-end — here is exactly, path by path and with the sample math, how we validate or refute it." No placeholders. Return {spec_path, q500k_answer, q20k_answer, summary}.',
  { label: 'synthesis:validator', phase: 'Synthesis', agentType: 'general-purpose', schema: SYNTH_SCHEMA })

phase('MetaAudit')
const meta_ = await agent(
  'META-VERIFICATION (the auditor of the auditor). Read docs/architecture/verification/*.md. Ask: can CARDEEP validator ITSELF be fooled or give false confidence? Attack it: where could a lie still slip through (e.g. two correlated "independent" sources, a sample too small, a detector threshold gameable, the Inquisition sharing state with the producer, capture-recapture assumptions violated)? Be ruthless and specific. Return weaknesses, exactly how it could be fooled, and the fixes.',
  { label: 'metaaudit', phase: 'MetaAudit', agentType: 'general-purpose', schema: META_SCHEMA })

return {
  facets: facetsOk.map(f => ({ facet: f.facet, file: f.file_written, methods: f.methods })),
  synthesis: synth,
  meta_weaknesses: meta_ ? meta_.weaknesses : [],
  meta_fixes: meta_ ? meta_.fixes : [],
}

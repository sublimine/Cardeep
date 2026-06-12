# VALIDATOR SUPREMO — The Authoritative Specification of the CARDEEP Supreme Validator

> **CARDEEP NEVER SELLS LIES.** A number is not true because the path that produced
> it says so. It is true only when an *independent* path — one that did not share the
> producer's source, tool, cache, or code — re-derives it, within tolerance, and a
> tamper-evident ledger records that it did. Where reality is a population we cannot
> fully observe, we report an **interval with a stated confidence**, never a bare
> scalar. **Better to confess a gap than sell a lie.**
>
> This document is the single authoritative spec of how the six verification facets
> (V1–V6) compose into one validator. It **supersedes and subsumes** the light
> `05-VERIFICATION-VAM` sketch of the master-architecture set for every question of
> *"is this true, how many exist, and is it complete."* The per-source ingestion-fidelity
> count-quorum in `pipeline/verify.py` is **retained** as the cheap producer-side
> pre-check; it is an input gate, not the proof.
>
> **Anti-hallucination contract.** Every load-bearing fact about the live system is
> tagged `[VERIFIED]` (read from the repo / live DB on 2026-06-12) or `[ASSUMED]`
> (a design target not yet in code, or a modeling knob). No placeholders, no stubs.

---

## 0. Reading map

| § | Content |
|---|---|
| 1 | Ground truth — the live repo and DB state every claim is anchored to |
| 2 | The six facets and how they compose into one validator |
| 3 | The unified lie taxonomy (L1–L7) → which facet kills each |
| 4 | The verification lifecycle of ANY claim (the master pipeline) |
| 5 | The Gestionador state machine (detect → route → freeze → fix → re-prove → audit) |
| 6 | The publish-gate (the data API physically cannot serve an unproven number) |
| 7 | The honest-KPI dashboard |
| 8 | **PROTOCOL A — "an agent claims 500,000 entities exist": verify or refute, path by path** |
| 9 | **PROTOCOL B — "an agent claims 20,000 entities are completed E2E": validate or refute, with the sample math** |
| 10 | The migration & component surface this validator commissions |
| 11 | What the validator guarantees, and its honest limits |

---

## 1. Ground truth — what this is built on `[VERIFIED 2026-06-12]`

Read from the repo and the running `cardeep-pg` (PostgreSQL **16.14**):

**Schema (4 migrations, 11 tables).** `[VERIFIED — migrations/0001..0004 present;
0005 does NOT exist, so every 0005 schema below is correctly `[ASSUMED]`/proposed]`
- `0001_geo.sql` — province/comarca/municipality (52 provinces, 8.132 municipios, 0 orphans).
- `0002_entities.sql` — `entity(entity_ulid, cdp_code, kind, province_code,
  municipality_code, website, status, recipe_version, last_seen, …)`,
  `entity_source(entity_ulid, source_key, source_ref, seen_at)` `PRIMARY KEY
  (entity_ulid, source_key)` — **the capture-recapture substrate (V1)**, `entity_alias`.
- `0003_vehicles_events.sql` — `vehicle(vehicle_ulid, entity_ulid, deep_link,
  price NUMERIC(12,2), km INT, year INT, photo_url, status IN ('available','gone'),
  first_seen, last_seen)` `UNIQUE(entity_ulid, deep_link)`; `vehicle_event(event_type IN
  ('NEW','GONE','PRICE_CHANGE','PHOTO_CHANGE','KM_CHANGE'), old_value, new_value,
  observed_at)` append-only.
- `0004_verification_health.sql` — `verification_verdict(subject_type, subject_key,
  claim, primary_value, primary_path, verifier_paths JSONB, independent_values JSONB,
  divergence, verdict CHECK IN ('TRUSTWORTHY','REFUTED','UNVERIFIED'), evidence,
  created_at)` + `source_health` + `alert(origin, severity, message, payload,
  resolved_at)`. **The DB enforces only the verdict *label*, not the evidence behind
  it; `QUARANTINED` does not exist; no quorum is DB-enforced.** This is exactly the gap
  V5's migration 0005 closes.

**The shipped verifier `pipeline/verify.py::record_count_verdict`** `[VERIFIED — read
in full]`: a modal count-quorum over a `paths: dict[str,int]`. TRUSTWORTHY when the
modal value has ≥2 supporting paths, no rival value also reaches ≥2, **and the primary
(landed) path agrees with ≥1 other** (the `primary_agrees` rule, line 41 — ingestion
loss never reads TRUSTWORTHY). Else UNVERIFIED (< 2 values) or REFUTED. Call sites:
`discover.py` (`subject_type='source'`, paths `{db_ingested, fetched, source_declared}`)
and `ingest.py` (`subject_type='entity_inventory'`, paths `{db_available, harvested,
source_declared}`).

**`cdp_code` identity** `[VERIFIED — services/api/codes.py]`: format
`CDP-ES-{province2}-{8×Crockford-base32 of sha256(key)}`, alphabet
`0123456789ABCDEFGHJKMNPQRSTVWXYZ` (no I, L, O, U); key precedence domain > cif >
name+municipality > name+province. This is what makes recapture meaningful — the same
real-world entity collapses to one code across sources.

**Live corpus state** `[VERIFIED — PROGRESO.md, latest]`: **12.814 entities** (garaje
7.200 · compraventa 2.753 · concesionario_oficial 1.569 · desguace 1.292) · **22.300
serviceable vehicles** · **24.329 delta events** · 212 dealers with inventory · 52/52
provinces · 10 sources. *(V3-INQUISITION was written against an earlier snapshot —
12.862 entities / 39.068 vehicles — and cites it; the divergence is a write-time skew,
not a contradiction. The current figures govern.)*

**Denominator census** `[VERIFIED — docs/research/SOURCES_ES.md §6/§7]`: floor
**~44.000** auto POS (Páginas Amarillas: talleres 29.955 + concesionarios 11.202 +
compraventas 1.662 + desguaces 1.636), ceiling **50–90k** `[ASSUMED in census]` (CNAE 45
registral + Places). Per-segment anchors: desguaces DGT CAT **1.292** (official, exact),
DesguacesDirecto **1.386**, AEDRA **615**; concesionarios franquiciados FACONAUTO
**2.018**. Owner's §7 hand-verification (the gold standard this validator automates):
AS24 agent 278.163 vs live **278.329** (Δ+166, drift-pass); coches.net 248.920 vs
**249.139** (Δ+219, drift-pass); DGT `returnCountOnly` 1.292 vs **1.292** (Δ0, exact);
Kia **242**, MG **212** (Δ0); VW OneHub "263 dealers" **REFUTED** (HTTP 500).

---

## 2. The six facets — one validator, six organs

The supreme validator is one machine. Each facet owns one organ; they share the same
ledger, the same lie taxonomy, the same publish-gate, and the same routing.

```
                          ┌───────────────────────────────────────────────┐
   PRODUCERS              │            THE SUPREME VALIDATOR                │
   pipeline/*             │                                                │
   discover ┐             │   V2 COMPLETION   ── per-entity 5-gate proof    │
   harvest  │  emit       │   V1 DENOMINATOR  ── how-many-exist, CI + anchor│
   ingest   ├─ facts ───► │   V3 INQUISITION  ── adversarial re-derivation  │
   recipe   │  & claims   │   V6 STATISTICS   ── the math under V1/V2/V3    │
   api      ┘             │   V4 GESTIONADOR  ── manager: detect→route→close│
                          │   V5 LEDGER/API   ── DB-enforced store + gate   │
                          └───────────────────────────────────────────────┘
                                              │
                                publish-gate (V5 views) ──► data API serves ONLY proven values
```

| Facet | Question it answers | Authoritative output | Doc |
|---|---|---|---|
| **V1 DENOMINATOR** | *How many car POS truly exist?* | `N̂` + 95% CI + anchor floor/ceiling per segment×province | `V1-DENOMINATOR-PROOF.md` |
| **V2 COMPLETION** | *Is THIS entity completed E2E?* | binary 5-gate verdict + `entity_completion` ledger row | `V2-COMPLETION-PROOF.md` |
| **V3 INQUISITION** | *Is a single load-bearing claim reproducible by an independent path?* | TRUSTWORTHY/REFUTED/INCONCLUSIVE/QUARANTINED with independence score | `V3-INQUISITION.md` |
| **V4 GESTIONADOR** | *Across the whole corpus, where is a lie/gap forming, who fixes it, may we serve meanwhile?* | a routed, SLA'd `gestion_item` + quarantine | `V4-GESTIONADOR.md` |
| **V5 LEDGER/API** | *Where is the proof stored, and how is serving gated?* | DB-enforced quorum ledger + hash-chained audit + publish-gate views + API/dashboard | `V5-LEDGER-API.md` |
| **V6 STATISTICS** | *With what sample size, CI, and stopping rule?* | AQL plans, Chapman CIs, SPRT, per-field sizing, precision/recall split | `V6-STATISTICAL-RIGOR.md` |

**The chain of authority (who can overrule whom).** The producer's optimistic
`verify.py` quorum is an *opinion*. **V3 can downgrade it** (e.g. Lens C live re-fetch
reveals staleness the count-quorum never sees). **V6 governs V3 on content** (a
quorum-passing count whose blind sample is defective is REFUTED). **V5's DB CHECK is the
floor nobody can cross** (a TRUSTWORTHY row without ≥2 agreeing values across ≥2
families is physically unstorable). **V4 owns disposition** (nothing closes without an
independent V3 verdict id; nothing serves while quarantined). **V1 and V2 are the two
load-bearing *kinds* of claim** — population size and per-entity completion — and they
are exactly the owner's two questions in §8 and §9.

---

## 3. The unified lie taxonomy — which facet kills each

CARDEEP recognizes seven ways a served value can be a lie. Each has a dedicated
detector and a dedicated orthogonal refuter. Redundancy (three counters of the same
surface) is replaced by **orthogonality** (paths that cannot share a blind spot).

| # | Lie | Real CARDEEP instance `[VERIFIED]` | Why the count-quorum alone misses it | Killed by |
|---|---|---|---|---|
| L1 | **Inflated count** | Flexicar sitemap "23.769" = SEO landings, not stock | all paths count the same inflated surface → quorum agrees | V3 Lens B raw-recount; V6 §2 acceptance; V4 `count_inflation` |
| L2 | **Silent cap** | AS24 deep-paging caps ~1.000 (20×50); a 1.840-car dealer truncates | every path drains the same capped surface | V2 G2 drain-proof; V3 cap-aware refute; V4 `silent_cap`; V5 cap-suspect rule |
| L3 | **Dropped field** | recipe selector rots → `price` NULL across rows; count still reconciles | quorum tests row *count*, never field *fill* | V2 field-integrity floor; V6 §5 per-field; V4 `field_loss` z-test |
| L4 | **Staleness** | `unoauto` sitemap stale, PDPs 404; rows served "live" 30 d old | no freshness axis; a stale count quora-agrees forever | V2/V5 freshness SLA expiry; V3 Lens C live; V4 `staleness` |
| L5 | **Fabrication** | LLM enrich hallucinates a `cif`; km-doubling 6.5B `[VERIFIED bug]` | no path re-fetches source bytes | V2 §4 blind re-scrape orphans; V3 Lens C; V4 `fabrication` bounds; V5 replay |
| L6 | **Coverage gap** | "100% of Madrid" = only the AS24 subset; CNAE-45 tail missing | quorum verifies what *was* collected, never the denominator | V1 capture-recapture + anchors; V4 `coverage_gap`; V6 §4/§6 recall |
| L7 | **Kind mis-attribution** | `ingest.py:52` hardcoded `kind='concesionario_oficial'` for every AS24 dealer `[VERIFIED]` | count & identity correct; the *label* is the lie | V3 Lens D OEM-locator cross-proof; V4 `fabrication(distinct_collapse)` family |

> **The doctrine:** never verify a claim with the path that produced it; never verify it
> on a single axis. Each lie is killed by a *different* orthogonal lens.

---

## 4. The verification lifecycle of ANY claim (the master pipeline)

Every claim — a count, an entity field, an inventory, a completion, a coverage fraction,
a denominator — flows through the same nine stages. The facet that does the heavy lifting
changes with the claim's `subject_type`; the spine does not.

```
 (1) PRODUCER emits a claim envelope  ───────────────────────────────────────┐
     {subject_type, subject_key, claim, asserted_value,                       │
      producer_state=⟨source,tool,snapshot,code_path⟩, evidence_uri}          │
                                                                              ▼
 (2) PRODUCER-SIDE PRE-CHECK (verify.py)  — cheap optimistic count-quorum.
     Catches gross errors early. Its TRUSTWORTHY is provisional, never served as proof.
                                                                              │
 (3) DEFAULT-REFUTED.  The claim enters V3 with verdict = REFUTED (Law I).    │
                                                                              ▼
 (4) PRODUCER EXCLUSION + LENS SELECTION (V3 §3.6 routing matrix).
     Spawn N skeptics, each differing from the producer on ≥2 of
     ⟨source, tool, cache, code_path⟩; ≥1 must differ on all four (live re-fetch).
                                                                              │
 (5) ORTHOGONAL MEASUREMENT.  Each skeptic independently measures the value:  │
       count → Lens A re-query / B raw-recount / C live / D cross-source       │
       denominator/coverage → V1 capture-recapture + anchors (Lens D math)     │
       completion → V2 five-gate blind re-derivation                          │
       population correctness → V6 acceptance sample (blind re-scrape)         ▼
 (6) QUORUM DECISION (V3 §5.4, governed by V6 on content):
       Rh≥1 hard contradiction          → REFUTED (veto)
       INDEP<2                           → REFUTED (NO_INDEPENDENT_PATH)
       ≥2 independent ASSERT, no rival, refute-mass<assert-mass → TRUSTWORTHY
       rival quorum OR split             → REFUTED
       cap-suspect at a known ceiling    → QUARANTINED
       else                              → INCONCLUSIVE (re-queue +1 lens)
                                                                              │
 (7) PERSIST (V5).  Write verification_verdict; the DB CHECK refuses to store │
     TRUSTWORTHY unless quorum_n≥2 AND family_n≥2 (generated columns from the │
     JSONB evidence). Hash-chained verdict_audit row appended (append-only).  ▼
 (8) ROUTE (V4).  Any non-TRUSTWORTHY becomes a gestion_item → fix | research |
     quarantine | escalate. Quarantine freezes serving *immediately*.
                                                                              │
 (9) PUBLISH-GATE (V5 views).  The data API reads ONLY v_publishable_*; a     │
     value that isn't latest-TRUSTWORTHY-and-fresh is never served as fact —  │
     it is exposed via the verification API labelled UNVERIFIED/QUARANTINED.  ▼
        Closure (V4) is impossible without an independent V3 verdict_id.
```

**Tolerance regimes (V3 §5.2, calibrated on the owner's §7 data).**
- **EXACT** subjects (registral/official: DGT CAT, OEM locator counts, `cif`, `kind`):
  `tol = 0`. DGT 1.292 vs 1.292 → ASSERT; vs 1.290 → REFUTE.
- **DRIFT** subjects (live platform inventory counters): `tol(v) = max(τ_rel·v, τ_abs)`
  with `τ_rel = 0.005`, `τ_abs = 50` `[ASSUMED, calibrated]`. AS24 Δ166 ≤ max(1391,50)
  → ASSERT (matches the owner's manual ✓). A fabricated 350.000 vs live 278.329 → Δ71.671
  ≫ 1391 → REFUTE. **A DRIFT count landing *exactly* on a known cap (1000/2000) while raw
  bytes expose a larger `numberOfResults` escalates to REFUTE_HARD regardless of
  tolerance** — tolerance never excuses a cap.

---

## 5. The Gestionador state machine (V4) — detect, route, freeze, fix, re-prove, audit

V3 verifies a named claim on demand. V4 is the *manager*: it runs detectors over the
whole corpus on a schedule, turns each suspicion into one tracked `gestion_item`, routes
it, gates serving, and drives it to closure. The detectors (V4 §3) are each calibrated to
a lie that actually happened: `count_inflation` (`g_DL>0.02` or any `g_HL>0`),
`silent_cap` (page/ceiling/starve hit with `H<D`), `field_loss` (two-proportion z-test
`z>3` & `Δp≥0.05`), `staleness` (`age/TTL>1`, segment-tiered TTL), `fabrication`
(out-of-band bounds / distinct-collapse `>1.10` / degenerate distribution / Benford),
`coverage_gap` (`relgap>0.10` vs V1's CI lower bound / anchor breach), `price_trap`
(monthly-finance rate sold as price).

```
  detector fires → [OPEN] ──route()──► [ROUTED] ──pickup──► [IN_PROGRESS]
        │ (quarantines)                                          │ remedy applied
        ▼                                                        ▼
   [QUARANTINED] (serving frozen, still worked) ─────────► [REVERIFYING] ── calls V3
        ▲                                            indep PASS │   │ indep FAIL
        │ reopen if regresses                                   ▼   ▼
        └────────────────────────── [RESOLVED]            [REOPENED] → ROUTED, severity++
                                    (unquarantine, verdict_id set)

  ESCALATE_* : [OPEN]→[ROUTED]→[ESCALATED] → (owner/budget) → IN_PROGRESS | WONT_FIX
```

**Five lanes** (V4 §4.1): `AUTO_FIX` (mechanical reversible — re-harvest, re-ingest,
bump max_pages), `RESEARCH` (new adapter / recipe change / anchor reconciliation),
`QUARANTINE` (stop serving *now*, then sub-route to fix/research), `ESCALATE_GASTO`
(needs spend — proxies, paid API), `ESCALATE_OWNER` (irreversible / legal / scope).
Routing is deterministic on the detection's reason code — same lie always routes the
same way, no agent discretion.

**The spine rule (non-negotiable):** an item reaches `RESOLVED` **only** through
`REVERIFYING`, and `REVERIFYING` **must** be an independent V3 recheck whose
`verification_verdict.id` is stored in `gestion_item.verdict_id`. **No verdict_id → no
RESOLVED.** Closure literally cannot be written without an independent proof. Transitions
are append-only (`gestion_transition`) — the history is the audit.

---

## 6. The publish-gate — the data API physically cannot serve an unproven number (V5)

Honesty is not application logic that can be bypassed; it is a **bound view** the read
API is wired to. A subject is served **iff** its latest, non-expired verdict is
TRUSTWORTHY **and** no open quarantining `gestion_item` references it.

```sql
-- latest verdict per (subject_type, subject_key, claim); is_publishable folds in freshness
CREATE OR REPLACE VIEW v_latest_verdict AS
SELECT DISTINCT ON (subject_type, subject_key, claim)
       id, subject_type, subject_key, claim, claim_kind, verdict,
       quorum_n, family_n, divergence, expires_at, created_at,
       (verdict='TRUSTWORTHY' AND (expires_at IS NULL OR expires_at > now())) AS is_publishable
FROM verification_verdict
ORDER BY subject_type, subject_key, claim, created_at DESC;

-- a subject vanishes the instant a quarantining item opens; returns the instant it RESOLVES
CREATE OR REPLACE VIEW servable_entity AS
SELECT e.* FROM entity e
JOIN v_latest_verdict lv
  ON lv.subject_type='entity' AND lv.subject_key=e.cdp_code
 AND lv.claim_kind='existence' AND lv.is_publishable
WHERE NOT EXISTS (
  SELECT 1 FROM gestion_item g
  WHERE g.quarantines AND g.closed_at IS NULL
    AND g.subject_type='entity' AND g.subject_key=e.cdp_code);
```

The DB-enforced quorum is the deepest line: `quorum_n` and `family_n` are **generated
columns** the database recomputes from the JSONB evidence via IMMUTABLE functions, and
`CONSTRAINT chk_trustworthy_needs_quorum CHECK (verdict <> 'TRUSTWORTHY' OR (quorum_n>=2
AND family_n>=2))` makes a TRUSTWORTHY lie **physically unstorable** — an operator cannot
hand-pass `quorum_n=2`; the DB derives it. *(V5 proved this against the live PG 16.14 in
rolled-back transactions: the CHECK accepts the 3-family desguace case and rejects a
single-family TRUSTWORTHY insert; the hash-chain audit blocks tampering UPDATEs.)*

**Two KPIs, never conflated:** coverage of the *estimated real population* (with CI) and
coverage of the *official register*. `observed` (12.814) is never merged with `served`
(the smaller publishable count) into one triumphant figure.

---

## 7. The honest-KPI dashboard (V5 §9)

A read-only board over the verification API; every tile is engineered so an operator
*cannot be lied to*:

1. **Integrity** — green only if the audit hash-chain verifies AND every verdict row has
   a `verdict_audit` witness. Red ⇒ tampering/data-loss.
2. **Coverage matrix** — segment × province heatmap of `coverage_pct`, each cell colored
   by verdict (TRUSTWORTHY green / UNVERIFIED amber / QUARANTINED red), CI band on hover.
   Denominator-less cells are **grey, never green**.
3. **Trust ledger** — TRUSTWORTHY vs UNVERIFIED vs REFUTED vs QUARANTINED; publishable %.
4. **Gestionador backlog** — open items by lane × severity; SLA breaches.
5. **Denominator panel** — per-segment CI, the capture-recapture inputs (n1,n2,m), the
   sources used, staleness countdown.
6. **Drift / freshness** — subjects whose verdict expires in <24h (the re-harvest queue).

KPI honesty rules: coverage is **always** shown against a CI; a segment with no
denominator shows "coverage: unknown," not 100%; "Entities: 12.814" is labelled
**observed**, distinct from **served**; every TRUSTWORTHY tile click-throughs to its
audit row + replayable evidence.

---

## 8. PROTOCOL A — "An agent claims 500,000 entities/platforms exist in Spain"

### Verify or refute, exactly, path by path

This is the owner's first literal question. The claim is a **denominator** claim
(`subject_type='denominator'`), so V1 leads, with V3 Lens D as the adversary and V6 §4
supplying the CI. **The burden of proof is on the claim.** A denominator is a *latent
population size* — never observed, only estimated from how independent sources overlap,
and bounded by official registers.

#### Step A0 — Inversion of burden (the falsification rule, V1 §6.2)

The claim "500,000" arrives as a bare scalar. It is **`REFUTED` on sight** unless it
carries **all three**: (1) a *recapture basis* — the source set and the observed overlap
`m` it was computed from; (2) a *confidence interval* `[N_lower, N_upper]`; (3) *anchor
consistency* with every applicable official register. "500,000" satisfies none. We do not
labor to disprove it; the claimant must show the recapture, or there is no number.

#### Step A1 — Confront it with the orthogonal source ceilings `[VERIFIED]`

Pull the capture matrix from `entity_source` for the orthogonal sources (V1 §4):
Páginas Amarillas (self-listing), INE DIRCE CNAE 45 (mandatory registration), OSM/FSQ/
Overture (geo-survey), DGT CAT (legal register), OEM locators (franchise membership).
The largest *whole-universe* signal we have is PA's dedup'd auto-rubric union ≈ **44.000**
`[VERIFIED]`; the registral ceiling (CNAE 4520 motor-vehicle repair alone) is tens of
thousands; the highest defended estimate is the **50–90k** ceiling `[ASSUMED in census]`.
**500.000 exceeds every orthogonal source's total and every registral ceiling by an order
of magnitude, with zero overlap evidence.** `N_lower` for any real source pair is nowhere
near 500.000.

#### Step A2 — Compute the *real* denominator per segment, with a CI (V1 §2 / V6 §4)

We never estimate `N` over the whole heterogeneous population in one shot (heterogeneity
biases CR downward). We **stratify by segment × province**, estimate each, and sum
variances. For two orthogonal sources A, B with overlap `m` (matched by `cdp_code`), the
bias-corrected **Chapman** estimator and its log-normal CI (the reported object — never
the point estimate alone):

```
N̂_Chapman = (n_A+1)(n_B+1)/(m+1) − 1
Var        = (n_A+1)(n_B+1)(n_A−m)(n_B−m) / [ (m+1)²(m+2) ]
f̂00 = N̂ − D ;  C = exp(1.96·√(ln(1 + Var/f̂00²)))
95% CI = [ D + f̂00/C ,  D + f̂00·C ]     (D = distinct observed; CI never drops below D)
```

With **≥3 orthogonal sources** we fit the **log-linear model** (estimates the
dependence term instead of assuming it away) and report **Chao's lower bound**
`N̂_Chao = D + f_1²/(2·f_2)` as the heterogeneity-robust hard floor.

#### Step A3 — The self-validating worked example (desguaces, real anchors) `[VERIFIED inputs]`

Desguaces is the proving segment because it has orthogonal directory lists **and** a
near-exact official anchor (DGT CAT). Inputs: DGT CAT **1.292** (anchor), DesguacesDirecto
`n_A=1.386`, AEDRA `n_B=615`; measured overlap `m=560` `[ASSUMED — the value the
`entity_source` join returns at run time; used here so the arithmetic is concrete]`.
`D = 1386+615−560 = 1.441`.

```
N̂ = (1387·616)/561 − 1 = 854.392/561 − 1 = 1.522
Var = (1387·616·826·55)/(561²·562) = 38.815.028.560 / 176.873.202 = 219.45 ;  SE = 14.81
f̂00 = 1.522 − 1.441 = 81 ;  C = exp(1.96·√(ln(1+219.45/6561))) = exp(0.3556) = 1.4270
CI = [1441 + 81/1.4270 , 1441 + 81·1.4270] = [1.498 , 1.556] ;  coverage = 1441/1522 = 94.7%
```

**Result: `N̂ = 1.522`, 95% CI [1.498, 1.556], coverage 94.7%.** *(Every figure
independently recomputed in Python by V1 and matches exactly.)*

#### Step A4 — The anchor gate, read correctly (V1 §5.3)

DGT CAT = 1.292 is the official census of *CAT-authorized* centers. The estimate lands
*above* it — and this is **not** a refutation: directories include non-CAT scrap dealers
operating under CNAE 4677, so the true broad-segment population is legitimately larger;
**CAT is a floor, not a ceiling, for the broad segment.** Gate: `N_upper (1556) ≥ floor
(1292)` ✓ and `N_lower (1498) ≤ ceiling·(1+slack)` (DIRCE 4677, tens of thousands) ✓ ⇒
**TRUSTWORTHY**. *(Contrast: had `N̂` come back at 850 with CI [810,895], then
`N_upper=895 < floor=1292` ⇒ **REFUTED** — you cannot have fewer total desguaces than the
officially licensed subset.)*

#### Step A5 — Adjudicate 500.000 (V1 §10 + V3 quorum)

```
Producer P = ⟨agent, its-own-tool, its-snapshot, its-path⟩ claims N* = 500.000.
1. Falsification rule (A0): no recapture basis, no CI, no anchor → fails all three gates.
2. Anchor gate: N_lower for any real source pair ≪ 500.000; 500.000 > registral ceiling
   (CNAE 4520) by ~10× and > PA union 44k by ~11× → exceeds every ceiling.
3. Chao floor: 500.000 is not below any floor, but it has no f_1,f_2 basis at all.
⇒ VERDICT = REFUTED, instantly, reason logged:
   "exceeds DIRCE-4520 ceiling ×~10 and PA-union ×~11; NO recapture basis; NO CI."
   Persist verification_verdict(subject_type='denominator', verdict='REFUTED', evidence=tuple);
   alert(origin='national/denominator', severity='critical'); V4 routes → RESEARCH
   (reconcile the claim's provenance — almost certainly duplicates + out-of-scope rows
   counted as entities, the default failure of a bare count, V1 §6.1).
```

#### What the owner is told (Protocol A deliverable)

> *We do not believe the 500.000. A denominator is a latent population size, estimated
> from how independent sources overlap and bounded by the official registers — it is
> never a number an agent can simply assert. 500.000 exceeds every orthogonal source's
> total (PA's whole auto-rubric union is ~44.000) and every registral ceiling by an order
> of magnitude, with zero overlap evidence, so it is **REFUTED on sight**. What we DO say,
> per segment, is the interval: e.g. desguaces **N̂ = 1.522, 95% CI [1.498, 1.556],
> coverage 94.7%, DGT-CAT floor 1.292 respected — TRUSTWORTHY.** That tuple is a proof;
> "500.000" — and even a bare "44.000" presented as a point with no interval — is a
> rumor. We confess "we have a verified **floor** of 44k; the **estimate with CI** is
> pending the N-source log-linear fit per segment" rather than dressing a floor up as a
> denominator.*

---

## 9. PROTOCOL B — "An agent claims 20,000 entities are completed end-to-end"

### Validate or refute, path by path, with the sample math

This is the owner's second literal question. **No agent's word counts.** An entity is
`COMPLETED` only when an *independent* validator re-derives every lifecycle stage by paths
that did **not** produce the data (V2), and "20.000 are completed" is asserted only at the
confidence a **blind re-scrape sample** statistically supports (V6) — never the bare count.

### Part 1 — Is a single entity actually completed? The binary five-gate proof (V2)

Completion is a **logical AND of five binary sub-gates** — no weighted score, no "90%
done." Each gate is re-derived independently; a single FAIL makes the entity INCOMPLETE
with an exact failing-stage origin.

```
G1 DISCOVERED  entity row exists, province∈{01..52}, cdp_code parses
               ^CDP-ES-[0-9]{2}-[0-9A-HJKMNP-TV-Z]{8}$, (lat,lon) set or geo_partial+reason
G2 HARVESTED   3-path count reconcile with DB-LANDED AS AUTHORITY:
               S=source-declared, H=harvested distinct deep_links, D=DB-landed available.
               TRUSTWORTHY ⟺ (D==H==S) ∨ (D==H ∧ |S−D|≤τ·max ∧ residual logged).
               If H>D (rows fetched but not landed) → FAIL even if H==S (ingestion loss
               never reads TRUSTWORTHY). Field-integrity floor: D_valid/D ≥ 0.98
               (deep_link, price-or-justified, recipe_version non-null) — kills hollow rows.
G3 RECIPE      countries/ES/recipes/<C>.yaml written AND git-committed at a SHA reachable
               from HEAD (not disk-only), parses, recipe.version == entity.recipe_version.
G4 SERVED      live GET /entities/{C}/inventory → 200, ok:true, len==D; /entities → available==D.
G5 DELTA       a 2nd harvest emits type-consistent events: GONE⊆prev-available, NEW∉prev,
               KM_CHANGE new≥old (odometers don't decrease), PRICE old≠new, and the
               conservation identity D_after == D_before + #NEW − #GONE closes.
+ Freshness    now() − last_harvest_at ≤ tier SLA (24h tier-1 / 7d standard / 30d long-tail).
⇒ COMPLETED  ⟺  G1∧G2∧G3∧G4∧G5 ∧ fresh  → write entity_completion verdict='COMPLETED'.
```

The `entity_completion` ledger (proposed migration 0005, `[ASSUMED]`) has a DB-enforced
invariant: `verdict='COMPLETED'` requires all five gate booleans TRUE and
`completed_at IS NOT NULL` — even a buggy validator cannot fabricate a completion. **The
only trustworthy answer to "how many are completed" is a `COUNT(*)` against this ledger**,
not an agent's assertion.

### Part 2 — The blind re-scrape (the heart, V2 §4) — kills fabrication & coverage gap

For sampled entities, the validator does **not** look at stored data first. It performs a
**cold, independent re-harvest using the committed recipe** (proving the recipe asset
works), then set-compares against what we serve:

```
orphans = stored_links − fresh_links     # we serve it, source doesn't have it → FABRICATION (L5)
missing = fresh_links − stored_links     # source has it, we don't serve it     → COVERAGE GAP (L6)
e_set(C)   = (|orphans|+|missing|)/|fresh_links|       (θ_set = 0.02)
e_field(C) = mismatched(price,km,make,model)/|matched| (θ_field = 0.01)
entity_defect ⟺ e_set > θ_set ∨ e_field > θ_field.  Orphans weighted 2× (fabrication is the worst lie).
```
A re-scrape is only valid within the entity's SLA window of the original; otherwise drift
is legitimate churn and the entity is re-sampled (never scored on stale comparison).

### Part 3 — "20.000 completed" by acceptance sampling (V6 §2/§5, V2 §5)

Re-scraping all 20.000 to validate 20.000 is circular (same cost as building it). The
population claim is proven by **statistical acceptance sampling**: blind-re-scrape a
random sample, assert the claim only at the confidence the sample supports.

**Sample size (attribute sampling, worst case p=0.5, FPC over N=20.000):**
```
n0 = z²·p(1−p)/m² ;  n = n0/(1+(n0−1)/N)
 95% conf, ±3% : n0 = 1.96²·0.25/0.03² = 1067.1 → n = 1014
 95% conf, ±2% : n0 = 2401.0 → n = 2144
```
**The accept/reject gate (LQAS — the actual decision):** AQL p₁=1%, RQL p₂=5%, producer
risk α=0.05, consumer risk β=0.10. The plan meeting these is **n=132, c=3**:
```
P_accept(0.01) = Σ_{d≤3} C(132,d)·0.01^d·0.99^{132−d} ≈ 0.9557  (good lot accepted, ≥1−α ✓)
P_accept(0.05) = Σ_{d≤3} C(132,d)·0.05^d·0.95^{132−d} ≈ 0.0992  (bad lot rejected, ≤β ✓)
```
> **Operational rule:** blind re-scrape **132** random claimed-completed entities (via the
> §4 blind compare). If **≤3** fail, ACCEPT "20.000 completed at AQL 1%". If **≥4** fail,
> REJECT — the lot is a lie at the 5% floor; V4 quarantines the lot and the count reverts
> to the per-entity-TRUSTWORTHY subset only.

**Stratified, to kill the "we did the EASY 20k" lie (L6, V2 §5.5):** the sample is
stratified — tier-1 platforms (100% if ≤30, else LQAS n=80,c=2), hard-WAF dealers
(datadome/akamai/perimeterx, min 50), low-churn desguace/garaje (min 50), bulk remainder —
with **Neyman allocation** (`n_h ∝ N_h·S_h`). **Acceptance is an AND across strata**:
passing the bulk while tier-1 fails does NOT accept the 20.000.

**What we are allowed to publish (Clopper–Pearson one-sided upper bound, V6 §5.4):**
`p_U = BetaInv(1−α; d+1, n−d)`. We **never write "20.000 done"** — we write the bound the
evidence earns:
- d=3 in n=132: `p_U = BetaInv(0.95; 4, 129) ≈ 0.0577` ⇒ **"≥ 18.845 verified complete at 95%."**
- d=0 in n=132: `p_U = 1−0.05^{1/132} ≈ 0.0224` ⇒ **"≥ 19.552 verified complete at 95%."**

### Part 4 — Precision vs recall are MEASURED APART (V6 §6) — the cardinal rule

"20.000 completed" conflates two orthogonal questions that need **different samples and
different estimators**:
- **Precision** (no fabrication) = (rows we hold that are TRUE)/(rows we hold). Measured
  by an acceptance sample drawn **from the DB**, re-verified against primary reality.
- **Recall** (no missing) = (true entities we hold)/(all true entities). Measured **only**
  against an external frame — the V1 capture-recapture denominator. **A sample drawn from
  the DB can NEVER measure recall** ("98% recall verified by sampling our DB" is a
  structural lie → automatic quarantine).

End-to-end on the 20.000 (V6 §8): count quorum TRUSTWORTHY (div 0.01%); precision
major-defect <1% @99% (n=459/c=0) PASS; the `cif` field 3.8% (Wilson CI [2.8%,5.2%])
**FAILS** the 3% field gate → route *fix* (one parser, not a full re-ingest); recall vs a
fresh PA+Overture recapture: `N̂ = (20001·24001)/16501 − 1 ≈ 29.091`, recall = 20.000/29.091
= **68.8%** → **SEALED-WITH-DECLARED-GAP ≈ 9.091 missing**, route *research*.

#### Worked single entity (V2 §8) `[example]`

`C = CDP-ES-28-7Q2K9ABX` (Pinto/Madrid concesionario): G1 code parses, prov 28, lat/lon ✓;
G2 S=84,H=84,D=84,D_valid=83→fi=0.988≥0.98 ✓; G3 recipe at HEAD SHA, version 1==1 ✓; G4
GET /inventory→200, len=84==D ✓; G5 2nd harvest 2 NEW,1 GONE,1 PRICE, 84+2−1=85==D_after,
odo monotone ✓; fresh 6h ago vs 7d SLA ✓ → **COMPLETED**.

#### What the owner is told (Protocol B deliverable)

> *No agent's count is taken. An entity is COMPLETED only when an independent validator
> re-derives all five lifecycle gates — identity, a 3-path count reconcile with DB-landed
> as authority, a git-committed recipe, a live API serve, and a type-consistent second
> delta — by paths that did not produce the data; that fact is a `COUNT(*)` against the
> `entity_completion` ledger, which the database refuses to mark COMPLETED unless all five
> gates passed. For the population claim we blind-re-scrape a **stratified sample of 132**
> (tier-1 100%, hard-WAF and low-churn floored, bulk remainder) and accept "20.000
> completed at AQL 1%" only if ≤3 fail; we then publish the Clopper–Pearson bound the
> sample earns — e.g. **"≥ 18.845 of 20.000 verified complete to spec at 95% confidence;
> tier-1 stratum 100% clean; 2 defects routed to fix"** — never the bare "20.000 done."
> And we report precision and recall apart: the rows we hold are clean, but we hold ~69%
> of the estimated ~29.100 universe — **~9.091 entities we do not yet hold, confessed, not
> hidden.** That number nobody can refute, with the gap stated out loud, is the product.*

---

## 10. The component & migration surface this validator commissions

`[ASSUMED — proposed, NOT claimed as built; migrations/0005 does not exist today]`. The
six facets converge on **one additive, reversible migration 0005** (each facet drafted its
slice; V5 owns the canonical merge) plus a small set of pipeline modules:

| Component | Proposed path | Builds on `[VERIFIED]` | Owner facet |
|---|---|---|---|
| Quorum-enforced ledger (superset of 0004) + generated `quorum_n`/`family_n` + CHECK | `migrations/0005` | `verification_verdict` 0004 | V5 |
| Hash-chained append-only `verdict_audit` (pgcrypto) | `migrations/0005` | — | V5 |
| Publish-gate views `v_publishable_*` / `servable_*` | `migrations/0005` | `entity`, `vehicle`, API | V5 + V4 |
| `denominator_estimate` (Chapman point + CI) | `migrations/0005` | `entity_source`, `geo_province` | V5 + V1 |
| `entity_completion` ledger (5-gate, DB invariant) | `migrations/0005` | `entity`, `verification_verdict` | V2 |
| `gestion_item` / `gestion_transition` (router queue) | `migrations/0005` | `verification_verdict`, `alert` | V4 |
| Inquisition `inquisition_claim/skeptic/verdict` (INDEP≥2 CHECK, read-only `cardeep_inquisitor` role) | `migrations/0005` | `alert`, `source_health` | V3 |
| Per-entity gate runner | `pipeline/complete.py` | `ingest_dealer`, `record_count_verdict`, `write_recipe` | V2 |
| Blind re-scrape comparator | `pipeline/blind.py` | `harvest_dealer`, committed recipe | V2 |
| Acceptance sampler (LQAS, stratified, Clopper–Pearson) | `pipeline/accept.py` | `entity_completion`, `is_tier1`/`website_waf`/`kind` | V6 |
| Denominator estimator (Chapman / log-linear / Chao) | `pipeline/denominator.py` | `entity_source` capture matrix | V1 |
| Inquisition prosecutor + lenses | `pipeline/inquisition/` | claim queue, separate egress | V3 |
| Gestionador detectors + scheduler | `pipeline/gestionador/` | the quorum triplet, `last_seen`, recipe baselines | V4 |
| Verification API + dashboard | extends `services/api/main.py` | `{ok,data,error,meta}` envelope | V5 |

Anti-stub discipline: the formulas, thresholds, schemas, and routing tables above are
complete and implementable as written; none of these files exists yet and none is claimed
as built.

---

## 11. What the supreme validator guarantees — and its honest limits

**Guarantees [by construction]:**
1. No load-bearing value is served as *verified* unless ≥2 mutually-independent paths from
   ≥2 collector families agreed within tolerance, with ≥1 path differing from the producer
   on all four state dimensions — **enforced as a DB CHECK**, not a convention.
2. Every lie-class L1–L7 has a dedicated detector and a dedicated orthogonal refuter.
3. A denominator is **never** a bare scalar: it is an interval with a stated CI, gated
   against official registers; "100% coverage" is mathematically un-assertable without ≥3
   orthogonal sources whose Chapman CI supports it.
4. "Completed" is a binary five-gate, DB-invariant ledger fact, and a population
   completion claim is published only at the Clopper–Pearson bound a stratified blind
   sample earns.
5. Every non-TRUSTWORTHY detection is ticketed, routed, and — if it is a served lie —
   frozen *immediately*; closure is impossible without an independent V3 verdict id.
6. The audit trail is immutable and hash-chained; tampering is detectable; verdicts are
   re-runnable (RNG seed + sampled-key list persisted).

**Honest limits [ASSUMED / out of scope]:**
- `migrations/0005`, the read-only `cardeep_inquisitor` role, and the separate-egress
  network identity for live re-fetch are **design requirements not yet in the repo**; the
  independence guarantees are *physical* only once they are built.
- Capture-recapture assumes (relaxable) independence, closure, and perfect matching; real
  sources are positively dependent and heterogeneous, both biasing the 2-source estimate
  **downward** — which is exactly why we report a *bounded interval and refuse "100%"*
  rather than over-claiming, and treat the 2-source point as a lower-leaning central
  estimate with Chao as the hard floor.
- Live re-fetch and blind re-scrape cost real requests against defended sources; they run
  on a sampled cadence for high-volume drift subjects and on *every* registral/EXACT and
  fabrication claim. The sampling rate is a calibration parameter, not yet measured.
- Detector thresholds (τ_count=0.02, z_crit=3.0, κ=1.10, the SLAs) are calibrated from
  real drift (sub-0.1% curl drift) and real bugs (175→48 collapse, km-doubling) but are
  starting constants that must live in config and be tuned against a false-positive log.

> **The validator's final promise, made structural:** CARDEEP confesses every gap it
> cannot close and refuses to serve a single number it cannot prove by a path other than
> the one that made it. The database itself refuses to let the lie be stored.

---

*End VALIDATOR_SUPREMO. Six organs, one machine: V1 bounds how many exist, V2 proves each
entity done, V6 supplies the math, V3 prosecutes every claim adversarially, V4 manages the
lie to closure, V5 stores the proof and gates the serving. A claim that cannot survive an
independent path is REFUTED; a population that cannot be fully observed is reported as an
interval; a gap is confessed, never filled in silence.*

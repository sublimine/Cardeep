## Task Report — TASK-008

## Status
DONE

## Mode
AUDIT_ONLY

**Verification note:** This report was produced by an investigation pass that connected read-only to the already-live `cardeep-pg` database and was then independently spot-checked by an adversarial verification pass that re-read 12 of the cited claims. 11 held up exactly; 1 minor overstatement was found (a grep claim that undercounted its own hits) and is corrected inline below. It does not affect the audit's central finding (§11 — the served identity views rest on `vam_verified=TRUE` flags with no DB-enforced proof).

---

# DEDUP_IDENTITY_AUDIT.md — Dealer/Entity/Vehicle Identity & Deduplication Subsystem

**Task:** TASK-008 | **Risk level:** CRITICAL | **Mode:** read-only audit | **Audit date:** 2026-07-16
**Scope:** `pipeline/ids.py`, `pipeline/identity/` (12 files), `scripts/build_canonical_dedup.py`, `scripts/build_particular_dedup.py`, `scripts/build_residual_namemuni_dedup.py`, `scripts/cross_platform_dedup_watermark.py`, `scripts/associations/dedup_upsert.py`, `pipeline/exhaustiveness/splink_merge.py`, `migrations/`, `tests/`.

This document was produced by static reading of every file in scope plus **read-only SQL SELECT queries** against the already-running local dev Postgres container `cardeep-pg` (127.0.0.1:5433, started before this session — not started by this audit). No file was written, edited, migrated, or mutated. No INSERT/UPDATE/DELETE was executed. No server/container was started.

---

## 0. Executive summary

Cardeep's identity/dedup subsystem is a multi-layer pipeline: (1) a deterministic hash-based **cdp_code** minted at ingest time from name/domain/CIF/municipality, (2) a **union-find clusterer for dealers** (`cluster_dealers.py`, B1) and a separate one **for vehicles** (`cluster_vehicles.py`, B7), both writing non-destructive overlay tables, (3) a chain of **canonical-dedup overlays** (`scripts/build_canonical_dedup.py` → `build_particular_dedup.py` → `build_residual_namemuni_dedup.py`) that further fuse B1 canonicals, (4) two **computed-but-not-served** alternative resolvers (`cross_source_dedup.py`, `resolve_entities.py`), and (5) a genuinely destructive but reversible **VIN-exact row-collapse** script (`cross_platform_dedup_watermark.py`) that is the only piece of this subsystem that deletes `vehicle` rows.

The team has clearly been burned by both failure modes before and has built real regression tests for each: a documented **113k-row over-merge incident** (private-seller aggregates fused via a relisted-car deep-link chain) and at least three documented **under-merge/fragmentation incidents** (Das WeltAuto, Mercedes-Benz wholesale, Milanuncios — one physical dealer split into up to ~480 cdp_codes because a volatile per-listing ID was hashed into the identity key). Both classes are now covered by targeted regression tests.

However, this audit found a concrete, currently-live governance gap: **the two most consequential, actually-served clustering runs (`dealer-identity-det-v1` and `vehicle-identity-det-v1`) have `vam_verified=TRUE` with `vam_verdict_id IS NULL`** — i.e. the "served" flag on the runs that back `v_dealer_resolved` and `v_canonical_vehicle` (the two views the API actually queries) carries **no DB-enforced proof of quorum review**, and the one migration that adds that DB-level protection (0070) was applied to `canonical_dedup_run` only, is forward-only (no backfill), and does not cover `entity_cluster_run` or `vehicle_cluster_run` at all — ever, today. A second concrete governance gap: `entity_resolution_run.vam_verified=TRUE` while its own linked `verification_verdict` (id 1093) says `verdict='UNVERIFIED', quorum_n=0` — a live, in-database contradiction of the project's own `vam_verified_allowed()` rule. This second run is not served (0 code consumers of `v_resolved_dealer`, confirmed by grep), so its blast radius is currently zero, but it proves the "manual boolean with no check" failure mode the team's own code comments warn about has already happened once, inside this exact subsystem.

Overmerge risk today is well-guarded (regression tests, multiple deterministic edge guards, country-proof triple-belt, all currently green/0-violations against the live DB). Undermerge risk is structurally larger and less guarded: none of the seven heavy identity/dedup batch scripts are on the automated scheduler (only `canonical_key_backfill_job` is), so every entity/vehicle ingested since the last manual run is an un-deduped singleton until an operator re-runs the pipeline by hand — a gap independently confirmed to be non-zero and growing at the moment of this audit (595 dealer-kind entities ingested since the last served B1 run, ~0.65% of the dealer census).

**Production-readiness label:** **PARTIALLY MATURE, NOT GOVERNANCE-HARDENED.** The identity math is well-engineered and well-tested at the pure-function level; the operational/governance envelope around "what is actually served and on what proof" has real, verifiable holes. See §15.

---

## 1. Dealer identity — end to end

### 1.1 Layer 0 — source identity (cdp_code minting at ingest, per connector)

**File:** `services/api/codes.py` (VERIFIED_STATIC, read in full).

Every `pipeline/platform/*.py` connector computes a deterministic `cdp_code` for a dealer via `cdp_code()` / `cdp_pair()` (`services/api/codes.py:100-131`). The **canonical_key priority order** (`canonical_key()`, `services/api/codes.py:56-97`) is:

1. `particular_platform + particular_seller_id` → `particular:{platform}:{sellerId}` (private sellers only)
2. `domain` (bare host only, no path) → `domain:{host}`
3. `cif` → `cif:{CIF}`
4. `name + municipality_code (+ optional address)` → `name:{norm}|{muni}`
5. `name + province_code (+ optional address)` → `name:{norm}|p{prov}`

`cdp_code = CDP-{country2}-{province2}-{8×Crockford-base32(sha256(canonical_key))}` (`mint_code`, `services/api/codes.py:44-53`). `entity.cdp_code` has a **UNIQUE INDEX only, not a UNIQUE constraint** (`migrations/0002_entities.sql:35`; explicitly called out in `migrations/0020_entity_cluster.sql:9-11` as the reason `entity_cluster` FKs on `entity_ulid`, not `cdp_code`).

This hash-based key IS the first, and in practice the dominant, dealer-dedup mechanism: two independent connectors that resolve to the same `(domain)` or same `(name, municipality_code)` mint the **same** `cdp_code` and collapse into one `entity` row at INSERT time via an `ON CONFLICT`-style attach-to-`entity_source` pattern (seen directly in `scripts/associations/dedup_upsert.py:191-257`, the pattern `canonical_key_backfill.py`'s docstring describes as replicated across "~70 hand-rolled `INSERT INTO entity` sites across ~40 connectors").

**Historical undermerge bugs at this layer (fixed, regression-tested):**
- **Das WeltAuto** (`tests/test_das_weltauto_dealer_identity.py`, VERIFIED_STATIC): the portal emits 2-3 Bnr format variants (`0311K`/`C311K`/`30060`) per physical dealership; the old code hashed `address=f"bnr:{d.bnr}"` into the identity, so each variant minted a different `cdp_code`, splitting one dealer into 2-3 entities. Fixed by dropping the Bnr from the hash (`address=None`); Bnr kept only as `entity_source.source_ref`.
- **Mercedes-Benz wholesale** (`tests/test_mercedes_benz_wholesale_dealer_identity.py`, VERIFIED_STATIC): per-car `dealerCode` prefix was hashed into identity → **"MOBILITY CENTRO / muni 28134 → 480 distinct cdp_codes for 488 vehicles (ratio 1.02)"** — i.e. almost one entity per car, not per dealer. Fixed the same way (name+municipality only).
- **Milanuncios** (`tests/test_milanuncios_dealer_identity.py`, VERIFIED_STATIC): `authorId` is per-listing-session, not per-dealer; "121 intra-source groups detected in prod." Same fix pattern.

These three are documented, source-level **undermerge** incidents, all fixed by removing a volatile field from the identity hash, and all covered by regression tests that assert both directions (same-dealer variants collapse to one code; genuinely-distinct dealers stay distinct). Confidence: VERIFIED_STATIC (code + tests read directly).

### 1.2 Layer 1 — deterministic dealer clustering (B1, `pipeline/identity/cluster_dealers.py`)

**File read in full**, `pipeline/identity/cluster_dealers.py` (1027 lines). `run_id='dealer-identity-det-v1'`, writes `entity_cluster` + `entity_cluster_run` (`migrations/0020_entity_cluster.sql`).

- **Scope:** `kind <> 'particular' AND status <> 'closed'` (`cluster_dealers.py:79`).
- **Edges (union-find, all country-scoped by `(value, muni, country)` or `(value, country)`):**
  1. CIF exact match, cross-municipality (`_normalize_cif`, `cluster_dealers.py:162-176`) — placeholders (`000000000`, `XXXXXXXXX`) rejected. **Highest-precision edge.**
  2. `normalized_name + municipality_code + country_code`, exact — `name_normalize.normalize_name()` (anyascii transliteration + legal-suffix strip).
  3. `phone_digits (>=7) + municipality_code + country_code`, exact.
  4. `normalized_website_host + municipality_code + country_code` — same-municipality guard (deliberately NOT a global website match, to avoid collapsing a chain's shared domain across branches).
  5. SQL `levenshtein(normalized_name) <= 2` within the same `(municipality_code, country_code)` block, **only for blocks ≤ 500 entities** (`FUZZY_BLOCK_CAP`), name length ≥ 8 chars (`FUZZY_MIN_NAME_LEN`, guards against `megar`/`vegar`-style false merges on short names).
- **Canonical selection** (`_select_canonical`, `cluster_dealers.py:516-535`): `source_group` rank → field richness → `first_seen` (older wins) → `cdp_code` lexicographic tiebreak.
- **Country-proof "triple belt"**: (1) country in every block key, (2) `_country_guard.assert_single_country_clusters()` runs post-clustering and raises `CrossCountryClusterError` (fail-closed) before write, (3) DB trigger `trg_entity_cluster_country` (`migrations/0071_entity_cluster_country_proof.sql`) rejects any INSERT/UPDATE into `entity_cluster` where the member and canonical entity have different `country_code`. VERIFIED_RUNTIME: this trigger exists live (`pg_trigger` query, see §Evidence) and is enabled (`tgenabled='O'`).
- **Idempotent** (`DELETE ... WHERE cluster_run_id=RUN_ID` then re-INSERT), **not automatically scheduled** (see §11.3).
- Ships its own built-in `_verify_and_report()` (7 checks incl. Flexicar/OcasionPlus chain-separation, MOBILITY CENTRO must-collapse-to-1, Megar≠Vegar) — this is print-only output from a manual run, not a CI gate.

**VERIFIED_RUNTIME (live query against `entity_cluster_run`, `docker exec cardeep-pg psql`):**
```
cluster_run_id             | resolver                  | vam_verified | n_entities_in | n_clusters_out | n_merged
dealer-identity-det-v1     | union-find-deterministic  | t            | 91319         | 58520          | 32799   (run_at 2026-06-22 22:42)
cross-source-dedup-v1      | cross-source              | f            | 50497         | 49809          | 688
cross-source-dedup-v1-SAMPLE | cross-source            | f            | 8764          | 8645           | 119
```
Served run collapses 32,799 of 91,319 dealer-kind entities (35.9%) into 58,520 canonical dealers.

### 1.3 Layer 2 — canonical-dedup overlay chain (the *actually served* dealer identity)

Three scripts, applied in sequence, each writing a new `canonical_dedup_run` row (`migrations/0027_canonical_dedup.sql`):

1. **`scripts/build_canonical_dedup.py`** (read in full) — `run_id='canonical-dedup-deeplink-v1'`. Groups `vehicle.deep_link` by resolved B1 canonical; two canonicals sharing a `(country_code, deep_link)` pair (K<3, anti-hub guard) are the same physical dealer → union-find. **Explicitly excludes `kind='particular'`** (`build_canonical_dedup.py:170-177`) — this is the direct root-fix for the 113k-car over-merge incident (§10.1). Hard-asserts against 4 sealed count constants and `sys.exit(1)` on any divergence ("DIVERGENCE DETECTED... DO NOT force the asserts").
2. **`scripts/build_particular_dedup.py`** (read in full) — `run_id='particular-canonkey-v1'`. Adds merges for private sellers whose `entity.canonical_key` (= `particular:{platform}:{sellerId}`, a **collision-free, definitive** discriminator — it IS the platform's own user id) is shared across >1 `cdp_code` (one human listed across N provinces). Copies the served run verbatim, then adds only same-`canonical_key`+country merges. Case A/B/C classification with an explicit "Case C: cross-kind or ambiguous → SKIP" guard. Built inert (`vam_verified=FALSE`); gated separately by `scripts/gate_particular_dedup.py`.
3. **`scripts/build_residual_namemuni_dedup.py`** (read in full) — `run_id='residual-namemuni-v1'`, currently the **served** run. Folds a small residual of same-name+same-municipality dealers that escaped B1's blocking into the dominant already-merged cluster. Guards: single address per group (else "possible branch", excluded), chain-name token exclusion (`flexicar`, `ocasionplus`, `clicars`, …), and a **"bystander drag" eligibility guard** (`_is_eligible`, `build_residual_namemuni_dedup.py:200-207`) that refuses a merge if it would collaterally absorb a base-super-canonical member outside the group — this is described in-code as "the root fix for the cross-dealer over-merge the safety assert caught," i.e. a second over-merge was caught and fixed during this script's own development. Writes a `verification_verdict` with a genuine 2-path VAM (arithmetic `served_before - collapsed` vs. structural overlay-recount) before flipping `vam_verified=TRUE`.

**Served view:** `v_dealer_resolved` (`migrations/0028_dealer_resolved.sql`) composes B1 (`v_canonical`) ∘ `canonical_dedup` (latest `vam_verified=TRUE` row). It is explicitly labeled `AUTHORITATIVE served dealer-identity resolver` (`migrations/0038_identity_resolver_labels.sql:8-9`) and is consumed by `services/api/deps.py:104-136` (`resolve_cluster`), `services/api/stats.py:29-32`, `services/api/routers/geo.py:298-308` (VERIFIED_STATIC via grep across `services/`).

**VERIFIED_RUNTIME (`canonical_dedup_run`, live):**
```
run_id                        | vam_verified | n_canonicals_in | n_super_canonicals | n_merged | deduped_count | run_at
residual-namemuni-v1          | t            | 50               | 4449               | 4908     | 47519         | 2026-06-23 02:16:51  <- currently SERVED
particular-canonkey-v1        | t            |                  |                    |          |               | 2026-06-23 02:15:36
canonical-dedup-deeplink-v1   | t            | 58520            | 3587               | 4043     | 54488         | 2026-06-22 23:46:36
```
`v_dealer_resolved`'s `latest_run` CTE picks the served row via `ORDER BY run_id DESC` (**string** sort, `migrations/0028_dealer_resolved.sql:43`), not `run_at DESC`. In this instance the alphabetically-latest run_id (`residual-namemuni-v1`, 'r') also happens to be the chronologically latest, so today it agrees — but this is a **latent inconsistency** vs. the sibling views `v_canonical` (0020), `v_canonical_vehicle` (0023) and `v_resolved_dealer` (0025), which all use `ORDER BY run_at DESC`. See Finding F-06 / Risk R-06.

### 1.4 End-to-end dealer identity flow (summary)

```
connector parses dealer page
   → cdp_code_dealer() / cdp_pair() [name+muni | domain | cif]  (source identity, per-connector)
   → INSERT ... entity (UNIQUE INDEX on cdp_code collapses same-key dealers at write time)
   → [manual, unscheduled] cluster_dealers.py -> entity_cluster (B1, run 'dealer-identity-det-v1', SERVED, vam_verified=TRUE, vam_verdict_id=NULL)
   → [manual, unscheduled] build_canonical_dedup.py -> canonical_dedup (deep-link fusion, excludes particulares)
   → [manual, unscheduled] build_particular_dedup.py -> canonical_dedup (particular canonical_key province-split fusion)
   → [manual, unscheduled] build_residual_namemuni_dedup.py -> canonical_dedup (currently SERVED layer, residual name+muni stragglers)
   → v_dealer_resolved (B1 ∘ dedup, "ORDER BY run_id DESC")  <-- what services/api/deps.py:resolve_cluster actually reads
```
Two **parallel, computed-but-NOT-served** alternative resolvers exist off to the side (§4).

---

## 2. Entity identity

`entity` (`migrations/0002_entities.sql`) is the single table for dealers, chains/OEM branches, and private sellers (`kind`), keyed by `entity_ulid` (PK) with `cdp_code` (unique index, immutable "identity hash"), `canonical_key` (nullable, the audit *pre-image* of `cdp_code`, backfilled lazily by `pipeline/identity/canonical_key_backfill.py`), `org_id` (FK to `organization`, `migrations/0007_organization.sql`, used as the **chain guard** — two entities sharing a non-null `org_id` are branches of the same legal chain and are **hard-blocked from merging** regardless of any other signal, in both `resolve_entities.py` and `cross_source_dedup.py`), and `country_code` (CHAR(2) NOT NULL DEFAULT 'ES', `migrations/0052_country.sql`, the axis every dedup edge is scoped by).

`pipeline/identity/canonical_key_backfill.py` (read in full) is a **self-verifying, re-hash-gated** lazy backfill: it recomputes candidate `canonical_key`s from a row's *stored* fields and writes the key **only if the recompute re-hashes to the row's already-stored `cdp_code`** — "a WRONG key is impossible to write (the hash is the witness)." This is the one identity job that IS on the automated scheduler (`pipeline/ops/scheduler.py:875-885`, `canonical_key_backfill_job`, interval-based). It is audit-only (doesn't gate any dedup decision, doesn't touch `entity` rows beyond the one NULL→value UPDATE).

---

## 3. Source identity

Cross-source dedup happens at two layers:
1. **Hash collision at INSERT** (§1.1) — the dominant mechanism for dealers with a stable domain/CIF/name+municipality across sources.
2. **`entity_source(entity_ulid, source_key)`** (`migrations/0002_entities.sql:43-48`, composite PK) — every source that has seen an entity attaches a row here; this is provenance, not a merge decision, but it is what `cross_source_dedup.py`'s orthogonality guard and `resolve_entities.py`'s block-1 fingerprint both read to know which sources/kinds an entity comes from.

`pipeline/identity/cross_source_dedup.py` (read in full, 1071 lines, `run_id='cross-source-dedup-v1'`) is a **separate, NOT-served** attempt at this problem specifically for OSM×digital-platform pairs (digital classifieds carry near-zero lat/lon/phone, so B1 cannot bridge them to their OSM twin). Signals: phone (9-digit, `PROB_PHONE=0.97`), website domain (`PROB_WEBSITE=0.98`), exact normalized name + orthogonal source types (`PROB_NAME_EXACT=0.82`, name length ≥ 6, chain-pattern exclusion). VERIFIED_RUNTIME: `vam_verified=FALSE` for both the full run (688 merges over 50,497 entities) and the province-sample run. Per `docs/architecture/11-IDENTITY-RESOLUTION-AUTHORITY.md` (dated 2026-06-15, VERIFIED_STATIC), this is a **deliberate deferral**: only ~13 of the 688 candidate merges are estimated "genuine," and serving any of them would require rebuilding `v_dealer_resolved` as a full union-find transitive closure over {B1, canonical_dedup, cross-source} edges — judged too high-risk for the estimated value. This is a documented, reasoned engineering decision, not an oversight — but it does mean **cross-source (OSM×digital) duplicates are a known, accepted, currently-unaddressed dealer-identity gap** (undermerge by omission).

`scripts/associations/dedup_upsert.py` (read in full) is a **third, independent** source-identity dedup path used specifically when ingesting dealers discovered via association mining: bare-host → name+muni → name+prov match against a live in-memory index built once from `entity`. Country-scoped throughout (`DedupIndex.match/register`, `country_code` in every key). A new dealer is inserted only if none of the three match; otherwise it's attached as a corroborating `entity_source` row on the existing entity.

`pipeline/exhaustiveness/splink_merge.py` (read in full, 294 lines) implements a **fourth, orthogonal** cross-source dealer-linking mechanism using the `splink` probabilistic-matching library (Fellegi-Sunter, DuckDB backend), but its **sole purpose is capture-recapture exhaustiveness estimation** (writes `discovery_splink_cluster`, `migrations/0049_discovery_splink_cluster.sql`) — it explicitly UNIONs its own equivalence classes with the existing `v_dealer_resolved` mapping so "the capture unit is NEVER finer than v_dealer_resolved," and it is **not** a dedup path that feeds anything served. It is gated behind an optional dependency: `splink_available()` returns `False` and the whole run degrades to `{"status": "splink_unavailable"}` if the `splink` package isn't installed (GATED — I did not verify whether `splink` is installed in this environment).

---

## 4. The two computed-but-not-served identity resolvers

**`pipeline/identity/resolve_entities.py`** (read in full, 1458 lines, `run_id='entity-resolution-fingerprint-v1'`, writes `entity_resolution` / `entity_resolution_run`, `migrations/0025_entity_resolution.sql`). This is the most sophisticated resolver in the codebase:

- **Dominant signal:** inventory fingerprint — Jaccard similarity ≥ `JACCARD_THETA=0.30` on the set of shared *used-car* `canonical_vehicle_ulid`s (from B7) between two P-stratum (`compraventa`, `concesionario_oficial`, `garaje`) entities, excluding catalog/high-collision canonicals (`MAX_ENTITY_COLLISION_K=5`).
- **Reinforcement:** phone / website, with a "centralita" (call-center) guard: a phone shared by ≥3 P-entities (`MAX_PHONE_COLLISION_K=3`) cannot merge alone — needs fingerprint or a second identifier.
- **Hard guards:** `ConstrainedUnionFind` propagates **city** (INE-municipality-validated token, e.g. blocks "AutosMadrid Alcorcón" ≠ "AutosMadrid Leganés" even at Jaccard 1.0), **org_id** (chain-sibling), and **country** constraints *transitively* — i.e. it defends against the classic union-find "bridge entity" transitivity bug (A merges with C, C merges with B, therefore A~B even though A and B individually don't match) by rejecting any union whose merged component would carry >1 distinct city/org/country value.
- **Seeds** the B1 (`v_canonical`) edges before applying its own β edges, so it composes B1∘β.

**VERIFIED_RUNTIME:** `entity_resolution_run`: `vam_verified=TRUE`, `n_in=59506`, `n_resolved_dealers=38555`, `n_merged=20951` (35.2% collapse), `vam_verdict_id=1093`. **`verification_verdict WHERE id=1093` → `verdict='UNVERIFIED', quorum_n=0, family_n=0, origin_n=0`.** This directly contradicts the project's own gating rule, `pipeline/identity/vam_gate.vam_verified_allowed(verdict, quorum_n) = verdict=='TRUSTWORTHY' and quorum_n>=2` (`pipeline/identity/vam_gate.py`, tested by `tests/test_vam_gate.py`) — by that rule this run should never have been marked `vam_verified=TRUE`. **CONTRADICTION**, confirmed live.

Mitigating fact: `v_resolved_dealer` (the view exposing this run) is confirmed to have **zero code consumers** — `grep -r "v_resolved_dealer" services/**/*.py` returns no hits (VERIFIED_STATIC), and `migrations/0038_identity_resolver_labels.sql:11-12` explicitly documents this: *"BETA fingerprint resolution... COMPUTED BUT NOT SERVED (0 code consumers)... Do NOT wire into any serving path; use v_dealer_resolved."* So today's practical blast radius is zero — but the contradiction is a live demonstration, inside this exact table family, of the exact "manual boolean, no proof" risk the team is otherwise defending against (§9).

---

## 5. Vehicle identity — end to end

**File read in full:** `pipeline/identity/cluster_vehicles.py` (1108 lines). `run_id='vehicle-identity-det-v1'`, writes `vehicle_cluster` + `vehicle_cluster_run` (`migrations/0023_vehicle_cluster.sql`). Scope: `status='available'`.

- **Signal A — photo_url exact match** (normalized: strip scheme/query/trailing-slash/resize-suffix). "Sufficient alone" — but with four layered guards:
  - **km=0/NULL guard**: disabled unless both listings share an identical non-null `vin_ref`. Explicitly documented, accepted bias: *"a genuine cross-platform duplicate of a new car will be double-counted (over-count)... strictly preferable to collapsing distinct dealer stock (under-count)."*
  - **Country guard**: only merges within one `country_code` (reached via `entity`, since `vehicle` has no country column, `migrations/0003`/`0052`).
  - **High-collision guard** (`PHOTO_HIGH_COLLISION_K=12`): a normalized photo URL shared by ≥12 listings is classified catalogue/stock (BCA placeholder shared 1,752×, SEAT render 220-274×, Flexicar `coming_soon.jpg` 331×) and excluded from Signal A. Calibrated against a stated production sample (1.689M vehicles, 2026-06-15).
  - **Generation-span guard** (`_photo_pair_spans_generations`, added per "audit pass-4 D7"): a shared sub-threshold catalogue photo whose two listings differ by >2 model-years or >50,000 km is rejected — documented real defect: a 2008 Citroën C4 (€3,000/285k km) had collapsed with a 2024 C4 (€19,990/16k km) before this guard. Unit-tested in `tests/test_cluster_photo_guard.py`.
- **Signal B — "firma"**: exact `(make, model, year, km)` + price within ±2% + same `country_code`+`province_code` + **different** `entity_ulid` (same-entity pairs are never firma-merged — same-dealer stock-bulk of the same model is legitimate distinct inventory) + same normalized title (transliterated per `name_normalize._ascii_fold_transliterate`, shared with the dealer-name normalizer so non-Latin scripts don't silently erase the corroboration gate). **Non-null-price guard**: both prices must be non-NULL, else the ±2% check is vacuously satisfied by two NULLs — documented real defect this closed: "VW Caddy: 1,752 listings → 1 cluster in previous run."
- **Canonical selection:** earliest `first_seen` wins; tiebreak `vehicle_ulid` ascending.
- **Pre-write BLOCKING country-isolation guard** (`_assert_no_cross_country_clusters`, raises `RuntimeError` before any commit if a cluster spans >1 country) + DB trigger `trg_vehicle_cluster_country` (`migrations/0072_vehicle_cluster_country_proof.sql`, VERIFIED_RUNTIME present + enabled).

**Served view:** `v_canonical_vehicle` (`migrations/0023_vehicle_cluster.sql:57-76`), latest `vam_verified=TRUE` run by `run_at DESC` (consistent with the other cluster tables, unlike `v_dealer_resolved`). Consumed directly by `services/api/routers/vehicles.py:92`, `entities.py:76,135`, `main.py:27`, `stats.py:40` (VERIFIED_STATIC via grep).

**VERIFIED_RUNTIME (`vehicle_cluster_run`):**
```
cluster_run_id           | vam_verified | n_in    | n_clusters | n_merged | run_at
vehicle-identity-det-v1  | t            | 2262673 | 1939474    | 323199   | 2026-06-22 14:17:10
```
323,199 of 2,262,673 available listings (14.3%) collapse to a shared canonical car. `vam_verdict_id` is NULL for this row (same gap as B1, §9).

**LEFT-JOIN + COALESCE-to-self fallback**: a vehicle absent from `v_canonical_vehicle` (i.e. ingested after the last B7 run, or never clustered) is its own canonical. This is explicit and documented in-code (`services/api/routers/entities.py:70-72`): *"a vehicle absent from v_canonical_vehicle (not yet in a cluster run — 9,827 available cars / 1,329 dealers as of audit P2 E-inventory) is its own canonical and MUST be counted. An INNER JOIN dropped them, reporting 0 stock for live dealers."* This is the correct behavior for *serving* (no data loss), but it means those 9,827+ vehicles (as of that prior audit) get **zero cross-platform dedup** until the next manual B7 run.

---

## 6. Canonical IDs

| ID | Minted by | Mutable? | Purpose |
|---|---|---|---|
| `entity_ulid` | `pipeline/ids.py::ulid()` (48-bit ms time + 80-bit random, Crockford base32) or the near-identical copy in `scripts/associations/dedup_upsert.py::ulid()` | No (PK) | Row identity |
| `cdp_code` | `services/api/codes.py::cdp_code()`/`cdp_pair()` (sha256 of `canonical_key`) | **Immutable by design** (`migrations/0020` comment: "never rewriting an immutable cdp_code") | Human-facing dealer identity, `CDP-{country}-{prov}-{8×b32}` |
| `canonical_key` | `services/api/codes.py::canonical_key()` | Audit pre-image, lazily backfilled | Forensics only — "NOT a hot-path dedup key" |
| `canonical_ulid` (entity_cluster) | B1 clusterer, `_select_canonical` | Recomputed on every re-run | The B1-chosen representative |
| `resolved_cdp_code` (v_dealer_resolved) | Composition of B1 + canonical_dedup | Recomputed on every re-run | **What the API actually serves as "the dealer"** |
| `canonical_vehicle_ulid` (vehicle_cluster) | B7 clusterer | Recomputed on every re-run | What the API serves as "the physical car" |
| `resolved_dealer_ulid` (entity_resolution) | β resolver | Not served | Dead-end, see §4 |
| `splink_cluster` | Splink probabilistic clusterer | MSE-only | Not an identity, an exhaustiveness-denominator unit |

`pipeline/ids.py` itself is an 18-line generic ULID generator with no dedup logic of its own; it is a dependency of the identity subsystem, not a resolver.

---

## 7. Cluster/dedup tables (all VERIFIED_STATIC from migrations, cross-checked against live schema)

| Table | Migration | Served view | Currently served run (VERIFIED_RUNTIME) |
|---|---|---|---|
| `entity_cluster` / `entity_cluster_run` | 0020 | `v_canonical` (deprecated per `deps.py` comment, not queried directly by endpoints) | `dealer-identity-det-v1` |
| `vehicle_cluster` / `vehicle_cluster_run` | 0023 | `v_canonical_vehicle` (SERVED, queried directly) | `vehicle-identity-det-v1` |
| `entity_resolution` / `entity_resolution_run` | 0025 | `v_resolved_dealer` (NOT served, 0 consumers) | `entity-resolution-fingerprint-v1` |
| `canonical_dedup` / `canonical_dedup_run` | 0027 | `v_canonical_deduped_draft` (draft, most-recent-regardless-of-vam) | 3 rows, all `vam_verified=TRUE` |
| — (composition) | 0028 | `v_dealer_resolved` (SERVED, queried directly) | `residual-namemuni-v1` (via `ORDER BY run_id DESC`) |
| `discovery_splink_cluster` | 0049 | none (exhaustiveness-internal) | per-`build_run_id`, not a "served" concept |

---

## 8. Dedup scoring

There is **no single probabilistic score** used to gate serving anywhere in this subsystem except in `cross_source_dedup.py` and `resolve_entities.py` (both NOT served) and `splink_merge.py` (MSE-only, gated dependency). The two **served** resolvers (`cluster_dealers.py`, `cluster_vehicles.py`) are **fully deterministic union-find**: every edge is a boolean pass/fail on exact-match block keys (plus a bounded-Levenshtein exact-threshold for dealers). `match_probability` is written to `entity_cluster`/`vehicle_cluster` for record-keeping but is `NULL` for deterministic edges and is not consulted by any threshold logic in the served path (`cluster_dealers.py:580`, always `None`; `cluster_vehicles.py` also writes `None` for match_probability). The scored paths (`cross_source_dedup.py`'s `PROB_PHONE=0.97`/`PROB_WEBSITE=0.98`/`PROB_NAME_EXACT=0.82`/`PROB_MULTI=0.99`, and `resolve_entities.py`'s raw Jaccard as `probability`) exist only in the two computed-but-unserved layers.

---

## 9. Blocking keys (by module)

| Module | Blocking key(s) |
|---|---|
| `cluster_dealers.py` (B1) | `(cif, country)`; `(norm_name, muni, country)`; `(phone_digits, muni, country)`; `(website_host, muni, country)`; SQL-side muni block for fuzzy (≤500/block) |
| `cluster_vehicles.py` (B7) | `normalized_photo_url` (global, country-filtered post-hoc); `(make, model, year, km, country, province)` for firma |
| `cross_source_dedup.py` | `(phone9, muni, country)`; `(domain, muni, country)`; `(norm_name, muni, country)` |
| `resolve_entities.py` (β) | shared `canonical_vehicle_ulid` (fingerprint block); `norm_phone`; `norm_website_host` |
| `dedup_upsert.py` (associations) | `bare_host`; `(norm_name, muni, country)`; `(norm_name, province, country)` |
| `splink_merge.py` | `(municipality_code, name_prefix[:4])`; `phone`; `website_host`; `cif` |
| `build_canonical_dedup.py` | `(country_code, deep_link)` |
| `build_particular_dedup.py` | `(canonical_key, country_code)` |
| `build_residual_namemuni_dedup.py` | `(normalized_name, municipality_code, country_code)` |

---

## 10. Merge criteria — overmerge and undermerge risk (exhaustive, as mandated)

### 10.1 Overmerge risk

**Historical incident (fixed, regression-tested).** A deep-link super-canonical chain fused the 52 provincial "Particulares coches.net {Province}" `kind='particular'` aggregates into one **113,000-car** cluster — root cause: a single relisted private car shared across two provincial aggregates chained them together transitively. Root-fixed by excluding `kind='particular'` from the deep-link dedup graph (`scripts/build_canonical_dedup.py:170-177`, `AND e.kind <> 'particular'`). Documented in the docstring of `tests/test_dedup_invariants.py` (VERIFIED_STATIC, lines 1-33) and guarded by 6 live-DB regression tests (`TestServedRunNoOverMerge`): no cross-kind (`particular`+dealer) component, max component size ≤30 (real observed max 22), max distinct normalized trade-names per component ≤12 (real observed max 8), representative = richest member (gross check, >50-car margin), served dealer count cross-checked against an independent recompute. **VERIFIED_RUNTIME**: `v_country_proof_violations` (the cross-border analogue, `migrations/0057`) returns **0 rows** for both the `dealer` and `vehicle` served layers right now.

**Second, self-caught incident during development.** `build_residual_namemuni_dedup.py`'s docstring and its `_is_eligible`/"bystander drag" guard (`build_residual_namemuni_dedup.py:200-207`, `# root fix for the cross-dealer over-merge the safety assert caught`) describe a second over-merge caught by the script's own safety asserts before it was ever served — a name-key edge would have collaterally fused a bystander base-super-canonical member outside the residual group. This is evidence the safety-assert discipline works, but also evidence that a **name+municipality-only edge is intrinsically over-merge-prone** and needed a dedicated eligibility filter to be safe.

**Currently-serving over-merge surface area not covered by the regression suite:**
- `cluster_dealers.py`'s **fuzzy Levenshtein edge (edge 5)** is the one edge in the served B1 clusterer with no dedicated unit test of its own (see §13/§14) — it is only exercised indirectly through 4 country-isolation tests in `tests/test_country_isolation_dealer.py`. A regression in `FUZZY_MAX_LEVENSHTEIN`/`FUZZY_MIN_NAME_LEN`/`FUZZY_BLOCK_CAP` would not be caught by any unit test, only (maybe) by the live-DB integrity suite after the fact.
- `cluster_vehicles.py` Signal A (photo_url) is "sufficient alone" for a merge within one country — a wholesale/auction feed that reuses one photo URL across two genuinely distinct dealers' listings of visually-identical stock (e.g. a batch of identical fleet cars) would over-merge unless it also trips the high-collision guard (K=12) or the generation-span guard, neither of which detects *same-model, same-photo, different-VIN, different-owner* duplication directly — the sole protection there is the K=12 threshold, which is a volume heuristic, not an identity proof.

### 10.2 Undermerge risk

**Structural, currently-live, and largest identified risk of this audit.** None of the seven identity/dedup batch scripts (`cluster_dealers.py`, `cluster_vehicles.py`, `cross_source_dedup.py`, `resolve_entities.py`, `build_canonical_dedup.py`, `build_particular_dedup.py`, `build_residual_namemuni_dedup.py`) appear anywhere under `pipeline/ops/` — a clean grep of `pipeline/ops/` specifically for all 7 names returns zero hits. **[Corrected after adversarial verification]** The broader claim that a grep across `pipeline/ops/`, `scripts/`, `.github/` combined "returns only the scripts themselves and their own `__pycache__`" was overstated: `scripts/cutover_road13.sh` mentions `cluster_dealers`/`cross_source_dedup`/`build_canonical_dedup` in comment prose describing a manual DDL cutover procedure a human operator runs, and `scripts/gate_particular_dedup.py` mentions `build_particular_dedup` in a docstring cross-reference — neither is an automated scheduler or CI trigger. The substantive conclusion is unchanged: no automated mechanism invokes any of these 7 scripts. `pipeline/ops/scheduler.py` has exactly one identity-related scheduled job: `canonical_key_backfill_job` (interval-based, `scheduler.py:875-885`). Every entity or vehicle ingested since the last **manual** run of a clusterer is an un-deduped singleton in the served views (COALESCE-to-self fallback, confirmed at both `services/api/routers/entities.py:70-72` for vehicles and structurally identical in `v_dealer_resolved` for dealers). **VERIFIED_RUNTIME**: as of this audit, `entity WHERE kind<>'particular' AND status<>'closed'` = **91,914** rows, vs. `n_entities_in=91,319` fed to the currently-served B1 run (`run_at 2026-06-22`) — **595 dealer-kind entities (≈0.65%) have been ingested since the last dealer-identity clustering pass and are not deduped.** A prior audit pass (P2, referenced in the same `entities.py` comment) had already quantified an analogous vehicle-side gap of "9,827 available cars / 1,329 dealers... not yet in a cluster run." This gap grows monotonically between manual re-runs and directly inflates the served inventory/dealer counts (phantom duplicates), which is precisely the metric-falsification risk this audit was asked to prioritize.

**Deliberately accepted, disclosed undermerge (not a bug).** `scripts/cross_platform_dedup_watermark.py` (read in full) documents the project's explicit doctrine: *"over-merge must stay strictly below under-merge... Everything weaker [than VIN-exact or pHash+attrs] → distinct row (accept slight over-count, never over-merge)."* It measures the material cross-platform duplication at the strictest fuzzy floor (exact make+model+year+km+price+province, no photo signal) as **≈131.8K excess rows lower bound**, cross-validated by two independent grouping paths (SQL `GROUP BY` vs. Python streaming) agreeing within 0.09% divergence, and explicitly does **not** auto-merge them — it records the bound to `verification_verdict` via `pipeline.verify.record_count_verdict` so downstream counters can be served "WITH its measured bound" rather than silently. It notes `photo_hash` (the pHash arm of the doctrine's strong key) is **populated on 0 vehicles**, so today the *only* doctrine-permitted auto-merge is VIN-exact (18 rows, immaterial), applied via a real `DELETE FROM vehicle` that is reversible only via a JSON backup file this script writes — **no restore/replay script for that backup was found anywhere in the repo** (GATED/unknown — see §12).

**Deliberately deferred merges (documented, reasoned, but still a live gap).** Per `docs/architecture/11-IDENTITY-RESOLUTION-AUTHORITY.md` (2026-06-15): β (`entity_resolution`, ~388 net-new merges beyond served) and cross-source (`cross-source-dedup-v1`, ~13 genuine dealer merges out of 688 candidate pairs) are both computed but withheld because serving either requires rebuilding `v_dealer_resolved` as a full transitive-closure union-find over multiple edge families — judged too risky for the estimated ≤1% gain. This is sound risk management, but it is worth flagging that **this ADR is now stale relative to the live DB**: it cites "42,259 B1 canonicals / 40,016 deduped / 369,561 total resolved," while the live DB (post a 2026-06-22/23 B1 re-cluster) shows 58,520 B1 canonicals and 47,519 deduped — the census "grows continuously" exactly as the ADR itself predicts, but the specific numbers in the doc should not be trusted as current state (CONTRADICTION between docs and live DB, expected/disclosed drift per the doc's own framing, but a concrete instance of the governance rule "do not trust docs as truth without code/runtime evidence").

**Fuzzy-name-only edges are intentionally conservative** (undermerge-favoring by design): `cluster_dealers.py`'s Levenshtein edge requires name length ≥8 and distance ≤2, explicitly to avoid over-merging short names — the flip side is that any two genuinely-identical dealers whose names differ by >2 edits (e.g. abbreviation vs. full legal name beyond what the legal-suffix stripper catches) will never be linked by this edge and depend entirely on a shared phone/website/CIF/deep_link to be caught by a later layer.

---

## 11. Governance/proof-of-serving gap (new finding, not explicitly requested by the outline but directly load-bearing for CRITICAL risk)

`pipeline/identity/vam_gate.py` (read in full) defines the single intended rule: `vam_verified_allowed(verdict, quorum_n) = verdict=='TRUSTWORTHY' and quorum_n>=2`, unit-tested in `tests/test_vam_gate.py` (4/4 cases pass, including the "grandfathered TRUSTWORTHY/quorum_n=0 rows must NOT pass" case). `migrations/0070_vam_verified_needs_proof.sql` implements this as a DB trigger — **but only on `canonical_dedup_run`** (VERIFIED_RUNTIME: `pg_trigger` shows exactly `trg_canonical_dedup_vam_proof` on `canonical_dedup_run`, `trg_entity_cluster_country` on `entity_cluster`, `trg_vehicle_cluster_country` on `vehicle_cluster` — **no equivalent vam-proof trigger exists on `entity_cluster_run`, `vehicle_cluster_run`, or `entity_resolution_run`, today, at all**). And it is forward-only (per its own comment: "no backfill of existing rows"), applied 2026-06-29 (`schema_migrations` table, VERIFIED_RUNTIME) — **after** every currently-served run's `vam_verified=TRUE` transition (all `run_at` between 2026-06-14 and 2026-06-23).

**VERIFIED_RUNTIME, direct query of every run/verdict table in this subsystem:**
| Run (table) | `vam_verified` | `vam_verdict_id` | Linked verdict |
|---|---|---|---|
| `dealer-identity-det-v1` (entity_cluster_run) | TRUE | **NULL** | none |
| `vehicle-identity-det-v1` (vehicle_cluster_run) | TRUE | **NULL** | none |
| `entity-resolution-fingerprint-v1` (entity_resolution_run) | TRUE | 1093 | **UNVERIFIED, quorum_n=0** — contradicts vam_gate.py's own rule |
| `canonical-dedup-deeplink-v1` (canonical_dedup_run) | TRUE | **NULL** | (a matching `verification_verdict` id 1121/1112 DOES exist in the ledger with `TRUSTWORTHY, quorum_n=2`, but is not FK-linked from the run row) |
| `particular-canonkey-v1` (canonical_dedup_run) | TRUE | **NULL** | (ledger has id 1423, `TRUSTWORTHY, quorum_n=2`, not linked) |
| `residual-namemuni-v1` (canonical_dedup_run) | TRUE | **NULL** | its own build script's code inserts a verdict and links it — live state shows the link is absent regardless |

**Net effect:** every currently-served identity/dedup decision in this product (which dealer you get from `/entities/{cdp_code}`, which vehicle counts as unique in `/stats`) rests on a `vam_verified=TRUE` flag that is **either mechanically unenforced (entity_cluster_run, vehicle_cluster_run — no trigger exists) or mechanically-unenforced-in-practice (canonical_dedup_run — trigger exists but is forward-only and predates every current row)**. This is not evidence any of these runs is *wrong* — the live over-merge/country-proof checks all currently pass — but it is evidence that **nothing in the database would stop a future bad run from being marked served**, for the two tables (`entity_cluster_run`, `vehicle_cluster_run`) that back the two views the API actually queries. This is the single most consequential finding of this audit for a CRITICAL-risk subsystem whose stated failure mode is "silently deletes real market coverage" / "inflates inventory counts with phantom duplicates."

---

## 12. Unmerge / recovery support

**No fine-grained per-pair override, exclusion-list, or "force-split" mechanism exists anywhere in this subsystem** (VERIFIED_STATIC: `grep -rli "manual_override|split_override|unmerge|force_split|merge_exclude|dedup_exclusion|blacklist_pair|denylist_merge"` across `pipeline/identity/`, `scripts/`, `migrations/` returns zero hits for any actual mechanism). Recovery is coarse-grained only:

1. **Whole-run revert**: `scripts/gate_particular_dedup.py --revert` flips `vam_verified=FALSE` on a specific `canonical_dedup_run`, causing `v_dealer_resolved` to fall back to the next-most-recent `vam_verified=TRUE` run (chosen by the `ORDER BY run_id DESC` quirk noted in §1.3). This un-serves an entire run; it does not fix or exclude a single bad pair within it.
2. **Full idempotent rebuild**: every script `DELETE`s its own `run_id` and re-INSERTs; the standard "fix" for a bad merge is to correct the code and re-run the whole clusterer. `entity`/`vehicle` rows are never mutated by any of the union-find clusterers, so this is always safe/non-destructive to the base data — but it is an all-or-nothing operation on the *run*, not a targeted unmerge.
3. **`canonical_dedup_backup_20260620`**: a one-off snapshot table created ad hoc by `build_residual_namemuni_dedup.py` immediately before its write (`CREATE TABLE IF NOT EXISTS ... AS SELECT * FROM canonical_dedup WHERE FALSE; TRUNCATE; INSERT INTO ... SELECT * FROM canonical_dedup`). Not a general mechanism — a single hand-rolled snapshot for that one script's own safety.
4. **`cross_platform_dedup_watermark.py`'s VIN-fold JSON backup** (`.backups/cross_platform_vin_merge_{stamp}.json`) is the **only reversibility artifact for the one truly destructive operation** in this subsystem (a real `DELETE FROM vehicle`). It records survivor, folded `vehicle_ulid`s, and every repointed `platform_listing`/`vehicle_event` edge. **No restore/replay script that reads this JSON back was found anywhere in the repo** (`grep -rl "cross_platform_vin_merge|\.backups" scripts/ pipeline/` returns only the writer script itself) — GATED/UNKNOWN whether restoring a bad VIN-fold is actually operationally possible today beyond a fully manual SQL replay of the JSON by a human.

---

## 13. Tests existing (by file, VERIFIED_STATIC — every file listed was read or grepped this session)

**Pure unit tests (no DB), the strongest layer of this suite:**
- `tests/test_cluster_vehicles.py` (1029 lines) — extensive: photo/title normalization incl. non-Latin transliteration, price tolerance, Signal A/B individually and combined, anti-FP guards, canonical selection, union-find primitives, **km=0/NULL + VIN guard** (14 dedicated cases), photo high-collision guard, firma non-null-price guard.
- `tests/test_resolve_entities.py` (1195 lines) — phone/website normalization, Jaccard, fingerprint/phone/website merge + anti-collision (centralita) guards, transitive closure incl. **no-spurious-transitive-merge**, canonical selection, union-find, **chain guard** (org_id), **city guard** (INE-validated, incl. multiword municipality), B1-seeding composition.
- `tests/test_cluster_photo_guard.py` — `_photo_pair_spans_generations` (the 2008-vs-2024-C4 defect fix), 5 cases.
- `tests/test_cif_dedup_edge.py` / `tests/test_recluster_cif_e2e.py` — CIF edge for `cluster_dealers.py` (merge, no-merge, cross-country, placeholder rejection; end-to-end simulated re-cluster).
- `tests/test_vam_gate.py` — the vam-proof predicate itself (4 cases incl. the grandfathered-zero-quorum case).
- `tests/test_name_normalize_properties.py`, `tests/test_norm_name_translit.py`, `tests/test_phone_es.py`, `tests/test_cross_source_phone.py` — normalizer correctness/byte-identity.
- `tests/test_das_weltauto_dealer_identity.py`, `tests/test_mercedes_benz_wholesale_dealer_identity.py`, `tests/test_milanuncios_dealer_identity.py` — the three source-identity undermerge-fix regressions (§1.1), each with explicit positive (collapse) and negative (stay-distinct) cases.
- 9 `tests/test_country_isolation_*.py` files (`_associations`, `_beta`, `_dealer`, `_dedup`, `_multicountry`, `_overlay_dedup`, `_seal`, `_serving`, `_vehicle`, `_vin_xplatform`) — the country-proof invariant, tested from unit level up through DB-integration level, across essentially every module in scope.
- `tests/test_country_proof_guard.py`, `tests/test_cross_source_country_belt.py` — additional country-belt coverage for `cluster_dealers.py`/`cross_source_dedup.py`.

**DB-integration tests (require the populated dev DB; excluded from ephemeral CI per `tests/ci_local_only.txt`):**
- `tests/test_dedup_integrity.py` (88 lines) — 4 structural invariants on the live `v_dealer_resolved`: no entity in 2 clusters, no dangling `resolved_ulid`, no alias-of-alias chain, canonical universe stays in a 30k-60k sanity band.
- `tests/test_dedup_invariants.py` (466 lines) — the over-merge regression suite (§10.1), 6 live-DB tests + 2 DB-free constant-sanity tests + 2 candidate-run superset/safety tests.
- `tests/test_entity_cluster_country_db.py`, `tests/test_vehicle_cluster_country_db.py` — DB-level country-isolation checks specific to the two served cluster tables.

**Overall assessment:** this is a genuinely substantial test suite (~3,100+ lines across the files sampled in depth alone, 25+ files total in scope) with real, specific regression coverage for both documented historical incident classes (overmerge and undermerge). It is one of the better-tested subsystems a governance audit is likely to encounter in this codebase.

## 14. Tests missing (VERIFIED_STATIC gaps, confirmed by targeted grep, not assumed)

- **No dedicated unit-test file for `cluster_dealers.py`'s core edges.** Confirmed via `grep -rl "from pipeline.identity.cluster_dealers import _select_canonical"` (zero hits) and `grep -rln "cluster_dealers"` (only 7 files, all focused on the CIF edge or country-isolation, none testing edge 1 (name+muni) in isolation, edge 2 (phone+muni), edge 3 (website+muni same-muni guard), or the `FUZZY_BLOCK_CAP`/`FUZZY_MIN_NAME_LEN` fuzzy-edge behavior as a unit). This is the module backing the *first, largest* dealer-clustering layer and has materially thinner direct unit coverage than its sibling `cluster_vehicles.py` (1029-line dedicated file) or `resolve_entities.py` (1195-line dedicated file, itself unserved).
- **`_select_canonical` in `cluster_dealers.py` has zero test references anywhere** (confirmed by grep) — the source_group-rank → richness → first_seen → cdp_code tiebreak chain that decides *which* entity becomes the served dealer for a cluster is untested in isolation (though partially exercised as a side effect of the live-DB `test_dedup_invariants.py::test_canonical_is_richest_member` check, which is a gross >50-car-drift check, not a precise assertion of the tiebreak order).
- **No test exercises the `ORDER BY run_id DESC` vs `run_at DESC` inconsistency** in `v_dealer_resolved` (§1.3) — no test asserts that the served `canonical_dedup_run` is the chronologically-latest one; it only happens to be true today because the alphabetically-latest run_id is also newest.
- **No test asserts `vam_verdict_id IS NOT NULL` for a `vam_verified=TRUE` row** across `entity_cluster_run`/`vehicle_cluster_run` (only `canonical_dedup_run` has the DB trigger, and even that has no corresponding *test* found in scope — `grep` for `trg_canonical_dedup_vam_proof` in `tests/` returns no hits I found).
- **No restore/replay test** for `cross_platform_dedup_watermark.py`'s VIN-fold JSON backup (consistent with no restore *script* existing either, §12).
- **`splink_merge.py` has no direct unit test for its own logic** — `tests/test_exhaustiveness.py` covers it only at the exhaustiveness-integration level, and the whole module degrades silently (`splink_available()==False`) if the optional dependency is absent, with no test asserting the degraded-mode return shape is what callers expect.
- **The residual-namemuni "bystander drag" eligibility guard** (`_is_eligible`, §10.1) — I found no test file specifically targeting `build_residual_namemuni_dedup.py`'s `compute_residual_overlay` pure core in `tests/`; its own docstring references `tests/test_country_isolation_overlay_dedup.py` as sharing the module-scope SQL/core, but that test's stated focus is country isolation, not the eligibility/bystander-drag logic itself. (PARTIAL — I read the docstring's claim but did not independently open `test_country_isolation_overlay_dedup.py` in full to confirm eligibility-guard-specific assertions exist there; flagged as an unknown, not asserted as a gap.)

---

## 15. Production-readiness label

**PARTIALLY MATURE, NOT GOVERNANCE-HARDENED.** I am not claiming "production-ready" — I have runtime evidence only from a local dev Postgres instance (`127.0.0.1:5433`, local-development credential redacted in this recovered copy), not from a verified production deployment, and I have no evidence of what serves real end users. Within that scope:

- **Strengths (VERIFIED_STATIC + VERIFIED_RUNTIME):** deterministic, reproducible, idempotent clustering; a real, working country-proof triple-belt (code path + Python assertion + DB trigger, all confirmed live); a substantial and specifically-targeted regression-test suite covering both documented historical failure classes; an explicit, documented risk doctrine ("over-merge must stay strictly below under-merge") that is actually followed in the one destructive script in this subsystem; honest, disclosed measurement of a known unaddressed duplication bound (131.8K rows) rather than silent under-counting.
- **Weaknesses (VERIFIED_RUNTIME):** the two views the API actually serves identity from (`v_dealer_resolved`, `v_canonical_vehicle`) rest on cluster runs whose `vam_verified=TRUE` flag has **zero DB-enforced proof** behind it today; one run in this exact table family already demonstrated the flag can disagree with its own linked proof (`entity_resolution_run` / verdict 1093); none of the 7 heavy dedup scripts run on a schedule, so the served identity resolution is a manually-refreshed snapshot that is **measurably stale right now** (595 un-clustered dealer-kind entities); the served-view "latest run" selection logic is inconsistent across sibling views (`run_id DESC` vs `run_at DESC`); at least one architecture doc cited as authoritative in code comments is confirmed stale relative to live data.

None of the above are hypothetical — every claim in this paragraph is backed by a file:line citation or a live query quoted above.

## 16. Required next tasks (RFC-gated where they touch threshold/merge logic, per this task's instructions)

1. **RFC_REQUIRED — extend the `vam_verified_needs_proof` trigger** (or an equivalent mechanism) to `entity_cluster_run` and `vehicle_cluster_run`, the two tables that actually back served identity. This is a schema/threshold-adjacent change to CRITICAL-risk serving logic and must go through `docs/ai/control/02_EXECUTION_MODES.md`'s RFC process, not be applied directly.
2. **Non-RFC, low-risk**: backfill `vam_verdict_id` on the 3 currently-live `canonical_dedup_run` rows and the 2 currently-live `entity_cluster_run`/`vehicle_cluster_run` rows from the `verification_verdict` ledger entries that already exist for them (ids 1121/1112/1423 are visibly present for the `canonical_dedup_run` family) — this is a data-completeness fix, not a merge-logic change, but should still be reviewed given it touches the served-identity tables.
3. **RFC_REQUIRED if it changes what's served**; otherwise **operational-only**: put `cluster_dealers.py`, `cluster_vehicles.py`, and the `build_*_dedup.py` chain on a scheduled cadence (or at minimum add a health/staleness metric — "entities ingested since last B1 run" / "vehicles ingested since last B7 run" — to the existing scheduler health surface) so the undermerge gap in §10.2 stops growing silently between manual runs.
4. **Non-RFC**: fix `v_dealer_resolved`'s `latest_run` CTE to `ORDER BY run_at DESC` for consistency with `v_canonical`/`v_canonical_vehicle`/`v_resolved_dealer`, or explicitly document why it deliberately differs.
5. **Non-RFC, test-only**: add a dedicated `tests/test_cluster_dealers.py` unit-test file mirroring the structure of `tests/test_cluster_vehicles.py`, covering edges 1-3 and the fuzzy edge (5) in isolation, plus `_select_canonical`.
6. **Investigate, not RFC**: locate or build a restore/replay tool for `cross_platform_dedup_watermark.py`'s `.backups/cross_platform_vin_merge_*.json` artifacts, or explicitly document that recovery is manual-SQL-only.
7. **Investigate, not RFC**: refresh `docs/architecture/11-IDENTITY-RESOLUTION-AUTHORITY.md`'s cited counts against current live state, or add a "these numbers are illustrative of the mechanism, not current state" disclaimer, given the census growth already documented in-file.

---

## Evidence appendix (representative live queries run this session, read-only)

```sql
-- entity_cluster_run (dealer B1)
SELECT cluster_run_id, resolver, vam_verified, n_entities_in, n_clusters_out, n_merged, run_at
FROM entity_cluster_run ORDER BY run_at DESC;
--> dealer-identity-det-v1 | t | 91319 | 58520 | 32799 | 2026-06-22 22:42:13
--> cross-source-dedup-v1  | f | 50497 | 49809 |   688 | 2026-06-14 06:54:07
--> cross-source-dedup-v1-SAMPLE | f | 8764 | 8645 | 119 | 2026-06-14 06:47:09

-- vehicle_cluster_run (vehicle B7)
--> vehicle-identity-det-v1 | t | 2262673 | 1939474 | 323199 | 2026-06-22 14:17:10

-- entity_resolution_run (beta, unserved)
--> entity-resolution-fingerprint-v1 | t | 59506 | 38555 | 20951 | 2026-06-14 23:47:25 | vam_verdict_id=1093

-- verification_verdict WHERE id=1093
--> UNVERIFIED, quorum_n=0, family_n=0, origin_n=0  <-- contradicts vam_verified=TRUE on the run above

-- canonical_dedup_run (all 3 rows)
--> canonical-dedup-deeplink-v1 | t | vam_verdict_id NULL | run_at 2026-06-22 23:46
--> particular-canonkey-v1      | t | vam_verdict_id NULL | run_at 2026-06-23 02:15
--> residual-namemuni-v1        | t | vam_verdict_id NULL | run_at 2026-06-23 02:16  (currently served)

-- pg_trigger (subsystem-relevant triggers only)
--> trg_canonical_dedup_vam_proof on canonical_dedup_run (enabled)
--> trg_entity_cluster_country    on entity_cluster (enabled)
--> trg_vehicle_cluster_country   on vehicle_cluster (enabled)
-- (no vam-proof trigger on entity_cluster_run / vehicle_cluster_run / entity_resolution_run)

-- schema_migrations
--> 0070/0071/0072 applied 2026-06-29 13:06 -- AFTER every run row's vam_verified=TRUE transition above

-- v_country_proof_violations
--> 0 rows (both dealer and vehicle served layers currently clean of cross-border merges)

-- live entity/vehicle population vs. last B1 input
SELECT count(*) FROM entity WHERE kind<>'particular' AND status<>'closed';  --> 91914
-- vs n_entities_in=91319 fed to the currently-served B1 run --> 595 (≈0.65%) un-clustered since last run

SELECT count(DISTINCT country_code) FROM entity;  --> 1  (single-tenant ES census in practice today)
```

All numbers above were obtained via `docker exec cardeep-pg psql -U cardeep -d cardeep -c "SELECT ..."` — read-only SELECT statements only, against a Postgres container that was already running before this session (confirmed via `docker ps`, not started by this audit).

---

## Corrections Applied (adversarial verification pass)

An independent verification pass re-checked 12 of this report's citations against the live repository. 11 held up exactly; 1 was overstated:

- **Overstated grep claim (cosmetic, substance unaffected):** the original draft stated a combined grep across `pipeline/ops/`, `scripts/`, `.github/` for all 7 identity/dedup script names "returns only the scripts themselves and their pycache." Two additional files actually match: `scripts/cutover_road13.sh` (comment prose describing a manual DDL cutover a human runs) and `scripts/gate_particular_dedup.py` (a docstring cross-reference). Neither is an automated trigger, so the underlying finding — no scheduler or CI invokes any of these 7 scripts — is unchanged. Corrected in §10.2.

## Files Modified By This Task
- `docs/ai/audits/DEDUP_IDENTITY_AUDIT.md` (new — this file)
- `docs/ai/findings/FINDINGS.md`, `docs/ai/findings/TECH_DEBT.md` (appended)
- `docs/ai/control/05_EVIDENCE_LEDGER.md`, `docs/ai/control/06_RISK_REGISTER.md` (appended)
- `docs/ai/tasks/TASK_QUEUE.yml` (status field only — disclosed exception, see FINDING-0001)

## Forbidden Files Touched
NO

## Validation Result
PASSED

## Next Recommended Task
TASK-009 — Audit source connectors and create source matrix.

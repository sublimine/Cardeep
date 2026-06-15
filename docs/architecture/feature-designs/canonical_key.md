# Feature Design — Persist `entity.canonical_key` (INSERT sites + self-verifying backfill)

**Review verdict:** NEEDS-REVISION → **revisions folded in below; PROCEED.**
**Effort:** L
**Files:** `services/api/codes.py`, `pipeline/discover.py`, `pipeline/ingest.py`, `scripts/overture_ingest.py`, `scripts/associations/*.py`, `scripts/upsert_paginas_amarillas.py`, `scripts/geo_sweep_collect.py`, `scripts/seed_pilot.py`, `pipeline/platform/*_wholesale.py` (35), `migrations/0039_entity_canonical_key_backfill.sql` (NEW), `tests/test_geo_upsert_backfill.py`, `docs/recon/AUDIT_2026-06-15_PHASE2.md`.

---

## 1. Summary & finding closed

Closes **B-canonical-key-column-empty** ([VERIFIED] 100% NULL on **391,944** rows; `SELECT count(canonical_key)=0`). `services/api/codes.py:34 canonical_key()` and `codes.py:73 cdp_code()` already exist — `cdp_code()` internally calls `canonical_key()` then sha256+base32, but only returns the formatted code, so the pre-image key is **computed and thrown away** at every call. The fix exposes the key (sibling `cdp_pair()` returning `(key, code)`) and writes `canonical_key` at the entity INSERT sites, then backfills the recoverable rows.

**Value:** `canonical_key` is the human-readable dedup pre-image (`particular:wallapop:{user_id}`, `domain:ford.es`, `name:{norm}|{muni5}`) — the only way to audit WHY two entities share/differ a `cdp_code`, debug a collision, or re-cluster without re-hashing blind. The `cdp_code` is a one-way hash; without the stored key, identity is opaque. It also exposes the audit signal **B-cross-province-split** (the same human in N provinces = N cdp_codes but ONE canonical_key).

### What the review corrected (folded in, not appended)
- **DROP `canonical_key` from every steady-state `ON CONFLICT ... DO UPDATE SET`** (esp. the milanuncios/wallapop/coches BULK unnest upserts). Add it ONLY to the **INSERT column list** so brand-new rows get it free, and rely on the one-time 0039 backfill for existing rows. This eliminates the PG-MVCC hot-path dead-tuple churn the original plan flagged as "for review": the bulk upserts re-run every harvest window over 330k particular rows; a COALESCE-self-write of the identical value = one dead tuple per row per window on the busiest table.
- **Dealer cascade yield is UNKNOWN, not a fixed number.** [VERIFIED counterexample] coches dealer key = `cdp_code(province_code=d.province_code, name=d.name, municipality_code=muni, address=f"contract:{d.contract_id}")` (coches_net_wholesale.py:445). Recomputing PORSMISTRAL (prov 47, contract 117145, stored cdp_code `CDP-ES-47-YXHJSXWV`) from the now-stored muni + `address='contract:117145'` gives `CDP-ES-47-DG4CRR3X` — **NO MATCH**. The stored `municipality_code`/`trade_name` differ from mint-time inputs (geo backfilled / name normalized post-mint = the **mutable-input-in-key** pathology). The reviewer's "coches recovers cleanly" claim is itself only partially right. **So: particulars are verified-recoverable; dealers are best-effort, gate-verified, count reported post-run.** The self-verifying re-hash gate keeps this SAFE (a non-matching recompute simply stays NULL; never a wrong write).
- **Branch the particular recompute on `source_key`** (the autocasion-orphan class): [VERIFIED] ml/wp use `source_ref` as `seller_id` (`particular:milanuncios:208044982`); coches uses `province_code` as `seller_id` with platform token `coches.net` — `cdp_code(province_code='50', particular_platform='coches.net', particular_seller_id='50')` = `CDP-ES-50-FPB3W1R6` (**MATCH**). The stored coches `source_ref` is the literal string `particular:50` (NOT a seller id) — using it naively yields all-misses (safe via gate, but 0 coverage).
- **Guard `province_code IS NULL`:** [VERIFIED] **365** NULL-province rows + **122** subasta rows are hard-blocked (`cdp_code` format requires `province_code`). The backfill predicate must skip them or the recompute raises.
- **`canonical_key` is NON-UNIQUE by design** — a private listed in N provinces yields N rows with N distinct cdp_codes (province in the prefix) but the SAME canonical_key. State this explicitly and add NO UNIQUE index ([VERIFIED] none exists in `pg_indexes`).
- **Maximize gate hits:** the backfill tries, per row, the FULL set of key variants (domain bare-host; `name|muni5`; `name|pPROV`; each with the `|norm(address-suffix)` variant built from `entity_source.source_ref` — e.g. `contract:{ref}`, `wallapop_user:{ref}`) and accepts the first whose re-hash == stored `cdp_code`.
- **Counts refreshed:** 391,944 entities; particular=330,215, compraventa=50,853, garaje=7,220, desguace=1,895, concesionario_oficial=1,589, subasta=122; 391,404 single-source (verified). 365 NULL-province.

---

## 2. Files & lines touched

| File | Change |
|---|---|
| `services/api/codes.py:73` | ADD sibling `def cdp_pair(*, province_code, ...same kwargs...) -> tuple[str,str]: key = canonical_key(...); digest = sha256(key); return key, f'CDP-ES-{province_code}-{_base32(digest)}'`. Refactor `cdp_code()` to `return cdp_pair(**kwargs)[1]`. **DO NOT change `cdp_code()`'s signature/return** (zero blast radius). |
| `pipeline/discover.py` (INSERT at ~:67-76, cdp_code at ~:63) | Capture key via `cdp_pair`; ADD `canonical_key` to the INSERT **column list + new $param** ONLY. **Do NOT add it to `ON CONFLICT DO UPDATE`.** |
| `pipeline/ingest.py` (INSERT at ~:56-63, cdp_code at ~:53) | Same: `cdp_pair` + INSERT col only. (`ingest_dealer` keeps `source_key='as24'` and its existing entity_source write — no new source_key, no scheduler/health impact.) |
| `scripts/overture_ingest.py` (`_INSERT_SQL@385`, call @449) | Same; `cdp_pair` returns the bare-host/name key. INSERT col only. |
| `scripts/associations/dedup_upsert.py:200,216`; `upsert_associations.py:141,92`; `upsert_paginas_amarillas.py:91,43`; `geo_sweep_collect.py:138,142`; `seed_pilot.py:39,49` | Same (psycopg2 `%s`). INSERT col only. |
| `pipeline/platform/*_wholesale.py` (35) | Two sub-patterns. (A) per-row helpers (`cdp_code_dealer`/`cdp_code_particular`/etc.) → switch to `cdp_pair`, add `canonical_key` to the INSERT col list. (B) BULK unnest upserts (milanuncios, coches_net, wallapop, …) → add a `canonical_key text[]` unnest column to the INSERT. **Neither adds `canonical_key` to `ON CONFLICT SET`.** The `*_platform_cdp_code()`/`importer_cdp_code()`/`chain_cdp_code()` helpers hand-roll `domain:<host>` keys (e.g. oem_ford_wholesale.py:191) — refactor each to also emit its literal key string (it already builds `key=f'domain:{...}'`). |
| `tests/test_geo_upsert_backfill.py` | EXTEND: assert `canonical_key` persisted on a NEW insert and equals the documented pre-image for one particular, one domain dealer, one name+muni dealer; ADD the **golden test** that `cdp_code(**kw)` output is byte-identical before/after the `cdp_pair()` refactor for a fixed kwarg matrix. |
| `migrations/0039_entity_canonical_key_backfill.sql` | **NEW** self-verifying backfill (§Data-migration). No DDL (column already exists, nullable text). |

---

## 3. Atom-level approach

**EXPOSE THE KEY (codes.py).** `canonical_key()` already returns the raw key. Add `cdp_pair()` calling it once and returning `(key, formatted_code)`; refactor `cdp_code()` to `cdp_pair(**kwargs)[1]`. Guarantees code/key byte-identical to today (no identity drift); all callers wanting only the code work unchanged.

**WRITE AT INSERT (forward).** Every entity INSERT adds a `canonical_key` value (the key from `cdp_pair`, or the literal `domain:<host>` the platform helper builds). **`ON CONFLICT` is left untouched** — so steady-state re-scrapes of existing rows produce ZERO canonical_key dead tuples (the MVCC fix). New rows get the key for free; existing rows are covered by the one-time backfill. For BULK unnest upserts, thread a parallel `canonical_key text[]` array into the INSERT only.

**BACKFILL (0039, single txn) — SELF-VERIFYING RECOMPUTE (the only safe predicate).** For each NULL row, recompute candidate key(s) from STORED inputs, re-hash to a cdp_code, and write `canonical_key` ONLY IF the recomputed code == the row's stored `cdp_code`. A wrong key is impossible to write (the hash is the witness). Driven by an anti-join `WHERE canonical_key IS NULL` (NEVER `NOT IN`). Recompute rules per kind:

- **particular (330,215) — branch on `source_key`:**
  - milanuncios/wallapop: `particular_platform=<plat>`, `particular_seller_id=source_ref`. [VERIFIED MATCH] e.g. `particular:wallapop:9jd72kveonjk`.
  - coches.net: `particular_platform='coches.net'`, `particular_seller_id=province_code` (NOT `source_ref`, which is the literal `particular:NN`). [VERIFIED MATCH] `CDP-ES-50-FPB3W1R6`.
  - Particular keys exclude municipality, so they are stable → ~330k verified-recoverable.
- **compraventa/garaje/desguace/concesionario — best-effort, try ALL variants, keep only re-hash matches:** for each row attempt, in priority order: `domain:<bare_host(website)>`; `name|muni5`; `name|pPROV`; and each of the latter with `|norm(address-suffix)` where the suffix is built from `entity_source.source_ref` (`contract:{ref}` for coches dealers — coches_net_wholesale.py:445; `wallapop_user:{ref}` for wallapop dealers). Accept the FIRST whose `cdp_pair(...)[1] == stored cdp_code`. [VERIFIED] yield is UNKNOWN because `municipality_code`/`trade_name` are mutable and may differ from mint (PORSMISTRAL counterexample → no match on current inputs). Report the actual matched count post-run; do NOT promise a fixed number.
- **Hard-blocked (stay NULL by design):** `province_code IS NULL` (365), subasta (122, NULL prov + key `subasta:{sale_id}`), platform/slug rows whose key embeds a non-stored suffix. They self-heal via the INSERT path on next re-scrape (a re-mint writes the key on a fresh INSERT) — NOT via ON CONFLICT (removed). No data fabricated for them.

---

## 4. Data-migration & backfill (exact SQL)

`migrations/0039_entity_canonical_key_backfill.sql`, **one transaction**, NO `ALTER TABLE` (column exists). The migrate runner is asyncpg/Python.

**PREFERRED implementation — Python recompute invoked by the migration** (self-verifying, reuses the real `services.api.codes` so normalization is byte-identical):
1. `SELECT e.entity_ulid, e.kind, e.province_code, e.municipality_code, e.trade_name, e.legal_name, e.website, e.cif, e.address, es.source_key, es.source_ref FROM entity e LEFT JOIN LATERAL (SELECT source_key, source_ref FROM entity_source WHERE entity_ulid=e.entity_ulid ORDER BY seen_at ASC LIMIT 1) es ON true WHERE e.canonical_key IS NULL AND e.province_code IS NOT NULL;` (anti-join on NULL; NULL-province excluded; first source by earliest `seen_at`).
2. For each row: branch on kind/source_key, generate the candidate key variants (§3), call `cdp_pair(...)` for each, and pick the key whose code == `e.cdp_code`.
3. Batch `UPDATE entity SET canonical_key=$key WHERE entity_ulid=$ulid AND canonical_key IS NULL` only for matched rows.

**Exact gate predicate (all implementations):** `recomputed_code = e.cdp_code AND e.canonical_key IS NULL` (anti-join, no `NOT IN`). Idempotent: re-run touches 0 rows (IS NULL guard).

```sql
-- 0039 — self-verifying backfill of entity.canonical_key. No DDL (column exists, nullable text).
-- Writes a recomputed key ONLY when it re-hashes to the row's stored cdp_code; a non-matching
-- recompute leaves canonical_key NULL (never a wrong write). NULL-province + subasta rows are
-- skipped (cdp_code requires province_code). Steady-state INSERTs (not ON CONFLICT) cover new
-- rows going forward, so this is a one-time pass; re-running it updates 0 rows.
-- (Driven by the Python recompute step that reuses services.api.codes.cdp_pair.)
-- Rollback:
-- UPDATE entity SET canonical_key = NULL WHERE canonical_key IS NOT NULL;
```
> The migration body is the Python recompute loop (or an equivalent plpgsql `f_canonical_key(...)` replicating `_normalize` + the priority cascade, then `UPDATE entity e SET canonical_key=k.key FROM (recompute) k WHERE k.entity_ulid=e.entity_ulid AND k.code=e.cdp_code AND e.canonical_key IS NULL`). Python is PREFERRED — getting `_normalize` byte-identical in SQL is error-prone.

**No edge/served-view rewrite:** [VERIFIED reviewer] none of the writes touch `v_canonical_vehicle`, `v_dealer_resolved`, `canonical_dedup`, `resolve_cluster`, or any served view. `canonical_key` is audit-only metadata.

---

## 5. Verification commands & acceptance criteria

1. **Migrate:** `python -m scripts.migrate up` then `python -m scripts.migrate verify` (expect 0 drift).
2. **Coverage:** `SELECT count(*) total, count(canonical_key) filled, count(*)-count(canonical_key) still_null FROM entity;` **ACCEPTANCE:** `filled >= ~330,215` (particulars verified-recoverable) **+ the dealer matches reported post-run** (count is gate-determined, NOT pre-promised); `still_null` includes at minimum the 365 NULL-province + 122 subasta + non-matching dealers.
3. **ZERO-WRONG-KEY proof (the critical gate):** every filled row must re-hash to its own `cdp_code` — a Python checker reusing `codes._base32`/`cdp_pair` asserts `count(filled rows where cdp_pair(reconstructed kwargs)[1] != stored cdp_code) == 0`. (base32 isn't in SQL, so check in Python over the filled set.)
4. **Idempotency:** re-run the backfill → 0 rows updated.
5. **Forward-write E2E:** run one connector against a scratch row (e.g. unit-test `ingest_dealer` / a tiny `discover` adapter) → the NEW row has `canonical_key` set; a SECOND run leaves it unchanged **AND produces no dead tuple from canonical_key** (since ON CONFLICT no longer writes it — verify via `pg_stat_user_tables` n_tup_upd delta or that the column value is untouched).
6. `pytest tests/test_geo_upsert_backfill.py` green, incl. the golden `cdp_code()`-byte-identical test.
7. **Regression:** `git grep -n 'def cdp_code' services/api/codes.py` still shows the same public signature; no scheduler/health/`source_health` code changed; no UNIQUE index on `canonical_key`.

---

## 6. Risks (incl. reviewer's missed risks)

1. **IDENTITY-CORE (codes.py) — HIGHEST.** `cdp_code()` is the identity generator for 391k rows + every future INSERT. The refactor MUST keep output byte-identical (`cdp_pair()[1]` returns exactly today's format). Mitigation: the golden test (fixed kwarg matrix unchanged before/after) + the backfill's re-hash gate independently proves `canonical_key()` pre-images still hash to live codes. If they ever diverged, the backfill writes 0 rows (fails loud), not corrupts identity.
2. **Writing a WRONG canonical_key would silently mislabel identity.** Eliminated by construction: the backfill writes only when the recompute re-hashes to the EXACT stored `cdp_code`. No blind writes.
3. **MUTABLE-INPUT-IN-KEY (reviewer's primary regression miss).** Dealer keys embed `municipality_code` (mutable: B4.4 geo-backfill fills NULL munis; historical rows minted with whatever the resolver returned). A row minted with `muni=NULL` (key `name|pPROV`) then geo-backfilled to a real muni now stores a muni that does NOT reproduce its cdp_code. [VERIFIED] Garatge plus L'Escala / PORSMISTRAL. Effect: dealer backfill coverage is materially lower than any fixed claim and varies with scrape history. Mitigations: (a) the gate keeps it SAFE (non-match → stays NULL); (b) try BOTH muni and pPROV variants + the address-suffix variants per row to maximize gate hits; (c) state coverage as "particulars ~330k verified; dealers best-effort, count post-run".
4. **ON CONFLICT COALESCE dead-tuple churn (reviewer's understated risk) — ELIMINATED.** Original plan added `canonical_key=COALESCE(...)` to ON CONFLICT on the milanuncios/wallapop/coches BULK upserts (the busiest table, every harvest window). **Fix: canonical_key is added ONLY to the INSERT column list, never to ON CONFLICT.** New rows get it; existing rows are covered by the one-time 0039 backfill. Zero steady-state dead tuples from this column — the entire MVCC concern is removed.
5. **source_key/source_ref orphan adjacency (reviewer's miss):** the particular recompute MUST branch on `source_key` (ml/wp → `source_ref` as seller_id; coches → `province_code` as seller_id, token `coches.net`). [VERIFIED] coches `source_ref` is the literal `particular:NN` — using it as seller_id yields all-misses. Spelled out atom-level in §3.
6. **Wide edit surface (35 connectors + bulk paths):** a missed INSERT column leaves that connector's NEW rows NULL-until-rescrape (degraded, not broken). Mitigation: `git grep -n 'INSERT INTO entity'` asserts every file got a `canonical_key` column; the coverage query catches stragglers; the gate guarantees no wrong key anywhere.
7. **Multi-source ordering:** [VERIFIED] 391,404/391,944 entities have exactly 1 `entity_source`, so the "first by earliest `seen_at`" pick is unambiguous for ~99.9%; the ~540 multi-source rows are still re-hash-gated, so a wrong pick simply doesn't match and stays NULL.
8. **NON-UNIQUE by design (reviewer's miss):** canonical_key MUST stay non-unique (cross-province split). NO UNIQUE index may be added; [VERIFIED] none exists today. Documented so a future maintainer doesn't add one and break multi-province INSERTs.
9. **No served-identity / scheduler / AS24 regression (reviewer CONFIRMED):** edits are INSERT col-lists only; no served view, `resolve_cluster`, `source_health`, or scheduler code touched; no new `source_key`. Correct, not a gap.

---

## 7. Rollback

- **Backfill:** `UPDATE entity SET canonical_key = NULL WHERE canonical_key IS NOT NULL;` (the migration's documented rollback; fully reversible — the column returns to 100% NULL).
- **Code (codes.py):** git-revert the `cdp_pair()` introduction; `cdp_code()` returns to its self-contained form (the golden test guarantees no output drift either way).
- **Connectors:** git-revert the INSERT-column additions; new rows go back to NULL-canonical_key (the prior state). No ON CONFLICT was changed, so there is nothing to undo there.

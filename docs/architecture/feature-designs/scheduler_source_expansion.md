# Feature Design — Schedule the unscheduled harvesters (coches.net segments + AS24)

**Review verdict:** NEEDS-REVISION → **revisions folded in below; SHIP** with the silence-watchdog sentinel fix.
**Effort:** S
**Files:** `pipeline/platform/coches_net_segments.py`, `pipeline/ops/scheduler.py`, `migrations/0039_schedule_segments_as24.sql` (NEW), `tests/test_scheduler_due.py`, `docs/recon/AUDIT_2026-06-15_PHASE2.md`, `PROGRESO.md`/`docs/SUPERPLAN.md`.

---

## 1. Summary & findings closed

Closes two CRITICAL findings (`AUDIT_2026-06-15_PHASE2.md`): **C-cochesnet-segments-unscheduled-no-cadence** and **C-as24-unscheduled-proof-only**. Today ~10.5k dealer-owned coches.net new/km0/renting listings and the AS24 platform surface never refresh in cadence: the segments connector writes health under the SHARED `COCHES_SOURCE_KEY` (can't get an independent schedule without colliding), and AS24 has NO `source_health` row + its per-dealer drain never calls `record_run`.

The scheduler's `_due_sources` reads ONLY `source_health`, and `heartbeat_tick` skips any due key not in `REGISTRY`, so a source needs BOTH a seeded `source_health` row AND a `REGISTRY` entry under the SAME key.

- **SEGMENTS:** give `coches_net_segments` its own `source_key='coches_net_segments'` (connector writes `record_run`/`is_open` under the new key, not the shared one), seed its row via migration 0039, add it to `REGISTRY`.
- **AS24:** schedule the governor-paced, `record_run`-writing `autoscout24_wholesale` (key `as24_wholesale`) at a ban-safe **168h** cadence — NOT the literal `as24` per-dealer driver (which never writes `record_run` → would become a perpetual-DUE 15-min hammer = the exact AS24 ban scar). The full per-dealer drain (`scripts/scale_as24.py`, `scripts/as24_harvest_batch.py`) stays operator-controlled.

### What the review corrected (folded in, not appended)
- **MANDATORY — silence_watchdog false alert on NULL/NULL seed.** [VERIFIED] `find_silent_sources` (silence_watchdog.py:80-81) computes `now() - COALESCE(last_ok, last_fail, '1970-01-01') > 2*harvest_interval_hours*interval`. With both timestamps NULL this collapses to `now()-epoch`, which ALWAYS exceeds the threshold → the hourly `silence_watchdog_job` fires `coches_net_segments:silence` and `as24_wholesale:silence` the first time it runs after the migration. Worse: a successful run does NOT clear it — [VERIFIED] `record_run` success resolves alerts for origin `<key>:scrape` (health.py:162, phase defaults to `'scrape'`), NOT `<key>:silence`. **Fix:** seed `last_fail` to a sentinel in the past beyond the interval but NOT beyond the 2× silence threshold (so the row is immediately DUE but NOT silent). See §Data-migration. ([VERIFIED] 0 of the existing live `source_health` rows have NULL/NULL timestamps, so this is a genuinely new state.)
- **MANDATORY — delete the stale `as24_wholesale` comment.** [VERIFIED] scheduler.py:261-262 states `as24_wholesale ... is NOT in source_health ... handled outside the scheduler via its own governor`. Once 0039 seeds the row and the REGISTRY entry lands, this comment is a live lie. Added to files_touched.
- **Edge count corrected:** live `platform_listing` for the coches.net platform entity is **new=6151** (NOT 8380), km0=3107, renting=1212 (total 10,470). The 8380 figure was internally inconsistent in the audit.
- **Cadence-self-maintenance asymmetry documented:** segments adds `is_tier1=False, harvest_interval_hours=24` to its `record_run` call → code-asserts its cadence. AS24's `autoscout24_wholesale.py:462` calls `record_run` WITHOUT those kwargs → via `COALESCE($3, source_health.harvest_interval_hours)` it PRESERVES the seeded 168 but never ASSERTS it. So AS24's 168h lives ONLY in the 0039 seed row. State this so a future cadence change is made in the right place.

---

## 2. Files & lines touched

| File:lines | Change |
|---|---|
| `coches_net_segments.py:~53` | ADD `COCHES_SEGMENTS_SOURCE_KEY = 'coches_net_segments'` (keep importing `COCHES_SOURCE_KEY` for parse/cage + owner attribution; stop using it as the HEALTH key). |
| `coches_net_segments.py:~384` | `is_open(conn, COCHES_SOURCE_KEY)` → `is_open(conn, COCHES_SEGMENTS_SOURCE_KEY)` (independent breaker). |
| `coches_net_segments.py:~447` (one logical `record_run(...)` stmt starting at :447) | `record_run(conn, COCHES_SOURCE_KEY, ...)` → `record_run(conn, COCHES_SEGMENTS_SOURCE_KEY, ..., is_tier1=False, harvest_interval_hours=24)` (COALESCE self-asserts cadence). |
| `coches_net_segments.py:~201` | **DO NOT CHANGE** — `_BULK_UPSERT_OWNERS` passes `COCHES_SOURCE_KEY` for entity_source ATTRIBUTION (platform identity), not health. Must stay. |
| `coches_net_segments.py:~420-425` (per-segment verdict) | No change — `subject_key=platform_segment_slice:CDP:name`, independent of source_key. |
| `scheduler.py` Tier-1 block (after the `coches_net_wholesale` facet entry) | ADD `SourceEntry('coches_net_segments', 'pipeline.platform.coches_net_segments', [])` (`extra_args=[]` runs all 3 segments full). |
| `scheduler.py` Tier-1 block (near giants, with comment) | ADD `SourceEntry('as24_wholesale', 'pipeline.platform.autoscout24_wholesale', [])` (`is_tier1=FALSE` per 00-TIER1-REGISTRY, but an open giant; `extra_args=[]` → DEFAULT_MAX_PAGES=12). |
| `scheduler.py:261-262` | **DELETE/REWRITE** the stale comment (`as24_wholesale ... NOT in source_health ... handled outside the scheduler`) — now false. |
| `migrations/0039_schedule_segments_as24.sql` | **NEW** seed (§Data-migration), with the sentinel-`last_fail` watchdog fix. |
| `tests/test_scheduler_due.py:~167-178` | ADD `test_segments_and_as24_mapped` asserting both keys in `REGISTRY`. (The live `test_registry_covers_live_source_health` passes once row+entry exist; the comment "All 47 rows" at :307 → 49, comment-only.) |

---

## 3. Atom-level approach

### PART A — coches.net segments (own key + seed + register)
Root cause [VERIFIED coches_net_segments.py:53,384,447]: the connector writes `record_run`+`is_open` under `COCHES_SOURCE_KEY='coches_net_wholesale'`. Sharing the key means `_due_sources` sees ONE row for both the used drain and segments, and a segment failure would trip the used-catalog breaker. To schedule segments independently it MUST own a key.

- **A1.** Add `COCHES_SEGMENTS_SOURCE_KEY = 'coches_net_segments'`. Keep `from ...coches_net_wholesale import (... COCHES_SOURCE_KEY ...)` — `COCHES_SOURCE_KEY` is still used for the OWNER/source bulk upserts (entity_source attribution to the coches.net platform identity, `_BULK_UPSERT_OWNERS` at ~:201; that is NOT health and must NOT change). Only the HEALTH/breaker calls move.
- **A2.** `:384` → `is_open(conn, COCHES_SEGMENTS_SOURCE_KEY)`.
- **A3.** `:447` → `record_run(conn, COCHES_SEGMENTS_SOURCE_KEY, ok=run_ok, rows=total_caged, error=fetch_error, http_status=last_http, is_tier1=False, harvest_interval_hours=24)`. COALESCE in health.py asserts cadence every run without reverting a tuned row. 24h chosen: segments are small (~10.5k) on the SAME unwalled JSON gateway the used drain hits daily; ~106 pages (10.5k/100) of trivial load.
- **A4.** `scheduler.py`: add (Tier-1 block, with comment) `SourceEntry('coches_net_segments', 'pipeline.platform.coches_net_segments', [])`.

[VERIFIED reviewer — no health regression]: facet writes its own row under `COCHES_SOURCE_KEY` at :440-441; segments will write under `coches_net_segments`; no shared-row clobber. Verdict subject_keys disjoint (`platform_segment_slice:CDP:name` vs `platform_facet:CDP`).

### PART B — AS24 (schedule the health-writing wholesale, ban-safe)
Root cause [VERIFIED]: two AS24 keys. `as24_wholesale` (autoscout24_wholesale.py:61) calls `record_run` (:462) + `is_open` (:322) and is governor-paced (host `www.autoscout24.es` @ 0.5 rps). The literal `as24` (ingest_dealer default, scale_as24.py:47, as24_harvest_batch.py:43) never calls `record_run`.

- **B1.** Add (near giants, comment noting `is_tier1=FALSE` but open-giant) `SourceEntry('as24_wholesale', 'pipeline.platform.autoscout24_wholesale', [])`. `extra_args=[]` → `DEFAULT_MAX_PAGES=12`. Refreshes the platform edge surface on cadence with breaker-aware skip + auto-repair, closing the "zero cadence / zero auto-repair" half.
- **B2.** Cadence = **168h**. AS24 is ban-sensitive [scar]: 168h × 12 pages × 0.5 rps with min_spacing 2s ≈ 24s of fetch once a week — maximally conservative. **Do NOT set 24h.** NOTE: this 168h is **migration-seed-only** (the connector does not pass `harvest_interval_hours`); a future cadence change must edit the seed row (or add the kwarg to the connector's `record_run`).
- **B3.** Do **NOT** schedule the literal `as24` key. Its driver never writes `last_ok`, so `now()-COALESCE(last_ok,last_fail,epoch)` stays huge → DUE every 15-min tick → AS24 hammered to ban (the autocasion-orphan failure mode INVERTED: orphan = never runs; this = never stops). Document in the audit closure.

[VERIFIED reviewer]: this DEVIATES (correctly) from the audit's own proposed fix, which named the literal `as24` key. Scope boundary: `as24_wholesale` is a 12-page (~240-car) proof slice, not full coverage of the ~278k declared — this closes cadence/auto-repair, NOT full coverage. The 268 existing AS24 edges persist (keyed by `vehicle_ulid+platform_entity_ulid`, not source_key) — no edge rewrite.

### PART C — the stale comment (mandatory)
Delete/rewrite scheduler.py:261-262. New text e.g.: `# as24_wholesale is seeded in source_health (0039) and mapped in REGISTRY; it is the AS24 record_run writer (the literal 'as24' per-dealer driver stays operator-run and is intentionally NOT scheduled).`

---

## 4. Data-migration & backfill (exact SQL — with the watchdog sentinel fix)

`migrations/0039_schedule_segments_as24.sql` (idempotent seed; THIS is the backfill). Seed `last_fail` to a sentinel so each row is **immediately DUE** (`> harvest_interval_hours` old) but **NOT silent** (`< 2× harvest_interval_hours` old), neutralizing the `silence_watchdog` false alert:

```sql
-- 0039 — seed source_health so the durable scheduler can SELECT the two newly-registered
-- sources on their FIRST tick. _due_sources reads source_health; a key with no row is
-- invisible to the scheduler until record_run UPSERTs it — but the scheduler can't launch
-- it the first time without a row (the autocasion-orphan lesson).
--
-- last_fail is seeded to a past sentinel that is OLDER than harvest_interval_hours (so the
-- row is immediately DUE) but NEWER than 2*harvest_interval_hours (so silence_watchdog,
-- which uses now()-COALESCE(last_ok,last_fail,epoch) > 2*interval, does NOT flag it).
-- status='unknown' + consecutive_fails=0 keep the breaker CLOSED so _due_sources won't skip.
-- ON CONFLICT DO NOTHING: idempotent, never reverts a live cadence row.
INSERT INTO source_health (source_key, is_tier1, harvest_interval_hours, status,
                           consecutive_fails, last_ok, last_fail)
VALUES ('coches_net_segments', FALSE, 24, 'unknown', 0, NULL, now() - interval '25 hours')
ON CONFLICT (source_key) DO NOTHING;

INSERT INTO source_health (source_key, is_tier1, harvest_interval_hours, status,
                           consecutive_fails, last_ok, last_fail)
VALUES ('as24_wholesale', FALSE, 168, 'unknown', 0, NULL, now() - interval '169 hours')
ON CONFLICT (source_key) DO NOTHING;

-- Rollback:
-- DELETE FROM source_health
--  WHERE source_key IN ('coches_net_segments','as24_wholesale')
--    AND last_ok IS NULL AND status='unknown' AND consecutive_fails=0;
```

Apply: `python -m scripts.migrate up` then `python -m scripts.migrate verify`. Ledger row auto-written into `schema_migrations`.

**On first successful harvest:** `record_run` sets `last_ok=now()`, flips status to `healthy`, and the 24h/168h cadence takes over. The sentinel `last_fail` is harmless thereafter.

**No backfill of historical edges:** the ~10.5k segment listings already exist (new=6151, km0=3107, renting=1212) and the 268 AS24 edges persist; this migration only creates the cadence rows.

---

## 5. Verification commands & acceptance criteria

```
python -m scripts.migrate up \
 && python -m scripts.migrate verify \
 && python -m pipeline.ops.scheduler --dry-run \
 && python -m pytest tests/test_scheduler_due.py -q
```
Plus the **extra watchdog check** (reviewer-mandated): after applying 0039, run the silence check (`python -m pipeline.ops.silence_watchdog --check-silence` or equivalent) and confirm `coches_net_segments` and `as24_wholesale` are **NOT** listed as silent.

**ACCEPT when:** 0039 applied + 0 drift; `--dry-run` shows `UNMAPPED=0` and both `coches_net_segments` and `as24_wholesale` as `[WOULD RUN]` with correct module cmds; all scheduler tests pass incl. the live `registry-covers-source_health` returning `Unmapped=[]`; the two new keys are NOT silent. Then one live governed run each (`coches_net_segments --segment renting`; `autoscout24_wholesale`) writes a `harvest_run` + flips `source_health` to `healthy` under the NEW keys with `last_ok` set, while `coches_net_wholesale`'s row is unchanged (no used-catalog regression).

---

## 6. Risks (incl. reviewer's missed risks)

1. **REGRESSION (MEDIUM) — silence_watchdog false WARNING on the seed** (reviewer's primary miss). Bounded (both `is_tier1=FALSE` → WARNING not CRITICAL; on a RUNNING scheduler the 15-min heartbeat sets `last_ok` before the 1-hour watchdog fires) but real, and `:silence` alerts are NOT auto-resolved by a successful `:scrape` run. **NEUTRALIZED** by the sentinel-`last_fail` seed (§4): DUE-but-not-silent. The plan originally called NULL/NULL "honest" without this; fixed.
2. **Entity attribution must stay on `COCHES_SOURCE_KEY`** (the `_BULK_UPSERT_OWNERS` call at :201) — move ONLY health/breaker calls. [VERIFIED reviewer] correct and load-bearing.
3. **Schedule `as24_wholesale` NOT `as24`** to avoid the perpetual-DUE 15-min ban hammer. [VERIFIED] the literal `as24` driver never writes `record_run`.
4. **Seed-then-register coupling (orphan guard):** the live `test_registry_covers_live_source_health` FAILS if a seed lands without its REGISTRY entry — forcing both to ship together.
5. **Single-producer advisory lock** (scheduler.py:613-624) means no double-governor on AS24.
6. **AS24 12-page slice closes cadence/auto-repair but is NOT full coverage** — documented scope boundary.
7. **AS24 168h is migration-seed-only** (connector doesn't assert it) — a future cadence change must edit the seed row, unlike segments (code-asserted). Documented.
8. **Stale comment becomes a live lie** (scheduler.py:261-262) — deleted in this change (PART C).
9. **Scheduler never deployed (pre-existing, F-scheduler-never-deployed):** `apscheduler_jobs` absent in prod; the seeded rows + REGISTRY entries are inert until the scheduler runs as a service. The watchdog false-alert (mitigated by #1) would otherwise surface at first real deploy.

---

## 7. Rollback

- **Seed:** `DELETE FROM source_health WHERE source_key IN ('coches_net_segments','as24_wholesale') AND last_ok IS NULL AND status='unknown' AND consecutive_fails=0;` (only removes never-harvested seed rows; a row that has since run keeps `last_ok` and is preserved).
- **REGISTRY:** remove the two `SourceEntry` lines (the keys become unscheduled again; the seed-removal above must also run, else `test_registry_covers_live_source_health` fails).
- **Connector:** revert the 3 `coches_net_segments.py` health/breaker edits to `COCHES_SOURCE_KEY` (segments goes back to sharing the used-catalog key — the prior degraded-but-stable state).
- **Comment:** restore the prior scheduler.py:261-262 text if reverting the AS24 scheduling.

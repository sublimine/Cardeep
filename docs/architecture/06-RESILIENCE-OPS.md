# CARDEEP — 06 · Resilience & Operations

> Pillar document. The control system that makes the mandate's hardest promise true:
> **"if one source fails, an alert fires with the EXACT origin, it self-repairs, and
> Cardeep never falls."** This is the watchdog, the exact-origin alerting, recipe-drift
> detection, the auto-repair loops, the circuit breakers, the ban/throttle response, the
> observability surface, and graceful degradation — designed so the live API keeps
> serving the last trustworthy snapshot while individual sources break, heal, and
> recover underneath it, with no human in the inner loop.
>
> **Supersedes** the one-line `S-HEALTH` row in `docs/ORQUESTACION.md §Sistemas` ("F7,
> tabla lista") and the bare retry/backoff in `pipeline/sources/autoscout24.py:61-81`.
> It is the operational layer *on top of* the fetch engine of
> `docs/architecture/02-SCRAPING-ENGINE.md`: that doc decides *how to fetch one source*;
> this doc decides *what the fleet does when a fetch goes wrong, repeatedly, at scale,
> across 181 sources, without falling over.*
>
> Anchor reality (read & verified before designing this doc):
> `migrations/0004_verification_health.sql` (the live `source_health` / `alert` /
> `verification_verdict` DDL — every column referenced here is `[VERIFIED]` against it),
> `pipeline/ingest.py` (delta engine + VAM call site), `pipeline/verify.py` (quorum
> judge), `pipeline/sources/autoscout24.py:61-81` (current retry/backoff), `scripts/scale_as24.py`
> (the loop that already met throttling), `PROGRESO.md` (the 138-dealer throttle
> incident), `docs/ARCHITECTURE.md` (data layer), `docs/architecture/02-SCRAPING-ENGINE.md`
> (tier engine), `docs/architecture/00-TIER1-REGISTRY.md` (the source universe).
>
> Marking discipline: every claim is **[VERIFIED]** (read from repo/DB/live this session)
> or **[ASSUMED]** (inferred design choice, to be confirmed in implementation). No
> placeholders, no stubs.

---

## 0. The incident this pillar exists to never repeat

The system has **already fallen once**, and the failure is documented honestly:

> *"138 dealers cayeron por throttling de AS24 bajo carga 4×. La cosecha es el cuello
> (rate-limit de fuente), no el sistema."* `[VERIFIED, PROGRESO.md 2026-06-12]`

Anatomy of that failure, read from the code that produced it:

1. **No global concurrency governor.** The scale run launched 4 parallel harvest workers
   (`as24_harvest_batch` ×4) against one host, AutoScout24. `scale_as24.py` itself paces
   a *single* loop at `time.sleep(0.5)` per dealer (`scale_as24.py:45,61`) and
   `fetch_page` at `time.sleep(0.8)` per page (`autoscout24.py:274`) `[VERIFIED]` — but
   **nothing coordinates the four workers**, so the effective request rate against AS24
   was 4× what any single worker believed it was emitting. The per-worker politeness was
   real and the aggregate was a hammer. The pacing must be **per-host across the whole
   fleet**, not per-process.

2. **Retry without a circuit breaker.** `fetch_page` retries `429/500/502/503/504` with
   linear backoff `2*(attempt+1)` for 3 attempts, then raises (`autoscout24.py:67-81`)
   `[VERIFIED]`. This is correct for a *transient* blip (it recovered the HTTP 504 case,
   `PROGRESO.md`) but **catastrophic under sustained throttling**: 138 dealers each burned
   3 doomed retries into an already-saturated host, *deepening* the ban instead of backing
   off the whole source. There is no state that says "AS24 is throttling us right now,
   stop sending."

3. **The failure was invisible until the post-mortem.** The loss surfaced as
   `totals["errors"] += 1` printed to stdout (`scale_as24.py:58-60`) `[VERIFIED]`.
   Nothing wrote a `source_health` row, nothing raised an `alert`, nothing knew *which*
   138 dealers to retry. The recovery was manual ("Recuperación pendiente con menor
   concurrencia" `[VERIFIED]`). The mandate's promise — *alert with exact origin, then
   self-repair* — was unmet because the machinery did not exist. The tables exist
   (`migrations/0004`) but **nothing writes to them yet.** This doc is the wiring.

The redesign turns every line of that anatomy into a mechanism: a fleet-wide per-host
concurrency governor (§7.1), a circuit breaker that trips a source *before* it burns
retries (§5), exact-origin alerting on the real `alert` table (§3), a per-source health
watchdog on the real `source_health` table (§2), and an auto-repair ladder that requeues
exactly the lost work (§6). The live API never noticed the 138-dealer loss because it
serves the DB, not the harvester — that decoupling is the foundation of "never falls"
(§9), and we make it a designed invariant rather than an accident.

---

## 1. Doctrine (the seven laws of resilience, in priority order)

Govern every operational decision. When they conflict, lower number wins.

1. **THE API NEVER FALLS; THE HARVESTER MAY.** The live API serves the last trustworthy
   snapshot from PostgreSQL. A source breaking, a recipe drifting, a ban, an entire tier
   going dark — none of these may take the API down or corrupt served data. Harvest
   failures degrade *freshness*, never *availability* or *integrity* (§9). This is law #1
   because it is the literal mandate: "Cardeep never falls."

2. **EXACT ORIGIN, ALWAYS.** Every failure is attributed to a precise, machine-readable
   origin tuple `(source_key, entity_cdp_code?, phase, tier?, defense?)` before any
   response is chosen. "Something failed" is a bug in this system; "`as24` failed at
   phase `scrape`, tier 0, defense `none`, on dealer `CDP-ES-08-…`, http 429" is the
   contract. The `alert.origin` column is `NOT NULL` for exactly this reason
   `[VERIFIED, migrations/0004:36]`.

3. **SELF-REPAIR BEFORE ESCALATION TO A HUMAN.** Every typed failure has a typed
   automatic response that the system attempts *first* (re-fingerprint, escalate tier,
   re-derive recipe, backoff+rotate, quarantine+requeue). A human is paged only when the
   auto-repair ladder is exhausted or the repair requires a decision the system is
   forbidden to make alone (spend authorization, irreversible action). The mandate:
   "it self-repairs."

4. **FAIL CLOSED ON INTEGRITY, FAIL OPEN ON FRESHNESS.** A source we cannot verify does
   **not** overwrite good data with bad — it is quarantined and the old snapshot stands
   (fail closed: integrity is sacred). A source that is merely *slow* or *temporarily
   down* keeps serving its last good data, stale-flagged (fail open: availability over
   freshness). Never the reverse. This is the operational form of the VAM: nothing
   becomes TRUSTWORTHY without quorum, and non-trustworthy never lands
   (`pipeline/verify.py` already enforces "silent data loss never reads as TRUSTWORTHY"
   `[VERIFIED]`).

5. **A FAILING SOURCE MUST NOT HARM A HEALTHY ONE.** Isolation is mandatory. One source
   throttling must not starve the worker pool, exhaust the DB connection pool, or block
   the loop for every other source (the 138-dealer incident was partly a *coordination*
   failure across workers, §0). Bulkheads per source/host; one circuit trips one source,
   not the fleet (§5, §8).

6. **EVERY REPAIR IS EVIDENCE, AND EVIDENCE IS PERSISTED.** Health transitions, alerts,
   breaker trips, drift detections, repair attempts and their outcomes are written to
   durable tables (`source_health`, `alert`, and the two new tables of §10), never only
   to stdout (the incident's blind spot, §0.3). The operational history is queryable,
   auditable, and survives a restart — the system can recover its own state after a crash
   because the state lives in PostgreSQL, not in a process's memory.

7. **CHEAPEST CORRECT RESPONSE.** Mirrors the cost doctrine
   (`ORQUESTACION.md` `[VERIFIED]`): the watchdog, breakers, backoff, and drift detection
   are *deterministic and local* (free, run every cycle). Expensive intelligence (an
   agent re-hunting a Tier-1 recipe) is invoked only when the cheap ladder is exhausted
   and only behind its gate. Resilience is mostly arithmetic, not LLM calls.

---

## 2. The per-source health watchdog (`source_health`, mechanized)

The watchdog is the heartbeat monitor for all 181 sources. It owns the real table:

```sql
source_health (
    source_key        TEXT PRIMARY KEY,
    last_ok           TIMESTAMPTZ,
    last_fail         TIMESTAMPTZ,
    consecutive_fails INT NOT NULL DEFAULT 0,
    status            TEXT NOT NULL DEFAULT 'unknown'
        CHECK (status IN ('healthy','degraded','down','unknown'))
)   -- [VERIFIED, migrations/0004:24-31]
```

### 2.1 What counts as an OK and what counts as a FAIL

The watchdog is fed **one outcome per (source_key, cycle)** by every phase that touches a
source. The outcome is not a raw HTTP code — it is a **classified result** so that an
expected-empty (a dealer genuinely listing 0 cars) is never mistaken for a failure (the
incident's lesson that error-vs-empty must be distinguished; `scale_as24.py` already
separates `empty` from `errors` `[VERIFIED, scale_as24.py:42-50]`):

| Classified outcome | Counts as | Rationale |
|---|---|---|
| `OK` (records extracted, VAM TRUSTWORTHY) | success | the only true green |
| `OK_EMPTY` (reachable, validly 0 records) | success (neutral) | source genuinely empty; not a fault |
| `SOFT_FAIL` (transient: 5xx, timeout, conn-reset, single 429) | fail (transient) | retryable; feeds backoff not breaker-trip alone |
| `HARD_FAIL` (403/blocked, challenge wall, auth/credential) | fail (hard) | defense escalation; routes to §6 repair |
| `DRIFT_FAIL` (reached + extracted but null-rate/count drift) | fail (integrity) | recipe drift, §4 — *the silent killer* |
| `VERIFY_FAIL` (VAM REFUTED) | fail (integrity) | quorum broke; fail-closed, §4.4 |

### 2.2 State machine (consecutive-fail tracking → status)

`consecutive_fails` is the column the schema already gives us `[VERIFIED]`; the watchdog
drives `status` off it with hysteresis (different up/down thresholds, so a source does not
flap between `healthy`/`degraded` on a single blip):

```
            OK / OK_EMPTY                          OK (×N_RECOVER consecutive)
   ┌──────────────────────────────┐        ┌───────────────────────────────────┐
   ▼                              │         │                                   │
┌─────────┐  fail (any)   ┌──────────┐  fail (≥ DEGRADE_AT)  ┌──────┐  fail (≥ DOWN_AT)  ┌──────┐
│ healthy │──────────────▶│ degraded │─────────────────────▶│ down │──────────────────▶│ down │
└─────────┘   resets to   └──────────┘                       └──────┘  (stays; breaker  └──────┘
   ▲          degraded on        │  OK resets consecutive_fails=0          open, §5)
   │          first fail         │  → back toward healthy after N_RECOVER
   └─────────────────────────────┘
```

- **Thresholds (per-source-tunable, defaults `[ASSUMED]`, calibrated from the incident):**
  `DEGRADE_AT = 1` (first fail → degraded, eager — we want early visibility),
  `DOWN_AT = 3` (matches the existing 3-retry budget of `fetch_page` `[VERIFIED]`: when
  even the in-fetch retries are exhausted 3 cycles running, the source is genuinely down,
  not blipping), `N_RECOVER = 2` (two clean cycles to climb out of `down` — prevents
  declaring victory on one lucky request, the §1.4 "never declare victory on one request"
  rule mirrored from `verify.py`'s primary-agrees guard).
- **Tier-1 sources carry stricter thresholds** (`DEGRADE_AT=1, DOWN_AT=2`) and **separate
  status namespacing** — a Tier-1 source going down is a higher-severity event and must
  not be averaged into long-tail health (the `_tier1` separation of
  `ARCHITECTURE.md §Separación Tier-1` `[VERIFIED]` extends to operations: Tier-1 health
  is reported, alerted, and dashboarded on its own track).
- **`unknown`** is the cold-start status (the schema default `[VERIFIED]`): a source never
  yet run. The watchdog's first outcome moves it to `healthy` or `degraded`.

### 2.3 The update contract (idempotent, single writer)

The watchdog is updated through one function, the *only* writer of `source_health`, called
by every phase at its boundary. This mirrors the anti-collision contract
(`ORQUESTACION.md §Contrato anti-colisión` — "la ingesta la centraliza el main-loop"
`[VERIFIED]`): health writes are centralized so parallel harvest workers never race the
status column.

```python
async def record_outcome(conn, source_key, outcome: Outcome, *, tier1=False) -> Status:
    """The single writer of source_health. Idempotent per (source_key, cycle).
    Returns the new status so the caller can react (e.g. skip if 'down')."""
    deg_at, down_at, recover = thresholds_for(source_key, tier1)
    async with conn.transaction():                       # serialize per source_key
        row = await conn.fetchrow(
            "SELECT consecutive_fails, status FROM source_health WHERE source_key=$1 "
            "FOR UPDATE", source_key)                     # row lock = no race (law #5)
        if outcome.is_success:
            new_fails, new_status = 0, _climb(row, recover)   # OK / OK_EMPTY
            await conn.execute(
                "INSERT INTO source_health (source_key,last_ok,consecutive_fails,status) "
                "VALUES ($1,now(),0,$2) ON CONFLICT (source_key) DO UPDATE SET "
                "last_ok=now(), consecutive_fails=0, status=$2", source_key, new_status)
        else:
            new_fails = (row["consecutive_fails"] if row else 0) + 1
            new_status = "down" if new_fails >= down_at else "degraded"
            await conn.execute(
                "INSERT INTO source_health (source_key,last_fail,consecutive_fails,status) "
                "VALUES ($1,now(),$2,$3) ON CONFLICT (source_key) DO UPDATE SET "
                "last_fail=now(), consecutive_fails=$2, status=$3",
                source_key, new_fails, new_status)
        return new_status
```

- **`FOR UPDATE` row lock** is the law-#5 isolation primitive: concurrent workers for the
  same source serialize on the row, so `consecutive_fails` is never lost-update-corrupted.
  Different sources lock different rows → full parallelism preserved.
- **A status *transition* (not every fail) is what triggers an alert and a repair** (§3,
  §6) — `record_outcome` returns the new status and the caller diffs it against the prior
  to fire side-effects exactly once on the edge, never on every cycle (avoids alert storms).

---

## 3. Exact-origin alerting (`alert`, mechanized)

The mandate verb is *"salta una alerta con el origen exacto."* The `alert` table is built
for it; `origin` is `NOT NULL` `[VERIFIED, migrations/0004:34-43]`. We make "exact" a
**structured, non-negotiable contract**, not a prose string.

### 3.1 The origin contract

`alert.origin` is a **canonical, parseable key**, and the full structured origin lives in
`alert.payload` (JSONB, already in the schema `[VERIFIED]`). One canonical form:

```
origin  = "<source_key>:<phase>[:<entity_cdp_code>]"
            e.g.  "as24:scrape:CDP-ES-08-7F3KQ2"   (a specific dealer harvest failed)
                  "coches_net:recipe"               (the Adevinta recipe drifted)
                  "spoticar:fetch"                  (the Akamai wall blocked the whole source)

payload = {
  "source_key":   "as24",
  "phase":        "scrape",            # discover|scrape|recipe|ingest|verify|fetch|geocode
  "tier":         0,                   # fetch tier reached (02-SCRAPING-ENGINE §2)
  "defense":      "none",              # is-antibot label at failure (02 §3)
  "entity":       "CDP-ES-08-7F3KQ2",  # nullable: null = whole-source failure
  "outcome":      "HARD_FAIL",         # the §2.1 classification
  "http_status":  429,                 # when applicable
  "signal":       "rate_limited",      # typed failure cause (§3.3)
  "consecutive_fails": 4,
  "repair_attempted": "backoff_rotate",# what auto-repair tried (§6), null if none yet
  "repair_outcome":   "pending",       # pending|recovered|exhausted|escalated
  "evidence":     "4× concurrent load on host autoscout24.es; …",
  "cycle_id":     "2026-06-12T16:40Z#7"
}
```

The phases are **the real pipeline phases**, verified from code, not invented:
`discover` (`pipeline/discover.py`), `scrape`/`fetch` (`sources/*.py`),
`recipe` (`pipeline/recipe.py`), `ingest` (`pipeline/ingest.py`),
`verify` (`pipeline/verify.py`), `geocode` (`pipeline/geocode.py`) `[VERIFIED, repo tree]`.

### 3.2 Severity mapping (the real `CHECK` constraint)

`alert.severity ∈ {info, warning, critical}` `[VERIFIED, migrations/0004:37-38]`. We map
deterministically so severity is a function of state, never a judgment call:

| Condition | Severity | Why |
|---|---|---|
| Health `healthy → degraded` (first fail) | `info` | expected noise; visible but not paging |
| Health `degraded → down` (long-tail source) | `warning` | a source is out; freshness degrading |
| Health `→ down` (**Tier-1** source) | `critical` | a giant is dark (§2.2 strict track) |
| Circuit breaker **trips** (§5) | `warning` | source quarantined; auto-repair running |
| Recipe **drift** detected (§4) | `critical` | silent-wrong-data risk — the worst failure mode |
| VAM **REFUTED** (§4.4) | `critical` | integrity quorum broke; fail-closed engaged |
| Spend gate hit / Tier-2 needed, unauthorized (§6.4) | `warning` | needs human decision, not a bug |
| Auto-repair ladder **exhausted** | `critical` | self-repair failed; human required |
| Fingerprint self-test fail at engine start (`02 §8`) | `critical` | X25519MLKEM768 missing → block start |

> **Drift and REFUTED are `critical` even though nothing "crashed."** This is law #4
> (integrity ≫ freshness). A source that returns 200 and clean-looking but *wrong* data
> (drift) is more dangerous than one returning 503, because the 503 fails loudly and the
> drift poisons the database silently. The whole §4 exists to make the silent failure
> loud.

### 3.3 Typed failure signals (the vocabulary of "what exactly broke")

`payload.signal` is a closed vocabulary so repair (§6) can switch on it. Each maps a raw
observation to a cause and a default repair:

| `signal` | Detected from | Default auto-repair (§6) |
|---|---|---|
| `rate_limited` | 429, or 200s slowing + rising latency | backoff + lower per-host concurrency (§7) |
| `gateway_transient` | 500/502/503/504 | bounded retry w/ jitter (existing, §6.1) |
| `network_blip` | conn-reset / timeout / DNS | retry; if persistent → degrade |
| `challenge_wall` | is-antibot label flips to CF/DataDome/Akamai/GeeTest | escalate tier (§6.2) |
| `fingerprint_stale` | challenge-rate spike correlated w/ FP (`02 §8`) | rotate/refresh impersonation (§6.2) |
| `recipe_drift` | null-rate / count drift vs golden (§4) | re-derive recipe (§6.3) |
| `schema_change` | data-layer JSON path missing (§4.2) | re-hunt recipe (§6.3) |
| `auth_required` | 401/login wall (B2B auctions, `00 §T1.7–T1.9`) | park: needs credentials (§6.4) |
| `spend_required` | Tier-2 needed, unauthorized (`02 §2 Tier-2`) | park: needs spend gate (§6.4) |
| `geo_gated` | wall trips only outside ES (milanuncios, `00 §T1.2`) | route ES residential exit (§6.2) |
| `quorum_refuted` | VAM REFUTED (`verify.py`) | quarantine snapshot, fail-closed (§4.4) |

### 3.4 Alert lifecycle & dedup (no storms)

- **One open alert per `(origin, signal)`.** A partial unique index keys it; a repeating
  failure **updates** the open alert's `payload` (bumps `consecutive_fails`, appends repair
  attempts) rather than inserting a new row — so 138 dealers throttling is *one* AS24
  rate-limit alert with a growing affected-entity list, not 138 rows (the incident would
  have produced a stdout flood; here it is one actionable alert).
- **Auto-resolution.** When the watchdog records the `→ healthy` transition for a source,
  the alerter sets `resolved_at = now()` on its open alerts for that origin
  (`alert.resolved_at` exists `[VERIFIED, migrations/0004:42]`; the
  `idx_alert_unresolved` partial index `[VERIFIED:45]` makes "what is currently broken" a
  fast query). Self-repair closes its own alert — the loop is observable end to end.
- **Escalation timer.** An alert open longer than `ESCALATE_AFTER` (per-severity:
  `critical=15min`, `warning=2h` `[ASSUMED]`) without resolution flips a `paged` flag in
  payload and emits to the human channel (§8.3). Auto-repair gets first crack; humans get
  what auto-repair could not fix.

---

## 4. Recipe-drift detection (the silent killer)

The most dangerous failure is **not** a source going down — it is a source that **silently
changed** so extraction still "succeeds" (HTTP 200, rows produced) but the rows are now
wrong: a field that went `null` because a JSON path moved, a count that quietly halved
because a facet partition broke, a price that is now the *monthly financing* number
instead of the cash price. The §0 incident was *loud*; drift is *quiet*, and law #4 makes
catching it the highest-integrity job in the system. This section is the operational
counterpart to `02-SCRAPING-ENGINE.md §9.3` (which defined the recipe's `heal:` block);
here we define *the detector and its response*.

### 4.1 The golden sample (the drift baseline)

Every recipe carries a committed `reference_sample`
(`02-SCRAPING-ENGINE.md §9.1 heal.reference_sample` `[VERIFIED]`) — a small, frozen,
hand-or-VAM-blessed extraction (`fixtures/<source>/golden.json`). The golden sample
records, per field, the **expected null-rate**, **expected value distribution shape**
(numeric ranges, enum sets), and the **expected record count band** for a fixed query.
The golden is versioned with the recipe (`recipe_version`, the column already in `entity`
and `vehicle` `[VERIFIED, ARCHITECTURE.md]`) so "what is correct" is pinned to a recipe
version and a date.

### 4.2 The four drift detectors (run every harvest, deterministic, €0)

On every harvest of a source, before ingest commits, the detector compares the fresh
extraction against the golden. Four orthogonal checks — any one tripping = `DRIFT_FAIL`:

1. **Field null-rate drift.** For each `field_map` field, `null_rate_now` vs
   `null_rate_golden`. Exceeding `drift_alert_threshold` (default 0.15, the value already
   specified in the recipe schema `[VERIFIED, 02 §9.1 heal.drift_alert_threshold]`) on a
   `required` field → drift. *This is the canonical "fields go null, auto re-derive recipe"
   of the mandate.* Example: AS24 moves `pageProps.dealerInfoPage` → every dealer name
   nulls → null-rate of `dealer` jumps 0→1.0 → instant drift, not a silent fleet of
   nameless entities.

2. **Schema-path existence.** Each `field_map` JSON path is probed against the live
   data-layer artifact (`__NEXT_DATA__` / API JSON / JSON-LD). A path that *no longer
   resolves on any record* is `schema_change` (a structural break, distinct from a value
   that merely went null). This catches the Adevinta/AS24 class of "they renamed the
   field" before it nulls the column.

3. **Count-band drift.** The harvest's record count vs the golden's expected band, AND vs
   the source's own `declared_count` (AS24 `numberOfResults`, advgo `total`
   `[VERIFIED, autoscout24.py:286]`). A harvest returning 50% of declared is drift even if
   every returned row is perfect — it means pagination/facet-partition silently broke
   (`02 §7`). This reuses the count the VAM already consumes (`ingest.py:116-118`
   `[VERIFIED]`).

4. **Value-distribution drift.** Per numeric field, the new distribution vs golden bounds
   (`02 §9.1 validation.bounds`, e.g. `km: [1, 5000000]` `[VERIFIED]`). A spike of
   out-of-bounds values flags a *unit/format* change — exactly the class of the already-fixed
   `{raw,formatted}` km-doubling bug (`PROGRESO.md F3 causa raíz #2`, `02 §10.3`
   `[VERIFIED]`). The bug that once shipped doubled-km is now a typed drift signal that
   blocks ingest.

### 4.3 Drift response: fail closed, then re-derive

```
detect DRIFT_FAIL  →  (law #4: integrity)  quarantine the harvest (do NOT ingest)
                   →  record_outcome(DRIFT_FAIL)  →  source_health degraded/down
                   →  alert(critical, signal=recipe_drift|schema_change, exact field+observed/expected)
                   →  auto-repair §6.3 (re-derive recipe → version N+1 → VAM on blind sample)
                   →  on success: ingest with new recipe, resolve alert
                   →  on failure: park source, escalate to human (recipe re-hunt, §6.3/§8.3)
```

The **quarantine** is the law-#4 teeth: a drifted harvest is *never* ingested over good
data. The previous trustworthy snapshot keeps serving (stale-flagged, §9) while the recipe
self-heals. Wrong data never reaches the API. This is why drift is survivable: the cost of
drift is *staleness for one source for one repair cycle*, never *corruption*.

### 4.4 VAM REFUTED is a first-class resilience event

`pipeline/verify.py` already returns `REFUTED` when the quorum breaks and **specifically
when ingestion silently lost rows** (`db_ingested` must agree with ≥1 path or REFUTED
`[VERIFIED, verify.py:38-47]`). Today `REFUTED` is only recorded as a verdict; the scale
loop counts it (`scale_as24.py:55`) but takes no action `[VERIFIED]`. The wiring: a
`REFUTED` verdict emits `record_outcome(VERIFY_FAIL)` + a `critical` alert
(`signal=quorum_refuted`) + quarantine. The VAM becomes not just the judge of "done" but
a live tripwire feeding the watchdog — closing the loop between
`migrations/0004`'s two halves (verification and health) that currently sit unconnected.

---

## 5. Circuit breakers (stop burning a source that is already down)

The §0 incident's deepest bug: 138 dealers each burned 3 retries into a host that was
already throttling, *deepening* the ban. A circuit breaker is the missing state that says
"this source is failing — stop sending, let it cool." One breaker **per source_key**
(bulkhead, law #5: a tripped AS24 breaker never touches coches.net).

### 5.1 Three states (classic breaker, source-scoped)

```
   CLOSED  ──(consecutive HARD_FAIL ≥ TRIP_AT, or rate_limited burst)──▶  OPEN
     ▲                                                                      │
     │                                                            (cool-down COOL_FOR)
     │                                                                      ▼
   CLOSED ◀──(probe succeeds: OK)──  HALF_OPEN  ──(probe fails)──▶  OPEN (re-arm, longer cool)
```

- **CLOSED** — normal. Requests flow. Fails increment the counter (shared with
  `source_health.consecutive_fails`, single source of truth, §2).
- **OPEN** — the source is quarantined. **No harvest requests are sent.** The scheduler
  skips this source entirely (`record_outcome` returning `down` is the skip signal, §2.3).
  Cool-down `COOL_FOR` is **exponential per consecutive trip** (`base 60s × 2^trips`,
  capped `[ASSUMED]`) — a source that keeps tripping cools longer, the politeness the
  incident lacked. During OPEN the API still serves that source's last good data (§9).
- **HALF_OPEN** — after cool-down, **exactly one** canary probe is allowed (the cheapest
  possible: one record, Tier-0). Success → CLOSED + alert auto-resolves. Failure → back to
  OPEN with a longer cool-down. This is the "never declare victory on one request" guard
  (`verify.py` primary-agrees rule mirrored): one probe re-opens cautiously; full health
  (`→ healthy`) still needs `N_RECOVER` clean cycles (§2.2).

### 5.2 Trip conditions (typed, not just "N fails")

- **`TRIP_AT` consecutive `HARD_FAIL`** (default 3, aligned to the 3-retry budget
  `[VERIFIED, autoscout24.py:67]`): after the in-fetch retries are exhausted and the
  source still hard-fails, the breaker trips — *the retries no longer compound the ban.*
- **Rate-limit burst**: ≥ `RL_BURST` `rate_limited` signals within a window trips
  immediately, even below `TRIP_AT` — a 429 storm needs no patience, it needs silence
  (the direct fix for the 4×-load throttle).
- **Drift / REFUTED** (§4): an integrity trip opens the breaker for **ingest**, not fetch —
  fetching may continue to gather evidence for re-derivation, but nothing lands until the
  recipe heals (law #4).

### 5.3 The breaker is the scheduler's gate

The harvest scheduler (§7) consults the breaker before dispatching any unit of work:
`if breaker(source).state is OPEN: skip` — so an open breaker *automatically* sheds load
from a dying source and frees the worker pool for healthy sources (law #5 isolation). The
incident's "lower concurrency manually" recovery becomes automatic: the breaker sheds, the
governor (§7.1) re-paces, the source cools, the canary re-probes, work resumes.

---

## 6. The auto-repair ladder (self-healing, mechanized)

"It self-repairs." Every typed `signal` (§3.3) maps to a rung; the system climbs the
ladder automatically, cheapest first (law #7), escalating only on exhaustion. Each rung's
attempt + outcome is written to `repair_attempt` (§10) and reflected in the alert payload
(`repair_attempted`/`repair_outcome`, §3.1) so the repair is observable.

### 6.1 Rung 0 — bounded retry with jitter (transient)

For `gateway_transient` / `network_blip`: the existing retry (`autoscout24.py:67-81`
`[VERIFIED]`) **promoted to the engine level and corrected** — linear `2*(attempt+1)`
becomes **exponential with full jitter** (`base * 2^attempt * random()`), capped, max 3
attempts. Jitter is the fix for the thundering-herd the incident created (4 workers
retrying in lockstep). Recovers the HTTP-504 class the current code already handles
`[VERIFIED, PROGRESO.md]`, without the lockstep.

### 6.2 Rung 1 — re-fingerprint / escalate tier (defense)

For `challenge_wall` / `fingerprint_stale` / `geo_gated`: invoke the §3/§8 mechanisms of
the fetch engine — re-run `is-antibot` classification (`02 §3`), bump the source's floor
tier (Tier-0→1→2, `02 §2`), refresh the impersonation target (`02 §8`, assert
X25519MLKEM768), and for `geo_gated` lease a Spanish residential exit (`02 §5`, milanuncios
case `[VERIFIED, 00 §T1.2]`). On success the router **writes the working tier back into the
recipe** (`02 §9.4 self-tuning tier` `[VERIFIED]`) so the next run starts correct — the
repair is *learned*, not repeated. Tier-2 escalation is **gated** (§6.4).

### 6.3 Rung 2 — re-derive / re-hunt recipe (drift)

For `recipe_drift` / `schema_change` (§4): the self-heal of `02 §9.3`.
- **Long-tail / data-layer:** re-derive deterministically (re-locate JSON paths, regenerate
  the field map by local-LLM mapping against the live artifact — cheap, `ORQUESTACION.md`
  cost doctrine `[VERIFIED]`), bump to `recipe_version N+1`, **VAM on a blind sample**
  (`02 §9.2`), commit to git `main` on pass. HTML-fallback recipes use Scrapling adaptive
  selectors (`02 §9.3` `[VERIFIED]`). All automatic.
- **Tier-1:** re-derivation is *expensive intelligence* → dispatch a `WF-TIER1-HUNT` agent
  (`ORQUESTACION.md` `[VERIFIED]`) to re-hunt the receta or report the exact new wall. This
  is the only rung that routinely spends an LLM; it is reserved for the giants whose value
  justifies it (`00-TIER1-REGISTRY.md`).

### 6.4 Rung 3 — park & escalate (decision required)

For `auth_required` / `spend_required`, or any rung-exhausted state: the source is **parked**
in `state/blocked.json` (long-tail) / `state/tier1-blocked.json` (Tier-1, the file
`02 §2 Tier-2` already names `[VERIFIED]`) with the **exact wall** ("Akamai `_abck`,
sensor_data v3, ES residential required" — the `S-TIER1` "muro exacto que exige gasto"
`[VERIFIED, ORQUESTACION.md]`), a `warning`/`critical` alert is paged, and the source is
**never silently retried**. This is the law-#3 boundary: the system self-repairs up to the
point where a repair requires a human decision (spend money, provision B2B credentials,
accept an irreversible action) — there it stops and asks, exactly as the owner's autonomy
doctrine demands. Parked ≠ forgotten: a parked source is re-evaluated when its gate clears
(spend authorized → un-park → retry the right tier).

### 6.5 The ladder as one decision function

```python
def auto_repair(source, signal, ctx) -> RepairOutcome:
    match signal:
        case "gateway_transient" | "network_blip":   return rung0_retry_jitter(source, ctx)
        case "rate_limited":                          return rung_backoff_and_repace(source, ctx)   # §7.1
        case "challenge_wall" | "fingerprint_stale" | "geo_gated":
                                                      return rung1_refingerprint_escalate(source, ctx)
        case "recipe_drift" | "schema_change":        return rung2_rederive_recipe(source, ctx)
        case "auth_required" | "spend_required":      return rung3_park_escalate(source, signal, ctx)
        case "quorum_refuted":                        return quarantine_failclosed(source, ctx)       # §4.4
    # each rung records repair_attempt(§10) + updates the open alert(§3.4); on exhaustion → rung3
```

---

## 7. The ban / throttle response & concurrency governance

The direct, mechanized fix for the §0 incident. Three coordinated controls.

### 7.1 Fleet-wide per-host concurrency governor (the incident's root fix)

The incident's root cause was **per-process** politeness with **no fleet coordination**
(4 workers × polite-each = rude-aggregate). The fix is a **per-host token bucket shared
across the entire fleet**, not per worker:

- One token bucket **keyed by registrable host** (not source_key — coches.net,
  milanuncios, fotocasa, segundamano share the Adevinta `bon` host family `[VERIFIED,
  00 §1.1.5]`, so they must share *one* budget or they collectively re-create the 4× hammer
  against one infra). The Adevinta family, the AUTO1 family (Autohero/Clicars/
  compramostucoche `[VERIFIED, 00]`), and per-host OEM portals each get a coordinated bucket.
- **Per-host concurrency cap + RPS cap, both tunable per host** (the incident proved
  "concurrency is a tuned per-source knob, not a global max" `[VERIFIED, 02 §6]`). AS24's
  cap is set *below* the level that triggered throttling at 4× load.
- Workers **lease** from the bucket before each request; an empty bucket *blocks the
  worker* (or yields it to another host's work, §7.3), so the aggregate rate is bounded
  **by construction**, regardless of worker count. This makes the 138-dealer loss
  structurally impossible: you cannot exceed the host budget no matter how many workers
  run.

### 7.2 Adaptive backoff & rotation (the `rate_limited` repair)

On `rate_limited` (§3.3) the response is **multi-axis**, escalating:
1. **Backoff**: exponential-with-jitter on that host (rung 0, but applied to the *host
   bucket*, slowing every worker on it).
2. **De-rate**: the governor *lowers the host's RPS cap* (AIMD — additive-increase on
   sustained success, multiplicative-decrease on throttle), so the fleet learns each
   host's true tolerance from evidence and converges below it. This is the automatic form
   of "Recuperación pendiente con menor concurrencia" `[VERIFIED, PROGRESO.md]`.

   > **AIMD is for VOLUMETRIC limits ONLY — not for behaviorally-scored walls `[adversarial GAP-24]`.**
   > AIMD optimizes against a *volumetric* 429 (the scar it fixes — 138 AS24 dealers lost to
   > throttling — was an **OPEN** source with no real WAF). But against a 2026 behavioral ML scorer
   > (DataDome / Akamai Bot Manager v4+), a client that methodically **ramps rate until it trips, backs
   > off exactly 50%, then ramps again** is a textbook automated-probing pattern — the very behavioral
   > regularity these models flag, *distinct* from the volumetric 429 AIMD targets. Applying AIMD to a
   > walled host **trains the defender**. So the governor runs **two pacing regimes, selected by the
   > source's defense tier**:
   > - **OPEN / no-behavioral-WAF → AIMD** (volumetric optimization is correct and safe here).
   > - **Behaviorally-scored Tier-1 / walled → a fixed, randomized, HUMAN-SHAPED pace**: jittered
   >   inter-request delays drawn from a human-like distribution, **no convergence-to-ceiling
   >   probing**. The governor never ramp-probes a behaviorally-scored host; it picks a conservative
   >   constant pace and holds it. "Rate-limit avoidance" (AIMD) and "behavioral-pattern avoidance"
   >   (randomized pacing) are different bottlenecks, no longer conflated as one.
3. **Rotate** (Tier-0→2): rotate the exit IP / refresh the session fingerprint (`02 §6`).
   At Tier-2 lease a fresh sticky residential exit (`02 §5`); **never rotate mid-session**
   (`02 law #3` — mid-session IP rotation is itself a bot signal `[VERIFIED]`).
4. **Quarantine**: if backoff+de-rate+rotate do not clear it, the breaker trips (§5) and
   the source cools. Escalation is evidence-driven, cheapest axis first.

### 7.3 Bulkheads (isolation, law #5)

- **Per-source worker bulkhead**: a bounded share of the worker pool per source/host, so
  one throttling source cannot consume every worker and starve healthy sources (the
  incident froze AS24 work; it must never freeze coches.com work). When a source's breaker
  is OPEN, its bulkhead is freed back to the pool for healthy sources.
- **DB connection pool guard**: the API owns its own `asyncpg` pool (`max_size=8`
  `[VERIFIED, main.py:23]`); the **harvest fleet must use a *separate* pool** so a harvest
  storm can never exhaust the connections the API needs to keep serving (law #1: the API
  never falls). This is a designed bulkhead between the write-side fleet and the read-side
  API.
- **Tier-1 ↔ long-tail isolation**: per `ARCHITECTURE.md §Separación Tier-1` `[VERIFIED]`,
  Tier-1 operations run on a separate schedule, separate worker pool, separate spend
  ledger — a Tier-1 source melting down (Akamai ban, spend exhausted) cannot touch the
  long-tail harvest at all.

---

## 8. Observability (metrics, dashboards, the operator's eyes)

You cannot self-repair what you cannot see, and the incident was invisible until the
post-mortem (§0.3). Observability is built on the tables that already exist plus the two
of §10 — **PostgreSQL is the metrics store** (no new infra required to start; law #6,
evidence persisted where it already lives).

### 8.1 The four golden signals, per source and fleet-wide

Derived as SQL views over `source_health` + `alert` + `verification_verdict` +
`harvest_run` (§10) — queryable today, no external TSDB needed:

| Signal | Definition (per source / fleet) | Source of truth |
|---|---|---|
| **Freshness** | `now() - last_ok` per source; fleet = worst/median | `source_health.last_ok` `[V]` |
| **Health** | `status` distribution (healthy/degraded/down/unknown) | `source_health.status` `[V]` |
| **Integrity** | TRUSTWORTHY : REFUTED : UNVERIFIED ratio, drift count | `verification_verdict.verdict` `[V]` |
| **Throughput / errors** | records/cycle, OK:fail ratio, retry rate | `harvest_run` (§10) |

Plus operational: **breaker state** per source, **open-alert count** by severity
(`idx_alert_unresolved` `[VERIFIED:45]`), **spend** per source/day (spend-ledger,
`02 §5`), **fingerprint health** (X25519MLKEM768 present, challenge-rate trend, `02 §8`).

### 8.2 The operator dashboard (what one screen must answer)

A single board answering the operator's real questions (not a vanity wall):
1. **Is Cardeep serving?** API liveness + served counts (the existing `/health` endpoint
   already returns entity/vehicle/event counts `[VERIFIED, main.py:41-51]`) — extended
   with **freshness age** ("oldest source last_ok: 3h ago") and **stale-source list**.
2. **What is broken right now?** Open `critical`/`warning` alerts, grouped by origin, with
   the exact failing field/wall and the repair state (running/exhausted/escalated).
3. **What is self-repairing?** Sources in `degraded`/`down` with breaker state + cool-down
   ETA + which repair rung (§6) is active.
4. **Is data trustworthy?** Per-source VAM verdict + drift status; any source serving
   over-the-drift-threshold data flagged red.
5. **Tier-1 board (separate track, §2.2):** each giant's status, last_ok, wall, spend, and
   whether it needs a human (spend/credentials).

`GET /ops/health` (full fleet), `GET /ops/sources/{key}` (one source's full history),
`GET /ops/alerts?unresolved=1` extend the existing FastAPI envelope (`{ok,data,error,meta}`
`[VERIFIED, main.py:33-38]`) — observability is API-native, same contract as the data API.

### 8.3 Alerting channels (where a page goes)

- **In-DB** (always): the `alert` table is the durable record (law #6).
- **Push** (escalation, §3.4): when an alert crosses its `ESCALATE_AFTER` timer or is born
  `critical`, it emits to the human channel via the available `PushNotification` /
  unified-notification surface. Auto-repair gets the first window; the human gets only what
  auto-repair could not close — minimizing noise (the §3.4 dedup means one AS24 throttle =
  one page, not 138).
- **Self-resolution closes the loop**: when the watchdog records `→ healthy`, the alert
  auto-resolves (§3.4) and a resolution notice is emitted — the operator sees both the
  break and the heal, so trust in the auto-repair is earned by visible evidence.

---

## 9. Graceful degradation ("Cardeep never falls", mechanized)

Law #1 made concrete. Degradation is **layered**, each layer failing into the next without
the layer above noticing.

### 9.1 The decoupling that makes it possible

The API serves **PostgreSQL**, never the harvester (`main.py` reads only DB tables
`[VERIFIED]`). The harvest fleet writes to PostgreSQL on its own cadence. These are
**physically decoupled processes with separate connection pools** (§7.3). Therefore: a
harvester crash, a source ban, a recipe drift, an entire tier going dark — **none of them
are on the API's request path.** The API serves the last committed snapshot regardless.
This is *why* the API did not notice the 138-dealer loss (§0) — and we promote that
accident to a **designed, defended invariant**.

### 9.2 The degradation ladder (what the user sees as things break)

| Failure scope | What still works | What degrades | User-visible |
|---|---|---|---|
| One dealer harvest fails | everything | that dealer's freshness | stale flag on 1 entity |
| One source down (§5 breaker OPEN) | all other sources, full API | that source's entities' freshness | `meta.stale_sources` |
| Recipe drift (§4) | API serves last good snapshot | that source frozen until heal | stale flag + no bad data |
| A whole tier dark (e.g. all Tier-2 spend-exhausted) | OPEN + long-tail fully live | Tier-1 walled-source freshness | Tier-1 stale; OPEN fresh |
| Harvest fleet entirely down | **full API, all served data** | all freshness (nothing updates) | global stale banner |
| PostgreSQL primary down | **read replica serves** (`[ASSUMED]` HA) | writes (ingest pauses) | read-only mode |

The bottom rows are the law-#1 floor: even with **zero** harvesting, Cardeep *serves* —
degraded to "last known good," never down. The mandate's "never falls" = the API's
availability is a function of the DB, and the DB holds durable committed truth that no
harvest failure can erase (ingest is INSERT/close, never destructive
`[VERIFIED, ARCHITECTURE.md §Doctrina de mutación]`; `GONE` is a status flip + event, never
a hard-delete `[VERIFIED, ingest.py:107-108]` — so even a buggy harvest cannot delete the
served universe).

### 9.3 Staleness as a first-class served field

Degradation is **honest** (anti-makeup): when a source is stale/down, the API says so. The
envelope's `meta` carries `{stale_sources: [...], oldest_last_ok: ts, degraded: bool}` so a
consumer always knows the freshness of what they got. Serving stale data *silently* would
violate the anti-hallucination standard; serving it *labeled* is correct graceful
degradation. The freshness comes straight from `source_health.last_ok` (§2) joined at
query time.

### 9.4 Self-recovery after total crash

Because all operational state is in PostgreSQL (law #6: `source_health`, `alert`,
breaker/repair state §10), a fleet restart **reconstructs its own state** from the DB:
open breakers stay open (cool-downs honored via persisted `opened_at`), parked sources stay
parked, in-flight repair attempts resume from their last recorded rung. There is no
in-memory state to lose — the system boots back into exactly the operational posture it
crashed in, and continues self-repairing. This is what makes "never falls" survive a power
cut, not just a source ban.

---

## 10. New schema (additive migration `0005`, the minimum to wire this)

`source_health`, `alert`, `verification_verdict` already exist and carry most of the load
`[VERIFIED, migrations/0004]`. Resilience needs **two** more durable tables (breaker state
must survive restart, §9.4; repair attempts are evidence, law #6) and **two** columns on
`source_health` (per-source tuning). Additive, idempotent, reversible — same discipline as
`0001-0004` `[VERIFIED, ARCHITECTURE.md §Motor]`.

```sql
-- 0005_resilience_ops.sql  (additive, idempotent, reversible)

-- Per-source circuit breaker state (must survive restart, §5/§9.4).
CREATE TABLE IF NOT EXISTS source_breaker (
    source_key      TEXT PRIMARY KEY REFERENCES source_health(source_key),
    state           TEXT NOT NULL DEFAULT 'closed'
        CHECK (state IN ('closed','open','half_open')),
    opened_at       TIMESTAMPTZ,                 -- for cool-down ETA after restart
    consecutive_trips INT NOT NULL DEFAULT 0,    -- drives exponential cool-down (§5.1)
    cool_until      TIMESTAMPTZ,                 -- scheduler skips source until this
    last_probe_at   TIMESTAMPTZ
);

-- Per-harvest evidence + the throughput/error golden signal (§8.1). One row per
-- (source_key, cycle): the audit trail the §0 incident lacked.
CREATE TABLE IF NOT EXISTS harvest_run (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_key    TEXT NOT NULL,
    cycle_id      TEXT NOT NULL,
    phase         TEXT NOT NULL,                 -- discover|scrape|recipe|ingest|verify|fetch|geocode
    tier          INT,                           -- fetch tier reached (02 §2)
    outcome       TEXT NOT NULL,                 -- OK|OK_EMPTY|SOFT_FAIL|HARD_FAIL|DRIFT_FAIL|VERIFY_FAIL
    records_in    INT, records_out INT,          -- count-band drift input (§4.2)
    declared_count INT,                          -- source's own counter (VAM, §4.2)
    null_rates    JSONB,                         -- per-field null-rate vs golden (§4.2)
    http_status   INT, signal TEXT,              -- typed failure (§3.3)
    duration_ms   INT, retries INT,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_harvest_run_source ON harvest_run (source_key, started_at DESC);

-- Auto-repair audit (every rung attempt + outcome; §6, law #6).
CREATE TABLE IF NOT EXISTS repair_attempt (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_key    TEXT NOT NULL,
    alert_id      BIGINT REFERENCES alert(id),   -- links repair to its alert (§3.4)
    signal        TEXT NOT NULL,                 -- §3.3 vocabulary
    rung          TEXT NOT NULL,                 -- rung0_retry|rung1_refingerprint|rung2_rederive|rung3_park
    outcome       TEXT NOT NULL                  -- recovered|failed|escalated|parked
        CHECK (outcome IN ('recovered','failed','escalated','parked','pending')),
    detail        JSONB,
    attempted_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_repair_source ON repair_attempt (source_key, attempted_at DESC);

-- Per-source tuning (thresholds/caps live with the source, not hardcoded; §2.2/§7.1).
ALTER TABLE source_health ADD COLUMN IF NOT EXISTS is_tier1 BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE source_health ADD COLUMN IF NOT EXISTS tuning JSONB;  -- {down_at, host_rps_cap, concurrency, ...}

-- Rollback:
-- ALTER TABLE source_health DROP COLUMN IF EXISTS tuning;
-- ALTER TABLE source_health DROP COLUMN IF EXISTS is_tier1;
-- DROP TABLE IF EXISTS repair_attempt;
-- DROP TABLE IF EXISTS harvest_run;
-- DROP TABLE IF EXISTS source_breaker;
```

> The two existing `0004` tables are deliberately **not** altered — the resilience layer
> *consumes* `source_health`/`alert`/`verification_verdict` and *adds* breaker/run/repair
> state beside them. No regression to the live schema; `0005` is purely additive.

---

## 11. Concrete fixes this design forces on existing code

Grounded, not abstract — the bug-fix list the resilience layer imposes, every line
`[VERIFIED]`:

1. **`scale_as24.py:58-60` — replace `totals["errors"] += 1; print(...)`** with
   `record_outcome(HARD_FAIL)` + structured `alert` + `harvest_run` row + breaker check.
   The 138-dealer loss must produce *one actionable alert with the exact dealer list*, not
   a stdout count. `[VERIFIED bug: errors only printed]`
2. **`autoscout24.py:67-81` — promote retry to the engine, fix linear→exponential+jitter**,
   and gate it behind the circuit breaker so exhausted retries trip the breaker instead of
   compounding the ban. `[VERIFIED: linear backoff, no breaker]`
3. **`scale_as24.py` + `as24_harvest_batch` ×4 — replace per-process `time.sleep`** with
   the fleet-wide per-host token bucket (§7.1). The 4× hammer is structurally impossible
   once the bucket is the only path to a request. `[VERIFIED: per-process sleep, no fleet
   coordination]`
4. **`ingest.py:113-118` — wire VAM `REFUTED` to `record_outcome(VERIFY_FAIL)` +
   quarantine** (§4.4). Today the verdict is recorded and ignored; it must trip the
   watchdog and fail closed. `[VERIFIED: verdict returned, no action taken]`
5. **`main.py` — separate the API's `asyncpg` pool from the harvest fleet's pool** (§7.3)
   and add `meta.stale_sources` to the envelope (§9.3) + `GET /ops/*` endpoints (§8.2).
   `[VERIFIED: single pool max_size=8, no staleness in meta]`
6. **A drift detector before every `ingest_dealer` commit** (§4.2) reading the recipe's
   golden sample — quarantine on drift, never ingest wrong data over good. `[VERIFIED: no
   drift check exists; ingest commits whatever harvest returns]`

These ship as a new `pipeline/ops/` package (`watchdog.py`, `breaker.py`, `alerts.py`,
`repair.py`, `governor.py`, `drift.py`) consuming `migrations/0005` + the existing `0004`
tables, with `scale_as24.py`/`as24_harvest_batch` reduced to thin callers of the governed
scheduler. Implementation is out of scope for this doc (architecture only); the contracts
above are the spec.

---

## 12. Sources (repo-verified 2026-06-12)

- The health/alert/verdict DDL every column is checked against — `migrations/0004_verification_health.sql`.
- The delta engine + VAM call site — `pipeline/ingest.py` (REFUTED unwired at `:113-118`).
- The quorum judge + "silent data loss never reads TRUSTWORTHY" — `pipeline/verify.py:38-47`.
- The retry/backoff this doc fixes — `pipeline/sources/autoscout24.py:61-81,274`.
- The throttle incident (138 dealers, 4× load, manual recovery) + per-process pacing —
  `scripts/scale_as24.py:42-61`, `PROGRESO.md` (2026-06-12 INVENTARIO A ESCALA).
- The API decoupling, envelope, pool, `/health` — `services/api/main.py:23,33-51`.
- Cost doctrine, anti-collision contract, S-HEALTH row, WF-TIER1-HUNT — `docs/ORQUESTACION.md`.
- Mutation doctrine (INSERT/close, append-only history), Tier-1 separation, schema layers —
  `docs/ARCHITECTURE.md`.
- The fetch engine this layer sits on (tiers, is-antibot routing, session coherence,
  self-tuning tier, recipe `heal:` block, X25519MLKEM768) — `docs/architecture/02-SCRAPING-ENGINE.md`.
- The source universe (Tier-1 walls, Adevinta/AUTO1 host families, auth/spend-gated B2B) —
  `docs/architecture/00-TIER1-REGISTRY.md`.
```

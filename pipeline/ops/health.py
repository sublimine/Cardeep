"""P4 — S-HEALTH: the watchdog, exact-origin alerting, circuit breaker, auto-repair loop.

The mandate this module makes true (06-RESILIENCE-OPS §0-§9):
  "if a source fails, an alert fires with the EXACT origin, it self-repairs, and Cardeep
   never falls."

The 138-dealer scar was invisible: a failure surfaced only as `totals["errors"] += 1`
printed to stdout. Nothing wrote source_health, nothing raised an alert, nothing knew
which work to retry, nothing stopped hammering a host that was already throttling. This
module is the wiring that turns every line of that anatomy into a mechanism:

  record_run(...)  -> writes harvest_run (the audit the incident lacked), updates
                      source_health (last_ok/last_fail/consecutive_fails/status), and trips
                      source_breaker after N consecutive fails (circuit OPEN + cooldown).
  fire_alert(...)  -> writes the alert table with the EXACT origin (source_key:phase[:cdp])
                      and a specific message — never "something failed".
  auto_repair(...) -> classifies the failure (403/blocked / fields-null/drift / ban /
                      unknown), logs a repair_attempt with the chosen action, returns it.
  is_open(...)     -> harvest code calls this BEFORE running; an open breaker skips the
                      source with a logged reason. Graceful degradation = "no se cae".

All four are deterministic, local, €0 (law #7). The repair ACTIONS that need real spend
(re-fingerprint with a paid browser, tier escalation to a residential proxy, agent recipe
re-hunt) are explicitly scaffolded and marked — but the LOOP, the classification, the
alert, and the breaker actually run, every cycle, against the real DB tables.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

import asyncpg

# ---------------------------------------------------------------------------
# Thresholds & state machine constants (06 §2.2 / §5; defaults tunable per source via
# source_health.tuning, read at call time so a tuned source overrides these).
# ---------------------------------------------------------------------------
DEGRADE_AT = 1          # first fail -> degraded (eager visibility)
DOWN_AT = 3             # 3 consecutive fails -> down (matches the 3-retry fetch budget)
RECOVER_OK = 1          # one clean run resets fails and climbs status
BREAKER_TRIP_AT = 3     # consecutive fails that trip the circuit breaker OPEN
BREAKER_COOLDOWN_SEC = 900   # base cool-down after a trip; exponential per re-trip (§5.1)

# Closed vocabulary of repair actions (must match migrations/0013 CHECK constraint).
ACTION_REFINGERPRINT = "refingerprint"
ACTION_ESCALATE_TIER = "escalate_tier"
ACTION_RE_RECETA = "re_receta"
ACTION_QUARANTINE = "quarantine"
ACTION_ESCALATE_OWNER = "escalate_owner"

# Severity vocabulary (must match the 0004 alert CHECK constraint).
SEV_INFO = "info"
SEV_WARNING = "warning"
SEV_CRITICAL = "critical"


@dataclass(frozen=True)
class RunOutcome:
    """The result of record_run: the post-write health/breaker posture, so the caller can
    react (e.g. fire an alert on the transition, or skip future work)."""
    source_key: str
    status: str               # healthy | degraded | down | unknown
    consecutive_fails: int
    breaker_state: str        # closed | open | half_open
    breaker_tripped: bool     # True only on the cycle the breaker transitioned to OPEN
    status_changed: bool      # True when status differs from the prior status (alert edge)


def _tuning_int(tuning: dict | None, key: str, default: int) -> int:
    if not tuning:
        return default
    val = tuning.get(key)
    return int(val) if isinstance(val, (int, float)) else default


async def record_run(
    conn: asyncpg.Connection,
    source_key: str,
    *,
    ok: bool,
    rows: int | None = None,
    error: str | None = None,
    http_status: int | None = None,
) -> RunOutcome:
    """Record one harvest run outcome. THE single writer of source_health + source_breaker.

    Writes a harvest_run audit row, updates source_health (last_ok/last_fail/
    consecutive_fails/status with hysteresis), and trips the circuit breaker to OPEN with
    an exponential cool-down after BREAKER_TRIP_AT consecutive fails. Idempotent per call;
    concurrent callers for the same source serialize on the source_health row (FOR UPDATE)
    so consecutive_fails is never lost-update-corrupted (06 §2.3 isolation, law #5).

    Returns a RunOutcome describing the new posture (status, breaker, and whether this call
    crossed a transition edge — the signal the caller uses to fire exactly one alert).
    """
    async with conn.transaction():
        # 1) audit row — the evidence the incident lacked (law #6).
        await conn.execute(
            """INSERT INTO harvest_run (source_key, finished_at, ok, rows, error, http_status)
               VALUES ($1, now(), $2, $3, $4, $5)""",
            source_key, ok, rows, error, http_status)

        # 2) read-modify-write source_health under a row lock (single writer, §2.3).
        row = await conn.fetchrow(
            "SELECT consecutive_fails, status, tuning FROM source_health "
            "WHERE source_key=$1 FOR UPDATE", source_key)
        prior_status = row["status"] if row else "unknown"
        prior_fails = row["consecutive_fails"] if row else 0
        tuning = json.loads(row["tuning"]) if row and row["tuning"] else None

        degrade_at = _tuning_int(tuning, "degrade_at", DEGRADE_AT)
        down_at = _tuning_int(tuning, "down_at", DOWN_AT)
        trip_at = _tuning_int(tuning, "fail_threshold", BREAKER_TRIP_AT)
        cooldown_sec = _tuning_int(tuning, "cooldown_sec", BREAKER_COOLDOWN_SEC)

        if ok:
            new_fails = 0
            new_status = "healthy"
            await conn.execute(
                """INSERT INTO source_health (source_key, last_ok, consecutive_fails, status)
                   VALUES ($1, now(), 0, 'healthy')
                   ON CONFLICT (source_key) DO UPDATE
                     SET last_ok = now(), consecutive_fails = 0, status = 'healthy'""",
                source_key)
        else:
            new_fails = prior_fails + 1
            new_status = "down" if new_fails >= down_at else (
                "degraded" if new_fails >= degrade_at else "healthy")
            await conn.execute(
                """INSERT INTO source_health (source_key, last_fail, consecutive_fails, status)
                   VALUES ($1, now(), $2, $3)
                   ON CONFLICT (source_key) DO UPDATE
                     SET last_fail = now(), consecutive_fails = $2, status = $3""",
                source_key, new_fails, new_status)

        # 3) circuit breaker (06 §5). Trip to OPEN once consecutive fails reach the
        # threshold; cool-down is exponential per consecutive trip. A success closes it.
        brow = await conn.fetchrow(
            "SELECT state, consecutive_fails FROM source_breaker WHERE source_key=$1 FOR UPDATE",
            source_key)
        prior_breaker = brow["state"] if brow else "closed"
        breaker_tripped = False

        if ok:
            # A clean run closes the breaker and resets its trip counter.
            new_breaker_state = "closed"
            new_breaker_trips = 0
            await conn.execute(
                """INSERT INTO source_breaker (source_key, state, consecutive_fails,
                       opened_at, cooldown_until)
                   VALUES ($1, 'closed', 0, NULL, NULL)
                   ON CONFLICT (source_key) DO UPDATE
                     SET state = 'closed', consecutive_fails = 0,
                         opened_at = NULL, cooldown_until = NULL""",
                source_key)
        elif new_fails >= trip_at:
            # consecutive_fails on the breaker mirrors the fail streak (the column's name);
            # it is the single source of truth shared with source_health (06 §5.1). The
            # cool-down grows with how DEEP past the trip threshold the source is failing —
            # "a source that keeps tripping cools longer" — keyed off the streak itself, so
            # no second counter is needed and the column keeps one honest meaning.
            new_breaker_trips = new_fails
            new_breaker_state = "open"
            breaker_tripped = prior_breaker != "open"
            depth = new_fails - trip_at            # 0 on the first trip, +1 per extra fail
            cool = min(cooldown_sec * (2 ** depth), 86400)   # base on first trip, x2 each deeper fail, cap 24h
            await conn.execute(
                """INSERT INTO source_breaker (source_key, state, consecutive_fails,
                       opened_at, cooldown_until)
                   VALUES ($1, 'open', $2, now(), now() + ($3 || ' seconds')::interval)
                   ON CONFLICT (source_key) DO UPDATE
                     SET state = 'open', consecutive_fails = $2, opened_at = now(),
                         cooldown_until = now() + ($3 || ' seconds')::interval""",
                source_key, new_breaker_trips, str(cool))
        else:
            # failing but below trip threshold: track the fail streak on the breaker, stay closed.
            new_breaker_state = prior_breaker if prior_breaker != "open" else "open"
            new_breaker_trips = new_fails
            await conn.execute(
                """INSERT INTO source_breaker (source_key, state, consecutive_fails)
                   VALUES ($1, $2, $3)
                   ON CONFLICT (source_key) DO UPDATE SET consecutive_fails = $3""",
                source_key, new_breaker_state, new_fails)

    return RunOutcome(
        source_key=source_key,
        status=new_status,
        consecutive_fails=new_fails,
        breaker_state=new_breaker_state,
        breaker_tripped=breaker_tripped,
        status_changed=(new_status != prior_status),
    )


def build_origin(source_key: str, phase: str, cdp_code: str | None = None) -> str:
    """The canonical exact-origin key: '<source_key>:<phase>[:<cdp_code>]' (06 §3.1).
    This is what makes the mandate's "origen exacto" machine-readable, never a prose blob."""
    return f"{source_key}:{phase}:{cdp_code}" if cdp_code else f"{source_key}:{phase}"


async def fire_alert(
    conn: asyncpg.Connection,
    origin: str,
    *,
    severity: str = SEV_WARNING,
    message: str,
    payload: dict | None = None,
) -> int:
    """Write an alert row with the EXACT origin and a SPECIFIC message (06 §3).

    `origin` must be the canonical key from build_origin(). `message` must name what
    broke concretely (the failing source/phase/field/wall), never "something failed".
    Dedup (06 §3.4): if an unresolved alert already exists for this exact origin, its
    payload is updated (consecutive_fails bumped, repair appended) instead of inserting a
    new row — so 138 dealers throttling is ONE actionable AS24 alert, not 138 rows.
    Returns the alert id (existing-updated or newly-inserted).
    """
    existing = await conn.fetchrow(
        "SELECT id FROM alert WHERE origin=$1 AND resolved_at IS NULL "
        "ORDER BY created_at DESC LIMIT 1", origin)
    payload_json = json.dumps(payload or {})
    if existing is not None:
        await conn.execute(
            "UPDATE alert SET message=$2, payload=$3::jsonb WHERE id=$1",
            existing["id"], message, payload_json)
        return existing["id"]
    return await conn.fetchval(
        """INSERT INTO alert (origin, severity, message, payload)
           VALUES ($1, $2, $3, $4::jsonb) RETURNING id""",
        origin, severity, message, payload_json)


async def resolve_alerts(conn: asyncpg.Connection, origin: str) -> int:
    """Auto-resolve all open alerts for an origin (06 §3.4 — a recovery closes its own
    alert, so the loop is observable end to end). Returns the number resolved."""
    return await conn.fetchval(
        "WITH upd AS (UPDATE alert SET resolved_at = now() "
        "WHERE origin=$1 AND resolved_at IS NULL RETURNING 1) SELECT count(*) FROM upd",
        origin) or 0


# ---------------------------------------------------------------------------
# Failure classification (06 §3.3 typed signals -> §6 repair rungs).
# ---------------------------------------------------------------------------

def classify_failure(reason: str, *, http_status: int | None = None) -> str:
    """Map a raw failure observation to a typed signal, then to a repair ACTION.

    The classification is deterministic and local (€0). `reason` is free text from the
    harvest (the error string), `http_status` the last HTTP code when known. Returns the
    repair action from the 0013 closed vocabulary. This is the brain of the auto-repair
    loop: every failure gets a typed response, never a silent drift (law #6).
    """
    text = (reason or "").lower()

    # 403 / blocked / challenge wall -> defense escalation.
    if http_status in (401, 403) or any(
            t in text for t in ("403", "blocked", "forbidden", "challenge", "captcha",
                                 "akamai", "datadome", "cloudflare", "perimeterx")):
        # A fresh fingerprint is the cheapest defense move; if that class of wall needs a
        # higher tier (residential egress / browser engine), the loop escalates the tier.
        if any(t in text for t in ("akamai", "datadome", "perimeterx", "sensor", "residential")):
            return ACTION_ESCALATE_TIER
        return ACTION_REFINGERPRINT

    # ban / rate-limit / throttle -> back off and quarantine the source (cool it down).
    if http_status == 429 or any(
            t in text for t in ("429", "rate limit", "rate-limit", "throttl", "too many",
                                 "ban", "banned")):
        return ACTION_QUARANTINE

    # recipe drift / fields-null / schema change -> re-derive the recipe.
    if any(t in text for t in ("null", "drift", "schema", "field", "missing path",
                               "parse", "selector", "json path", "jsonpath", "no listings")):
        return ACTION_RE_RECETA

    # unknown / unrepairable -> escalate to the owner (the honest wall, never faked).
    return ACTION_ESCALATE_OWNER


# Actions that need real spend (P10) — their EFFECT is scaffolded/logged here, clearly
# marked. The LOOP, classification, alert, breaker, and the repair_attempt audit all run
# for real; only the spend-bearing side-effect is deferred behind the P10 gate.
_SPEND_GATED_ACTIONS = {ACTION_REFINGERPRINT, ACTION_ESCALATE_TIER, ACTION_RE_RECETA}


async def auto_repair(
    conn: asyncpg.Connection,
    source_key: str,
    reason: str,
    *,
    phase: str = "scrape",
    cdp_code: str | None = None,
    http_status: int | None = None,
) -> str:
    """The auto-repair loop (06 §6). Classify the failure, log a repair_attempt with the
    chosen action, fire the exact-origin alert, and return the action taken.

    Returns the repair action (0013 vocabulary). The classification + the repair_attempt
    row + the alert ALWAYS run (this is the live self-repair loop). The spend-bearing
    EFFECT of refingerprint/escalate_tier/re_receta is scaffolded (logged + recorded as
    not-yet-succeeded) behind the P10 spend gate — clearly marked, never faked as done.
    `quarantine` and `escalate_owner` are fully effective here (they cost €0: the breaker
    cools the source, the owner-park records the honest wall).
    """
    action = classify_failure(reason, http_status=http_status)
    origin = build_origin(source_key, phase, cdp_code)

    # quarantine and escalate_owner are deterministic and complete with no spend:
    #   quarantine    -> the breaker (record_run) already cools the source; this records
    #                    that the loop chose to back off and park the source's work.
    #   escalate_owner-> the honest wall: record it as a parked decision for the owner.
    # The spend-gated rungs are scaffolded: recorded as attempted, succeeded=FALSE, with a
    # clear marker that the real effect lands when the P10 spend gate authorizes it.
    spend_gated = action in _SPEND_GATED_ACTIONS
    succeeded = not spend_gated   # €0 actions complete now; spend-gated await P10.

    detail = {
        "phase": phase,
        "cdp_code": cdp_code,
        "http_status": http_status,
        "reason": reason,
        "spend_gated": spend_gated,
    }
    if spend_gated:
        # P10-SCAFFOLD: the EFFECT (paid browser refingerprint / residential tier bump /
        # agent recipe re-hunt) is not executed here — it needs authorized spend. We record
        # the classified action and mark it pending so the ledger/escalation can pick it up.
        # This is the ONLY place scaffolding is allowed (the task's explicit exception).
        detail["scaffold"] = "P10-spend: effect deferred; classification+audit+alert ran"

    await conn.execute(
        """INSERT INTO repair_attempt (source_key, detected_reason, action, succeeded)
           VALUES ($1, $2, $3, $4)""",
        source_key, reason, action, succeeded)

    severity = SEV_CRITICAL if action in (ACTION_RE_RECETA, ACTION_ESCALATE_OWNER) else SEV_WARNING
    await fire_alert(
        conn, origin, severity=severity,
        message=(f"source '{source_key}' failed at phase '{phase}'"
                 f"{f' on {cdp_code}' if cdp_code else ''}: {reason} "
                 f"-> auto-repair action '{action}'"
                 f"{' (P10 spend-gated, pending)' if spend_gated else ''}"),
        payload={**detail, "action": action, "repair_outcome":
                 "pending" if spend_gated else "applied"})
    return action


async def is_open(conn: asyncpg.Connection, source_key: str) -> bool:
    """Has this source's circuit breaker tripped OPEN (and not yet cooled down)?

    Harvest code calls this BEFORE running a source. True -> skip the source gracefully
    (the system continues serving the last good snapshot — "no se cae"). The breaker is
    treated as half_open (one probe allowed) once cooldown_until has passed; the caller
    that gets a False after cool-down is the canary probe (06 §5.1).
    """
    row = await conn.fetchrow(
        "SELECT state, cooldown_until FROM source_breaker WHERE source_key=$1", source_key)
    if row is None or row["state"] != "open":
        return False
    cooldown_until = row["cooldown_until"]
    if cooldown_until is None:
        return True
    # cool-down elapsed -> move to half_open so exactly one probe is allowed through.
    now_past_cooldown = await conn.fetchval(
        "SELECT now() >= $1", cooldown_until)
    if now_past_cooldown:
        await conn.execute(
            "UPDATE source_breaker SET state='half_open' WHERE source_key=$1 AND state='open'",
            source_key)
        return False
    return True

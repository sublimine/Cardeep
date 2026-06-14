"""B2.3 — Delta GONE guard: prevent false GONEs from partial harvests.

A GONE sweep is only safe when the harvest is provably complete. Two probes:

  1. Primary (declared): if the connector reports a declared total (the site's own
     numberOfResults / totalHits / aggregates.count), the sweep fires only when
       harvested_count >= declared_count * DECLARED_THRESHOLD   (default 0.95)
     This is the 5% tolerance that absorbs dedup-collisions and trailing dedup across
     page boundaries without masking a genuinely partial drain.

  2. Fallback (previous_available): when no declared count is available (connectors
     that page by exhaustion and produce no site-level denominator), the guard falls
     back to the last-known DB count for the entity:
       harvested_count >= previous_available * PREVIOUS_THRESHOLD   (default 0.50)
     A 50% floor is conservative enough to catch a mid-drain timeout (e.g. page 3 of
     10) while still allowing legitimate inventory contractions of up to 49%. This
     threshold is DOCUMENTED here because it is not self-evident: the value is chosen
     as the midpoint between "any harvest is fine" (0%) and "must equal history" (100%),
     erring hard on the side of not corrupting the DB. Connectors that adopt this path
     MUST pass their real `previous_available` (fresh SELECT COUNT) — never a stale
     cached value, which would defeat the guard.

Usage::

    from pipeline.delta_guard import should_emit_gone

    allow, reason = should_emit_gone(
        harvested=len(harvest.vehicles),
        declared=harvest.declared_count,      # None if unknown
        previous_available=prev_count,        # None if first run
    )
    if allow:
        # perform GONE sweep
    else:
        # skip sweep; fire_alert with reason

Integration notes:
  - `ingest.py` (AS24): cabled here directly (has declared_count on DealerHarvest).
  - Wholesale connectors that already use `fetch_error is None` as their gate
    (group_subastas_wholesale, localizavo_wholesale, subastacar_wholesale) have a
    complementary but weaker guard — they block on ANY error, but not on a partial
    drain that happened without raising an exception. These connectors should also
    adopt should_emit_gone on their reconcile path (B2.3 TODO list, see module bottom).
  - Connectors with no GONE sweep at all (listed at module bottom) are not affected
    by this module today; they will need a GONE sweep + this guard added together.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Thresholds (module-level constants — named, not magic numbers)
# ---------------------------------------------------------------------------

#: Minimum ratio harvested/declared to consider the drain complete.
DECLARED_THRESHOLD: float = 0.95

#: Minimum ratio harvested/previous_available when no declared count exists.
#: Conservative: blocks GONE when inventory appears to have dropped by more than 50 %
#: in one run without a declared denominator to confirm it.
PREVIOUS_THRESHOLD: float = 0.50


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def should_emit_gone(
    harvested: int,
    declared: int | None,
    previous_available: int | None = None,
) -> tuple[bool, str]:
    """Decide whether it is safe to emit a GONE sweep for an entity/platform.

    Args:
        harvested:          Number of vehicles/listings actually ingested this run.
        declared:           Total count declared by the source (numberOfResults, etc.).
                            Pass None when the connector has no reliable site-level total.
        previous_available: Count of 'available' rows in the DB before this run
                            (fresh SELECT COUNT). Used as fallback when declared is None.
                            Pass None on a first-ever run (no history) — in that case the
                            function returns (True, ...) because there is nothing to GONE.

    Returns:
        (allow: bool, reason: str)
        - allow=True  → safe to emit GONE sweep; reason explains why it was allowed.
        - allow=False → skip GONE sweep; reason names the specific partial-harvest concern.
          The caller MUST log / fire_alert with this reason.

    All branches are explicit — no silent default-allow on ambiguous inputs.
    """
    # ---- Branch 1: declared count available (primary probe) ------------------
    if declared is not None:
        threshold = declared * DECLARED_THRESHOLD
        if harvested >= threshold:
            return (
                True,
                f"declared probe: harvested={harvested} >= declared*{DECLARED_THRESHOLD}"
                f"={threshold:.1f} (declared={declared})",
            )
        return (
            False,
            f"partial harvest (declared probe): harvested={harvested} < "
            f"declared*{DECLARED_THRESHOLD}={threshold:.1f} (declared={declared}); "
            f"GONE sweep suppressed to avoid false GONEs.",
        )

    # ---- Branch 2: no declared count; fall back to previous_available --------
    if previous_available is None or previous_available == 0:
        # First-ever run or empty history: nothing to falsely GONE, allow the sweep.
        # (A GONE sweep on a first run would retire 0 rows since DB was empty.)
        return (
            True,
            "no declared count and no previous_available (first run or empty history); "
            "GONE sweep allowed (nothing to falsely retire).",
        )

    threshold = previous_available * PREVIOUS_THRESHOLD
    if harvested >= threshold:
        return (
            True,
            f"fallback probe: harvested={harvested} >= previous*{PREVIOUS_THRESHOLD}"
            f"={threshold:.1f} (previous_available={previous_available}); "
            f"no declared count — conservative fallback applied.",
        )
    return (
        False,
        f"partial harvest (fallback probe): harvested={harvested} < "
        f"previous*{PREVIOUS_THRESHOLD}={threshold:.1f} "
        f"(previous_available={previous_available}); "
        f"no declared count — GONE sweep suppressed.",
    )


# ---------------------------------------------------------------------------
# B2.3 adoption TODO list — connectors that need to adopt this guard
# ---------------------------------------------------------------------------
#
# CONNECTORS WITH GONE/removed SWEEP — need should_emit_gone added:
#   Partially guarded (fetch_error is None, but no harvest-ratio check):
#     - pipeline/platform/group_subastas_wholesale.py   line ~1005  (Ayvens cage)
#     - pipeline/platform/localizavo_wholesale.py       line ~801   (_reconcile_aged_out)
#     - pipeline/platform/subastacar_wholesale.py       line ~813   (_reconcile_aged_out)
#   These three already block on any exception (`fetch_error is None`), which covers
#   hard failures but NOT silent partial drains where the loop ends without error.
#   Recommended: add should_emit_gone(harvested=stats["cars_caged"], declared=stats["declared_full"])
#   just before the reconcile call, using declared_full (populated from the site total).
#
# CONNECTORS WITHOUT ANY GONE SWEEP (no action needed for B2.3, but noted for B2.x):
#   - pipeline/ingest.py                          AS24 per-dealer (NOW GUARDED — see below)
#   All remaining connectors in pipeline/platform/ that are not listed above do NOT
#   perform a GONE sweep and never did — they are append-only ingesters that rely on
#   last_seen staleness / future eviction passes. They do not need this guard today.
#   When a GONE/eviction sweep is added to them, this guard MUST be wired at that point.
#
# ---------------------------------------------------------------------------

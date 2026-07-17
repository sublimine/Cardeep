"""services/api/lifetime_aggregates.py — 02-history-reports F2 "Vida en mercado" aggregates.

Pure computation over already-fetched vehicle/vehicle_event/lifetime_link rows — zero
asyncpg/FastAPI imports, mirrors services/api/stats.py's convention so the logic is
unit-testable without a DB and reusable from a future batch/cache job if F2's latency
measurement ever demands one (plans/cardeep-omni/02-history-reports.md §5: "la decisión
de cachear se toma en F2 con medición, no ahora").

Implements C1-C10 from plans/cardeep-omni/02-history-reports.md §4. Every function takes
plain dicts (already decoded from asyncpg/psycopg2 rows) and datetimes — no SQL here.
"""
from __future__ import annotations

import datetime
from typing import Any

# ---------------------------------------------------------------------------
# Constants — shared with pipeline/identity/link_lifetimes.py by VALUE (not
# import: this module must stay free of pipeline/ dependencies so a future
# lightweight deploy of the API alone does not need the scraper package tree).
# Keep these two constants numerically identical if either changes.
# ---------------------------------------------------------------------------

KM_NOISE_THRESHOLD_KM = 1000
"""Anti-noise threshold for km retreat detection (C8). Matches
pipeline/identity/link_lifetimes.KM_NOISE_THRESHOLD_KM exactly — see that
module's docstring for the rationale (same number, same anti-noise floor, used
by both the linker and the C8 alert so "linkable" and "alert-worthy" never
diverge)."""

C1_DUAL_PATH_TOLERANCE_HOURS = 24
"""§7 dual-path verification: vehicle.first_seen/last_seen vs the vehicle_event
NEW/GONE observed_at must agree within this tolerance or C1 is suppressed and
an alert is raised — never silently shown from a single, unverified path."""

C9_AVISOS_PRICE_DROPS = 3
C9_AVISOS_DAYS_ON_MARKET = 90
C9_AVISOS_REBOTADO_EPISODES = 2
C9_FUERTES_REBOTADO_EPISODES = 3
C9_FUERTES_DEALER_COUNT = 3


def _price_of(value: dict | None) -> float | None:
    if not value:
        return None
    p = value.get("price")
    return float(p) if p is not None else None


def _km_of(value: dict | None) -> int | None:
    if not value:
        return None
    k = value.get("km")
    return int(k) if k is not None else None


# ---------------------------------------------------------------------------
# compute_episode — C1 (dual-path), C3, C4, C8a for ONE vehicle_ulid's own
# vehicle_event stream (works with zero lifetime chain — every vehicle gets
# these, per §12: a section renders only if it has >=1 real datum, and these
# never depend on F1's cross-episode linking).
# ---------------------------------------------------------------------------


def compute_episode(
    vehicle: dict[str, Any],
    events: list[dict[str, Any]],
    now: datetime.datetime,
) -> dict[str, Any]:
    """One episode's per-vehicle metrics.

    vehicle: {vehicle_ulid, entity_ulid, status, first_seen, last_seen, ...}
    events: this vehicle_ulid's vehicle_event rows, ASC by observed_at
        (event_type, old_value, new_value, observed_at).
    """
    new_events = [e for e in events if e["event_type"] == "NEW"]
    gone_events = [e for e in events if e["event_type"] == "GONE"]
    price_change_events = [e for e in events if e["event_type"] == "PRICE_CHANGE"]
    km_change_events = [e for e in events if e["event_type"] == "KM_CHANGE"]

    c1_days: int | None
    c1_suppressed: bool
    c1_reason: str | None

    if not new_events:
        c1_days, c1_suppressed, c1_reason = None, True, "no NEW event in the vehicle_event stream"
    else:
        event_new_at = new_events[0]["observed_at"]
        event_gone_at = gone_events[-1]["observed_at"] if gone_events else None

        # §7 dual-path check: event stream vs vehicle.first_seen/last_seen.
        divergences: list[str] = []
        if abs((vehicle["first_seen"] - event_new_at).total_seconds()) > C1_DUAL_PATH_TOLERANCE_HOURS * 3600:
            divergences.append("first_seen/NEW-event divergence > 24h")
        if vehicle.get("status") == "gone" and event_gone_at is not None:
            if abs((vehicle["last_seen"] - event_gone_at).total_seconds()) > C1_DUAL_PATH_TOLERANCE_HOURS * 3600:
                divergences.append("last_seen/GONE-event divergence > 24h")

        if divergences:
            c1_days, c1_suppressed, c1_reason = None, True, "; ".join(divergences)
        elif vehicle.get("status") == "gone":
            end = event_gone_at if event_gone_at is not None else vehicle["last_seen"]
            c1_days, c1_suppressed, c1_reason = (end - event_new_at).days, False, None
        else:
            c1_days, c1_suppressed, c1_reason = (now - event_new_at).days, False, None

    # C3: price drops vs increases, counted separately, neither hidden.
    c3_price_drops = 0
    c3_price_increases = 0
    for e in price_change_events:
        old_p, new_p = _price_of(e.get("old_value")), _price_of(e.get("new_value"))
        if old_p is None or new_p is None:
            continue
        if new_p < old_p:
            c3_price_drops += 1
        elif new_p > old_p:
            c3_price_increases += 1

    # C4: (first observed price - last observed price) / first price.
    # First price = NEW event's price, or the first PRICE_CHANGE's old_value if
    # NEW recorded none (§4 C4 — the alternative the letter declares "verified
    # by F1 reading the real event emitter", resolved here: fall back honestly
    # rather than leaving C4 unset when NEW's price is simply absent).
    first_price: float | None = _price_of(new_events[0].get("new_value")) if new_events else None
    if first_price is None and price_change_events:
        first_price = _price_of(price_change_events[0].get("old_value"))
    last_price: float | None = None
    if price_change_events:
        last_price = _price_of(price_change_events[-1].get("new_value"))
    elif new_events:
        last_price = _price_of(new_events[0].get("new_value"))

    c4_pct_drop: float | None = None
    if first_price is not None and last_price is not None and first_price > 0:
        c4_pct_drop = round((first_price - last_price) / first_price * 100, 2)

    # C8a: intra-listing km retreat (>KM_NOISE_THRESHOLD_KM decrease), with the
    # two readings + two dates as evidence — never a bare accusation.
    c8a_km_retreats: list[dict[str, Any]] = []
    for e in km_change_events:
        old_km, new_km = _km_of(e.get("old_value")), _km_of(e.get("new_value"))
        if old_km is None or new_km is None:
            continue
        if old_km - new_km > KM_NOISE_THRESHOLD_KM:
            c8a_km_retreats.append({
                "old_km": old_km,
                "new_km": new_km,
                "delta": new_km - old_km,
                "observed_at": str(e["observed_at"]),
            })

    return {
        "vehicle_ulid": vehicle["vehicle_ulid"],
        "entity_ulid": vehicle.get("entity_ulid"),
        "c1_days": c1_days,
        "c1_suppressed": c1_suppressed,
        "c1_suppression_reason": c1_reason,
        "c3_price_drops": c3_price_drops,
        "c3_price_increases": c3_price_increases,
        "c4_pct_drop": c4_pct_drop,
        "c8a_km_retreats": c8a_km_retreats,
    }


# ---------------------------------------------------------------------------
# compute_chain — C2, C6, C7 across a verified lifetime chain (F1's edges).
# Absent/None whenever the chain isn't verified (single episode, no edges) —
# honest degradation, never an invented value.
# ---------------------------------------------------------------------------


def compute_chain(episodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    """episodes: list of compute_episode() outputs (or the minimal shape used
    in unit tests: vehicle_ulid/entity_ulid/c1_days/c1_suppressed).
    edges: F1's lifetime_link rows for this chain: {vehicle_ulid_from, vehicle_ulid_to, ...}.
    """
    c7_episode_count = len(episodes)
    chain_verified = len(edges) > 0

    c2_total_days: int | None
    if not chain_verified:
        c2_total_days = None
    elif any(ep.get("c1_suppressed") for ep in episodes):
        c2_total_days = None
    else:
        c2_total_days = sum(ep["c1_days"] for ep in episodes if ep["c1_days"] is not None)

    c6_dealer_count: int | None = (
        len({ep["entity_ulid"] for ep in episodes if ep.get("entity_ulid")}) if chain_verified else None
    )

    c7_rebotado = bool(
        chain_verified
        and c7_episode_count >= C9_AVISOS_REBOTADO_EPISODES
        and (c6_dealer_count or 0) >= C9_AVISOS_REBOTADO_EPISODES
    )

    return {
        "chain_verified": chain_verified,
        "c2_total_days": c2_total_days,
        "c6_dealer_count": c6_dealer_count,
        "c7_episode_count": c7_episode_count,
        "c7_rebotado": c7_rebotado,
    }


# ---------------------------------------------------------------------------
# compute_semaforo — C9, taxative closed-list 3-state traffic light (DGT
# Informe Reducido pattern). Never a verdict without at least one named cause.
# ---------------------------------------------------------------------------


def compute_semaforo(episode: dict[str, Any], chain: dict[str, Any]) -> dict[str, Any]:
    triggers: list[str] = []

    # "Con señales fuertes" — checked first; a strong signal always wins.
    if episode.get("c8a_km_retreats"):
        triggers.append("km_retreat_detected")
    if chain.get("c8b_km_retreats"):
        triggers.append("km_retreat_detected_inter_episode")
    if (chain.get("c7_episode_count") or 0) >= C9_FUERTES_REBOTADO_EPISODES:
        triggers.append(f"episodes>={C9_FUERTES_REBOTADO_EPISODES}")
    if (chain.get("c6_dealer_count") or 0) >= C9_FUERTES_DEALER_COUNT:
        triggers.append(f"dealers>={C9_FUERTES_DEALER_COUNT}")

    if triggers:
        return {"label": "con_senales_fuertes", "triggers": triggers}

    # "Con avisos".
    if (episode.get("c3_price_drops") or 0) >= C9_AVISOS_PRICE_DROPS:
        triggers.append(f"price_drops>={C9_AVISOS_PRICE_DROPS}")
    if (episode.get("c1_days") or 0) > C9_AVISOS_DAYS_ON_MARKET:
        triggers.append(f"days_on_market>{C9_AVISOS_DAYS_ON_MARKET}")
    if chain.get("c7_episode_count") == C9_AVISOS_REBOTADO_EPISODES and chain.get("c7_rebotado"):
        triggers.append(f"episodes=={C9_AVISOS_REBOTADO_EPISODES}")

    if triggers:
        return {"label": "con_avisos", "triggers": triggers}

    return {"label": "sin_senales", "triggers": []}


# ---------------------------------------------------------------------------
# freshness_label — C10.
# ---------------------------------------------------------------------------


def freshness_label(last_seen: datetime.datetime, now: datetime.datetime) -> str:
    delta = now - last_seen
    hours = delta.total_seconds() / 3600
    if hours < 24:
        n = max(1, int(hours))
        return f"visto hace {n} hora{'s' if n != 1 else ''}"
    days = int(hours / 24)
    return f"visto hace {days} día{'s' if days != 1 else ''}"

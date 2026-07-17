"""
tests/test_lifetime_aggregates.py
Unit tests for services/api/lifetime_aggregates.py — 02-history-reports F2
("Vida en mercado" aggregates C1-C10, plans/cardeep-omni/02-history-reports.md §4).

Pure logic, zero DB/FastAPI imports — mirrors services/api/stats.py's convention
of keeping computation testable without a live connection.

Covers:
  - C1 days-on-market with the §7 dual-path suppression (event stream vs
    vehicle.first_seen/last_seen divergence > 24h -> suppressed + alert reason)
  - C3/C4 price drops + cumulative percentage (increases counted, never hidden)
  - C8a intra-listing km retreat (>1000km anti-noise threshold, matches
    link_lifetimes.py's KM_NOISE_THRESHOLD_KM)
  - C2/C6/C7 chain aggregates (total days, distinct dealers, episode count,
    "rebotado" badge >= 2 episodes / >= 2 dealers)
  - C9 taxative 3-state semaforo (closed trigger list, never a verdict with no cause)
  - C10 freshness label
"""
from __future__ import annotations

import datetime

from services.api.lifetime_aggregates import (
    compute_chain,
    compute_episode,
    compute_semaforo,
    freshness_label,
)

_BASE = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)


def _dt(days: float) -> datetime.datetime:
    return _BASE + datetime.timedelta(days=days)


def _event(event_type: str, old_value: dict | None, new_value: dict | None, observed_at) -> dict:
    return {"event_type": event_type, "old_value": old_value, "new_value": new_value, "observed_at": observed_at}


def _vehicle(
    vehicle_ulid: str = "V1",
    entity_ulid: str = "E1",
    status: str = "available",
    first_seen=None,
    last_seen=None,
) -> dict:
    return {
        "vehicle_ulid": vehicle_ulid,
        "entity_ulid": entity_ulid,
        "status": status,
        "first_seen": first_seen or _dt(0),
        "last_seen": last_seen or _dt(0),
    }


# ---------------------------------------------------------------------------
# compute_episode — C1, C3, C4, C8a
# ---------------------------------------------------------------------------


class TestC1DaysOnMarket:
    def test_gone_vehicle_uses_new_to_gone_span(self) -> None:
        v = _vehicle(status="gone", first_seen=_dt(0), last_seen=_dt(45))
        events = [
            _event("NEW", None, {"price": 10000}, _dt(0)),
            _event("GONE", None, None, _dt(45)),
        ]
        ep = compute_episode(v, events, now=_dt(100))
        assert ep["c1_days"] == 45
        assert ep["c1_suppressed"] is False

    def test_available_vehicle_uses_now(self) -> None:
        v = _vehicle(status="available", first_seen=_dt(0), last_seen=_dt(10))
        events = [_event("NEW", None, {"price": 10000}, _dt(0))]
        ep = compute_episode(v, events, now=_dt(30))
        assert ep["c1_days"] == 30

    def test_dual_path_divergence_suppresses_c1(self) -> None:
        # vehicle.first_seen/last_seen diverges from the event stream by > 24h
        # (§7: two independent paths must agree within 24h or the datum is
        # suppressed and an alert is raised, never silently shown).
        v = _vehicle(status="gone", first_seen=_dt(0), last_seen=_dt(45))
        events = [
            _event("NEW", None, {"price": 10000}, _dt(2)),  # 2 days off from vehicle.first_seen
            _event("GONE", None, None, _dt(45)),
        ]
        ep = compute_episode(v, events, now=_dt(100))
        assert ep["c1_days"] is None
        assert ep["c1_suppressed"] is True
        assert "divergence" in ep["c1_suppression_reason"]

    def test_small_divergence_within_24h_is_not_suppressed(self) -> None:
        v = _vehicle(status="gone", first_seen=_dt(0), last_seen=_dt(45))
        events = [
            _event("NEW", None, {"price": 10000}, _dt(0.5)),  # 12h off, within tolerance
            _event("GONE", None, None, _dt(45)),
        ]
        ep = compute_episode(v, events, now=_dt(100))
        assert ep["c1_suppressed"] is False

    def test_no_events_suppresses_c1(self) -> None:
        v = _vehicle(status="available", first_seen=_dt(0), last_seen=_dt(0))
        ep = compute_episode(v, events=[], now=_dt(30))
        assert ep["c1_days"] is None
        assert ep["c1_suppressed"] is True


class TestC3C4PriceChanges:
    def test_counts_drops_and_increases_separately(self) -> None:
        v = _vehicle(status="available")
        events = [
            _event("NEW", None, {"price": 20000}, _dt(0)),
            _event("PRICE_CHANGE", {"price": 20000}, {"price": 19000}, _dt(5)),
            _event("PRICE_CHANGE", {"price": 19000}, {"price": 19500}, _dt(10)),  # increase
            _event("PRICE_CHANGE", {"price": 19500}, {"price": 18000}, _dt(15)),
        ]
        ep = compute_episode(v, events, now=_dt(20))
        assert ep["c3_price_drops"] == 2
        assert ep["c3_price_increases"] == 1

    def test_c4_percentage_from_new_event_price(self) -> None:
        v = _vehicle(status="available")
        events = [
            _event("NEW", None, {"price": 20000}, _dt(0)),
            _event("PRICE_CHANGE", {"price": 20000}, {"price": 18000}, _dt(5)),
        ]
        ep = compute_episode(v, events, now=_dt(20))
        assert ep["c4_pct_drop"] == 10.0

    def test_c4_falls_back_to_first_price_change_old_value_when_new_has_no_price(self) -> None:
        v = _vehicle(status="available")
        events = [
            _event("NEW", None, {}, _dt(0)),  # NEW recorded no price
            _event("PRICE_CHANGE", {"price": 20000}, {"price": 19000}, _dt(5)),
            _event("PRICE_CHANGE", {"price": 19000}, {"price": 18000}, _dt(10)),
        ]
        ep = compute_episode(v, events, now=_dt(20))
        assert ep["c4_pct_drop"] == 10.0

    def test_no_price_data_leaves_c4_none(self) -> None:
        v = _vehicle(status="available")
        events = [_event("NEW", None, {}, _dt(0))]
        ep = compute_episode(v, events, now=_dt(20))
        assert ep["c4_pct_drop"] is None


class TestC8aIntraListingKmRetreat:
    def test_large_km_decrease_flagged(self) -> None:
        v = _vehicle(status="available")
        events = [
            _event("NEW", None, {"km": 50000}, _dt(0)),
            _event("KM_CHANGE", {"km": 50000}, {"km": 48000}, _dt(5)),
        ]
        ep = compute_episode(v, events, now=_dt(20))
        assert len(ep["c8a_km_retreats"]) == 1
        assert ep["c8a_km_retreats"][0]["old_km"] == 50000
        assert ep["c8a_km_retreats"][0]["new_km"] == 48000

    def test_small_km_decrease_within_noise_not_flagged(self) -> None:
        v = _vehicle(status="available")
        events = [
            _event("NEW", None, {"km": 50000}, _dt(0)),
            _event("KM_CHANGE", {"km": 50000}, {"km": 49500}, _dt(5)),
        ]
        ep = compute_episode(v, events, now=_dt(20))
        assert ep["c8a_km_retreats"] == []

    def test_km_increase_not_flagged(self) -> None:
        v = _vehicle(status="available")
        events = [
            _event("NEW", None, {"km": 50000}, _dt(0)),
            _event("KM_CHANGE", {"km": 50000}, {"km": 55000}, _dt(5)),
        ]
        ep = compute_episode(v, events, now=_dt(20))
        assert ep["c8a_km_retreats"] == []


# ---------------------------------------------------------------------------
# compute_chain — C2, C6, C7
# ---------------------------------------------------------------------------


class TestComputeChain:
    def test_unverified_chain_has_none_aggregates(self) -> None:
        chain = compute_chain(episodes=[{"c1_days": 30, "c1_suppressed": False, "vehicle_ulid": "V1", "entity_ulid": "E1"}], edges=[])
        assert chain["c2_total_days"] is None
        assert chain["c6_dealer_count"] is None
        assert chain["c7_episode_count"] == 1
        assert chain["c7_rebotado"] is False

    def test_two_episode_chain_sums_days_and_counts_dealers(self) -> None:
        episodes = [
            {"vehicle_ulid": "A", "entity_ulid": "E1", "c1_days": 30, "c1_suppressed": False},
            {"vehicle_ulid": "B", "entity_ulid": "E2", "c1_days": 20, "c1_suppressed": False},
        ]
        edges = [{"vehicle_ulid_from": "A", "vehicle_ulid_to": "B"}]
        chain = compute_chain(episodes, edges)
        assert chain["c2_total_days"] == 50
        assert chain["c6_dealer_count"] == 2
        assert chain["c7_episode_count"] == 2

    def test_rebotado_badge_requires_two_episodes_and_two_dealers(self) -> None:
        episodes = [
            {"vehicle_ulid": "A", "entity_ulid": "E1", "c1_days": 10, "c1_suppressed": False},
            {"vehicle_ulid": "B", "entity_ulid": "E2", "c1_days": 10, "c1_suppressed": False},
        ]
        edges = [{"vehicle_ulid_from": "A", "vehicle_ulid_to": "B"}]
        chain = compute_chain(episodes, edges)
        assert chain["c7_rebotado"] is True

    def test_same_dealer_relist_is_not_rebotado(self) -> None:
        episodes = [
            {"vehicle_ulid": "A", "entity_ulid": "E1", "c1_days": 10, "c1_suppressed": False},
            {"vehicle_ulid": "B", "entity_ulid": "E1", "c1_days": 10, "c1_suppressed": False},
        ]
        edges = [{"vehicle_ulid_from": "A", "vehicle_ulid_to": "B"}]
        chain = compute_chain(episodes, edges)
        assert chain["c7_rebotado"] is False

    def test_suppressed_episode_suppresses_c2_total(self) -> None:
        episodes = [
            {"vehicle_ulid": "A", "entity_ulid": "E1", "c1_days": None, "c1_suppressed": True},
            {"vehicle_ulid": "B", "entity_ulid": "E2", "c1_days": 20, "c1_suppressed": False},
        ]
        edges = [{"vehicle_ulid_from": "A", "vehicle_ulid_to": "B"}]
        chain = compute_chain(episodes, edges)
        assert chain["c2_total_days"] is None


# ---------------------------------------------------------------------------
# compute_semaforo — C9, taxative closed list
# ---------------------------------------------------------------------------


class TestSemaforo:
    def test_no_signals(self) -> None:
        episode = {"c3_price_drops": 0, "c1_days": 10, "c8a_km_retreats": []}
        chain = {"c7_episode_count": 1, "c7_rebotado": False, "c6_dealer_count": None, "c8b_km_retreats": []}
        s = compute_semaforo(episode, chain)
        assert s["label"] == "sin_senales"
        assert s["triggers"] == []

    def test_avisos_from_price_drops(self) -> None:
        episode = {"c3_price_drops": 3, "c1_days": 10, "c8a_km_retreats": []}
        chain = {"c7_episode_count": 1, "c7_rebotado": False, "c6_dealer_count": None, "c8b_km_retreats": []}
        s = compute_semaforo(episode, chain)
        assert s["label"] == "con_avisos"
        assert "price_drops>=3" in s["triggers"]

    def test_avisos_from_long_days_on_market(self) -> None:
        episode = {"c3_price_drops": 0, "c1_days": 95, "c8a_km_retreats": []}
        chain = {"c7_episode_count": 1, "c7_rebotado": False, "c6_dealer_count": None, "c8b_km_retreats": []}
        s = compute_semaforo(episode, chain)
        assert s["label"] == "con_avisos"

    def test_senales_fuertes_from_km_retreat(self) -> None:
        episode = {"c3_price_drops": 0, "c1_days": 10, "c8a_km_retreats": [{"old_km": 1, "new_km": 2}]}
        chain = {"c7_episode_count": 1, "c7_rebotado": False, "c6_dealer_count": None, "c8b_km_retreats": []}
        s = compute_semaforo(episode, chain)
        assert s["label"] == "con_senales_fuertes"

    def test_senales_fuertes_from_three_dealers(self) -> None:
        episode = {"c3_price_drops": 0, "c1_days": 10, "c8a_km_retreats": []}
        chain = {"c7_episode_count": 3, "c7_rebotado": True, "c6_dealer_count": 3, "c8b_km_retreats": []}
        s = compute_semaforo(episode, chain)
        assert s["label"] == "con_senales_fuertes"

    def test_strong_signal_always_wins_over_avisos(self) -> None:
        episode = {"c3_price_drops": 3, "c1_days": 100, "c8a_km_retreats": [{"old_km": 1, "new_km": 2}]}
        chain = {"c7_episode_count": 1, "c7_rebotado": False, "c6_dealer_count": None, "c8b_km_retreats": []}
        s = compute_semaforo(episode, chain)
        assert s["label"] == "con_senales_fuertes"

    def test_triggers_never_empty_when_not_sin_senales(self) -> None:
        # "nunca un veredicto sin causas" — every non-'sin_senales' label carries
        # at least one named trigger.
        episode = {"c3_price_drops": 3, "c1_days": 10, "c8a_km_retreats": []}
        chain = {"c7_episode_count": 1, "c7_rebotado": False, "c6_dealer_count": None, "c8b_km_retreats": []}
        s = compute_semaforo(episode, chain)
        assert len(s["triggers"]) > 0


class TestFreshnessLabel:
    def test_hours_ago(self) -> None:
        label = freshness_label(_dt(0), now=_BASE + datetime.timedelta(hours=5))
        assert "hora" in label

    def test_days_ago(self) -> None:
        label = freshness_label(_dt(0), now=_dt(3))
        assert "día" in label

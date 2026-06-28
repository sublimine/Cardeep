"""Country-autopilot campaign gate registry — GASTO / PROD / LEGAL (Phase E, the spine).

THE DOCTRINE (plans/country-autopilot/01-ARCHITECTURE.md, "Las PUERTAS" + "LA FRONTERA HONESTA"):
a campaign gate **PARKS** — it returns a :data:`GateStatus.GATED` / PENDIENTE-OWNER result WITHOUT
raising and WITHOUT stopping the loop. A closed gate marks its item PENDING-OWNER; the orchestrator
records that and proceeds with the NEXT country (the never-stop doctrine). This is the
*aparca-no-detiene* frontier — the deliberate opposite of ``config_guard``'s fail-closed RAISE.

The three irreducible gates and what each REUSES:
  * **GASTO** (€>0) — elevates ``discover_schedule._gated`` / ``requires_env`` (the "AUTO-run is
    gated when a required env var is absent" primitive). An action that costs money needs an owner
    to unlock the budget via env (:data:`BUDGET_ENV`); absent -> PARK. Today every route is €0, so
    the gate is OPEN by default — current behaviour preserved.
  * **PROD** — reuses ``pipeline.config_guard``. A live :5433 / prod-cutover write is structurally
    the owner's call (THE HONEST FRONTIER). The gate runs ``config_guard.require_prod_secrets`` and
    converts its fail-closed RAISE into a GATED PARK, so the loop never crashes on a prod route.
    Build + dry-run (:5434) is auto-approved -> OPEN.
  * **LEGAL/ToS** — has NO code primitive (architecture: "sin primitivo código -> a construir como
    gate de campaña"). It parks until the KNOW_COUNTRY legal/ToS dossier is owner-signed
    (``CampaignAction.legal_cleared``).

This module is PURE (stdlib + config_guard only): no DB, no network. Persistence of the
PENDIENTE-OWNER mark belongs to the orchestrator (a later piece); a gate only computes the pure
decision. That keeps the frontier trivially testable and the loop un-stoppable by construction.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum

from pipeline import config_guard

#: Owner-set env var that unlocks a spend (€>0) route. Mirrors the ``requires_env`` primitive of
#: ``discover_schedule.DiscoveryJob`` — an AUTO route is gated until this is present.
BUDGET_ENV: str = "CARDEEP_BUDGET_AUTHORIZED"


class GateStatus(str, Enum):
    """A gate's two terminal outcomes — NEVER an exception.

    OPEN:  clear — the action may proceed (build / dry-run is auto-approved).
    GATED: parked, PENDIENTE-OWNER — the loop marks the item and carries on with the next country.
    """

    OPEN = "OPEN"
    GATED = "GATED"


@dataclass(frozen=True)
class GateResult:
    """One gate's verdict on one :class:`CampaignAction`. Immutable, pure data."""

    gate: str
    status: GateStatus
    reason: str | None = None

    @property
    def is_open(self) -> bool:
        return self.status is GateStatus.OPEN

    @property
    def is_gated(self) -> bool:
        return self.status is GateStatus.GATED

    @property
    def pending_owner(self) -> bool:
        """A GATED result IS the PENDIENTE-OWNER mark the loop records before moving on."""
        return self.status is GateStatus.GATED


@dataclass(frozen=True)
class CampaignAction:
    """The gate context: what the autopilot wants to do for a country, and its risk surface.

    Every field defaults to the SAFE / €0 / dry-run value, so a bare action crosses no gate.
    """

    country_code: str
    spend_eur: float = 0.0          # > 0 trips the GASTO gate
    targets_prod: bool = False      # a live :5433 / prod-cutover write trips the PROD gate
    dsn: str | None = None          # resolved DSN for the action (PROD gate validates via config_guard)
    legal_cleared: bool = False     # owner-signed legal/ToS dossier present -> clears the LEGAL gate


# ---------------------------------------------------------------------------
# Gates — each .check() is total: it ALWAYS returns a GateResult, never raises.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GastoGate:
    """€>0 spend gate. Elevates ``discover_schedule._gated`` / ``requires_env`` to campaign scope."""

    name: str = "GASTO"
    requires_env: tuple[str, ...] = (BUDGET_ENV,)

    def check(self, action: CampaignAction) -> GateResult:
        if action.spend_eur <= 0:
            # €0 route: nothing to gate (today's invariant — all routes are €0).
            return GateResult(self.name, GateStatus.OPEN)
        missing = self._gated()
        if missing is not None:
            return GateResult(
                self.name, GateStatus.GATED,
                f"spend €{action.spend_eur:g} needs owner budget authorization; "
                f"{missing} absent — PENDIENTE-OWNER",
            )
        return GateResult(self.name, GateStatus.OPEN)

    def _gated(self) -> str | None:
        """First required env var that is ABSENT, or None — mirror of discover_schedule._gated."""
        for var in self.requires_env:
            if not os.environ.get(var):
                return var
        return None


@dataclass(frozen=True)
class ProdGate:
    """Live-prod / cutover gate. Reuses config_guard and converts its RAISE into a PARK."""

    name: str = "PROD"
    require_api_key: bool = False

    def check(self, action: CampaignAction) -> GateResult:
        if not action.targets_prod:
            # Build + dry-run (:5434) is auto-approved.
            return GateResult(self.name, GateStatus.OPEN)
        # A live :5433 / prod-cutover is structurally the owner's call -> PARK. Reuse config_guard
        # to surface the precise fail-closed reason WITHOUT letting it stop the loop.
        reason = "live prod write / cutover is owner-structural — PENDIENTE-OWNER"
        try:
            dsns = ((action.dsn, "CARDEEP_DSN"),) if action.dsn else ()
            config_guard.require_prod_secrets(*dsns, require_api_key=self.require_api_key)
        except RuntimeError as exc:
            # config_guard fail-closed fired (it would STOP the world); convert to a PARK.
            reason = f"{reason}; config_guard fail-closed: {exc}"
        return GateResult(self.name, GateStatus.GATED, reason)


@dataclass(frozen=True)
class LegalGate:
    """Legal/ToS gate. No code primitive — parks until the owner signs the KNOW_COUNTRY dossier."""

    name: str = "LEGAL"

    def check(self, action: CampaignAction) -> GateResult:
        if action.legal_cleared:
            return GateResult(self.name, GateStatus.OPEN)
        return GateResult(
            self.name, GateStatus.GATED,
            "legal/ToS clearance not owner-signed (KNOW_COUNTRY dossier) — PENDIENTE-OWNER",
        )


#: The default campaign gate registry, evaluated for every action.
DEFAULT_GATES: tuple[object, ...] = (GastoGate(), ProdGate(), LegalGate())


# ---------------------------------------------------------------------------
# Registry evaluation — the frontier: this NEVER stops the loop.
# ---------------------------------------------------------------------------

def evaluate_gates(
    action: CampaignAction,
    gates: tuple[object, ...] = DEFAULT_GATES,
) -> tuple[GateResult, ...]:
    """Evaluate every gate against ``action``. ALWAYS returns; NEVER raises.

    Parked gates come back as :data:`GateStatus.GATED` results the orchestrator records as
    PENDIENTE-OWNER before moving to the next country. A gate's own ``.check`` is total, but we
    also defensively never let one gate's surprise abort the sweep — the loop must not stop.
    """
    results: list[GateResult] = []
    for gate in gates:
        try:
            results.append(gate.check(action))  # type: ignore[attr-defined]
        except Exception as exc:  # pragma: no cover - defense in depth; .check is total by contract
            results.append(GateResult(
                getattr(gate, "name", gate.__class__.__name__), GateStatus.GATED,
                f"gate raised unexpectedly — parked PENDIENTE-OWNER: {exc!r}",
            ))
    return tuple(results)


def parked(results: tuple[GateResult, ...]) -> tuple[GateResult, ...]:
    """The GATED (PENDIENTE-OWNER) subset of a gate sweep."""
    return tuple(r for r in results if r.is_gated)


def clear_to_proceed(results: tuple[GateResult, ...]) -> bool:
    """True iff EVERY gate is OPEN — the action may cross to a live/spend effect."""
    return all(r.is_open for r in results)

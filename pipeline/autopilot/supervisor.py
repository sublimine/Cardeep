"""Phase E3 — the SUPERVISA step of the country-autopilot loop: per-country health roll-up.

The loop (``plans/country-autopilot/01-ARCHITECTURE.md`` §E) ends EJECUTA → **SUPERVISA(per-país)**
→ SELLA. ``pipeline/ops/autopilot.py`` already gates EJECUTA on the proof view alone
(``_supervise_proof`` — ``v_country_proof_violations`` MUST be 0). This module is the FULL
supervisor: :func:`health_rollup` reads the country-aware served/observability surfaces and emits a
single :class:`CountryHealth` value object for ONE tenant — its OWN, isolated health.

Each country reads only its own slice, so a second tenant can NEVER perturb another's roll-up:

  * ``violations``        — ``v_country_proof_violations`` (mig 0057) rows whose cross-border cluster
                            INCLUDES this country. A cross-merge contaminates every country it
                            touches, so it must surface in each involved tenant's roll-up. MUST be 0.
  * ``servable_dealers``  — ``v_servable_dealer`` (mig 0058) scoped ``WHERE country_code = $cc``.
  * ``seal``              — ``v_exhaustiveness_seal`` (mig 0060) for the tenant: certificate strata,
                            how many are SEALED, and the grand-national headline's sealed flag +
                            ``coverage_lower`` (the weakest-link floor).
  * ``gestion_by_state``  — ``gestion_item`` (mig 0064) ledger histogram by ``state``, ``WHERE
                            country_code = $cc``.
  * ``sources``           — ``source_health`` (mig 0068) scoped to the tenant: total, ``healthy``
                            (status), and ``silent`` (the EXACT predicate the silence watchdog fires
                            on — reused 1:1 via :data:`SILENCE_MULTIPLIER`, no drift).

CONTRACT (mirrors ``pipeline/autopilot/state.py`` and ``run_campaign``): pure-async over an
``asyncpg`` connection; the CALLER owns the transaction boundary. :func:`health_rollup` only READS
(``count`` / ``GROUP BY`` over views + tables) — it writes nothing, commits nothing, and leaves zero
residue. ``run_campaign`` will call it as the SUPERVISA step after EJECUTA; this module only EXPOSES
the function — the wiring into ``pipeline/ops/autopilot.py`` is a later phase and is NOT done here.

ES byte-identical / no migration: every query is additive read-only SQL over surfaces that already
carry ``country_code``; with a single ES tenant ``health_rollup(conn, 'ES')`` simply describes the
whole census, exactly as today.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import asyncpg

# The silence predicate's single source of truth: a source is SILENT past this multiple of its
# cadence without a response. Imported (not re-defined) so the supervisor's "silent" is byte-for-byte
# what pipeline/ops/silence_watchdog.py fires on — they can never drift apart.
from pipeline.ops.silence_watchdog import SILENCE_MULTIPLIER

# ---------------------------------------------------------------------------
# The country-aware surfaces this supervisor reads (each with its migration of origin).
# ---------------------------------------------------------------------------
PROOF_VIEW: str = "v_country_proof_violations"      # mig 0057 — served-layer cross-country guard
SERVABLE_DEALER_VIEW: str = "v_servable_dealer"     # mig 0058 — the served dealer census
EXHAUSTIVENESS_SEAL_VIEW: str = "v_exhaustiveness_seal"  # mig 0060 — the MSE coverage certificate
GESTION_TABLE: str = "gestion_item"                 # mig 0064 — the managed-anomaly ledger
SOURCE_HEALTH_TABLE: str = "source_health"          # mig 0068 — the producer-health table

#: The source_health.status value that counts as a healthy producer (0004 CHECK vocabulary).
HEALTHY_STATUS: str = "healthy"


# ---------------------------------------------------------------------------
# The roll-up value objects (frozen — a roll-up is an immutable observation)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SealHealth:
    """The exhaustiveness CERTIFICATE posture for one tenant (``v_exhaustiveness_seal``, mig 0060)."""
    rows: int                                # certificate strata for this country (0 ⇒ no build yet)
    sealed_segments: int                     # strata with sealed = TRUE
    national_sealed: bool | None             # grand-national headline (province+segment NULL) sealed?
    national_coverage_lower: float | None    # its conservative coverage floor; None if no headline


@dataclass(frozen=True)
class SourceHealthRollup:
    """The producer-health posture for one tenant (``source_health``, mig 0068)."""
    total: int      # sources scoped to this country
    healthy: int    # status = 'healthy'
    silent: int     # past SILENCE_MULTIPLIER × cadence since the last event (the watchdog predicate)


@dataclass(frozen=True)
class CountryHealth:
    """The SUPERVISA roll-up for ONE country — its own, isolated health.

    ``contaminated`` is the single fail-closed signal the orchestrator reads after EJECUTA: any
    cross-country merge touching this tenant makes it True and the loop must NOT seal a lie.
    """
    country_code: str
    violations: int                       # v_country_proof_violations involving this country — MUST be 0
    servable_dealers: int                 # v_servable_dealer WHERE country_code
    seal: SealHealth
    gestion_by_state: Mapping[str, int]   # gestion_item state histogram WHERE country_code
    sources: SourceHealthRollup

    @property
    def contaminated(self) -> bool:
        """True iff a cross-country false-merge contaminates this tenant's served layer."""
        return self.violations > 0

    @property
    def gestion_total(self) -> int:
        """Total managed items for this tenant across every state."""
        return sum(self.gestion_by_state.values())


# ---------------------------------------------------------------------------
# Country-code normalization — the package's canonical CHAR(2) ISO normalizer (reused, not redefined)
# ---------------------------------------------------------------------------
from pipeline.autopilot.state import _normalize_cc  # noqa: E402  (single normalization rule for the package)


# ---------------------------------------------------------------------------
# The per-surface readers (each scoped to ONE tenant — the isolation guarantee)
# ---------------------------------------------------------------------------
async def _proof_violations(conn: asyncpg.Connection, cc: str) -> int:
    """Count served-layer cross-country clusters (mig 0057) that INCLUDE this tenant.

    The guard view returns every served cluster spanning >1 country. A contaminated cluster harms
    EVERY country in it, so per-tenant supervision counts the rows whose ``countries`` array contains
    ``cc``. For a clean tenant this is 0 (the SUPERVISA invariant)."""
    return int(await conn.fetchval(
        f"SELECT count(*) FROM {PROOF_VIEW} WHERE $1 = ANY(countries::text[])", cc))


async def _servable_dealers(conn: asyncpg.Connection, cc: str) -> int:
    """Count the served dealer census (mig 0058) scoped to this tenant."""
    return int(await conn.fetchval(
        f"SELECT count(*) FROM {SERVABLE_DEALER_VIEW} WHERE country_code = $1", cc))


async def _seal_health(conn: asyncpg.Connection, cc: str) -> SealHealth:
    """Read the exhaustiveness certificate posture (mig 0060) for this tenant in one pass.

    ``count(*) FILTER`` never returns NULL (0 when empty); ``bool_or``/``max`` FILTERed to the
    grand-national headline return NULL when the tenant has no national row yet → exposed as None."""
    row = await conn.fetchrow(
        f"""
        SELECT
            count(*)                                                AS rows,
            count(*) FILTER (WHERE sealed)                          AS sealed_segments,
            bool_or(sealed) FILTER (
                WHERE province_code IS NULL AND segment IS NULL)    AS national_sealed,
            max(coverage_lower) FILTER (
                WHERE province_code IS NULL AND segment IS NULL)    AS national_coverage_lower
        FROM {EXHAUSTIVENESS_SEAL_VIEW}
        WHERE country_code = $1
        """,
        cc,
    )
    cov = row["national_coverage_lower"]
    return SealHealth(
        rows=int(row["rows"]),
        sealed_segments=int(row["sealed_segments"]),
        national_sealed=row["national_sealed"],
        national_coverage_lower=float(cov) if cov is not None else None,
    )


async def _gestion_by_state(conn: asyncpg.Connection, cc: str) -> dict[str, int]:
    """Histogram the managed-anomaly ledger (mig 0064) by ``state`` for this tenant."""
    rows = await conn.fetch(
        f"SELECT state, count(*) AS n FROM {GESTION_TABLE} "
        f"WHERE country_code = $1 GROUP BY state",
        cc,
    )
    return {r["state"]: int(r["n"]) for r in rows}


async def _source_health(conn: asyncpg.Connection, cc: str) -> SourceHealthRollup:
    """Roll up producer health (mig 0068) for this tenant: total, healthy, and silent.

    ``silent`` reuses the silence watchdog's EXACT predicate (``now() - last_event >
    SILENCE_MULTIPLIER × harvest_interval_hours``), so a source the supervisor calls silent is the
    same one the watchdog would alert on — never a second, divergent definition."""
    row = await conn.fetchrow(
        f"""
        SELECT
            count(*)                                AS total,
            count(*) FILTER (WHERE status = $2)     AS healthy,
            count(*) FILTER (
                WHERE now() - COALESCE(last_ok, last_fail, '1970-01-01'::timestamptz)
                      > $3::int * harvest_interval_hours * interval '1 hour'
            )                                       AS silent
        FROM {SOURCE_HEALTH_TABLE}
        WHERE country_code = $1
        """,
        cc, HEALTHY_STATUS, SILENCE_MULTIPLIER,
    )
    return SourceHealthRollup(
        total=int(row["total"]),
        healthy=int(row["healthy"]),
        silent=int(row["silent"]),
    )


# ---------------------------------------------------------------------------
# The SUPERVISA step
# ---------------------------------------------------------------------------
async def health_rollup(conn: asyncpg.Connection, country_code: str) -> CountryHealth:
    """SUPERVISA: emit the isolated health roll-up for ONE tenant.

    Reads the five country-aware surfaces (0057/0058/0060/0064/0068), each scoped to
    ``country_code``, and returns a single :class:`CountryHealth`. Pure read — writes nothing,
    commits nothing; the caller owns the transaction boundary (``run_campaign`` calls this as the
    SUPERVISA step after EJECUTA). Two tenants computed on the same connection never share a figure:
    every query filters on the tenant, so XX's roll-up is byte-isolated from ES's.

    Raises ``ValueError`` if ``country_code`` is not a 2-char ISO code (boundary validation)."""
    cc = _normalize_cc(country_code)
    return CountryHealth(
        country_code=cc,
        violations=await _proof_violations(conn, cc),
        servable_dealers=await _servable_dealers(conn, cc),
        seal=await _seal_health(conn, cc),
        gestion_by_state=await _gestion_by_state(conn, cc),
        sources=await _source_health(conn, cc),
    )


__all__ = [
    "PROOF_VIEW",
    "SERVABLE_DEALER_VIEW",
    "EXHAUSTIVENESS_SEAL_VIEW",
    "GESTION_TABLE",
    "SOURCE_HEALTH_TABLE",
    "HEALTHY_STATUS",
    "SealHealth",
    "SourceHealthRollup",
    "CountryHealth",
    "health_rollup",
]

"""V4 Gestionador — Detectors (V4-GESTIONADOR.md §3).

Each detector is a pure async function that:
  1. Queries the live DB (zero external calls, zero cost).
  2. Returns a list of AnomalyResult dataclasses.
  3. Is idempotent: re-running produces the same result set; the UPSERT
     in route.py ensures no duplicate gestion_items.

Detector status:
  3.1 count_inflation      LIVE — reads verification_verdict entity_inventory
  3.2 silent_cap           LIVE — reads verification_verdict (harvested=1000 & D>H)
  3.3 field_loss           LIVE — null-rate z-test against global baseline
  3.4 staleness            LIVE — entity.last_seen vs TTL per kind
  3.5 fabrication          LIVE — out-of-band values + distinct-collapse check
  3.6 coverage_gap         LIVE — covered count vs anchor floors
  3.7 price_trap           LIVE — model-aware cohort robust-z (median+MAD), two-sided QUARANTINE
  3.8 geo_resolution_drift STUB — requires sentinel placement tracking (no data yet)
  3.9 classifier_drift     STUB — requires golden-set evaluation harness (no data yet)

All thresholds are module-level constants (never magic numbers in logic).
"""
from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import asyncpg

from pipeline.gestionador.cohorts import (
    COHORT_MAD_FLOOR,
    COHORT_MIN_TIER_A,
    COHORT_MIN_TIER_B,
    cohort_ctes_sql,
)

# ---------------------------------------------------------------------------
# Configuration constants (V4 §3 — "thresholds live in config, not code")
# ---------------------------------------------------------------------------

# 3.1 count_inflation
TAU_COUNT = 0.02          # 2% — leaves 20x headroom over honest sub-0.1% drift
TAU_GHOST = 0.02          # 2% — L > D by more than 2% = stale ghosts

# 3.2 silent_cap
SILENT_CAP_MAX_PAGES = 50
SILENT_CAP_PAGE_SIZE = 20
SILENT_CAP_MAX_ROWS = SILENT_CAP_MAX_PAGES * SILENT_CAP_PAGE_SIZE  # 1000
SILENT_CAP_ROUND_CEILINGS = {500, 1000, 2000, 5000}

# 3.3 field_loss
FIELD_LOSS_Z_CRIT = 3.0         # ~0.13% one-sided false-alarm rate
FIELD_LOSS_ABS_FLOOR = 0.05     # ignore statistically-significant but tiny drifts
FIELD_LOSS_HARD_THRESH = 0.30   # hard-required fields: fire if p1 > 30% regardless of z
FIELD_LOSS_PHOTO_THRESH = 0.10  # photo_url: abs floor 10%

# 3.4 staleness — TTL in seconds per kind (V4 §3.4, MASTER_PLAN C-11)
STALENESS_TTL: dict[str, int] = {
    "compraventa":          3 * 86400,
    "concesionario_oficial": 3 * 86400,
    "plataforma":           1 * 86400,
    "garaje":               7 * 86400,
    "desguace":            30 * 86400,
    "particular":           7 * 86400,
    "rent_a_car_vo":        7 * 86400,
    "subasta":              3 * 86400,
    "importador":           7 * 86400,
    "oem_vo_portal":        3 * 86400,
    "_entity":             90 * 86400,   # entity existence re-confirmation
}
STALENESS_RATIO_WARN = 1.0
STALENESS_RATIO_CRIT = 3.0
STALENESS_STORM_THRESHOLD = 200  # suppress per-entity items if >200 for a source

# 3.5 fabrication
FAB_PRICE_FLOOR = 0
FAB_PRICE_CEIL = 5_000_000
FAB_YEAR_FLOOR = 1900
FAB_YEAR_CEIL = 2027          # next year for pre-reg
FAB_KM_CEIL = 1_000_000       # tighter than producer's 5M sanity cap
FAB_COLLAPSE_KAPPA = 1.10     # >10% of distinct sources fused
FAB_CV_DEGENERATE = 0.01      # coefficient of variation < 1% = degenerate

# 3.6 coverage_gap — anchor floors (V4 §1 VERIFIED sources)
# Keyed by (country_code, kind): coverage floors are country-specific national registries (the
# values below are the Spanish DGT / FACONAUTO / Páginas Amarillas figures). A second country
# onboards by ADDING its own ('XX', kind) rows; coverage_gap then evaluates each country against its
# OWN floor and dedupes per country. ES is byte-identical (same four floors, and in the single-tenant
# census the per-(country,kind) covered count equals the old per-kind count).
COVERAGE_ANCHORS: dict[tuple[str, str], int] = {
    ("ES", "desguace"):              1_292,   # DGT official CAT registry (exact)
    ("ES", "concesionario_oficial"): 2_018,   # FACONAUTO franchised
    ("ES", "compraventa"):           1_662,   # Paginas Amarillas floor
    ("ES", "garaje"):               29_955,   # Paginas Amarillas
}
COVERAGE_RELGAP_INFO = 0.10
COVERAGE_RELGAP_WARN = 0.40

# 3.7 price_trap — model-aware cohort robust-z (median + MAD on ln price).
# Low-side deposit floor per kind: a flagged-LOW car at/below this absolute price has a
# deposit/finance/placeholder shape -> 'critical'; above it (still a cohort outlier) -> 'warning'.
PRICE_TRAP_FLOOR: dict[str, float] = {
    "compraventa":           300.0,
    "concesionario_oficial": 300.0,
    "garaje":                300.0,
    "plataforma":            300.0,
    "particular":            300.0,
    "rent_a_car_vo":         300.0,
    "importador":            300.0,
    "oem_vo_portal":         300.0,
    "subasta":               300.0,
}
PRICE_TRAP_COHORT_Z = 6.0              # robust-z threshold, both sides (|z| >= 6)
# Cohort-size/MAD guards factored to pipeline/gestionador/cohorts.py (04-arbitrage.md F1:
# shared with the deal-score primitive, 00-MASTER.md C-1/C-12 — one cohort implementation).
# Aliased here under the original names so no external reference breaks.
PRICE_TRAP_COHORT_MIN_A = COHORT_MIN_TIER_A    # min cohort size, Tier-A (make, model, year)
PRICE_TRAP_COHORT_MIN_B = COHORT_MIN_TIER_B    # min cohort size, Tier-B fallback (make, year; model NULL)
PRICE_TRAP_MAD_FLOOR = COHORT_MAD_FLOOR        # skip near-degenerate cohorts (log-price MAD < 5%) — Law I
PRICE_TRAP_HIGH_ABS_FLOOR = 150_000.0  # HIGH flag ALSO requires price >= this (Law I co-guard)
PRICE_TRAP_LOW_MEDIAN_FRAC = 0.25      # LOW flag ALSO requires price < 0.25 * cohort median (Law I)
PRICE_TRAP_MAX_ROWS = 5000             # hard cap on flags per run


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class AnomalyResult:
    """One detection hit — maps 1:1 to a gestion_item row."""
    detector: str
    subject_type: str
    subject_key: str
    severity: str               # 'info' | 'warning' | 'critical'
    score: float                # 0..1 normalised anomaly score
    measured: dict[str, Any]
    baseline: dict[str, Any] | None
    lane: str                   # AUTO_FIX | RESEARCH | QUARANTINE | ESCALATE_*
    quarantines: bool
    dedupe_key: str             # detector|subject_key|bucket — idempotency
    country_code: str = "ES"    # tenant scope. Threaded into the dedupe_key of BY-KIND aggregated
                                # detectors (staleness storm, coverage_gap) so an ES and a DE alert of
                                # the same kind/bucket do NOT collapse, and written to
                                # gestion_item.country_code (migration 0064). Defaults 'ES' so every
                                # per-subject detector (cdp_code/vehicle_ulid keyed, already
                                # country-safe) stays byte-identical in the single-tenant census.


def _rel(a: float, b: float) -> float:
    """Two-sided relative divergence: |a-b| / max(a, b, 1)."""
    return abs(a - b) / max(a, b, 1.0)


def _z_two_prop(x0: int, n0: int, x1: int, n1: int) -> float:
    """One-sided z-test for null-rate increase (p1 > p0)."""
    if n0 <= 0 or n1 <= 0:
        return 0.0
    p0 = x0 / n0
    p1 = x1 / n1
    if p1 <= p0:
        return 0.0
    p_pool = (x0 + x1) / (n0 + n1)
    denom = math.sqrt(p_pool * (1 - p_pool) * (1 / n0 + 1 / n1))
    if denom == 0:
        return 0.0
    return (p1 - p0) / denom


def _daily_bucket(conn_or_today: str | None = None) -> str:
    """ISO date bucket for daily detectors."""
    from datetime import date
    return date.today().isoformat()


def _as_evidence_dict(raw: Any) -> dict | None:
    """Decode a verification_verdict.independent_values cell into an evidence dict.

    asyncpg returns JSONB as a str (no codec registered) -> json.loads; unit-test
    mocks pass a dict directly. The column is a generic JSONB that, for some
    verdicts, holds a JSON array (or scalar) rather than an object — a payload that
    carries no source_declared/harvested/db_available evidence. Any non-object payload
    returns None so the caller skips it exactly like incomplete evidence, instead of
    crashing on ``list.get`` (the production "'list' object has no attribute 'get'").
    """
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (ValueError, TypeError):
            return None
    return dict(raw) if isinstance(raw, Mapping) else None


def _row_country(row) -> str:
    """The row's country_code (asyncpg Record OR dict), else the 'ES' default.

    Per-subject detectors stamp this so a DE subject's gestion_item is tagged DE; a legacy row or a
    mock without the column defaults to 'ES' — byte-identical for the single-tenant census."""
    try:
        c = row["country_code"]
    except (KeyError, IndexError, TypeError):
        return "ES"
    return c or "ES"


# ---------------------------------------------------------------------------
# 3.1 — count_inflation
# ---------------------------------------------------------------------------

async def detect_count_inflation(conn: asyncpg.Connection) -> list[AnomalyResult]:
    """Detect divergence between source-declared (D), harvested (H), and
    landed (L) counts. Reads evidence already stored in verification_verdict
    (independent_values JSONB) — never re-harvests.

    Fires when:
      g_DL > TAU_COUNT (2%) — declared vs landed divergence
      g_HL > 0             — harvested rows we parsed but never landed (critical)
    """
    sql = """
        SELECT DISTINCT ON (subject_key)
            subject_key,
            independent_values,
            verdict,
            primary_value::int AS primary_value
        FROM verification_verdict
        WHERE subject_type = 'entity_inventory'
        ORDER BY subject_key, created_at DESC
    """
    rows = await conn.fetch(sql)
    results: list[AnomalyResult] = []
    bucket = _daily_bucket()

    for row in rows:
        # independent_values is a generic JSONB: an object for entity_inventory verdicts,
        # but a JSON array/scalar for other shapes -> skip non-objects instead of crashing
        # on list.get (the prod "'list' object has no attribute 'get'" error).
        iv = _as_evidence_dict(row["independent_values"])
        if iv is None:
            continue

        d = iv.get("source_declared")
        h = iv.get("harvested")
        l_val = iv.get("db_available")

        # Skip if evidence is incomplete
        if d is None or h is None or l_val is None:
            continue

        d, h, l = float(d), float(h), float(l_val)
        g_dh = _rel(d, h)
        g_hl = _rel(h, l) if h > 0 else 0.0
        g_dl = _rel(d, l)

        subject_key = row["subject_key"]

        # Hard rule: any ingest loss (H parsed but L < H) → critical/AUTO_FIX.
        # This takes absolute priority: H>L means rows we parsed never landed.
        if h > l:
            results.append(AnomalyResult(
                detector="count_inflation",
                subject_type="entity",
                subject_key=subject_key,
                severity="critical",
                score=min(g_hl, 1.0),
                measured={"g_hl": round(g_hl, 4), "h": int(h), "l": int(l), "d": int(d)},
                baseline={"threshold_g_hl": 0, "rule": "ingest_loss_zero_tolerance"},
                lane="AUTO_FIX",
                quarantines=True,
                dedupe_key=f"count_inflation|{subject_key}|{bucket}",
            ))
        # Ghost surplus: DB has MORE than source declares by > TAU_GHOST.
        # Checked before the generic g_dl path because L>D has a different
        # direction (stale ghosts) and different remedy (GONE reconcile).
        elif l > d and _rel(l, d) > TAU_GHOST:
            g_ghost = _rel(l, d)
            results.append(AnomalyResult(
                detector="count_inflation",
                subject_type="entity",
                subject_key=subject_key,
                severity="warning",
                score=min(g_ghost, 1.0),
                measured={"g_dl": round(g_ghost, 4), "d": int(d), "l": int(l),
                          "sub": "ghost_surplus"},
                baseline={"tau_ghost": TAU_GHOST},
                lane="AUTO_FIX",
                quarantines=False,
                dedupe_key=f"count_inflation|{subject_key}|{bucket}",
            ))
        # Under-landed: g_DL > 20% (≥1 full page lost) → critical QUARANTINE.
        elif g_dl > 0.20:
            results.append(AnomalyResult(
                detector="count_inflation",
                subject_type="entity",
                subject_key=subject_key,
                severity="critical",
                score=min(g_dl, 1.0),
                measured={"g_dl": round(g_dl, 4), "d": int(d), "l": int(l)},
                baseline={"tau_count": TAU_COUNT},
                lane="QUARANTINE",
                quarantines=True,
                dedupe_key=f"count_inflation|{subject_key}|{bucket}",
            ))
        # Under-landed: TAU_COUNT < g_DL ≤ 20% → warning RESEARCH.
        elif g_dl > TAU_COUNT:
            results.append(AnomalyResult(
                detector="count_inflation",
                subject_type="entity",
                subject_key=subject_key,
                severity="warning",
                score=min(g_dl, 1.0),
                measured={"g_dl": round(g_dl, 4), "d": int(d), "l": int(l)},
                baseline={"tau_count": TAU_COUNT},
                lane="RESEARCH",
                quarantines=False,
                dedupe_key=f"count_inflation|{subject_key}|{bucket}",
            ))

    return results


# ---------------------------------------------------------------------------
# 3.2 — silent_cap
# ---------------------------------------------------------------------------

async def detect_silent_cap(conn: asyncpg.Connection) -> list[AnomalyResult]:
    """Detect top-N truncation: harvest looks complete but hit a page/provider cap.

    Signal: the latest entity_inventory verdict where harvested == 1000 (the
    AS24 max-pages*size ceiling) and source_declared > harvested.
    These are the entities in the live DB that hit the cap and were never
    flagged (the old quorum read fetched=harvested as fine).
    """
    sql = """
        SELECT DISTINCT ON (subject_key)
            subject_key,
            independent_values,
            created_at
        FROM verification_verdict
        WHERE subject_type = 'entity_inventory'
        ORDER BY subject_key, created_at DESC
    """
    rows = await conn.fetch(sql)
    results: list[AnomalyResult] = []
    bucket = _daily_bucket()

    for row in rows:
        iv = _as_evidence_dict(row["independent_values"])
        if iv is None:
            continue
        d = iv.get("source_declared")
        h = iv.get("harvested")
        if d is None or h is None:
            continue
        d, h = float(d), float(h)

        cap_hit = (h >= SILENT_CAP_MAX_ROWS) and (d > h)
        ceiling_hit = (int(h) in SILENT_CAP_ROUND_CEILINGS) and (d > h)

        if not (cap_hit or ceiling_hit):
            continue

        subject_key = row["subject_key"]
        sub = "page_budget_cap" if cap_hit else "provider_ceiling"
        results.append(AnomalyResult(
            detector="silent_cap",
            subject_type="entity",
            subject_key=subject_key,
            severity="critical",
            score=min(_rel(d, h), 1.0),
            measured={"h": int(h), "d": int(d), "sub": sub,
                      "max_rows": SILENT_CAP_MAX_ROWS},
            baseline={"max_pages": SILENT_CAP_MAX_PAGES,
                      "page_size": SILENT_CAP_PAGE_SIZE},
            lane="AUTO_FIX" if cap_hit else "RESEARCH",
            quarantines=True,
            dedupe_key=f"silent_cap|{subject_key}|{bucket}",
        ))

    return results


# ---------------------------------------------------------------------------
# 3.3 — field_loss
# ---------------------------------------------------------------------------

async def detect_field_loss(conn: asyncpg.Connection) -> list[AnomalyResult]:
    """Detect null-rate spikes in high-value fields vs the PER-COUNTRY global baseline.

    Two-proportion z-test (V4 §3.3) where the baseline is computed per country: an ES source's recent
    null rate must be judged against the ES null-rate, NEVER a pooled ES+DE one (a degenerate second
    tenant would otherwise mask or invent ES spikes). Each source is matched to ITS country's baseline.
    ES is byte-identical: the single-tenant census yields one baseline whose counts equal the old global
    figures (vehicle.entity_ulid is a NOT NULL FK, so the entity join drops nothing) and every source
    is ES, so the same spikes fire with the same dedupe_keys.
    """
    # Per-country global baseline null rates. entity carries country_code; vehicle derives it via the
    # NOT NULL entity_ulid FK, so the join cannot change the population for the single ES tenant.
    baseline_sql = """
        SELECT
            e.country_code,
            count(*)                                       AS total,
            count(*) FILTER (WHERE v.price IS NULL)        AS price_null,
            count(*) FILTER (WHERE v.year IS NULL)         AS year_null,
            count(*) FILTER (WHERE v.km IS NULL)           AS km_null,
            count(*) FILTER (WHERE v.photo_url IS NULL)    AS photo_url_null
        FROM vehicle v
        JOIN entity e ON e.entity_ulid = v.entity_ulid
        WHERE v.status = 'available'
        GROUP BY e.country_code
    """
    baseline_rows = await conn.fetch(baseline_sql)
    baselines = {r["country_code"]: r for r in baseline_rows}
    if not baselines:
        return []

    # Per-(country, source) recent harvest null rates (last 7 days, min 10 vehicles).
    # Aliases match {fname}_null pattern for consistent lookup below.
    recent_sql = """
        SELECT
            e.country_code,
            es.source_key,
            count(*)                                       AS n,
            count(*) FILTER (WHERE v.price IS NULL)        AS price_null,
            count(*) FILTER (WHERE v.year IS NULL)         AS year_null,
            count(*) FILTER (WHERE v.km IS NULL)           AS km_null,
            count(*) FILTER (WHERE v.photo_url IS NULL)    AS photo_url_null
        FROM vehicle v
        JOIN entity_source es ON es.entity_ulid = v.entity_ulid
        JOIN entity e         ON e.entity_ulid = v.entity_ulid
        WHERE v.status = 'available'
          AND v.last_seen >= now() - interval '7 days'
        GROUP BY e.country_code, es.source_key
        HAVING count(*) >= 10
    """
    source_rows = await conn.fetch(recent_sql)
    results: list[AnomalyResult] = []
    bucket = _daily_bucket()

    # (field, severity-hint). Severity is recomputed below; the hint documents intent.
    fields = [("price", "critical"), ("year", "warning"), ("km", "warning"), ("photo_url", "info")]

    for src_row in source_rows:
        country = src_row["country_code"]
        b = baselines.get(country)
        if b is None:
            continue
        n0 = int(b["total"])
        if n0 == 0:
            continue
        source_key = src_row["source_key"]
        n1 = int(src_row["n"])

        for fname, _severity_hint in fields:
            x0_global = int(b[f"{fname}_null"])
            x1 = int(src_row[f"{fname}_null"])
            p0 = x0_global / n0
            p1 = x1 / n1

            z = _z_two_prop(x0_global, n0, x1, n1)
            abs_delta = p1 - p0

            # Hard-required: identity field spike regardless of z
            hard_fire = (fname in ("price",)) and p1 > FIELD_LOSS_HARD_THRESH

            if not hard_fire and not (z > FIELD_LOSS_Z_CRIT and abs_delta >= FIELD_LOSS_ABS_FLOOR):
                continue

            # Determine severity and lane
            if hard_fire or fname in ("price",):
                severity = "critical"
                quarantines = True
                lane = "RESEARCH"
            elif fname in ("year", "km"):
                severity = "warning"
                quarantines = False
                lane = "RESEARCH"
            else:  # photo_url
                if abs_delta < FIELD_LOSS_PHOTO_THRESH:
                    continue
                severity = "info"
                quarantines = False
                lane = "AUTO_FIX"

            results.append(AnomalyResult(
                detector="field_loss",
                subject_type="source",
                subject_key=f"{source_key}:{fname}",
                severity=severity,
                score=min(z / 10.0, 1.0),
                measured={"field": fname, "z": round(z, 2),
                          "p0": round(p0, 4), "p1": round(p1, 4),
                          "n0": n0, "n1": n1, "delta": round(abs_delta, 4)},
                baseline={"z_crit": FIELD_LOSS_Z_CRIT,
                          "abs_floor": FIELD_LOSS_ABS_FLOOR},
                lane=lane,
                quarantines=quarantines,
                dedupe_key=f"field_loss|{source_key}:{fname}|{bucket}",
                country_code=country,
            ))

    return results


# ---------------------------------------------------------------------------
# 3.4 — staleness
# ---------------------------------------------------------------------------

async def detect_staleness(conn: asyncpg.Connection) -> list[AnomalyResult]:
    """Detect entities whose last_seen has drifted past their segment TTL.

    Storm suppression: if >STALENESS_STORM_THRESHOLD entities from a single
    source are stale simultaneously, collapse into one source-level item.
    """
    sql = """
        SELECT
            e.cdp_code,
            e.kind,
            e.country_code,
            e.last_seen,
            extract(epoch FROM (now() - e.last_seen)) AS age_seconds
        FROM entity e
        WHERE e.last_seen IS NOT NULL
          AND e.status = 'active'
    """
    rows = await conn.fetch(sql)
    results: list[AnomalyResult] = []
    bucket = _daily_bucket()

    # Group by (country, kind) for storm suppression. A storm is per-country: an ES garaje storm and
    # a DE garaje storm are distinct source-level items and never share a dedupe_key (red-team final).
    stale_by_group: dict[tuple[str, str], list[dict]] = {}

    for row in rows:
        kind = row["kind"]
        country = row["country_code"]
        ttl = STALENESS_TTL.get(kind, STALENESS_TTL["garaje"])
        age = float(row["age_seconds"])
        ratio = age / ttl
        if ratio <= STALENESS_RATIO_WARN:
            continue

        entry = {
            "cdp_code": row["cdp_code"],
            "kind": kind,
            "country_code": country,
            "age_seconds": age,
            "ttl": ttl,
            "ratio": ratio,
        }
        stale_by_group.setdefault((country, kind), []).append(entry)

    for (country, kind), stale_list in stale_by_group.items():
        # Storm suppression: collapse if too many
        if len(stale_list) > STALENESS_STORM_THRESHOLD:
            results.append(AnomalyResult(
                detector="staleness",
                subject_type="source",
                subject_key=f"kind:{kind}",
                severity="critical",
                score=1.0,
                measured={"stale_count": len(stale_list),
                          "kind": kind,
                          "storm_suppressed": True,
                          "sample_cdp_codes": [e["cdp_code"] for e in stale_list[:10]]},
                baseline={"storm_threshold": STALENESS_STORM_THRESHOLD,
                          "ttl_seconds": STALENESS_TTL.get(kind)},
                lane="ESCALATE_GASTO",
                quarantines=False,
                dedupe_key=f"staleness|{country}|kind:{kind}|{bucket}",
                country_code=country,
            ))
            continue

        for entry in stale_list:
            cdp_code = entry["cdp_code"]
            ratio = entry["ratio"]
            severity = "critical" if ratio > STALENESS_RATIO_CRIT else "warning"
            quarantines = ratio > STALENESS_RATIO_CRIT
            results.append(AnomalyResult(
                detector="staleness",
                subject_type="entity",
                subject_key=cdp_code,
                severity=severity,
                score=min(ratio / 10.0, 1.0),
                measured={"age_seconds": round(entry["age_seconds"]),
                          "ttl_seconds": entry["ttl"],
                          "ratio": round(ratio, 2)},
                baseline={"ttl_warn_ratio": STALENESS_RATIO_WARN,
                          "ttl_crit_ratio": STALENESS_RATIO_CRIT},
                lane="AUTO_FIX",
                quarantines=quarantines,
                dedupe_key=f"staleness|{cdp_code}|{bucket}",
                country_code=entry["country_code"],
            ))

    return results


# ---------------------------------------------------------------------------
# 3.5 — fabrication
# ---------------------------------------------------------------------------

async def detect_fabrication(conn: asyncpg.Connection) -> list[AnomalyResult]:
    """Detect impossible / out-of-band / collapsed values.

    (a) Out-of-band hard bounds: price, year, km
    (b) Distinct-row-collapse: cdp_code cardinality vs source rows
    (c) Degenerate distribution: CV of price per entity < FAB_CV_DEGENERATE
    """
    results: list[AnomalyResult] = []
    bucket = _daily_bucket()

    # (a) Out-of-band bounds on vehicle table
    oob_sql = """
        SELECT
            v.vehicle_ulid,
            v.entity_ulid,
            e.cdp_code,
            v.price,
            v.year,
            v.km
        FROM vehicle v
        JOIN entity e ON e.entity_ulid = v.entity_ulid
        WHERE v.status = 'available'
          AND (
              (v.price IS NOT NULL AND (v.price <= 0 OR v.price > %(price_ceil)s))
           OR (v.year  IS NOT NULL AND (v.year < %(year_floor)s OR v.year > %(year_ceil)s))
           OR (v.km    IS NOT NULL AND v.km > %(km_ceil)s)
          )
        LIMIT 500
    """
    oob_rows = await conn.fetch(
        """
        SELECT v.vehicle_ulid, e.cdp_code, v.price, v.year, v.km, e.country_code
        FROM vehicle v
        JOIN entity e ON e.entity_ulid = v.entity_ulid
        WHERE v.status = 'available'
          AND (
              (v.price IS NOT NULL AND (v.price <= 0 OR v.price > $1))
           OR (v.year  IS NOT NULL AND (v.year < $2 OR v.year > $3))
           OR (v.km    IS NOT NULL AND v.km > $4)
          )
        LIMIT 500
        """,
        FAB_PRICE_CEIL, FAB_YEAR_FLOOR, FAB_YEAR_CEIL, FAB_KM_CEIL,
    )

    for row in oob_rows:
        vid = str(row["vehicle_ulid"])
        cdp = row["cdp_code"]
        reasons = []
        if row["price"] is not None and (row["price"] <= 0 or row["price"] > FAB_PRICE_CEIL):
            reasons.append(f"price={row['price']}")
        if row["year"] is not None and (row["year"] < FAB_YEAR_FLOOR or row["year"] > FAB_YEAR_CEIL):
            reasons.append(f"year={row['year']}")
        if row["km"] is not None and row["km"] > FAB_KM_CEIL:
            reasons.append(f"km={row['km']}")

        results.append(AnomalyResult(
            detector="fabrication",
            subject_type="vehicle",
            subject_key=vid,
            severity="critical",
            score=1.0,
            measured={"vehicle_ulid": vid, "cdp_code": cdp,
                      "oob_fields": reasons, "sub": "out_of_band"},
            baseline={
                "price_range": (FAB_PRICE_FLOOR, FAB_PRICE_CEIL),
                "year_range":  (FAB_YEAR_FLOOR, FAB_YEAR_CEIL),
                "km_max":       FAB_KM_CEIL,
            },
            lane="AUTO_FIX",
            quarantines=True,
            dedupe_key=f"fabrication|{vid}|{bucket}",
            country_code=_row_country(row),
        ))

    # (b) Distinct-row-collapse: entities where DB rows per cdp << source refs
    # Using entity_source table to count source distinct refs per cdp_code
    collapse_sql = """
        SELECT
            e.cdp_code,
            count(DISTINCT es.source_key || ':' || es.source_ref) AS source_refs,
            1 AS db_distinct
        FROM entity e
        JOIN entity_source es ON es.entity_ulid = e.entity_ulid
        GROUP BY e.cdp_code
        HAVING count(DISTINCT es.source_key || ':' || es.source_ref) > 1
    """
    # Use verification_verdict where multiple subjects map to same cdp_code
    # (simpler: look at entities where source_coverage has collapse signals)
    # The actual collapse signal is: for a given source_key, how many distinct
    # source_refs map to the same cdp_code vs how many cdp_codes
    collapse_sql2 = """
        SELECT
            es.source_key,
            count(DISTINCT es.source_ref)  AS source_distinct,
            count(DISTINCT e.cdp_code)             AS cdp_distinct
        FROM entity_source es
        JOIN entity e ON e.entity_ulid = es.entity_ulid
        GROUP BY es.source_key
        HAVING count(DISTINCT es.source_ref) > 0
           AND count(DISTINCT es.source_ref)::float /
               GREATEST(count(DISTINCT e.cdp_code), 1) > $1
    """
    collapse_rows = await conn.fetch(collapse_sql2, FAB_COLLAPSE_KAPPA)

    for row in collapse_rows:
        source_key = row["source_key"]
        src_dist = int(row["source_distinct"])
        cdp_dist = int(row["cdp_distinct"])
        ratio = src_dist / max(cdp_dist, 1)
        results.append(AnomalyResult(
            detector="fabrication",
            subject_type="source",
            subject_key=source_key,
            severity="critical",
            score=min((ratio - 1.0) / 5.0, 1.0),
            measured={"source_distinct": src_dist, "cdp_distinct": cdp_dist,
                      "collapse_ratio": round(ratio, 3), "sub": "distinct_collapse"},
            baseline={"kappa": FAB_COLLAPSE_KAPPA},
            lane="RESEARCH",
            quarantines=False,
            dedupe_key=f"fabrication|{source_key}:collapse|{bucket}",
        ))

    # (c) Degenerate price distribution (CV < 0.01) per entity with >= 20 vehicles
    degen_sql = """
        SELECT
            e.cdp_code,
            e.country_code,
            count(*)                   AS n,
            avg(v.price)               AS avg_price,
            stddev(v.price)            AS std_price
        FROM vehicle v
        JOIN entity e ON e.entity_ulid = v.entity_ulid
        WHERE v.status = 'available'
          AND v.price IS NOT NULL
          AND v.price > 0
        GROUP BY e.cdp_code, e.country_code
        HAVING count(*) >= 20
           AND avg(v.price) > 0
           AND (stddev(v.price) / NULLIF(avg(v.price), 0)) < $1
    """
    degen_rows = await conn.fetch(degen_sql, FAB_CV_DEGENERATE)

    for row in degen_rows:
        cdp = row["cdp_code"]
        avg_p = float(row["avg_price"])
        std_p = float(row["std_price"]) if row["std_price"] else 0.0
        cv = std_p / avg_p if avg_p > 0 else 0.0
        results.append(AnomalyResult(
            detector="fabrication",
            subject_type="entity",
            subject_key=cdp,
            severity="warning",
            score=max(0.0, 1.0 - cv / FAB_CV_DEGENERATE),
            measured={"n": int(row["n"]), "avg_price": round(avg_p, 2),
                      "std_price": round(std_p, 2), "cv": round(cv, 4),
                      "sub": "degenerate_distribution"},
            baseline={"cv_threshold": FAB_CV_DEGENERATE},
            lane="RESEARCH",
            quarantines=False,
            dedupe_key=f"fabrication|{cdp}:degen|{bucket}",
            country_code=_row_country(row),
        ))

    return results


# ---------------------------------------------------------------------------
# 3.6 — coverage_gap
# ---------------------------------------------------------------------------

async def detect_coverage_gap(conn: asyncpg.Connection) -> list[AnomalyResult]:
    """Detect gaps between covered entity count and anchor floors per segment.

    Uses the VERIFIED anchor floors from V4 §1 (DGT for desguace,
    FACONAUTO for concesionario_oficial, PA floor for compraventa/garaje).
    """
    # Covered count per (country, kind) (active entities only). Grouping by country keeps each
    # country's coverage compared to its OWN anchor floor (and dedupes the alert per country) — a
    # 2nd country's rows never inflate the ES count nor collide on the dedupe_key (red-team final).
    covered_sql = """
        SELECT country_code, kind, count(*) AS covered
        FROM entity
        WHERE status = 'active'
        GROUP BY country_code, kind
    """
    covered_rows = await conn.fetch(covered_sql)
    covered: dict[tuple[str, str], int] = {
        (r["country_code"], r["kind"]): int(r["covered"]) for r in covered_rows
    }

    results: list[AnomalyResult] = []
    bucket = _daily_bucket()

    for (country, kind), anchor in COVERAGE_ANCHORS.items():
        c = covered.get((country, kind), 0)
        gap = max(0, anchor - c)
        relgap = gap / max(anchor, 1)

        # Hard anchor breach: we are below the known minimum
        if c < anchor:
            severity = "critical"
        elif relgap > COVERAGE_RELGAP_WARN:
            severity = "warning"
        elif relgap > COVERAGE_RELGAP_INFO:
            severity = "info"
        else:
            continue

        results.append(AnomalyResult(
            detector="coverage_gap",
            subject_type="segment",
            subject_key=kind,
            severity=severity,
            score=min(relgap, 1.0),
            measured={"covered": c, "anchor_floor": anchor,
                      "gap": gap, "relgap": round(relgap, 4)},
            baseline={"relgap_info": COVERAGE_RELGAP_INFO,
                      "relgap_warn": COVERAGE_RELGAP_WARN},
            lane="RESEARCH",
            quarantines=False,  # coverage_gap never quarantines (V4 §3.10)
            dedupe_key=f"coverage_gap|{country}|{kind}|{bucket}",
            country_code=country,
        ))

    return results


# ---------------------------------------------------------------------------
# 3.7 — price_trap
# ---------------------------------------------------------------------------

async def detect_price_trap(conn: asyncpg.Connection) -> list[AnomalyResult]:
    """Model-aware cohort price-anomaly detector (two-sided robust-z on ln price).

    Cohort = (make, model, year) Tier-A (fire at n>=PRICE_TRAP_COHORT_MIN_A); a (make, year)
    Tier-B fallback (model NULL, n>=PRICE_TRAP_COHORT_MIN_B) covers rows missing model. Robust
    z = (ln price - median ln price) / (1.4826 * MAD ln price) — MAD not stddev, so a single junk
    outlier (e.g. 9M EUR) cannot inflate the scale and mask its siblings (MAD has ~50% breakdown).

    Fires QUARANTINE-only (reversible — NEVER NULLs or DELETEs vehicle.price; an open quarantining
    item just hides the car from servable_vehicle until closed):
      HIGH  z >= +Z  AND price >= HIGH_ABS_FLOOR     (the >1M EUR monsters; abs-floor is a Law I co-guard)
      LOW   z <= -Z  AND price <  LOW_MEDIAN_FRAC * cohort_median   (deposit / finance / placeholder)
    Near-degenerate cohorts (MAD < MAD_FLOOR) are SKIPPED on BOTH sides (Law I): a tight cohort must
    never amplify a normal-priced car's small deviation into a spurious z and quarantine legit stock.
    Pure async DB-only (zero external cost). Idempotent within a UTC day via dedupe_key.
    """
    # One cohort pass via the shared primitive (pipeline/gestionador/cohorts.py, 04-arbitrage.md F1:
    # factored out so detect_price_trap and the deal-score job share ONE cohort implementation,
    # 00-MASTER.md C-1/C-12). Tier min-size is chosen per-row in the HAVING (model present -> A, else
    # B). The cohort is keyed by (country_code, make, model, year): a "VW Golf 2020" in ES and one in
    # DE must NOT pool into one median/MAD. The base joins entity ONLY for country_code (kind is still
    # resolved later for the few flagged rows). ES is byte-identical: a single tenant means the country
    # column is constant, so the cohorts and statistics are exactly the previous ones.
    # Verified byte-identical against production cardeep-pg pre/post this refactor (04-F1 log):
    # same 5000-row flagged set, same order (hash cb132238020735529dc11d422e0ce1dd38d9e568b54a670ec6c9905db66a039c).
    base_select_sql = (
        "SELECT v.vehicle_ulid, v.price, v.make, v.model, v.year, e.country_code "
        "FROM vehicle v JOIN entity e ON e.entity_ulid = v.entity_ulid "
        "WHERE v.status = 'available'"
    )
    sql = f"""
        WITH {cohort_ctes_sql(base_select_sql)}
        SELECT vehicle_ulid, price, make, model, year, country_code, n, med_price, z, tier_b,
               CASE WHEN z >=  $4 AND price >= $5            THEN 'high'
                    WHEN z <= -$4 AND price <  $6 * med_price THEN 'low' END AS side
          FROM scored
         WHERE (z >=  $4 AND price >= $5)
            OR (z <= -$4 AND price <  $6 * med_price)
         ORDER BY abs(z) DESC
         LIMIT $7
    """
    rows = await conn.fetch(
        sql,
        PRICE_TRAP_COHORT_MIN_A, PRICE_TRAP_COHORT_MIN_B, PRICE_TRAP_MAD_FLOOR,
        PRICE_TRAP_COHORT_Z, PRICE_TRAP_HIGH_ABS_FLOOR, PRICE_TRAP_LOW_MEDIAN_FRAC,
        PRICE_TRAP_MAX_ROWS,
    )
    if not rows:
        return []

    # Resolve kind for ONLY the flagged rows (<=MAX_ROWS, indexed lookup): the cohort scan above joins
    # entity solely for country_code, so KIND is not dragged through the percentile aggregates over the
    # full base — it is looked up here for the handful of flagged vehicles instead.
    vids = [str(r["vehicle_ulid"]) for r in rows]
    kind_rows = await conn.fetch(
        "SELECT v.vehicle_ulid, e.kind FROM vehicle v "
        "JOIN entity e ON e.entity_ulid = v.entity_ulid "
        "WHERE v.vehicle_ulid = ANY($1::text[])",
        vids,
    )
    kind_by_vid: dict[str, str] = {str(r["vehicle_ulid"]): r["kind"] for r in kind_rows}

    bucket = _daily_bucket()
    results: list[AnomalyResult] = []
    for row in rows:
        vid = str(row["vehicle_ulid"])
        price = float(row["price"])
        z = float(row["z"])
        side = row["side"]
        kind = kind_by_vid.get(vid)
        # HIGH is always critical (the >1M monsters). LOW is critical at a deposit shape
        # (price <= the per-kind deposit floor) else a warning (cheap-but-real outlier).
        if side == "high":
            severity = "critical"
        else:
            deposit_floor = PRICE_TRAP_FLOOR.get(kind or "", 300.0)
            severity = "critical" if price <= deposit_floor else "warning"
        results.append(AnomalyResult(
            detector="price_trap",
            subject_type="vehicle",
            subject_key=vid,
            severity=severity,
            score=min(1.0, abs(z) / (2.0 * PRICE_TRAP_COHORT_Z)),
            measured={
                "price": round(price, 2),
                "robust_z": round(z, 2),
                "side": side,
                "make": row["make"],
                "model": row["model"],
                "year": row["year"],
                "cohort_median": round(float(row["med_price"]), 2),
                "cohort_n": int(row["n"]),
                "cohort_tier": "B" if row["tier_b"] else "A",
                "kind": kind,
            },
            baseline={
                "cohort_z_threshold": PRICE_TRAP_COHORT_Z,
                "high_abs_floor": PRICE_TRAP_HIGH_ABS_FLOOR,
                "low_median_frac": PRICE_TRAP_LOW_MEDIAN_FRAC,
                "mad_floor": PRICE_TRAP_MAD_FLOOR,
            },
            lane="QUARANTINE",
            quarantines=True,
            dedupe_key=f"price_trap|{vid}|{bucket}",
            country_code=_row_country(row),
        ))
    return results


# ---------------------------------------------------------------------------
# 3.8 — geo_resolution_drift  [STUB — no sentinel-placement data yet]
# ---------------------------------------------------------------------------

async def detect_geo_resolution_drift(conn: asyncpg.Connection) -> list[AnomalyResult]:
    """Detect geocoder regression via sentinel-placement rate spike.

    STUB: This detector requires tracking how many newly-placed entities
    land in sentinel directories (_sin-comarca / _sin-municipio) vs normal
    placement. The sentinel_placement_rate column / tracking table does not
    yet exist in the schema. When it does, this function will:
      - Read rolling sentinel-placement rate per time window
      - Compare to trailing 30-day baseline
      - Fire when rate > 2x baseline OR > 15% absolute
    Requires: new migration adding geo placement tracking.
    """
    return []   # STUB — no data, no items


# ---------------------------------------------------------------------------
# 3.9 — classifier_drift  [STUB — requires golden-set harness]
# ---------------------------------------------------------------------------

async def detect_classifier_drift(conn: asyncpg.Connection) -> list[AnomalyResult]:
    """Detect LLM kind-label accuracy regression on golden set.

    STUB: This detector requires a golden-set evaluation harness that:
      - Maintains a hand-labeled set of entities with known correct kinds
      - Runs the local LLM classifier nightly against this set
      - Scores precision/recall per kind
      - Fires when any per-kind metric drops below 0.95
    Requires: golden_set table + classifier evaluation pipeline.
    Both are T08 §5.1 items not yet implemented.
    """
    return []   # STUB — no golden set, no items


# ---------------------------------------------------------------------------
# Detector registry — single source of truth (consumed by dry_run_all AND run.run_all)
# ---------------------------------------------------------------------------

# (name, coroutine-fn). Order = execution order. dry_run_all (diagnostic, no writes) runs
# every entry; run.run_all (live, routes flags) skips STUB_DETECTORS so the cadence never
# implies coverage a detector cannot yet deliver.
DETECTORS: list[tuple[str, object]] = [
    ("count_inflation",      detect_count_inflation),
    ("silent_cap",           detect_silent_cap),
    ("field_loss",           detect_field_loss),
    ("staleness",            detect_staleness),
    ("fabrication",          detect_fabrication),
    ("coverage_gap",         detect_coverage_gap),
    ("price_trap",           detect_price_trap),
    ("geo_resolution_drift", detect_geo_resolution_drift),
    ("classifier_drift",     detect_classifier_drift),
]

# Wired but INERT until their backing tables/harness exist (T08 §5.1): they return []
# today. run_all() SKIPS these so a live run does not log false "ran, 0 found" coverage.
STUB_DETECTORS: frozenset[str] = frozenset({"geo_resolution_drift", "classifier_drift"})


# ---------------------------------------------------------------------------
# Dry-run entry point: count anomalies per detector without writing to DB
# ---------------------------------------------------------------------------

async def dry_run_all(conn: asyncpg.Connection) -> dict[str, int]:
    """Run all detectors, return anomaly counts per detector. No DB writes."""
    counts: dict[str, int] = {}
    for name, fn in DETECTORS:
        try:
            results = await fn(conn)
            counts[name] = len(results)
        except Exception as exc:
            counts[name] = -1  # -1 = detector raised an error
            print(f"  [ERROR] {name}: {exc}")
    return counts

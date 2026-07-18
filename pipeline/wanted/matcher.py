"""match_score — the SQL-deterministic matcher for the "Se busca" board.

plans/cardeep-omni/08-forum-community.md §4.4 (formula, exact weights) + §7.3 (verification
protocol: "el matcher es SQL determinista: ambas vías DEBEN coincidir"). This module is the
SINGLE source of truth for the formula in two forms that MUST stay numerically identical:

  1. ``build_candidate_sql`` — a SQL query the API/matcher job actually run against the live
     ``vehicle``/``entity`` tables, doing the heavy filtering + scoring in the database (the
     candidate set for a popular make can be 100k+ rows; scoring in SQL is the only tractable
     approach for a live "cuantos hay ahora mismo" render).
  2. ``compute_match_score`` — the pure-Python recomputation used as the independent
     cross-check leg (tests/test_wanted_matcher.py; same pattern as
     pipeline/market/cohort.py's percentile_cont, which exists for the identical reason).

Formula (carta §4.4, verbatim):
    match_score = 35*make_model + 15*year + 15*km + 20*price + 15*geo
      make_model: 1 if make AND model exact (normalized); 0 otherwise. No fuzzy in v1.
      year:  1 if |year - year_pedido| <= 1; 0.5 if <= 2; 0 otherwise.
      km:    1 if km <= km_max; 0.5 if <= km_max*1.2; 0 otherwise.
      price: 1 if price <= price_max; 0.5 if <= price_max*1.1; 0 otherwise.
      geo:   1 same province; 0.6 bordering province; 0.3 rest of Spain.

Declared interpretation gaps (both required to reconcile the carta's own §4.4 formula with its
§5.2 schema — documented, not silently guessed):
  * §4.4's "year" component tests distance from a SINGLE target year ("year_pedido"), but §5.2's
    wanted_listing schema stores a RANGE (year_min/year_max) — the form lets a buyer say "2018 a
    2021", not one year. Resolved here as: full score (1.0) when the vehicle's year falls INSIDE
    [year_min, year_max] widened by +/-1; half score when widened by +/-2; 0 otherwise. This is
    the only reading under which both sections of the carta are mutually consistent.
  * §4.4's make_model component requires "make y model exactos (normalizados por el mismo
    normalizador del pipeline)" but the pipeline only ships a MAKE normalizer
    (pipeline/identity/make_normalizer.py) — there is no model normalizer to reuse. Model is
    compared case/whitespace-insensitive exact (still zero fuzzy matching, just no alias table).
    A NULL wanted_listing.model is treated as "any model of this make" (product decision for an
    optional form field, not a fuzzy match on a filled one).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pipeline.identity.make_normalizer import canonical_make

# ---------------------------------------------------------------------------
# Config — every threshold named, none inline (carta §4.4: "toda constante es
# nombrada en config, nunca número mágico"). Weights/thresholds not pinned to a
# public source are marked [ASUMIDO] in the carta (§4.4/§4.5) — adjustable, not
# yet re-tuned against real usage.
# ---------------------------------------------------------------------------

WEIGHT_MAKE_MODEL: float = 35.0
WEIGHT_YEAR: float = 15.0
WEIGHT_KM: float = 15.0
WEIGHT_PRICE: float = 20.0
WEIGHT_GEO: float = 15.0

YEAR_FULL_RADIUS: int = 1
YEAR_HALF_RADIUS: int = 2
KM_HALF_MULTIPLIER: float = 1.2
PRICE_HALF_MULTIPLIER: float = 1.1

GEO_SAME_PROVINCE: float = 1.0
GEO_ADJACENT_PROVINCE: float = 0.6
GEO_OTHER: float = 0.3

MATCH_LIST_THRESHOLD: float = 50.0   # carta §4.4: "umbral de listado: >=50 aparece en coincidencias"
MATCH_NOTIFY_THRESHOLD: float = 70.0  # carta §4.4: "umbral de notificación: >=70 alerta al autor"

TTL_CHOICES: tuple[int, ...] = (7, 14, 30, 60)  # carta §4.4

WANTED_COOLDOWN_DAYS: int = 2      # carta §4.4 (PistonHeads-inspired, laxer — see carta rationale)
WANTED_MAX_OPEN: int = 5           # carta §4.4
WANTED_MAX_MONTH: int = 8          # carta §4.4

REVIEW_REVEAL_DAYS: int = 14       # carta §4.6, Airbnb-exact double-blind window

CLOSED_REASONS: tuple[str, ...] = ("bought_via_cardeep", "bought_elsewhere", "no_longer_interested")


# ---------------------------------------------------------------------------
# Pure scoring components (independent cross-check leg, §7.3)
# ---------------------------------------------------------------------------

def _normalize_make(value: str | None) -> str | None:
    """Canonical form via the pipeline's own alias map; falls back to a
    lower/trimmed string for a brand the map does not know (never invents a match
    for two DIFFERENT unknown strings, only makes comparison case-insensitive)."""
    if not value:
        return None
    canon = canonical_make(value)
    if canon:
        return canon
    return value.strip().lower()


def _normalize_model(value: str | None) -> str | None:
    if not value:
        return None
    return " ".join(value.strip().lower().split())


def make_model_component(
    vehicle_make: str | None,
    vehicle_model: str | None,
    wanted_make: str | None,
    wanted_model: str | None,
) -> float:
    if _normalize_make(vehicle_make) != _normalize_make(wanted_make):
        return 0.0
    if _normalize_make(vehicle_make) is None:
        return 0.0  # both sides blank normalizes to None == None; never "match" on absence
    if wanted_model is None:
        return 1.0  # any model of this make (declared gap above)
    return 1.0 if _normalize_model(vehicle_model) == _normalize_model(wanted_model) else 0.0


def year_component(vehicle_year: int | None, year_min: int | None, year_max: int | None) -> float:
    if vehicle_year is None or (year_min is None and year_max is None):
        return 0.0
    lo = year_min if year_min is not None else year_max
    hi = year_max if year_max is not None else year_min
    assert lo is not None and hi is not None
    if lo <= vehicle_year <= hi:
        return 1.0
    dist = (lo - vehicle_year) if vehicle_year < lo else (vehicle_year - hi)
    if dist <= YEAR_FULL_RADIUS:
        return 1.0
    if dist <= YEAR_HALF_RADIUS:
        return 0.5
    return 0.0


def km_component(vehicle_km: int | None, km_max: int | None) -> float:
    if vehicle_km is None or km_max is None:
        return 0.0
    if vehicle_km <= km_max:
        return 1.0
    if vehicle_km <= km_max * KM_HALF_MULTIPLIER:
        return 0.5
    return 0.0


def price_component(vehicle_price: float | None, price_max: float | None) -> float:
    if vehicle_price is None or price_max is None:
        return 0.0
    if vehicle_price <= price_max:
        return 1.0
    if vehicle_price <= price_max * PRICE_HALF_MULTIPLIER:
        return 0.5
    return 0.0


def geo_component(vehicle_province: str | None, wanted_province: str, adjacent_provinces: frozenset[str]) -> float:
    if vehicle_province is None:
        return GEO_OTHER
    if vehicle_province == wanted_province:
        return GEO_SAME_PROVINCE
    if vehicle_province in adjacent_provinces:
        return GEO_ADJACENT_PROVINCE
    return GEO_OTHER


@dataclass(frozen=True)
class WantedCriteria:
    make: str
    model: str | None
    year_min: int | None
    year_max: int | None
    km_max: int | None
    price_max: float | None
    province_code: str


@dataclass(frozen=True)
class VehicleCandidate:
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    province_code: str | None


def compute_match_score(
    wanted: WantedCriteria,
    vehicle: VehicleCandidate,
    adjacent_provinces: frozenset[str],
) -> float:
    """Pure recomputation of the exact SQL formula — the independent verification leg (§7.3)."""
    total = (
        WEIGHT_MAKE_MODEL * make_model_component(vehicle.make, vehicle.model, wanted.make, wanted.model)
        + WEIGHT_YEAR * year_component(vehicle.year, wanted.year_min, wanted.year_max)
        + WEIGHT_KM * km_component(vehicle.km, wanted.km_max)
        + WEIGHT_PRICE * price_component(vehicle.price, wanted.price_max)
        + WEIGHT_GEO * geo_component(vehicle.province_code, wanted.province_code, adjacent_provinces)
    )
    return round(total, 2)


# ---------------------------------------------------------------------------
# SQL candidate query — same formula, pushed into the database for scale.
#
# Make filtering reuses pipeline/identity/make_normalizer.py's OWN alias table (no second
# alias map invented in SQL, C-1/C-12 discipline): the canonical make's known raw spellings
# are looked up from _CANON and passed as a bound array, so "give me every row whose raw make
# string normalizes to Volkswagen" becomes a plain `= ANY($aliases)` the query planner can index.
# A vehicle with a BLANK make (title-recoverable per make_normalizer's own doctrine) is not
# recovered here — under-match over mis-match (make_normalizer.py's own "Law I"), declared gap.
# ---------------------------------------------------------------------------

def _known_aliases_for(canonical: str) -> list[str]:
    from pipeline.identity.make_normalizer import _CANON  # single source of truth, not duplicated

    aliases = [raw for raw, canon in _CANON.items() if canon == canonical]
    return aliases or [canonical.lower()]


_CANDIDATE_SQL_TEMPLATE = """
WITH scored AS (
    SELECT
        v.vehicle_ulid, v.entity_ulid, v.make, v.model, v.year, v.km, v.price,
        v.fuel, v.transmission, v.deep_link, v.photo_url, v.title, v.status,
        v.first_seen, v.last_seen,
        e.province_code AS vehicle_province,
        (
            CASE WHEN $2::text IS NULL
                 THEN 1.0
                 WHEN lower(regexp_replace(coalesce(v.model, ''), '\\s+', ' ', 'g')) =
                      lower(regexp_replace($2::text, '\\s+', ' ', 'g'))
                 THEN 1.0 ELSE 0.0 END
        ) AS make_model_score,
        (
            CASE
                WHEN v.year IS NULL OR ($3::int IS NULL AND $4::int IS NULL) THEN 0.0
                WHEN v.year BETWEEN coalesce($3::int, $4::int) AND coalesce($4::int, $3::int) THEN 1.0
                WHEN v.year BETWEEN coalesce($3::int, $4::int) - 1 AND coalesce($4::int, $3::int) + 1 THEN 1.0
                WHEN v.year BETWEEN coalesce($3::int, $4::int) - 2 AND coalesce($4::int, $3::int) + 2 THEN 0.5
                ELSE 0.0
            END
        ) AS year_score,
        (
            CASE
                WHEN v.km IS NULL OR $5::int IS NULL THEN 0.0
                WHEN v.km <= $5::int THEN 1.0
                WHEN v.km <= $5::int * 1.2 THEN 0.5
                ELSE 0.0
            END
        ) AS km_score,
        (
            CASE
                WHEN v.price IS NULL OR $6::numeric IS NULL THEN 0.0
                WHEN v.price <= $6::numeric THEN 1.0
                WHEN v.price <= $6::numeric * 1.1 THEN 0.5
                ELSE 0.0
            END
        ) AS price_score,
        (
            CASE
                WHEN e.province_code IS NULL THEN 0.3
                WHEN e.province_code = $7::varchar THEN 1.0
                WHEN e.province_code = ANY($8::varchar[]) THEN 0.6
                ELSE 0.3
            END
        ) AS geo_score
      FROM vehicle v
      JOIN entity e ON e.entity_ulid = v.entity_ulid
     WHERE v.status = 'available'
       AND e.country_code = 'ES'
       AND upper(trim(v.make)) = ANY($1::text[])
       -- Model is a HARD prefilter when the buyer specified one (same reasoning as the make
       -- alias filter above): a candidate that fails make_model shouldn't be surfaced just
       -- because year/km/price/geo alone sum past the listing threshold (measured live: without
       -- this filter, "Golf" searches surfaced unrelated Volkswagen models — Tiguan, Passat —
       -- purely on year/km/price/geo score. carta §4.4's weighted-sum formula is the RANKING
       -- signal among same-identity candidates, not a licence to cross identity boundaries).
       AND ($2::text IS NULL OR lower(regexp_replace(coalesce(v.model, ''), '\\s+', ' ', 'g')) =
                                 lower(regexp_replace($2::text, '\\s+', ' ', 'g')))
)
SELECT *, (35.0 * make_model_score + 15.0 * year_score + 15.0 * km_score
           + 20.0 * price_score + 15.0 * geo_score) AS match_score
  FROM scored
 WHERE (35.0 * make_model_score + 15.0 * year_score + 15.0 * km_score
        + 20.0 * price_score + 15.0 * geo_score) >= $9
 ORDER BY match_score DESC, vehicle_ulid
 LIMIT $10
"""

_COUNT_SQL_TEMPLATE = """
WITH scored AS (
    SELECT
        (
            CASE WHEN $2::text IS NULL
                 THEN 1.0
                 WHEN lower(regexp_replace(coalesce(v.model, ''), '\\s+', ' ', 'g')) =
                      lower(regexp_replace($2::text, '\\s+', ' ', 'g'))
                 THEN 1.0 ELSE 0.0 END
        ) AS make_model_score,
        (
            CASE
                WHEN v.year IS NULL OR ($3::int IS NULL AND $4::int IS NULL) THEN 0.0
                WHEN v.year BETWEEN coalesce($3::int, $4::int) AND coalesce($4::int, $3::int) THEN 1.0
                WHEN v.year BETWEEN coalesce($3::int, $4::int) - 1 AND coalesce($4::int, $3::int) + 1 THEN 1.0
                WHEN v.year BETWEEN coalesce($3::int, $4::int) - 2 AND coalesce($4::int, $3::int) + 2 THEN 0.5
                ELSE 0.0
            END
        ) AS year_score,
        (
            CASE
                WHEN v.km IS NULL OR $5::int IS NULL THEN 0.0
                WHEN v.km <= $5::int THEN 1.0
                WHEN v.km <= $5::int * 1.2 THEN 0.5
                ELSE 0.0
            END
        ) AS km_score,
        (
            CASE
                WHEN v.price IS NULL OR $6::numeric IS NULL THEN 0.0
                WHEN v.price <= $6::numeric THEN 1.0
                WHEN v.price <= $6::numeric * 1.1 THEN 0.5
                ELSE 0.0
            END
        ) AS price_score,
        (
            CASE
                WHEN e.province_code IS NULL THEN 0.3
                WHEN e.province_code = $7::varchar THEN 1.0
                WHEN e.province_code = ANY($8::varchar[]) THEN 0.6
                ELSE 0.3
            END
        ) AS geo_score
      FROM vehicle v
      JOIN entity e ON e.entity_ulid = v.entity_ulid
     WHERE v.status = 'available'
       AND e.country_code = 'ES'
       AND upper(trim(v.make)) = ANY($1::text[])
       AND ($2::text IS NULL OR lower(regexp_replace(coalesce(v.model, ''), '\\s+', ' ', 'g')) =
                                 lower(regexp_replace($2::text, '\\s+', ' ', 'g')))
)
SELECT COUNT(*) AS n
  FROM scored
 WHERE (35.0 * make_model_score + 15.0 * year_score + 15.0 * km_score
        + 20.0 * price_score + 15.0 * geo_score) >= $9
"""

DEFAULT_CANDIDATE_LIMIT: int = 500
"""Top-N by score persisted/returned per listing (carta doesn't name a cap; a popular
make+model (measured live: "Volkswagen Golf" in Malaga) can exceed 30k candidates at the
listing threshold — nobody scrolls past the best few hundred, and materializing all of
them as wanted_match rows for every open listing would be unbounded storage growth for
zero product value). The exact "matches_now" headline count (carta §6.1) is always the
UNCAPPED ``build_count_query`` result, never truncated by this limit."""


def _make_aliases(wanted_make: str) -> list[str]:
    canonical = canonical_make(wanted_make) or wanted_make.strip().lower()
    aliases = [a.upper() for a in _known_aliases_for(canonical)] + [canonical.upper()]
    return sorted(set(aliases))


def build_candidate_query(
    wanted: WantedCriteria,
    adjacent_provinces: frozenset[str],
    min_score: float = MATCH_LIST_THRESHOLD,
    limit: int = DEFAULT_CANDIDATE_LIMIT,
) -> tuple[str, list[Any]]:
    """Build the (sql, params) pair for the live candidate-scoring query.

    ``$1`` is the array of raw make-string aliases (upper-cased) that normalize to
    ``wanted.make``'s canonical form — computed from the SAME ``_CANON`` map
    ``compute_match_score`` uses, so the SQL and Python legs can never silently diverge
    on what counts as "the same make". Returns at most ``limit`` rows, best score first
    — use ``build_count_query`` for the exact (uncapped) "matches_now" number.
    """
    params: list[Any] = [
        _make_aliases(wanted.make),
        wanted.model,
        wanted.year_min,
        wanted.year_max,
        wanted.km_max,
        wanted.price_max,
        wanted.province_code,
        sorted(adjacent_provinces),
        min_score,
        limit,
    ]
    return _CANDIDATE_SQL_TEMPLATE, params


def build_count_query(
    wanted: WantedCriteria,
    adjacent_provinces: frozenset[str],
    min_score: float = MATCH_LIST_THRESHOLD,
) -> tuple[str, list[Any]]:
    """Exact, uncapped count of candidates scoring >= ``min_score`` — the carta §6.1/§4.9
    "hay N ahora mismo" headline number, never truncated by ``DEFAULT_CANDIDATE_LIMIT``."""
    params: list[Any] = [
        _make_aliases(wanted.make),
        wanted.model,
        wanted.year_min,
        wanted.year_max,
        wanted.km_max,
        wanted.price_max,
        wanted.province_code,
        sorted(adjacent_provinces),
        min_score,
    ]
    return _COUNT_SQL_TEMPLATE, params


def reveal_eligible(
    buyer_submitted_at: Any | None,
    dealer_submitted_at: Any | None,
    now: Any,
    reveal_days: int = REVIEW_REVEAL_DAYS,
) -> bool:
    """§4.6 double-blind (Airbnb-exact): reveal when BOTH sides have submitted, or when
    ``reveal_days`` have elapsed since the FIRST submission — whichever comes first."""
    if buyer_submitted_at is not None and dealer_submitted_at is not None:
        return True
    first = min(t for t in (buyer_submitted_at, dealer_submitted_at) if t is not None) \
        if (buyer_submitted_at or dealer_submitted_at) else None
    if first is None:
        return False
    from datetime import timedelta

    return now >= first + timedelta(days=reveal_days)

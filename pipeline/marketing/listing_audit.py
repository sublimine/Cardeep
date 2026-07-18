"""C1 — listing-quality audit engine (plans/cardeep-omni/07-marketing.md S4 "C1 —
Puntuacion de anuncio (0-100), determinista").

Pure, offline-testable core: every check is a deterministic function of already-known
fields (``vehicle``, ``platform_listing``, ``vehicle_event``). Zero LLM, zero network
here (S8: "Checks C1 ... SQL/Python puro, cero LLM. Usar un LLM aqui seria
incompetencia"). Photo dimensions (c8) are the ONE check needing a prior network fetch
(pipeline/marketing/photo_dims.py) -- this module accepts the *result* of that fetch as
plain input, never fetches itself, so the scoring core stays 100% offline-testable
(same separation-of-concerns precedent as pipeline/delta_photo.py's injected ``fetch``).

Each check's weight sums to exactly 100 (carta's own table, S4 C1) -- pinned by
``tests/test_listing_audit_engine.py::test_weights_sum_to_100`` so a future edit
cannot silently drift the total.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

# ---------------------------------------------------------------------------
# Weights (carta S4, table C1) -- named constants, never magic numbers inline.
# ---------------------------------------------------------------------------

POINTS_PRICE_PRESENT: int = 12          # c1
POINTS_MAKE_MODEL: int = 10             # c2
POINTS_YEAR_VALID: int = 8              # c3
POINTS_KM_PRESENT: int = 10             # c4
POINTS_VIN_PRESENT: int = 12            # c5
POINTS_FUEL_TRANSMISSION: int = 6       # c6
POINTS_PHOTO_PRESENT: int = 10          # c7
POINTS_PHOTO_MIN_SIZE: int = 8          # c8
POINTS_TITLE_RICH: int = 6              # c9
POINTS_PRICE_COHERENCE: int = 10        # c10
POINTS_NO_STAGNATION: int = 8           # c11

TOTAL_POINTS: int = (
    POINTS_PRICE_PRESENT + POINTS_MAKE_MODEL + POINTS_YEAR_VALID + POINTS_KM_PRESENT
    + POINTS_VIN_PRESENT + POINTS_FUEL_TRANSMISSION + POINTS_PHOTO_PRESENT
    + POINTS_PHOTO_MIN_SIZE + POINTS_TITLE_RICH + POINTS_PRICE_COHERENCE
    + POINTS_NO_STAGNATION
)
assert TOTAL_POINTS == 100, f"C1 weights must sum to 100, got {TOTAL_POINTS}"

# Google Vehicle Ads image-quality floor (carta S2, "Google Vehicle Ads" row): images
# must be >=800x600px.
MIN_PHOTO_WIDTH: int = 800
MIN_PHOTO_HEIGHT: int = 600

# c5: presence alone is not honest given the known real-world contamination (04-arbitrage
# F6 found 98.4% of vin_ref values across the census were platform listing-IDs, not real
# VINs -- migrations/0083_vin_ref_remediation.sql). A dealer whose vin_ref is a
# mislabeled listing-id would wrongly score full marks on "Google will accept this VIN"
# if this check only tested NULL-ness. Applying the real NHTSA/ISO-3779 VIN charset
# (excludes I/O/Q -- same regex family already used by web/src/pages/Assistant.tsx's
# 'vin' mode) is a stricter, more honest bar than the carta's literal wording ("vin_ref
# presente") and is declared here as a deliberate improvement, not a silent change.
_VIN_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")

# c11: >=N downward PRICE_CHANGE events within the trailing window while still
# available -- same threshold as scripts/f0_marketing_recon.py's F0 measurement.
STAGNATION_MIN_DROPS: int = 2
STAGNATION_WINDOW_DAYS: int = 30

# c9: minimum count of "extra" content tokens in the title beyond make/model/year.
TITLE_MIN_EXTRA_TOKENS: int = 1
_STOPWORDS = {"de", "del", "la", "el", "en", "con", "y", "un", "una", "the", "a", "of"}


@dataclass(frozen=True)
class PlatformEdge:
    """One platform_listing row relevant to c10 (carta S4 C10: "toda arista status=
    'listed'")."""
    platform_price: float | None
    status: str  # 'listed' | 'removed'


@dataclass(frozen=True)
class VehicleAuditInput:
    """Everything the C1 engine needs, already resolved by the caller (SQL query) --
    this dataclass has NO database access, so it is trivial to construct synthetic
    fixtures for tests/test_listing_audit_engine.py's golden cases."""
    vehicle_ulid: str
    price: float | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    vin_ref: str | None
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    title: str | None
    photo_width: int | None = None   # None = "not measured yet", never a false pass/fail
    photo_height: int | None = None
    platform_edges: tuple[PlatformEdge, ...] = ()
    price_drops_30d: int = 0
    today: date = field(default_factory=date.today)


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    label: str
    passed: bool
    points_awarded: int
    points_possible: int
    message: str        # dealer-facing, plain language (carta S6 Bloque 1 examples)
    evidence: dict[str, Any]


@dataclass(frozen=True)
class AuditResult:
    vehicle_ulid: str
    score: int
    checks: tuple[CheckResult, ...]

    @property
    def failed_checks(self) -> tuple[CheckResult, ...]:
        return tuple(c for c in self.checks if not c.passed)


def _check_price(v: VehicleAuditInput) -> CheckResult:
    passed = v.price is not None and v.price > 0
    return CheckResult(
        "c1", "Precio", passed, POINTS_PRICE_PRESENT if passed else 0, POINTS_PRICE_PRESENT,
        "Precio publicado." if passed else "Sin precio: Google y Meta rechazan el feed sin este campo.",
        {"price": v.price},
    )


def _check_make_model(v: VehicleAuditInput) -> CheckResult:
    passed = bool(v.make) and bool(v.model)
    return CheckResult(
        "c2", "Marca y modelo", passed, POINTS_MAKE_MODEL if passed else 0, POINTS_MAKE_MODEL,
        "Marca y modelo presentes." if passed else "Falta marca o modelo: campo obligatorio en todo feed de vehículos.",
        {"make": v.make, "model": v.model},
    )


def _check_year(v: VehicleAuditInput) -> CheckResult:
    current_year = v.today.year
    passed = v.year is not None and 1900 <= v.year <= current_year + 1
    return CheckResult(
        "c3", "Año", passed, POINTS_YEAR_VALID if passed else 0, POINTS_YEAR_VALID,
        "Año válido." if passed else "Año ausente o fuera de rango (YYYY): Google lo exige.",
        {"year": v.year},
    )


def _check_km(v: VehicleAuditInput) -> CheckResult:
    passed = v.km is not None and v.km >= 0
    return CheckResult(
        "c4", "Kilometraje", passed, POINTS_KM_PRESENT if passed else 0, POINTS_KM_PRESENT,
        "Kilometraje presente." if passed else "Sin kilometraje: obligatorio en usados según Google Vehicle Ads.",
        {"km": v.km},
    )


def _check_vin(v: VehicleAuditInput) -> CheckResult:
    passed = bool(v.vin_ref) and bool(_VIN_PATTERN.match(v.vin_ref.strip().upper())) if v.vin_ref else False
    return CheckResult(
        "c5", "VIN", passed, POINTS_VIN_PRESENT if passed else 0, POINTS_VIN_PRESENT,
        "VIN válido presente." if passed else "Sin VIN: Google no te lo acepta en Vehicle Ads.",
        {"vin_ref": v.vin_ref},
    )


def _check_fuel_transmission(v: VehicleAuditInput) -> CheckResult:
    passed = bool(v.fuel) and bool(v.transmission)
    return CheckResult(
        "c6", "Combustible y transmisión", passed, POINTS_FUEL_TRANSMISSION if passed else 0,
        POINTS_FUEL_TRANSMISSION,
        "Combustible y transmisión presentes." if passed else "Falta combustible o transmisión (recomendado por schema.org).",
        {"fuel": v.fuel, "transmission": v.transmission},
    )


def _check_photo_present(v: VehicleAuditInput) -> CheckResult:
    passed = bool(v.photo_url)
    return CheckResult(
        "c7", "Foto", passed, POINTS_PHOTO_PRESENT if passed else 0, POINTS_PHOTO_PRESENT,
        "Foto presente." if passed else "Sin foto: el anuncio no es publicable en ningún canal serio.",
        {"photo_url": v.photo_url},
    )


def _check_photo_size(v: VehicleAuditInput) -> CheckResult:
    measured = v.photo_width is not None and v.photo_height is not None
    passed = measured and v.photo_width >= MIN_PHOTO_WIDTH and v.photo_height >= MIN_PHOTO_HEIGHT
    if not measured:
        message = "Dimensiones de la foto aún no verificadas (pendiente del job de medición)."
    elif passed:
        message = f"Foto {v.photo_width}×{v.photo_height} cumple el mínimo de Google."
    else:
        message = f"Foto pequeña ({v.photo_width}×{v.photo_height}): mínimo {MIN_PHOTO_WIDTH}×{MIN_PHOTO_HEIGHT}."
    return CheckResult(
        "c8", "Tamaño de foto", passed, POINTS_PHOTO_MIN_SIZE if passed else 0, POINTS_PHOTO_MIN_SIZE,
        message,
        {"width": v.photo_width, "height": v.photo_height, "measured": measured, "photo_url": v.photo_url},
    )


def _title_extra_token_count(title: str, make: str | None, model: str | None, year: int | None) -> int:
    tokens = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", title.lower())
    exclude: set[str] = set(_STOPWORDS)
    if make:
        exclude |= {t.lower() for t in re.findall(r"[a-zA-ZÀ-ÿ0-9]+", make)}
    if model:
        exclude |= {t.lower() for t in re.findall(r"[a-zA-ZÀ-ÿ0-9]+", model)}
    if year:
        exclude.add(str(year))
    extra = [t for t in tokens if t not in exclude and len(t) >= 2]
    return len(extra)


def _check_title_richness(v: VehicleAuditInput) -> CheckResult:
    if not v.title:
        return CheckResult(
            "c9", "Riqueza del título", False, 0, POINTS_TITLE_RICH,
            "Sin título: no hay texto de anuncio que enriquecer.", {"title": None, "extra_tokens": 0},
        )
    extra = _title_extra_token_count(v.title, v.make, v.model, v.year)
    passed = extra >= TITLE_MIN_EXTRA_TOKENS
    return CheckResult(
        "c9", "Riqueza del título", passed, POINTS_TITLE_RICH if passed else 0, POINTS_TITLE_RICH,
        "Título con atributos más allá de marca/modelo/año." if passed
        else "Título pobre: añade un atributo más (color, versión, km) además de marca/modelo/año.",
        {"title": v.title, "extra_tokens": extra},
    )


def _check_price_coherence(v: VehicleAuditInput) -> CheckResult:
    mismatches = [
        e for e in v.platform_edges
        if e.status == "listed" and e.platform_price is not None
        and v.price is not None and float(e.platform_price) != float(v.price)
    ]
    passed = len(mismatches) == 0
    if passed:
        message = "Precio coherente en todas las plataformas donde estás publicado."
    else:
        parts = [f"{m.platform_price}€" for m in mismatches]
        message = (
            f"Precio incoherente: en otra plataforma aparece a {', '.join(parts)} "
            f"pero aquí lo tienes a {v.price}€ — Google rechaza el feed por esto."
        )
    return CheckResult(
        "c10", "Coherencia de precio cross-plataforma", passed,
        POINTS_PRICE_COHERENCE if passed else 0, POINTS_PRICE_COHERENCE,
        message, {"n_edges_checked": len(v.platform_edges), "n_mismatches": len(mismatches)},
    )


def _check_no_stagnation(v: VehicleAuditInput) -> CheckResult:
    passed = v.price_drops_30d < STAGNATION_MIN_DROPS
    return CheckResult(
        "c11", "Sin señal de estancamiento", passed,
        POINTS_NO_STAGNATION if passed else 0, POINTS_NO_STAGNATION,
        "Sin bajadas de precio repetidas recientes." if passed
        else f"{v.price_drops_30d} bajadas de precio en {STAGNATION_WINDOW_DAYS} días: el anuncio está estancado.",
        {"price_drops_30d": v.price_drops_30d, "window_days": STAGNATION_WINDOW_DAYS},
    )


_ALL_CHECKS = (
    _check_price, _check_make_model, _check_year, _check_km, _check_vin,
    _check_fuel_transmission, _check_photo_present, _check_photo_size,
    _check_title_richness, _check_price_coherence, _check_no_stagnation,
)


def evaluate(v: VehicleAuditInput) -> AuditResult:
    """Run all 11 checks and return the aggregate score + evidence — the SINGLE
    function both the production job (scripts/run_listing_audit.py) and the
    independent verifier (scripts/verify_listing_audit.py) call, so "one engine, two
    callers" rather than "two engines" (S7 protocol row 1 needs an INDEPENDENT
    recompute of the SAME 11 checks via direct SQL written apart — the independence is
    in the SQL/data-fetch path, not in re-deriving the scoring formula, which must stay
    identical or a legitimate methodology difference would be indistinguishable from a
    bug)."""
    checks = tuple(fn(v) for fn in _ALL_CHECKS)
    score = sum(c.points_awarded for c in checks)
    return AuditResult(vehicle_ulid=v.vehicle_ulid, score=score, checks=checks)

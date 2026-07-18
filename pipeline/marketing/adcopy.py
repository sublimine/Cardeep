"""C7 — grounded ad copy generation (plans/cardeep-omni/07-marketing.md S4 C7, S8, F5).

Pipeline (carta S8): SQL resuelve hechos -> snapshot+claims -> LLM caro redacta -> gate
determinista casa numerales -> ``grounded`` o ``rejected``. This module owns every step
EXCEPT the actual model call, which is injected (``LlmClient`` protocol) exactly like
``pipeline/delta_photo.py``'s ``fetch`` and ``pipeline/marketing/photo_dims.py``'s
network fetch — the pure logic (facts -> claims -> prompt -> gate) is 100%
offline-testable with a fake/deterministic client, and the REAL model call is a
separate, explicit wiring decision.

GASTO GATE (carta F5: "coste por generación medido y registrado... requiere su OK"):
this repository has NO LLM API credential configured anywhere (verified: no
ANTHROPIC_API_KEY/OPENAI_API_KEY in requirements/.env.example/services/api) — the SAME
class of gap as 05-multiposting's AS24 credential (F5, gated) and 06's WhatsApp Business
API (F7, gated). ``generate_copy`` therefore REQUIRES an explicit ``llm_client`` argument
with no default; the router (services/api/routers/marketing.py) checks for a configured
provider at request time and returns 503 declaring the gap rather than silently
fabricating copy or crashing. The full pipeline is built, tested, and ready to receive a
real client the moment the owner supplies one and signs off on the per-generation budget.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Protocol

# ---------------------------------------------------------------------------
# Facts (resolved by SQL, one query per fact — never re-derived by the LLM)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PricePositionFact:
    ratio: float
    band: str  # 'below_market' | 'at_market' | 'above_market'
    segment_n: int
    segment_p50: float
    scope: str  # 'prov' | 'nat'
    province_name: str | None


@dataclass(frozen=True)
class AdCopyFacts:
    vehicle_ulid: str
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    currency: str
    fuel: str | None
    transmission: str | None
    title: str | None
    price_position: PricePositionFact | None  # None = no comparables / no price / etc.
    platform_count: int  # count of OTHER platforms this vehicle is listed on (status='listed')


@dataclass(frozen=True)
class Claim:
    claim_id: str
    text: str                       # human-readable assertion, shown to the dealer as provenance
    numeric_values: tuple[str, ...]  # digit-only strings that must be traceable to THIS claim
    provenance: str                 # which query/endpoint backs this claim


def _extract_numerals(text: str) -> set[str]:
    """Digit-sequences (>=2 digits after stripping thousands/decimal punctuation) found
    in *text* — used both to seed the "vehicle identity" claim below (model names like
    "320d" carry digits that are NOT market assertions) and by the grounding gate
    further down. A lone single digit ("opción 1", "modo 2") is not claim-worthy and is
    skipped to avoid false rejections."""
    raw = re.findall(r"\d[\d.,]*\d|\d", text)
    out: set[str] = set()
    for r in raw:
        digits = re.sub(r"[.,]", "", r)
        if len(digits) >= 2:
            out.add(digits)
    return out


def build_claims(facts: AdCopyFacts) -> list[Claim]:
    """Every claim the copy is ALLOWED to make a number about. A numeral in the
    generated text that maps to NO claim here fails the gate (carta S4 C7: "Una
    afirmacion sin respaldo = generacion rechazada").

    Includes a "vehicle_identity" claim seeded from make/model/title's OWN digits
    (e.g. "320d", "C220d") — these are NOT market assertions needing verification, they
    are the vehicle's fixed identity, already given by ``facts`` itself. Without this,
    a perfectly honest copy that simply names the car (e.g. "BMW 320d") would fail the
    gate on "320" having no market claim behind it — a false rejection, not a real one.
    """
    claims: list[Claim] = []

    identity_source = " ".join(p for p in (facts.make, facts.model, facts.title) if p)
    identity_numerals = _extract_numerals(identity_source) if identity_source else set()
    if identity_numerals:
        claims.append(Claim(
            claim_id="vehicle_identity",
            text=f"{facts.make or ''} {facts.model or ''}".strip(),
            numeric_values=tuple(sorted(identity_numerals)),
            provenance="vehicle.make / vehicle.model / vehicle.title",
        ))

    if facts.price_position is not None:
        pp = facts.price_position
        pct = abs(round((pp.ratio - 1.0) * 100))
        scope_label = f"provincia de {pp.province_name}" if pp.scope == "prov" and pp.province_name else "España"
        direction = "por debajo de" if pp.band == "below_market" else "por encima de" if pp.band == "above_market" else "en línea con"
        claims.append(Claim(
            claim_id="price_position",
            text=f"{pct}% {direction} la mediana de {pp.segment_n} comparables verificados en {scope_label}, hoy",
            numeric_values=(str(pct), str(pp.segment_n)),
            provenance="market.py::compute_price_position (M2, 01-market-intelligence)",
        ))

    if facts.km is not None:
        claims.append(Claim(
            claim_id="km", text=f"{facts.km} km reales, censados por Cardeep",
            numeric_values=(str(facts.km),), provenance="vehicle.km",
        ))

    if facts.year is not None:
        claims.append(Claim(
            claim_id="year", text=f"año {facts.year}",
            numeric_values=(str(facts.year),), provenance="vehicle.year",
        ))

    if facts.platform_count > 0:
        claims.append(Claim(
            claim_id="platform_presence",
            text=f"presente en {facts.platform_count} plataforma{'s' if facts.platform_count != 1 else ''} más, verificado hoy",
            numeric_values=(str(facts.platform_count),),
            provenance="platform_listing (status=listed, count por vehicle_ulid)",
        ))

    return claims


# ---------------------------------------------------------------------------
# Snapshot — persisted input for caching + audit (carta S8: "Cacheable por
# (vehicle_ulid, hash(input_snapshot))")
# ---------------------------------------------------------------------------

def build_snapshot(facts: AdCopyFacts, claims: list[Claim]) -> dict[str, Any]:
    return {
        "vehicle_ulid": facts.vehicle_ulid,
        "make": facts.make, "model": facts.model, "year": facts.year, "km": facts.km,
        "price": facts.price, "currency": facts.currency, "fuel": facts.fuel,
        "transmission": facts.transmission,
        "price_position": (
            {"ratio": facts.price_position.ratio, "band": facts.price_position.band,
             "segment_n": facts.price_position.segment_n, "scope": facts.price_position.scope}
            if facts.price_position else None
        ),
        "platform_count": facts.platform_count,
        "claims": [{"claim_id": c.claim_id, "text": c.text} for c in claims],
    }


def snapshot_hash(snapshot: dict[str, Any]) -> str:
    canonical = json.dumps(snapshot, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Prompt construction (deterministic — the LLM only redacts, never calculates,
# carta S8: "el LLM solo redacta, no calcula ni recuerda nada")
# ---------------------------------------------------------------------------

def build_prompt(facts: AdCopyFacts, claims: list[Claim]) -> str:
    vehicle_desc = " ".join(p for p in (facts.make, facts.model, str(facts.year) if facts.year else None) if p) or "este vehículo"
    facts_block = "\n".join(f"- {c.text} (fuente: {c.provenance})" for c in claims)
    return (
        "Redacta una descripción de venta profesional, en español de compraventa (no genérico "
        f"de SaaS), para: {vehicle_desc}.\n\n"
        "HECHOS VERIFICADOS que PUEDES mencionar (y solo estos, con sus cifras exactas):\n"
        f"{facts_block or '(sin hechos verificados adicionales — describe solo lo genérico, sin inventar cifras)'}\n\n"
        "No inventes ninguna cifra, comparable, plataforma o afirmación que no esté en la lista "
        "anterior. Si no hay datos suficientes para una afirmación de precio, no la hagas."
    )


# ---------------------------------------------------------------------------
# LLM client injection point (GASTO gate — see module docstring)
# ---------------------------------------------------------------------------

class LlmClient(Protocol):
    def __call__(self, prompt: str) -> str: ...


class LlmNotConfiguredError(RuntimeError):
    """Raised when generate_copy is invoked without a real LLM client — the honest,
    declared state of this repository today (no API credential exists anywhere)."""


# ---------------------------------------------------------------------------
# Gate — deterministic claim/numeral matching (carta S4 C7, S7 protocol row 7)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GateResult:
    grounded: bool
    unbacked_numerals: tuple[str, ...]


def check_claims_grounded(output_text: str, claims: list[Claim]) -> GateResult:
    """Every numeral appearing in *output_text* must be traceable to at least one claim
    (carta S4 C7: "cada afirmacion factual... mapeada a la query y valor que la
    respalda"). A numeral with NO backing claim fails the gate — the whole generation
    is rejected, never silently trimmed."""
    output_numerals = _extract_numerals(output_text)
    backed: set[str] = set()
    for c in claims:
        backed |= set(c.numeric_values)
    unbacked = output_numerals - backed
    return GateResult(grounded=len(unbacked) == 0, unbacked_numerals=tuple(sorted(unbacked)))


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AdCopyResult:
    vehicle_ulid: str
    status: str  # 'grounded' | 'rejected'
    output_text: str | None
    claims: list[Claim]
    snapshot: dict[str, Any]
    snapshot_hash: str
    unbacked_numerals: tuple[str, ...]
    model_used: str | None


def generate_copy(facts: AdCopyFacts, llm_client: LlmClient, *, model_name: str) -> AdCopyResult:
    """Full F5 pipeline for one vehicle. Raises NOTHING for the "no comparables"/"no
    price" cases (those simply produce fewer claims — the prompt tells the model not to
    invent a price claim); the ONLY hard failure mode is the grounding gate rejecting an
    output that invented a numeral.

    ``llm_client`` has NO default — see module docstring's GASTO gate. Callers (the
    router) are responsible for resolving/injecting a real client or returning 503 if
    none is configured; this function never silently falls back to a fake redaction
    that could be mistaken for real LLM output.
    """
    claims = build_claims(facts)
    snapshot = build_snapshot(facts, claims)
    prompt = build_prompt(facts, claims)
    output_text = llm_client(prompt)
    gate = check_claims_grounded(output_text, claims)

    return AdCopyResult(
        vehicle_ulid=facts.vehicle_ulid,
        status="grounded" if gate.grounded else "rejected",
        output_text=output_text if gate.grounded else None,
        claims=claims,
        snapshot=snapshot,
        snapshot_hash=snapshot_hash(snapshot),
        unbacked_numerals=gate.unbacked_numerals,
        model_used=model_name,
    )

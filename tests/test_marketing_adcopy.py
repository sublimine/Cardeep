"""TDD for pipeline/marketing/adcopy.py (C7, plans/cardeep-omni/07-marketing.md S4/S9
F5). Pure unit tests, no DB, no real LLM — the injected client is a deterministic fake
so the GATE logic is exercised exactly, per the module's own offline-testable design.
"""
from __future__ import annotations

import pytest

from pipeline.marketing.adcopy import (
    AdCopyFacts,
    Claim,
    GateResult,
    PricePositionFact,
    build_claims,
    build_prompt,
    build_snapshot,
    check_claims_grounded,
    generate_copy,
    snapshot_hash,
)


def _facts(**overrides) -> AdCopyFacts:
    base = dict(
        vehicle_ulid="V1", make="BMW", model="320d", year=2021, km=68000,
        price=19900.0, currency="EUR", fuel="Diésel", transmission="Automático",
        title="BMW 320d 2021",
        price_position=PricePositionFact(
            ratio=0.94, band="below_market", segment_n=23, segment_p50=21100.0,
            scope="prov", province_name="Alicante",
        ),
        platform_count=2,
    )
    base.update(overrides)
    return AdCopyFacts(**base)


class TestBuildClaims:
    def test_perfect_facts_produce_all_claim_types(self):
        claims = build_claims(_facts())
        ids = {c.claim_id for c in claims}
        assert ids == {"vehicle_identity", "price_position", "km", "year", "platform_presence"}

    def test_price_position_claim_carries_correct_numerals(self):
        claims = build_claims(_facts())
        pp = next(c for c in claims if c.claim_id == "price_position")
        assert "6" in pp.numeric_values  # round(|0.94-1|*100) = 6
        assert "23" in pp.numeric_values
        assert "Alicante" in pp.text

    def test_no_price_position_produces_no_price_claim(self):
        claims = build_claims(_facts(price_position=None))
        ids = {c.claim_id for c in claims}
        assert "price_position" not in ids

    def test_zero_platform_count_produces_no_presence_claim(self):
        claims = build_claims(_facts(platform_count=0))
        ids = {c.claim_id for c in claims}
        assert "platform_presence" not in ids

    def test_national_scope_omits_province_name(self):
        facts = _facts(price_position=PricePositionFact(
            ratio=1.1, band="above_market", segment_n=50, segment_p50=20000.0,
            scope="nat", province_name=None,
        ))
        claims = build_claims(facts)
        pp = next(c for c in claims if c.claim_id == "price_position")
        assert "España" in pp.text


class TestSnapshot:
    def test_snapshot_is_deterministic(self):
        facts = _facts()
        claims = build_claims(facts)
        s1 = build_snapshot(facts, claims)
        s2 = build_snapshot(facts, claims)
        assert snapshot_hash(s1) == snapshot_hash(s2)

    def test_snapshot_hash_changes_with_different_facts(self):
        claims_a = build_claims(_facts())
        claims_b = build_claims(_facts(km=50000))
        h1 = snapshot_hash(build_snapshot(_facts(), claims_a))
        h2 = snapshot_hash(build_snapshot(_facts(km=50000), claims_b))
        assert h1 != h2


class TestPrompt:
    def test_prompt_includes_all_claim_texts(self):
        facts = _facts()
        claims = build_claims(facts)
        prompt = build_prompt(facts, claims)
        for c in claims:
            assert c.text in prompt

    def test_prompt_forbids_invention(self):
        prompt = build_prompt(_facts(), build_claims(_facts()))
        assert "No inventes" in prompt

    def test_empty_claims_still_produces_valid_prompt(self):
        facts = _facts(price_position=None, km=None, year=None, platform_count=0, make=None, model=None, title=None)
        prompt = build_prompt(facts, build_claims(facts))
        assert "sin hechos verificados adicionales" in prompt


class TestGate:
    def test_grounded_when_every_numeral_is_backed(self):
        claims = [Claim("km", "68000 km", ("68000",), "vehicle.km")]
        result = check_claims_grounded("Un coche con 68000 km impecable.", claims)
        assert result.grounded
        assert result.unbacked_numerals == ()

    def test_rejected_when_a_numeral_has_no_claim(self):
        claims = [Claim("km", "68000 km", ("68000",), "vehicle.km")]
        result = check_claims_grounded("Solo 12000 km, una ganga.", claims)
        assert not result.grounded
        assert "12000" in result.unbacked_numerals

    def test_single_digit_numerals_never_trigger_rejection(self):
        claims: list[Claim] = []
        result = check_claims_grounded("Es la opción 1 de esta categoría.", claims)
        assert result.grounded

    def test_fabricated_comparable_count_is_caught(self):
        """The exact adversarial case the carta's F5 verification demands: inject a
        false claim (a comparable count the facts never produced) and confirm rejection."""
        claims = build_claims(_facts())
        fabricated = "Un 6% por debajo de la mediana de 999 comparables verificados."
        result = check_claims_grounded(fabricated, claims)
        assert not result.grounded
        assert "999" in result.unbacked_numerals

    def test_percentages_and_currency_formatting_still_match(self):
        claims = [Claim("price_position", "6% por debajo", ("6",), "x")]
        result = check_claims_grounded("Un 6% por debajo de la mediana.", claims)
        assert result.grounded

    def test_model_name_digits_are_pre_backed_by_vehicle_identity_claim(self):
        """A model name like '320d' or 'C220d' carries digits that are NOT market
        assertions — build_claims must seed a vehicle_identity claim so simply naming
        the car never triggers a false rejection."""
        facts = _facts()
        claims = build_claims(facts)
        result = check_claims_grounded("Un BMW 320d en perfecto estado.", claims)
        assert result.grounded


class TestGenerateCopyOrchestration:
    def test_grounded_generation_end_to_end(self):
        facts = _facts()

        def fake_llm(prompt: str) -> str:
            assert "BMW 320d" in prompt
            return "BMW 320d 2021 con 68000 km, un 6% por debajo de la mediana de 23 comparables."

        result = generate_copy(facts, fake_llm, model_name="fake-test-model")
        assert result.status == "grounded"
        assert result.output_text is not None
        assert result.model_used == "fake-test-model"
        assert result.unbacked_numerals == ()

    def test_rejected_generation_never_leaks_output_text(self):
        facts = _facts()

        def hallucinating_llm(prompt: str) -> str:
            return "Un chollazo a 17 comparables de otra provincia, con VIN limpio garantizado."

        result = generate_copy(facts, hallucinating_llm, model_name="fake-test-model")
        assert result.status == "rejected"
        assert result.output_text is None  # never serve unverified copy, even partially
        assert "17" in result.unbacked_numerals

    def test_snapshot_persisted_even_on_rejection(self):
        """Carta S8: 'lo rechazado tambien se persiste (auditoria del gate)' — the
        snapshot/claims must be available regardless of the gate's verdict."""
        facts = _facts()
        result = generate_copy(facts, lambda p: "999 comparables inventados", model_name="m")
        assert result.snapshot["vehicle_ulid"] == "V1"
        assert len(result.claims) > 0

    def test_no_comparables_vehicle_gets_copy_without_price_claim(self):
        facts = _facts(price_position=None)

        def fake_llm(prompt: str) -> str:
            assert "precio" not in prompt.lower() or "no la hagas" in prompt.lower()
            return "BMW 320d 2021 con 68000 km, bien cuidado."

        result = generate_copy(facts, fake_llm, model_name="fake-test-model")
        assert result.status == "grounded"

"""Eval set for the free-text query parser (plan Bloque 1.3).

The plan's own ship order puts this BEFORE any model-backed fallback lane, and the
reason is discipline rather than caution: the only honest way to decide whether a
language model is needed is to measure where the deterministic lane actually
fails. Without a corpus, "the parser struggles with natural phrasing" is a feeling.

The corpus is written the way people write, not the way a parser likes to read:
misspellings, missing accents, colloquial phrasing, and the two extremes the owner
named — the buyer who types "Mercedes C63 S AMG" and the one who types "coche rojo
grande de familia".

Each case declares only what it EXPECTS to be resolved. A case may leave a field
out entirely; the assertion is never "nothing else was found", because resolving
more than the test demands is not a failure.

`xfail` marks the cases the deterministic lane is not expected to handle. They are
in the corpus deliberately: they are the specification for a fallback lane, and
the day one is built this file measures whether it earned its cost.

Run:  python -m pytest tests/test_search_parse_eval.py -q
      python -m pytest tests/test_search_parse_eval.py -q -rX   # show the gaps
"""
from __future__ import annotations

import asyncio
import os

import asyncpg
import pytest

from services.api.search_parse import QueryParser

DSN = os.environ.get(
    "CARDEEP_DSN", "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
)

# (query, expected fields). Only the listed fields are asserted.
CASES: list[tuple[str, dict]] = [
    # ── expert: the buyer who already knows the car ───────────────────────────
    ("BMW Serie 3 diesel por menos de 15.000 euros",
     {"make": "BMW", "model": "Serie 3", "fuel": "diesel", "price_max": 15000}),
    ("mercedes clase c",
     {"make": "Mercedes-Benz", "model": "Clase C"}),
    ("audi a4 avant automatico desde 2018",
     {"make": "Audi", "model": "A4", "transmission": "automatico", "year_min": 2018}),
    ("volkswagen golf gti",
     {"make": "Volkswagen"}),
    ("peugeot 208 gasolina hasta 12000 euros",
     {"make": "Peugeot", "model": "208", "fuel": "gasolina", "price_max": 12000}),
    # A bare year is an EXACT year, and it must not eat a model number: the same
    # four digits are a year here and a model in "peugeot 2008" two cases above.
    ("seat leon 2020",
     {"make": "SEAT", "model": "Leon", "year_min": 2020, "year_max": 2020}),
    ("porsche macan",
     {"make": "Porsche", "model": "Macan"}),
    # THE ambiguity: 2008 is a Peugeot model and 2020 is a year, and they are the
    # same shape. Resolving the model first is what tells them apart — read as a
    # year up front, this would have eaten the 2008, 3008 and 5008 out of the range.
    ("peugeot 2008 diesel",
     {"make": "Peugeot", "model": "2008", "fuel": "diesel"}),
    ("peugeot 3008 de 2021",
     {"make": "Peugeot", "model": "3008", "year_min": 2021}),
    # ── accents dropped, as people actually type ──────────────────────────────
    ("citroen c3 con menos de 60.000 km",
     {"make": "Citroën", "model": "C3", "km_max": 60000}),
    ("skoda octavia diesel",
     {"make": "Škoda", "model": "Octavia", "fuel": "diesel"}),
    ("renault megane",
     {"make": "Renault", "model": "Megane"}),
    # ── naive: the buyer who knows the shape, not the badge ───────────────────
    ("coche rojo grande de familia",
     {"color": "rojo", "is_family": True}),
    ("un suv familiar en Valencia",
     {"body_type": "suv", "is_family": True, "province_code": "46"}),
    ("monovolumen en Sevilla",
     {"body_type": "monovolumen", "province_code": "41"}),
    ("coche electrico por menos de 20.000 euros en Madrid",
     {"fuel": "electrico", "price_max": 20000, "province_code": "28"}),
    ("hibrido con menos de 50.000 km cerca de Barcelona",
     {"fuel": "hibrido", "km_max": 50000, "province_code": "08"}),
    ("furgoneta diesel",
     {"body_type": "furgoneta", "fuel": "diesel"}),
    ("descapotable rojo",
     {"body_type": "cabrio", "color": "rojo"}),
    ("berlina automatica en Bizkaia",
     {"body_type": "berlina", "transmission": "automatico", "province_code": "48"}),
    # ── budget only: no brand knowledge at all ────────────────────────────────
    ("menos de 5.000 euros y menos de 150.000 km",
     {"price_max": 5000, "km_max": 150000}),
    ("hasta 10000 euros",
     {"price_max": 10000}),
    # ── province naming, in every shape the country writes it ─────────────────
    ("coches en A Coruña", {"province_code": "15"}),
    ("en Alicante", {"province_code": "03"}),
    ("gasolina en Islas Baleares", {"fuel": "gasolina", "province_code": "07"}),
]

# Cases the deterministic lane is NOT expected to resolve. Each names the missing
# capability, so the list doubles as the specification for a fallback lane.
XFAIL_CASES: list[tuple[str, dict, str]] = [
    ("algo barato para ir a trabajar", {"price_max": 8000},
     "'barato' is a judgement, not a bound — needs a price model, not a parser"),
    ("un coche para llevar a los niños al colegio", {"is_family": True},
     "intent stated by purpose, with no vocabulary the census shares"),
    ("quiero un coche familiar que no gaste mucho", {"is_family": True, "fuel": "hibrido"},
     "'que no gaste mucho' is a judgement about consumption, which the census does not store"),
    ("un utilitario que gaste poco", {"body_type": "utilitario", "fuel": "hibrido"},
     "'que gaste poco' implies consumption, which the census does not store"),
    ("algo tipo Golf pero mas barato", {"model": "Golf"},
     "comparative reference — needs similarity, not lookup"),
]


@pytest.fixture(scope="module")
def parser() -> QueryParser:
    async def _load() -> QueryParser:
        conn = await asyncpg.connect(DSN)
        try:
            return await QueryParser.load(conn)
        finally:
            await conn.close()

    return asyncio.run(_load())


def _check(parser: QueryParser, query: str, expected: dict) -> None:
    got = parser.parse(query).to_dict()
    for field, want in expected.items():
        assert field in got, f"{query!r}: no resolvió {field} (obtuvo {got})"
        assert got[field] == want, f"{query!r}: {field}={got[field]!r}, esperaba {want!r}"


@pytest.mark.parametrize("query,expected", CASES, ids=[c[0] for c in CASES])
def test_deterministic_lane(parser: QueryParser, query: str, expected: dict) -> None:
    _check(parser, query, expected)


@pytest.mark.parametrize(
    "query,expected",
    [pytest.param(q, e, marks=pytest.mark.xfail(strict=False, reason=r)) for q, e, r in XFAIL_CASES],
    ids=[c[0] for c in XFAIL_CASES],
)
def test_fallback_lane_specification(parser: QueryParser, query: str, expected: dict) -> None:
    """Documents what a fallback lane would have to add, and reports when it arrives.

    The MARKER, not `pytest.xfail()`. The imperative call aborts the test before the
    assertion runs, so a case marked that way can never report XPASS — which made
    the previous version of this file structurally incapable of doing the one job
    its own docstring claimed: telling us the day a missing capability shows up. It
    was a list of things declared impossible, permanently, by construction.

    With the marker the body actually executes. A case that starts passing is
    reported as XPASS and someone has to come and delete it from the list.
    """
    _check(parser, query, expected)


def test_never_invents(parser: QueryParser) -> None:
    """A sentence with nothing to resolve must resolve NOTHING.

    This is the guard on the owner's standing rule against random results. A
    parser that reaches for a match when none exists is how a query gets quietly
    widened into a page of cars nobody asked for.
    """
    got = parser.parse("hola buenas tardes").to_dict()
    for field in ("make", "model", "fuel", "color", "body_type", "province_code"):
        assert field not in got, f"inventó {field}={got[field]!r} sobre un saludo"


def test_seats_are_resolved_not_reported(parser: QueryParser) -> None:
    """"7 plazas" is a filter now, and this case is the proof it stopped being noise.

    It used to assert the opposite — that "plazas" came back unresolved — because
    that was true: the word landed in the leftovers while "familiar" quietly
    resolved to the estate BODY STYLE, and the owner's own example answered 4.001
    cars where it means 58.052.
    """
    got = parser.parse("monovolumen 7 plazas en Sevilla").to_dict()
    assert got.get("body_type") == "monovolumen"
    assert got.get("seats_min") == 7
    assert got.get("province_code") == "41"
    assert not got.get("unresolved")


def test_seat_count_beats_the_word_familiar(parser: QueryParser) -> None:
    """"familiar" beside a seat count is a requirement, not a body style.

    On its own the word means the estate shape. "Coche familiar 7 plazas" is not
    asking for an estate with seven seats — a combination that barely exists — it
    is asking for room for seven.
    """
    got = parser.parse("coche familiar 7 plazas").to_dict()
    assert got.get("seats_min") == 7
    assert got.get("is_family") is True
    assert got.get("body_type") is None


def test_the_euro_sign_resolves_a_price(parser: QueryParser) -> None:
    """`€` must survive normalisation.

    It did not: `norm()` stripped every non-alphanumeric before the bound patterns
    ran, so the `€` branch of the price regex was unreachable and three of the
    examples the field teaches people to type lost their budget in silence. The
    eval corpus missed it for a year of writing because every case in it said
    "euros".
    """
    for query in ("menos de 20.000 €", "por menos de 20.000 euros", "hasta 20.000€"):
        got = parser.parse(query).to_dict()
        assert got.get("price_max") == 20000, f"{query!r} -> {got}"


def test_reports_what_it_did_not_understand(parser: QueryParser) -> None:
    """An unknown word is returned, never dropped.

    Dropping it silently is what widens a query into results nobody asked for.
    """
    got = parser.parse("monovolumen con techo panoramico").to_dict()
    assert got.get("body_type") == "monovolumen"
    assert "panoramico" in got.get("unresolved", [])

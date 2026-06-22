"""SEAT / Das WeltAuto connector — pure parser of the per-card data-configuration/data-partner blobs.

Fixture mirrors real HTML-entity-encoded attributes captured live 2026-06-22 (copersa dealer page).
"""
import html as _html
import json

import pytest

from pipeline.platform.seat_dasweltauto import (
    _slug,
    parse_seat_cards,
    parse_seat_dealer,
    seat_total,
)

pytestmark = pytest.mark.unit


def _attr(d):
    return _html.escape(json.dumps(d), quote=True)


CAR1 = {"VehicleManufacturer": "SEAT", "Carline": {"Name": "Ibiza"},
        "Model": {"Name": "SEAT Ibiza 1.0 TSI FR XL 110 CV", "Year": "2023"},
        "Vehicle": {"VehicleId": "151638480", "Milage": "94.960 km", "Registration": "0064MHD"},
        "Engine": {"FuelType": {"Main": "Gasolina"}},
        "Budget": {"Price": {"price": "14990"}}}
CAR2 = {"VehicleManufacturer": "CUPRA", "Carline": {"Name": "Formentor"},
        "Model": {"Name": "CUPRA Formentor 1.5 TSI", "Year": "2022"},
        "Vehicle": {"VehicleId": "151000001", "Milage": "30.000 km"},
        "Engine": {"FuelType": {"Main": "Gasolina"}},
        "Budget": {"Price": {"price": "28.500"}}}
PARTNER = {"InformationBnr": "03743", "InformationName": "COPERSA",
           "InformationCity": "Ourense", "InformationZIP": "32005"}

HTML = f"""
<div class="results">numberOfResults":"66"</div>
<article data-configuration="{_attr(CAR1)}" data-partner="{_attr(PARTNER)}"></article>
<article data-configuration="{_attr(CAR2)}" data-partner="{_attr(PARTNER)}"></article>
<article data-configuration="{_attr(CAR1)}" data-partner="{_attr(PARTNER)}"></article>
"""


def test_total():
    assert seat_total(HTML) == 66
    assert seat_total("<div>no count</div>") == 0


def test_dealer():
    d = parse_seat_dealer(HTML)
    assert d["bnr"] == "03743" and d["name"] == "COPERSA"
    assert d["city"] == "Ourense" and d["zip"] == "32005"


def test_cards_parse_and_dedup():
    cars = parse_seat_cards(HTML)
    assert len(cars) == 2                               # CAR1 appears twice -> deduped by VehicleId
    c1 = next(c for c in cars if c["ref"] == "151638480")
    assert c1["make"] == "SEAT" and c1["model"] == "Ibiza" and c1["year"] == 2023
    assert c1["km"] == 94960 and c1["price"] == 14990.0 and c1["fuel"] == "Gasolina"
    assert c1["title"] == "SEAT Ibiza 1.0 TSI FR XL 110 CV"
    assert c1["url"] == "https://www.dasweltauto.es/esp/vehiculo/151638480"
    c2 = next(c for c in cars if c["ref"] == "151000001")
    assert c2["make"] == "CUPRA" and c2["price"] == 28500.0 and c2["km"] == 30000


def test_empty():
    assert parse_seat_cards("<html></html>") == []
    assert parse_seat_dealer("<html></html>") is None


def test_slug_extract():
    assert _slug("https://www.concesionarios.seat/home/overview-dw.dealer.amarco-car.html") == "amarco-car"
    assert _slug(".../ofertas-coches-nuevos-stock.dealer.sarsa.html?idcmp=x") == "sarsa"
    assert _slug("https://example.com/no-slug") is None

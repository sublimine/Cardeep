"""Audi SCS used-car connector — pure parser of vehicleBasic.

Fixture mirrors a real vehicleBasic[0] captured live 2026-06-22: model.description, modelYear,
typedPrices (retail = selling price), carId, entryUrl, dealer.dealerContextLinkData[0].
"""
import pytest

from pipeline.platform.audi_used import parse_audi, total_count, vehicle_from_audi

pytestmark = pytest.mark.unit


CAR = {
    "carId": "ESP05346127430246",
    "entryUrl": "https://entry.audi.com/entry?country=ES&id=RVNQMDUzNDY",
    "model": {"code": "aacv", "description": "Audi A1 Sportback Adrenalin 1.0 TFSI 70 kW"},
    "modelYear": 2018,
    "typedPrices": [{"amount": 21313.0, "type": "regular"}, {"amount": 13590.0, "type": "retail"}],
    "fuel": {"description": "Gasolina"},
    "dealer": {"city": "Leioa", "dealerContextLinkData": [
        {"dealerId": "05346", "groupName": "LEIOA WAGEN"}]},
}


def test_vehicle_from_audi_real():
    v = vehicle_from_audi(CAR)
    assert v["make"] == "Audi" and v["model"].startswith("Audi A1 Sportback")
    assert v["year"] == 2018
    assert v["price"] == 13590.0          # retail selling price, not the 'regular' 21313
    assert v["km"] is None                # not exposed in this feed (honest)
    assert v["ref"] == "ESP05346127430246"
    assert v["url"].startswith("https://entry.audi.com/entry")
    assert v["dealer_id"] == "05346" and v["dealer_name"] == "LEIOA WAGEN" and v["city"] == "Leioa"


def test_no_carid_is_none():
    assert vehicle_from_audi({"model": {"description": "x"}}) is None


def test_parse_and_count():
    page = {"totalCount": 4082, "vehicleBasic": [CAR, {**CAR, "carId": "X2",
            "dealer": {"city": "Madrid", "dealerContextLinkData": [{"dealerId": "01", "groupName": "B"}]}}]}
    vs = parse_audi(page)
    assert len(vs) == 2 and {v["dealer_id"] for v in vs} == {"05346", "01"}
    assert total_count(page) == 4082


def test_parse_empty():
    assert parse_audi({"vehicleBasic": []}) == []
    assert total_count({}) == 0

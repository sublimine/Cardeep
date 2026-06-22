"""BMW STOLO used-car connector — pure parser of the vehiclesearch hits.

Fixture mirrors a real hit captured live 2026-06-22: vehicle.vehicleSpecification.modelAndOption,
vehicleLifeCycle.mileage.km, ordering.{productionData,distributionData}, offering.offerPrices
(real used price = offerGrossPrice keyed by the dealer buno, NOT price.grossSalesPrice/list price).
"""
import pytest

from pipeline.platform.bmw_used import parse_bmw_page, total_count, vehicle_from_bmw

pytestmark = pytest.mark.unit


HIT = {"score": 0, "vehicle": {
    "documentId": "WBA11AB0205U82863", "vssId": "018e92de-2ef2-7196",
    "price": {"grossSalesPrice": 44863.19},                      # list price -> must NOT be used
    "offering": {"offerPrices": {"34177": {"offerGrossPrice": 28900, "offerNetPrice": 23884.3}}},
    "vehicleLifeCycle": {"mileage": {"km": 98516}},
    "vehicleSpecification": {"modelAndOption": {"brand": "BMW", "model": {"modelName": "X1 xDrive20i"}}},
    "ordering": {"productionData": {"productionDate": "2021-12-22"},
                 "distributionData": {"destinationLocationDomesticDealerBuno": "34177",
                                      "destinationLocationDomesticDealerName": "Cabrero Motorsport, S.L."}},
}}


def test_vehicle_from_bmw_real():
    v = vehicle_from_bmw(HIT)
    assert v["make"] == "BMW" and v["model"] == "X1 xDrive20i" and v["year"] == 2021
    assert v["km"] == 98516
    assert v["price"] == 28900.0          # offerGrossPrice (used), NOT 44863 list price
    assert v["ref"] == "WBA11AB0205U82863"
    assert v["url"] == "https://www.bmw.es/es/coches-ocasion/vehicle/018e92de-2ef2-7196"
    assert v["dealer_id"] == "34177" and v["dealer_name"] == "Cabrero Motorsport, S.L."


def test_no_vehicle_is_none():
    assert vehicle_from_bmw({"score": 0}) is None


def test_parse_and_count():
    page = {"metadata": {"totalCount": 3331}, "hits": [HIT]}
    vs = parse_bmw_page(page)
    assert len(vs) == 1 and vs[0]["price"] == 28900.0
    assert total_count(page) == 3331


def test_parse_empty():
    assert parse_bmw_page({"hits": []}) == []
    assert total_count({}) == 0

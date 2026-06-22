"""Toyota used-car connector — pure parser of the usedcars/results JSON.

Fixture mirrors a real result captured live 2026-06-22 (product.brand/model/modelYear,
price.sellingPriceInclVAT, dealer.localId/name/address.city). HTTP + cage validated in vivo.
"""
import pytest

from pipeline.platform.toyota_used import parse_toyota_results, total_count, vehicle_from_result

pytestmark = pytest.mark.unit


RESULT = {
    "id": "e893ff61-84dd-4bb7-8424-75a82b0667d0", "vin": "YAREDYHT2RJ925025", "mileage": 15000,
    "price": {"sellingPriceInclVAT": 21450, "sellingPriceExclVAT": 0},
    "product": {"brand": {"code": "38", "description": "Toyota"},
                "model": {"code": "CR", "description": "Corolla"}, "modelYear": "2021"},
    "productionDate": "2021-12-03",
    "dealer": {"localId": "1900-6", "name": "SAKURAUTO TOYOTA VALENCIA",
               "address": {"city": "Pista de Silla", "region": "Valencia"}},
}


def test_vehicle_from_result_real():
    v = vehicle_from_result(RESULT)
    assert v["make"] == "Toyota" and v["model"] == "Corolla" and v["year"] == 2021
    assert v["km"] == 15000 and v["price"] == 21450.0
    assert v["ref"] == "YAREDYHT2RJ925025"
    assert v["url"] == "https://www.toyota.es/coches-segunda-mano/vo/e893ff61-84dd-4bb7-8424-75a82b0667d0"
    assert v["dealer_local"] == "1900-6" and v["city"] == "Pista de Silla"


def test_no_id_is_none():
    assert vehicle_from_result({**RESULT, "id": None}) is None


def test_parse_and_count():
    page = {"totalResultCount": 3157, "results": [RESULT, {**RESULT, "id": "x2",
            "product": {"brand": {"description": "Toyota"}, "model": {"description": "Yaris"},
                        "modelYear": "2023"}, "dealer": {"localId": "2000-1", "name": "B"}}]}
    vs = parse_toyota_results(page)
    assert len(vs) == 2 and {v["model"] for v in vs} == {"Corolla", "Yaris"}
    assert {v["dealer_local"] for v in vs} == {"1900-6", "2000-1"}
    assert total_count(page) == 3157


def test_parse_empty():
    assert parse_toyota_results({"results": []}) == []
    assert total_count({}) == 0

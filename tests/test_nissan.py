"""Nissan PACE used-car connector — pure parser of the GraphQL response.

Fixture mirrors a real vehicle captured live 2026-06-22 (data.getUsedCarsInventoryData.vehicles[]).
Token fetch + GraphQL POST validated in vivo; this tests the pure parse/normalize only.
"""
import pytest

from pipeline.platform.nissan_used import parse_nissan_page, total_pages, vehicle_from_nissan

pytestmark = pytest.mark.unit


VEH = {
    "vin": "VMQIFDH44X549055", "make": "NISSAN", "modelName": "NOTE", "version": "1.2 Acenta",
    "mileage": "91587.0", "registrationYear": "2012", "fuelType": "Gasolina",
    "rrpPrice": 7500.0, "discountedPrice": 6990.0, "vehiclesku": "SKU123",
    "dealer": {"dealerId": "41020118", "dealerName": "QUADIS LLANSA"},
}
RESP = {"data": {"getUsedCarsInventoryData": {
    "metaData": {"totalCount": 1526, "totalPages": 102, "pageIndex": 1, "hasMorePages": True},
    "vehicles": [VEH, {**VEH, "vin": "V2", "vehiclesku": "SKU2", "modelName": "QASHQAI",
                       "dealer": {"dealerId": "99", "dealerName": "B"}}]}}}


def test_vehicle_from_nissan_real():
    v = vehicle_from_nissan(VEH)
    assert v["make"] == "Nissan" and v["model"] == "NOTE" and v["year"] == 2012
    assert v["km"] == 91587 and v["price"] == 6990.0          # discountedPrice wins over rrpPrice
    assert v["ref"] == "VMQIFDH44X549055"
    assert v["url"] == "https://ocasion.nissan.es/vehicle/SKU123"
    assert v["dealer_id"] == "41020118" and v["dealer_name"] == "QUADIS LLANSA"


def test_price_falls_back_to_rrp():
    v = vehicle_from_nissan({**VEH, "discountedPrice": None})
    assert v["price"] == 7500.0


def test_parse_and_pages():
    vs = parse_nissan_page(RESP)
    assert len(vs) == 2 and {v["model"] for v in vs} == {"NOTE", "QASHQAI"}
    assert {v["dealer_id"] for v in vs} == {"41020118", "99"}
    assert total_pages(RESP) == 102


def test_parse_empty():
    assert parse_nissan_page({"data": {"getUsedCarsInventoryData": {"vehicles": []}}}) == []
    assert total_pages({}) == 0

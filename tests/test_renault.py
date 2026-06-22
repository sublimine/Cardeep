"""Renault Renew commerce-API connector — pure parser of the products `data` array.

Fixture mirrors a real product captured live 2026-06-22 (es.renew.auto, multi-brand used stock):
brand/model/version labels, modelYear, mileage(+unit), prices[0].priceWithTaxes, productId, dealer.
"""
import pytest

from pipeline.platform.renault_renew import (
    parse_renew_page,
    renew_total,
    vehicle_from_renew,
)

pytestmark = pytest.mark.unit


PROD = {
    "brand": {"label": "RENAULT"},
    "model": {"groupLabel": "CLIO", "label": "CLIO"},
    "version": {"label": "RENAULT  TCe Intens 90CV"},
    "modelYear": 2021,
    "mileage": 48160, "mileageUnit": "KM",
    "vin": "VF1RJA00967596783",
    "productId": "VEH_72405364_2710LRN",
    "identifier": "72405364_2710LRN",
    "energy": {"label": "Gasolina"},
    "prices": [{"priceWithTaxes": 13000, "customerDisplayPrice": 13000}],
    "assets": [{"assetType": "picture", "renditions": [
        {"url": "https://m/file_small.jpg", "resolutionType": "small"},
        {"url": "https://m/file_medium.jpg", "resolutionType": "medium"}]}],
    "dealer": {"dealerId": "72405364_001", "name": "ROMBOSOL AUTO, S.L.",
               "address": {"locality": "RONDA", "postalCode": "29400"}},
    "codeRRFSiteExposition": "72405364",
}
# trade-in of another brand at a Renault dealer (multi-brand) + dealer only in `dealers[]`
PROD2 = {
    "brand": {"label": "FORD"}, "model": {"label": "PUMA"},
    "version": {"label": "1.0 EcoBoost ST-Line X 125"},
    "modelYear": 2022, "mileage": 41246, "mileageUnit": "KM",
    "productId": "VEH_72405286_E3210LWK",
    "prices": [{"customerDisplayPrice": 19300}],
    "dealers": [{"dealerId": "72405286_001", "name": "TALLERES BLAS SERNA, S.A",
                 "address": {"postalCode": "03293"}}],
}


def test_total():
    assert renew_total({"totalElements": 5695}) == 5695
    assert renew_total({}) == 0


def test_vehicle_renault():
    v = vehicle_from_renew(PROD)
    assert v["make"] == "RENAULT" and v["model"] == "CLIO" and v["year"] == 2021
    assert v["km"] == 48160 and v["price"] == 13000.0 and v["fuel"] == "Gasolina"
    assert v["ref"] == "VEH_72405364_2710LRN"
    assert v["url"] == "https://es.renew.auto/vehiculo/VEH_72405364_2710LRN"
    assert v["title"] == "RENAULT CLIO RENAULT  TCe Intens 90CV"
    assert v["photo_url"] == "https://m/file_medium.jpg"
    assert v["dealer_id"] == "72405364_001" and v["dealer_zip"] == "29400"
    assert v["dealer_name"] == "ROMBOSOL AUTO, S.L."


def test_vehicle_multibrand_dealers_fallback():
    v = vehicle_from_renew(PROD2)
    assert v["make"] == "FORD" and v["price"] == 19300.0
    assert v["dealer_id"] == "72405286_001"        # falls back to dealers[0] when `dealer` absent


def test_no_id_is_none():
    assert vehicle_from_renew({"brand": {"label": "X"}}) is None


def test_parse_page():
    page = {"totalElements": 2, "data": [PROD, PROD2]}
    vs = parse_renew_page(page)
    assert len(vs) == 2 and {v["make"] for v in vs} == {"RENAULT", "FORD"}
    assert parse_renew_page({"data": []}) == []

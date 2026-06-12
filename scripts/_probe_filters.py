"""Probe: does the FULL canonical payload make filters take effect?
Send the complete initialSearch shape, vary ONE facet, watch totalResults move."""
from curl_cffi import requests as r
import json
import copy

H = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.coches.net",
    "Referer": "https://www.coches.net/segunda-mano/",
    "X-Schibsted-Tenant": "coches",
}
ENDPOINT = "https://web.gw.coches.net/search"

# The canonical full payload (from window.__INITIAL_PROPS__.initialSearch), size added.
CANON = {
    "batteryCapacity": {"from": None, "to": None},
    "bodyTypeIds": [], "categoryId": 2500,
    "chargingTimeFastMode": {"from": None, "to": None},
    "chargingTimeStandardMode": {"from": None, "to": None},
    "city": None, "colorIds": [], "commitmentMonths": [], "contractId": 0,
    "doors": {"from": None, "to": None}, "drivenWheelsIds": [],
    "electricAutonomy": {"from": None, "to": None}, "entry": None,
    "environmentalLabels": [], "equipments": [], "fee": {"from": None, "to": None},
    "fuelTypeIds": [], "hasInstalment": False, "hasOnlineFinancing": None,
    "hasPhoto": None, "hasPriceDrop": None, "hasReservation": None, "hasStock": None,
    "hasWarranty": None, "hp": {"from": None, "to": None},
    "instalment": {"from": None, "to": None}, "isCertified": False,
    "kms": {"from": None, "to": None}, "litres": {"from": None, "to": None},
    "location": {"lat": None, "long": None, "radio": None, "text": None, "provinceId": None},
    "luggageCapacity": {"from": None, "to": None}, "maxTerms": None, "offerTypeId": 0,
    "onlyPeninsula": False, "price": {"from": None, "to": None}, "priceDrop": None,
    "priceRank": [], "provinceIds": [], "rating": {"from": None, "to": None},
    "region": None, "searchText": None, "seats": {"from": None, "to": None},
    "sellerTypeId": 0, "targetBuyer": None, "transmissionTypeId": 0,
    "subscriptionVehicleState": None, "vehicles": [], "year": {"from": None, "to": None},
    "sortBy": "relevance", "sortOrder": "DESC", "page": 1, "model": {"name": ""},
    "pagination": {"page": 1, "size": 1},
}


def total(mut):
    body = copy.deepcopy(CANON)
    mut(body)
    resp = r.post(ENDPOINT, json=body, headers=H, impersonate="chrome131", timeout=40)
    if resp.status_code != 200:
        return f"HTTP{resp.status_code}"
    d = json.loads(resp.content.decode("utf-8"))
    return d.get("meta", {}).get("totalResults")


print("FULL canonical baseline:", total(lambda b: None))


def set_prov_in_location(b):
    b["location"]["provinceId"] = 28


def set_prov_ids(b):
    b["provinceIds"] = [28]


def set_price(b):
    b["price"] = {"from": 0, "to": 2000}


def set_year(b):
    b["year"] = {"from": 2024, "to": 2026}


def set_kms(b):
    b["kms"] = {"from": 0, "to": 5000}


print("location.provinceId=28 :", total(set_prov_in_location))
print("provinceIds=[28]       :", total(set_prov_ids))
print("price 0-2000           :", total(set_price))
print("year 2024-2026         :", total(set_year))
print("kms 0-5000             :", total(set_kms))

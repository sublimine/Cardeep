"""Probe: try /search/ (trailing slash, canonical path) with full payload + a province
filter, and try alternative gateways. Watch totalResults move below 272k."""
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

CANON = {
    "batteryCapacity": {"from": None, "to": None}, "bodyTypeIds": [], "categoryId": 2500,
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


def hit(url, mut, hdr=H):
    body = copy.deepcopy(CANON)
    mut(body)
    try:
        resp = r.post(url, json=body, headers=hdr, impersonate="chrome131", timeout=40)
    except Exception as e:
        return f"ERR {e}"
    if resp.status_code != 200:
        return f"HTTP{resp.status_code} ({resp.text[:60]})"
    d = json.loads(resp.content.decode("utf-8"))
    return d.get("meta", {}).get("totalResults")


prov28 = lambda b: b.update({"provinceIds": [28]}) or b["location"].update({"provinceId": 28})
noop = lambda b: None

for url in ["https://web.gw.coches.net/search/",
            "https://web.gw.coches.net/search"]:
    print(url)
    print("   baseline:", hit(url, noop))
    print("   prov28  :", hit(url, prov28))

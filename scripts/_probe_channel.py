"""Probe: add X-Adevinta-* channel headers; the gateway may only honor filters when
the request looks like the SPA (channel/page-url/referer headers present)."""
from curl_cffi import requests as r
import json
import copy

BASE_H = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.coches.net",
    "Referer": "https://www.coches.net/segunda-mano/",
    "X-Schibsted-Tenant": "coches",
}
CHANNEL_H = dict(BASE_H, **{
    "X-Adevinta-Channel": "web",
    "X-Adevinta-Page-Url": "https://www.coches.net/madrid/segunda-mano/",
    "X-Adevinta-Referer": "https://www.coches.net/segunda-mano/",
})

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
URL = "https://web.gw.coches.net/search"


def hit(mut, hdr):
    body = copy.deepcopy(CANON)
    mut(body)
    resp = r.post(URL, json=body, headers=hdr, impersonate="chrome131", timeout=40)
    if resp.status_code != 200:
        return f"HTTP{resp.status_code}"
    return json.loads(resp.content.decode("utf-8")).get("meta", {}).get("totalResults")


def prov(b):
    b["provinceIds"] = [28]
    b["location"]["provinceId"] = 28


def price(b):
    b["price"] = {"from": 0, "to": 1500}


for label, hdr in [("BASE headers", BASE_H), ("CHANNEL headers", CHANNEL_H)]:
    print(label)
    print("   baseline:", hit(lambda b: None, hdr))
    print("   prov28  :", hit(prov, hdr))
    print("   price<1500:", hit(price, hdr))

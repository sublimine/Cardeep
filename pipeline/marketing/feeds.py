"""C6 — feed export (plans/cardeep-omni/07-marketing.md S4 C6, S2 spec table).

Deterministic templates only, ZERO LLM (carta S8: "Generación de feeds C6: Plantillas
deterministas, cero LLM — Un feed spec es un contrato: se cumple con codigo, no con
probabilidad"). Three targets, each with its OWN required-field set codified from S2's
research table:

  google_vehicle_ads  — developers.google.com/vehicle-listings spec (S2 row 1).
  meta_aia            — Meta Automotive Inventory Ads (S2 row 2).
  schema_org_jsonld    — schema.org Thing>Product>Vehicle>Car rich-result (S2 row 3).

Every generator is pure: (VehicleFeedInput, DealerFeedInput) -> FeedItemResult, with
missing/unavailable fields listed BY NAME, never silently blank-filled or fabricated.
Two known, declared schema gaps (Cardeep's ``vehicle`` table, migrations/0003, has no
``body_style``/``exterior_color`` column): Meta AIA's optional ``body_style`` and
``exterior_color`` fields are OMITTED, not sent as empty strings pretending to be real
absence-of-value — the row is still valid without them (S2: not in Meta's base-required
set).
"""
from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Literal

FeedTarget = Literal["google_vehicle_ads", "meta_aia", "schema_org_jsonld"]
TARGETS: tuple[FeedTarget, ...] = ("google_vehicle_ads", "meta_aia", "schema_org_jsonld")

# c8's floor, reused here verbatim (a feed image below this fails Google's own policy,
# S2 row 1: "Imagenes >=800x600px sin overlays/watermarks/logos").
MIN_IMAGE_WIDTH = 800
MIN_IMAGE_HEIGHT = 600

_VIN_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")

# Cardeep is, by construction, a used/pre-owned marketplace census (migrations/0003 has
# no new-vs-used flag) -- every servable vehicle is declared 'used' for feed purposes.
# Declared default, not a per-vehicle fabrication: the product genuinely has no new-car
# inventory concept today.
DEFAULT_CONDITION = "used"


@dataclass(frozen=True)
class DealerFeedInput:
    cdp_code: str
    trade_name: str | None
    address: str | None
    postcode: str | None
    municipality_name: str | None
    province_name: str | None


@dataclass(frozen=True)
class VehicleFeedInput:
    vehicle_ulid: str
    deep_link: str
    title: str | None
    make: str | None
    model: str | None
    year: int | None
    km: int | None
    price: float | None
    currency: str
    fuel: str | None
    transmission: str | None
    photo_url: str | None
    photo_width: int | None
    photo_height: int | None
    vin_ref: str | None


@dataclass(frozen=True)
class FeedItemResult:
    vehicle_ulid: str
    valid: bool
    missing_fields: tuple[str, ...]
    row: dict[str, Any] | None  # None when invalid — never a half-built row


def _valid_vin(vin: str | None) -> str | None:
    if not vin:
        return None
    v = vin.strip().upper()
    return v if _VIN_PATTERN.match(v) else None


def _valid_photo(v: VehicleFeedInput) -> bool:
    return (
        v.photo_url is not None
        and v.photo_width is not None and v.photo_height is not None
        and v.photo_width >= MIN_IMAGE_WIDTH and v.photo_height >= MIN_IMAGE_HEIGHT
    )


# ---------------------------------------------------------------------------
# Google Vehicle Ads (S2 row 1)
# ---------------------------------------------------------------------------

_GOOGLE_REQUIRED = (
    "vin", "store_code", "dealership_name", "dealership_address", "price",
    "condition", "make", "model", "year", "mileage", "image_link",
)


def build_google_vehicle_ads_item(v: VehicleFeedInput, d: DealerFeedInput) -> FeedItemResult:
    vin = _valid_vin(v.vin_ref)
    address_parts = [p for p in (d.address, d.postcode, d.municipality_name, d.province_name) if p]
    address = ", ".join(address_parts) if address_parts else None

    row = {
        "vin": vin,
        "store_code": d.cdp_code,
        "dealership_name": d.trade_name,
        "dealership_address": address,
        "price": f"{v.price:.2f} {v.currency}" if v.price is not None else None,
        "condition": DEFAULT_CONDITION,
        "make": v.make,
        "model": v.model,
        "trim": None,  # not modeled in Cardeep's schema — omitted, not fabricated
        "year": v.year,
        "mileage": f"{v.km} KM" if v.km is not None else None,
        "image_link": v.photo_url if _valid_photo(v) else None,
        "link": v.deep_link,
    }
    missing = tuple(f for f in _GOOGLE_REQUIRED if row.get(f) is None)
    valid = len(missing) == 0
    return FeedItemResult(v.vehicle_ulid, valid, missing, row if valid else None)


# ---------------------------------------------------------------------------
# Meta Automotive Inventory Ads (S2 row 2)
# ---------------------------------------------------------------------------

_META_REQUIRED = (
    "id", "title", "price", "currency", "availability", "condition", "url",
    "image_link", "make", "model", "vin", "mileage", "year",
)


def build_meta_aia_item(v: VehicleFeedInput, d: DealerFeedInput) -> FeedItemResult:
    vin = _valid_vin(v.vin_ref)
    row: dict[str, Any] = {
        "id": v.vehicle_ulid,
        "title": v.title,
        "price": f"{v.price:.2f} {v.currency}" if v.price is not None else None,
        "currency": v.currency,
        "availability": "in stock",
        "condition": DEFAULT_CONDITION,
        "url": v.deep_link,
        "image_link": v.photo_url if _valid_photo(v) else None,
        "state_of_vehicle": DEFAULT_CONDITION,
        "make": v.make,
        "model": v.model,
        "vin": vin,
        "mileage": v.km,
        "year": v.year,
        "transmission": v.transmission,
        "fuel_type": v.fuel,
        # body_style / exterior_color: NOT sent — migrations/0003's `vehicle` table has
        # no such columns. Meta's spec lists these as part of the "auto" extension set,
        # not the base-required set, so their absence does not invalidate the row.
    }
    missing = tuple(f for f in _META_REQUIRED if row.get(f) is None)
    valid = len(missing) == 0
    return FeedItemResult(v.vehicle_ulid, valid, missing, row if valid else None)


# ---------------------------------------------------------------------------
# schema.org JSON-LD (S2 row 3, Google's "Vehicle Listing" rich result)
# ---------------------------------------------------------------------------

_SCHEMA_ORG_REQUIRED = ("itemCondition", "mileageFromOdometer")


def build_schema_org_jsonld_item(v: VehicleFeedInput, d: DealerFeedInput) -> FeedItemResult:
    vin = _valid_vin(v.vin_ref)
    jsonld: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Car",
        "itemCondition": f"https://schema.org/{'UsedCondition' if DEFAULT_CONDITION == 'used' else 'NewCondition'}",
        "mileageFromOdometer": (
            {"@type": "QuantitativeValue", "value": v.km, "unitCode": "KMT"} if v.km is not None else None
        ),
        "url": v.deep_link,
        "offers": {
            "@type": "Offer",
            "price": v.price,
            "priceCurrency": v.currency,
            "availability": "https://schema.org/InStock",
        } if v.price is not None else None,
    }
    if vin:
        jsonld["vehicleIdentificationNumber"] = vin
    if v.make:
        jsonld["brand"] = {"@type": "Brand", "name": v.make}
    if v.model:
        jsonld["model"] = v.model
    if v.year:
        jsonld["vehicleModelDate"] = str(v.year)
    if v.fuel:
        jsonld["fuelType"] = v.fuel
    if v.transmission:
        jsonld["vehicleTransmission"] = v.transmission
    if v.photo_url:
        jsonld["image"] = v.photo_url
    # driveWheelConfiguration / numberOfDoors / color / vehicleEngine: NOT modeled in
    # Cardeep's schema today — omitted from the recommended-but-optional set, never
    # fabricated. Declared schema gap (carta S2 row 3's "recomendados" list).

    row = {k: v2 for k, v2 in jsonld.items() if v2 is not None}
    missing = tuple(f for f in _SCHEMA_ORG_REQUIRED if row.get(f) is None)
    valid = len(missing) == 0
    return FeedItemResult(v.vehicle_ulid, valid, missing, row if valid else None)


_BUILDERS = {
    "google_vehicle_ads": build_google_vehicle_ads_item,
    "meta_aia": build_meta_aia_item,
    "schema_org_jsonld": build_schema_org_jsonld_item,
}


@dataclass(frozen=True)
class FeedResult:
    target: FeedTarget
    item_count: int
    valid_count: int
    invalid_report: tuple[dict[str, Any], ...]  # [{vehicle_ulid, missing_fields}, ...]
    content: str
    content_type: str


def _csv_content(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), extrasaction="ignore")
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    return buf.getvalue()


def generate_feed(
    target: FeedTarget, vehicles: list[VehicleFeedInput], dealer: DealerFeedInput,
) -> FeedResult:
    """Build the full feed for one target across a dealer's inventory. A vehicle that
    fails validation is EXCLUDED from the downloadable content but listed, with its
    exact failing field names, in ``invalid_report`` — carta S4 C6: "Un feed con <100%
    se puede descargar igualmente pero con el informe de fallos delante — sin
    maquillaje."
    """
    if target not in _BUILDERS:
        raise ValueError(f"unknown feed target: {target}")
    builder = _BUILDERS[target]

    results = [builder(v, dealer) for v in vehicles]
    valid_rows = [r.row for r in results if r.valid and r.row is not None]
    invalid_report = tuple(
        {"vehicle_ulid": r.vehicle_ulid, "missing_fields": list(r.missing_fields)}
        for r in results if not r.valid
    )

    if target == "schema_org_jsonld":
        content = json.dumps(valid_rows, ensure_ascii=False, indent=2)
        content_type = "application/ld+json"
    else:
        content = _csv_content(valid_rows)
        content_type = "text/csv"

    return FeedResult(
        target=target, item_count=len(vehicles), valid_count=len(valid_rows),
        invalid_report=invalid_report, content=content, content_type=content_type,
    )

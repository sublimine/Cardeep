"""TDD for pipeline/marketing/feeds.py (C6, plans/cardeep-omni/07-marketing.md S4/S9
F3: "suite de tests campo-por-campo contra el spec"). Pure unit tests, no DB.
"""
from __future__ import annotations

import csv
import io
import json

import pytest

from pipeline.marketing.feeds import (
    DEFAULT_CONDITION,
    MIN_IMAGE_HEIGHT,
    MIN_IMAGE_WIDTH,
    DealerFeedInput,
    VehicleFeedInput,
    build_google_vehicle_ads_item,
    build_meta_aia_item,
    build_schema_org_jsonld_item,
    generate_feed,
)

DEALER = DealerFeedInput(
    cdp_code="CDP-ES-46-TEST0001", trade_name="Autos Ejemplo SL",
    address="Calle Falsa 123", postcode="46001",
    municipality_name="Valencia", province_name="Valencia",
)


def _perfect_vehicle(**overrides) -> VehicleFeedInput:
    base = dict(
        vehicle_ulid="V1", deep_link="https://example.com/coche/1",
        title="BMW 320d 2021 automático", make="BMW", model="320d", year=2021,
        km=68000, price=19900.0, currency="EUR", fuel="Diésel",
        transmission="Automático", photo_url="https://cdn.example.com/1.jpg",
        photo_width=1200, photo_height=900, vin_ref="WBA3A5C50DF595785",
    )
    base.update(overrides)
    return VehicleFeedInput(**base)


class TestGoogleVehicleAds:
    def test_perfect_vehicle_is_valid(self):
        r = build_google_vehicle_ads_item(_perfect_vehicle(), DEALER)
        assert r.valid
        assert r.missing_fields == ()
        assert r.row["vin"] == "WBA3A5C50DF595785"
        assert r.row["condition"] == DEFAULT_CONDITION
        assert r.row["store_code"] == DEALER.cdp_code

    def test_missing_vin_invalidates(self):
        r = build_google_vehicle_ads_item(_perfect_vehicle(vin_ref=None), DEALER)
        assert not r.valid
        assert "vin" in r.missing_fields
        assert r.row is None

    def test_contaminated_vin_treated_as_missing(self):
        """The known real-world contamination pattern (listing-ID mislabeled as
        vin_ref) must not slip through as a valid VIN in the feed either."""
        r = build_google_vehicle_ads_item(_perfect_vehicle(vin_ref="12345678"), DEALER)
        assert not r.valid
        assert "vin" in r.missing_fields

    def test_small_photo_invalidates_image_link(self):
        r = build_google_vehicle_ads_item(
            _perfect_vehicle(photo_width=400, photo_height=300), DEALER,
        )
        assert not r.valid
        assert "image_link" in r.missing_fields

    def test_exact_minimum_photo_size_is_valid(self):
        r = build_google_vehicle_ads_item(
            _perfect_vehicle(photo_width=MIN_IMAGE_WIDTH, photo_height=MIN_IMAGE_HEIGHT), DEALER,
        )
        assert r.valid

    def test_missing_price_invalidates(self):
        r = build_google_vehicle_ads_item(_perfect_vehicle(price=None), DEALER)
        assert not r.valid
        assert "price" in r.missing_fields

    def test_missing_dealer_address_invalidates(self):
        bare_dealer = DealerFeedInput(
            cdp_code="CDP-X", trade_name="X", address=None, postcode=None,
            municipality_name=None, province_name=None,
        )
        r = build_google_vehicle_ads_item(_perfect_vehicle(), bare_dealer)
        assert not r.valid
        assert "dealership_address" in r.missing_fields

    def test_price_string_includes_currency(self):
        r = build_google_vehicle_ads_item(_perfect_vehicle(), DEALER)
        assert r.row["price"] == "19900.00 EUR"


class TestMetaAIA:
    def test_perfect_vehicle_is_valid(self):
        r = build_meta_aia_item(_perfect_vehicle(), DEALER)
        assert r.valid
        assert r.row["id"] == "V1"
        assert "body_style" not in r.row
        assert "exterior_color" not in r.row

    def test_missing_mileage_invalidates(self):
        r = build_meta_aia_item(_perfect_vehicle(km=None), DEALER)
        assert not r.valid
        assert "mileage" in r.missing_fields

    def test_missing_vin_invalidates(self):
        r = build_meta_aia_item(_perfect_vehicle(vin_ref=None), DEALER)
        assert not r.valid
        assert "vin" in r.missing_fields


class TestSchemaOrgJsonLd:
    def test_perfect_vehicle_is_valid(self):
        r = build_schema_org_jsonld_item(_perfect_vehicle(), DEALER)
        assert r.valid
        assert r.row["@type"] == "Car"
        assert r.row["mileageFromOdometer"]["value"] == 68000
        assert r.row["vehicleIdentificationNumber"] == "WBA3A5C50DF595785"

    def test_missing_mileage_invalidates_per_google_rich_result_minimum(self):
        r = build_schema_org_jsonld_item(_perfect_vehicle(km=None), DEALER)
        assert not r.valid
        assert "mileageFromOdometer" in r.missing_fields

    def test_no_condition_field_ever_omitted(self):
        r = build_schema_org_jsonld_item(_perfect_vehicle(), DEALER)
        assert r.row["itemCondition"] == "https://schema.org/UsedCondition"

    def test_no_vin_still_valid_since_vin_is_recommended_not_required(self):
        r = build_schema_org_jsonld_item(_perfect_vehicle(vin_ref=None), DEALER)
        assert r.valid
        assert "vehicleIdentificationNumber" not in r.row


class TestGenerateFeedAggregate:
    def test_mixed_batch_reports_invalid_with_exact_fields(self):
        vehicles = [
            _perfect_vehicle(vehicle_ulid="good-1"),
            _perfect_vehicle(vehicle_ulid="bad-1", vin_ref=None),
            _perfect_vehicle(vehicle_ulid="bad-2", price=None, km=None),
        ]
        result = generate_feed("google_vehicle_ads", vehicles, DEALER)
        assert result.item_count == 3
        assert result.valid_count == 1
        assert len(result.invalid_report) == 2
        bad1 = next(r for r in result.invalid_report if r["vehicle_ulid"] == "bad-1")
        assert bad1["missing_fields"] == ["vin"]
        bad2 = next(r for r in result.invalid_report if r["vehicle_ulid"] == "bad-2")
        assert set(bad2["missing_fields"]) >= {"price", "mileage"}

    def test_csv_output_is_parseable_and_contains_only_valid_rows(self):
        vehicles = [_perfect_vehicle(vehicle_ulid="good-1"), _perfect_vehicle(vehicle_ulid="bad-1", vin_ref=None)]
        result = generate_feed("google_vehicle_ads", vehicles, DEALER)
        rows = list(csv.DictReader(io.StringIO(result.content)))
        assert len(rows) == 1
        assert rows[0]["store_code"] == DEALER.cdp_code

    def test_jsonld_output_is_valid_json_array(self):
        vehicles = [_perfect_vehicle(vehicle_ulid="good-1")]
        result = generate_feed("schema_org_jsonld", vehicles, DEALER)
        parsed = json.loads(result.content)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        assert parsed[0]["@type"] == "Car"

    def test_empty_batch_produces_empty_content_not_an_error(self):
        result = generate_feed("google_vehicle_ads", [], DEALER)
        assert result.item_count == 0
        assert result.valid_count == 0
        assert result.content == ""

    def test_unknown_target_raises(self):
        with pytest.raises(ValueError):
            generate_feed("carfax_xml", [_perfect_vehicle()], DEALER)  # type: ignore[arg-type]

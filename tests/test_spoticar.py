"""Spoticar connector — pure parser of the Elasticsearch paginate/search JSON.

Fixture is a real hit._source captured live 2026-06-22 (Fiat 500 at 'spoticar comauto sport',
geo_id 0000115058). Every scalar is a 1-element array in the API; the parser must unwrap it and
normalize to the canonical vehicle dict. HTTP + cage are validated in vivo, not here.
"""
import pytest

from pipeline.platform.spoticar_api import (
    page_meta,
    parse_spoticar_page,
    vehicle_from_source,
)

pytestmark = pytest.mark.unit


REAL_SOURCE = {
    "marque": ["fiat"], "model": ["500"], "version": ["hb 320km 85kw (118cv)+style+com monotrim"],
    "field_vo_annee_modele": ["2024"], "field_vo_km": [10], "field_vo_prix_base": [21990],
    "field_vo_vin": ["zfaefaa4xpx169902"], "fuel_type": ["ELEC"], "boite_vitesse": ["automatico"],
    "field_pdv_title": ["spoticar comauto sport"], "field_pdv_city": ["castellon"],
    "field_pdv_geo_id": ["0000115058"],
    "url": ["/comprar-vehiculo-de-ocasion/fiat-500-hb-320km-castellon-169902"],
}


def test_vehicle_from_source_real():
    v = vehicle_from_source(REAL_SOURCE)
    assert v["make"] == "fiat" and v["model"] == "500"
    assert v["year"] == 2024 and v["km"] == 10 and v["price"] == 21990.0
    assert v["ref"] == "zfaefaa4xpx169902" and v["fuel"] == "ELEC"
    assert v["geo_id"] == "0000115058" and v["dealer_name"] == "spoticar comauto sport"
    assert v["city"] == "castellon"
    assert v["url"] == "https://www.spoticar.es/comprar-vehiculo-de-ocasion/fiat-500-hb-320km-castellon-169902"
    assert v["title"].startswith("fiat 500")


def test_vehicle_absolute_url_passthrough():
    v = vehicle_from_source({**REAL_SOURCE, "url": ["https://www.spoticar.es/x/y-1"]})
    assert v["url"] == "https://www.spoticar.es/x/y-1"


def test_vehicle_no_url_is_none():
    assert vehicle_from_source({**REAL_SOURCE, "url": []}) is None


def test_parse_page_and_meta():
    page = {"count": {"value": 6411, "relation": "eq"}, "lastPage": 583,
            "hits": [{"_source": REAL_SOURCE}, {"_source": {**REAL_SOURCE,
                     "url": ["/comprar-vehiculo-de-ocasion/peugeot-208-2"], "marque": ["peugeot"],
                     "field_pdv_geo_id": ["0000032788"]}}]}
    vs = parse_spoticar_page(page)
    assert len(vs) == 2
    assert {v["make"] for v in vs} == {"fiat", "peugeot"}
    assert {v["geo_id"] for v in vs} == {"0000115058", "0000032788"}   # carries per-car dealer
    assert page_meta(page) == (6411, 583)


def test_parse_page_empty():
    assert parse_spoticar_page({"hits": []}) == []
    assert page_meta({}) == (0, 1)

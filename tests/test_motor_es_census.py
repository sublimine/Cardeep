"""Offline unit tests for the motor.es CENSUS adapter (Vector 1)."""
from __future__ import annotations

import pytest

from pipeline.sources.motor_es_census import (
    MotorEsCensusAdapter,
    _PROV_INE,
    parse_dealer_page,
    parse_directory_page,
)

_DIR = """
<a href="https://www.motor.es/concesionarios/alicante/">Alicante</a>
<a href="https://www.motor.es/concesionarios/alicante/ankara-motor/">Ankara Motor (Alicante)</a>
<a href="https://www.motor.es/concesionarios/barcelona/adolfo-mariscal-sl/">Adolfo Mariscal Sl (Barcelona)</a>
<a href="https://www.motor.es/concesionarios/2">2</a>
<a href="https://www.motor.es/concesionarios/madrid/">Madrid</a>
"""

_DEALER = """<html><body>
<h1>ANKARA MOTOR (ALICANTE)</h1>
<span itemprop="streetAddress">Crta. de Ocana, 40-42</span>
<span itemprop="addressLocality">Alicante</span>
<span itemprop="postalCode">03006</span>
<a itemprop="telephone">34 637 717 378</a>
</body></html>"""


@pytest.mark.unit
def test_directory_filters_provinces_keeps_dealers():
    d = parse_directory_page(_DIR)
    assert ("alicante", "ankara-motor") in d
    assert ("barcelona", "adolfo-mariscal-sl") in d
    # province index links and pager numbers are not dealers
    assert all(slug not in _PROV_INE and not slug.isdigit() for _p, slug in d)
    # name suffix ' (Province)' stripped to match wholesale seller.name
    assert d[("alicante", "ankara-motor")] == "Ankara Motor"


@pytest.mark.unit
def test_parse_dealer_page_extracts_microdata():
    rec = parse_dealer_page(_DEALER)
    assert rec["name"] == "ANKARA MOTOR"          # h1, province suffix stripped
    assert rec["city"] == "Alicante"
    assert rec["postcode"] == "03006"
    assert rec["phone"] == "+34637717378"         # normalized E.164
    assert rec["street"].startswith("Crta")


@pytest.mark.unit
def test_parse_dealer_page_none_without_h1():
    assert parse_dealer_page("<html>no h1</html>") is None


@pytest.mark.unit
def test_entity_from_has_cdp_matching_address_and_geo():
    a = MotorEsCensusAdapter()
    e = a.entity_from("alicante", "ankara-motor",
                      {"name": "Ankara Motor", "city": "Alicante",
                       "postcode": "03006", "phone": "+34637717378", "street": "x"})
    assert e.source_key == "motor_es_census"
    assert e.kind == "compraventa"
    assert e.address == "concesionario:alicante/ankara-motor"  # matches wholesale cdp input
    assert e.province_name == "03"
    assert e.municipality_name == "Alicante"
    assert e.phone == "+34637717378"
    assert e.website is None
    assert e.extra["vector"] == 1


@pytest.mark.unit
def test_prov_ine_map_is_complete():
    # every distinct INE province code 01..52 is reachable from some motor.es slug
    codes = set(_PROV_INE.values())
    assert len(codes) == 52

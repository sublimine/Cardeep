"""Offline unit tests for the OcasionPlus CENSUS adapter (Vector 1)."""
from __future__ import annotations

import pytest

from pipeline.sources.ocasionplus_census import (
    OcasionPlusCensusAdapter,
    branch_slugs_from_sitemap,
)

_SITEMAP = """<?xml version="1.0"?>
<urlset><url><loc>https://www.ocasionplus.com/concesionarios/albacete</loc></url>
<url><loc>https://www.ocasionplus.com/concesionarios/alicante-san-juan</loc></url>
<url><loc>https://www.ocasionplus.com/concesionarios/</loc></url></urlset>"""


@pytest.mark.unit
def test_sitemap_slugs():
    assert branch_slugs_from_sitemap(_SITEMAP) == ["albacete", "alicante-san-juan"]


@pytest.mark.unit
def test_entity_from_geo_and_identity():
    a = OcasionPlusCensusAdapter()
    e = a.entity_from("alicante", {"name": "OcasionPlus Alicante", "city": "Alicante",
                                   "postcode": "03006", "phone": "+34865616415", "street": "x"})
    assert e.source_key == "ocasionplus_census"
    assert e.address == "ocasionplus:alicante"
    assert e.province_name == "03"
    assert e.municipality_name == "Alicante"
    assert e.phone == "+34865616415"
    assert e.website is None
    assert e.extra["chain"] == "ocasionplus"

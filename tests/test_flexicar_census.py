"""Offline unit tests for the Flexicar CENSUS adapter (Vector 1)."""
from __future__ import annotations

import pytest

from pipeline.sources.flexicar_census import (
    FlexicarCensusAdapter,
    _city_from_slug,
    branch_slugs_from_sitemap,
    parse_branch_page,
)

_SITEMAP = """<urlset>
<url><loc>https://www.flexicar.es/delegaciones-flexicar/</loc></url>
<url><loc>https://www.flexicar.es/delegaciones-flexicar/albacete/</loc></url>
<url><loc>https://www.flexicar.es/delegaciones-flexicar/alcala-de-henares/</loc></url>
<url><loc>https://www.flexicar.es/compramos-tu-coche/madrid/</loc></url>
</urlset>"""


@pytest.mark.unit
def test_sitemap_only_delegaciones():
    assert branch_slugs_from_sitemap(_SITEMAP) == ["albacete", "alcala-de-henares"]


@pytest.mark.unit
def test_city_from_slug_drops_branch_index():
    assert _city_from_slug("alcorcon-2") == "Alcorcon"
    assert _city_from_slug("alcala-de-henares") == "Alcala De Henares"


@pytest.mark.unit
def test_parse_branch_page():
    html = '<h1>Albacete</h1> <a href="tel:+34967800382">call</a>'
    rec = parse_branch_page(html, "albacete")
    assert rec["city"] == "Albacete"
    assert rec["phone"] == "+34967800382"


@pytest.mark.unit
def test_entity_chain_identity():
    e = FlexicarCensusAdapter().entity_from("albacete", {"city": "Albacete", "phone": "+34967800382"})
    assert e.legal_name == "Flexicar Albacete"
    assert e.address == "flexicar:albacete"
    assert e.municipality_name == "Albacete"
    assert e.province_name is None       # resolved via resolve_city_global at upsert
    assert e.extra["chain"] == "flexicar"

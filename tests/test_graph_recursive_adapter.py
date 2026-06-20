"""Offline unit tests for the V5 recursive-graph SourceAdapter.

No network: assert JSON-LD branch extraction, schema.org type matching, the
branch-link hint detector, and registrable-domain handling on fixed HTML.
"""
from __future__ import annotations

import pytest

from pipeline.sources import graph_recursive as gr

_HTML = """<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
 {"@type":"AutoDealer","name":"Quadis Barcelona","url":"https://quadis.es/bcn",
  "telephone":"+34931112233",
  "address":{"@type":"PostalAddress","streetAddress":"Av Diagonal 1",
             "addressLocality":"Barcelona","postalCode":"08019"},
  "geo":{"@type":"GeoCoordinates","latitude":"41.41","longitude":"2.22"}},
 {"@type":"AutoDealer","name":"Quadis Girona",
  "address":{"streetAddress":"C Nou 3","addressLocality":"Girona","postalCode":"17001"}},
 {"@type":"WebSite","name":"Quadis","url":"https://quadis.es"}
]}
</script></head><body>
<a href="/concesionarios">Nuestros concesionarios</a>
<a href="/quienes-somos">Quiénes somos</a>
<a href="https://otro.com/instalaciones">Instalaciones</a>
</body></html>"""


@pytest.mark.unit
def test_registrable_domain():
    assert gr._registrable_domain("https://www.quadis.es/bcn") == "quadis.es"
    assert gr._registrable_domain("https://sub.quadis.es") == "sub.quadis.es"


@pytest.mark.unit
def test_jsonld_branch_extraction():
    a = gr.GraphRecursiveAdapter
    nodes = [n for n in gr._iter_jsonld(_HTML) if gr._type_matches(n)]
    branches = [gr._branch_from_node(n, "https://quadis.es") for n in nodes]
    branches = [b for b in branches if b]
    by_name = {b.trade_name: b for b in branches}
    # both AutoDealer nodes with an address become branches; the WebSite node does not
    assert set(by_name) == {"Quadis Barcelona", "Quadis Girona"}
    bcn = by_name["Quadis Barcelona"]
    assert bcn.source_key == "graph_recursive"
    assert bcn.province_name == "08"           # from postcode
    assert bcn.municipality_name == "Barcelona"
    assert bcn.lat == pytest.approx(41.41)
    assert bcn.website == "https://quadis.es/bcn"
    assert bcn.extra["vector"] == 5


@pytest.mark.unit
def test_branch_links_only_same_domain_location_hints():
    links = gr._branch_links(_HTML, "https://quadis.es")
    # the location-hint, same-domain link is kept; "quienes-somos" and the off-domain
    # "otro.com" link are not followed
    assert links == ["https://quadis.es/concesionarios"]


@pytest.mark.unit
def test_node_without_address_is_skipped():
    node = {"@type": "AutoDealer", "name": "No Address Dealer"}
    assert gr._branch_from_node(node, "https://x.es") is None

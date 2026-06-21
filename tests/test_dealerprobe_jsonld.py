"""DealerProbe component 2 — JSON-LD Car/Vehicle + schema.org microdata parsers (pure).

Recon: JSON-LD Vehicle is the highest-quality (but rarer, 11%) signal; some sites use
schema.org microdata instead (autosantpedor). Both must yield the SAME normalized vehicle
dicts so the cascade can treat them uniformly. Fixtures mirror shapes seen live.
"""
import pytest

from pipeline.platform.dealerprobe import parse_jsonld_vehicles, parse_microdata_vehicles

pytestmark = pytest.mark.unit


# --- JSON-LD ----------------------------------------------------------------------------------
CAR_SINGLE = """
<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Car","name":"BMW X5 3.0d xDrive",
 "url":"https://alcala534.com/coches-ocasion/bmw-x5-17769",
 "brand":{"@type":"Brand","name":"BMW"},"model":"X5","productionDate":"2019",
 "mileageFromOdometer":{"@type":"QuantitativeValue","value":"90000","unitCode":"KMT"},
 "offers":{"@type":"Offer","price":"29990","priceCurrency":"EUR"}}
</script></head><body>...</body></html>
"""

CAR_ARRAY = """
<script type="application/ld+json">
[{"@type":"Car","name":"Seat Leon FR","brand":"Seat","model":"Leon","productionDate":"2021",
  "offers":{"price":24500,"priceCurrency":"EUR"},"url":"https://x.es/c/1"},
 {"@type":"Car","name":"Audi A3","brand":"Audi","model":"A3","dateVehicleFirstRegistered":"2020-05-01",
  "mileageFromOdometer":45000,"offers":{"price":"21000"},"url":"https://x.es/c/2"}]
</script>
"""

GRAPH_WITH_DEALER_AND_CAR = """
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
  {"@type":"AutoDealer","name":"Concesionario X"},
  {"@type":"Vehicle","name":"Opel Corsa","brand":{"name":"Opel"},"model":"Corsa",
   "productionDate":"2022","offers":{"price":"15990"},"url":"https://x.es/v/9"}]}
</script>
"""

DEALER_ONLY = """
<script type="application/ld+json">
{"@type":"AutoDealer","name":"Solo concesionario","url":"https://x.es"}
</script>
"""


def test_jsonld_single_car():
    v = parse_jsonld_vehicles(CAR_SINGLE)
    assert len(v) == 1
    c = v[0]
    assert c["make"] == "BMW" and c["model"] == "X5"
    assert c["year"] == 2019 and c["km"] == 90000 and c["price"] == 29990.0
    assert c["url"].endswith("bmw-x5-17769")


def test_jsonld_array_two_cars_with_fallbacks():
    v = parse_jsonld_vehicles(CAR_ARRAY)
    assert len(v) == 2
    a3 = [x for x in v if x["model"] == "A3"][0]
    assert a3["year"] == 2020           # from dateVehicleFirstRegistered[:4]
    assert a3["km"] == 45000 and a3["price"] == 21000.0


def test_jsonld_graph_keeps_vehicle_drops_dealer():
    v = parse_jsonld_vehicles(GRAPH_WITH_DEALER_AND_CAR)
    assert len(v) == 1 and v[0]["make"] == "Opel" and v[0]["price"] == 15990.0


def test_jsonld_autodealer_only_yields_no_vehicle():
    assert parse_jsonld_vehicles(DEALER_ONLY) == []


def test_jsonld_garbage_is_safe():
    assert parse_jsonld_vehicles("<html>no json here</html>") == []
    assert parse_jsonld_vehicles('<script type="application/ld+json">{bad json</script>') == []


# --- microdata (schema.org/Vehicle) ----------------------------------------------------------
MICRODATA = """
<div itemscope itemtype="https://schema.org/Vehicle">
  <h2 itemprop="name">Audi A4 2.0 TDI</h2>
  <span itemprop="brand">Audi</span>
  <meta itemprop="modelDate" content="2018">
  <span itemprop="mileageFromOdometer">120000</span>
  <div itemprop="offers" itemscope itemtype="https://schema.org/Offer">
    <meta itemprop="price" content="22500">
    <span>22.500 EUR</span>
  </div>
  <a itemprop="url" href="https://autosantpedor.com/Vehiculos/audi-a4/"></a>
</div>
"""


def test_microdata_vehicle():
    v = parse_microdata_vehicles(MICRODATA)
    assert len(v) == 1
    c = v[0]
    assert c["make"] == "Audi"
    assert c["year"] == 2018 and c["price"] == 22500.0
    assert "audi-a4" in (c["url"] or "")


def test_microdata_none_when_absent():
    assert parse_microdata_vehicles("<div>no microdata</div>") == []

"""DealerProbe component 4b-i — per-PDP signal cascade (JSON-LD -> microdata), fetch injected.

Given a per-vehicle detail URL, parse_pdp fetches it and returns ONE normalized vehicle by trying
the signals in quality order (JSON-LD first, then microdata). Pure cascade over the component-2
parsers; offline-testable with a fake fetch. The SSR inline-specs fallback is supplied by the
frontier card (handled in probe_dealer), not here.
"""
import asyncio

import pytest

from pipeline.platform.dealerprobe_wholesale import parse_pdp

pytestmark = pytest.mark.unit


def _run(c):
    return asyncio.run(c)


async def _async(v):
    return v


PDP_JSONLD = """<html><script type="application/ld+json">
{"@type":"Car","name":"BMW X5","brand":{"name":"BMW"},"model":"X5","productionDate":"2019",
 "mileageFromOdometer":{"value":"90000"},"offers":{"price":"29990"}}
</script></html>"""

PDP_MICRODATA = """<div itemscope itemtype="https://schema.org/Vehicle">
 <span itemprop="brand">Audi</span><meta itemprop="modelDate" content="2018">
 <meta itemprop="price" content="22500"></div>"""

PDP_EMPTY = "<html><body>Coche vendido</body></html>"


def test_parse_pdp_jsonld_first():
    v = _run(parse_pdp(lambda u: _async(PDP_JSONLD), "https://x.es/coches/bmw-x5-101"))
    assert v["make"] == "BMW" and v["price"] == 29990.0
    assert v["url"] == "https://x.es/coches/bmw-x5-101"   # url filled from the fetched URL


def test_parse_pdp_microdata_fallback():
    v = _run(parse_pdp(lambda u: _async(PDP_MICRODATA), "https://x.es/vehiculos/audi-a4"))
    assert v["make"] == "Audi" and v["year"] == 2018 and v["price"] == 22500.0
    assert v["url"] == "https://x.es/vehiculos/audi-a4"


def test_parse_pdp_no_vehicle_data_is_none():
    assert _run(parse_pdp(lambda u: _async(PDP_EMPTY), "https://x.es/c/1")) is None


def test_parse_pdp_dead_fetch_is_none():
    assert _run(parse_pdp(lambda u: _async(None), "https://dead.es/c/1")) is None


def test_parse_pdp_keeps_jsonld_url_when_present():
    html = """<script type="application/ld+json">{"@type":"Car","name":"Seat","model":"Leon",
        "offers":{"price":"15000"},"url":"https://x.es/canonical/seat-leon-9"}</script>"""
    v = _run(parse_pdp(lambda u: _async(html), "https://x.es/c/redirected"))
    assert v["url"] == "https://x.es/canonical/seat-leon-9"   # JSON-LD canonical wins over fetch URL

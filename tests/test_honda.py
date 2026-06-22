"""Honda ocasion connector — pure SSR article parser.

Fixture mirrors a real <article id="vehicleMDX-..."> block captured live 2026-06-22 (mcar-madrid):
data-link, IVA-incluido price, <li title=.. data-value> specs, año de matriculación.
"""
import pytest

from pipeline.platform.honda_ocasion import honda_found, parse_honda_cards

pytestmark = pytest.mark.unit


ART = """
<div data-found="28" data-xhr="/es/ocasion/page__PLACEHOLDER__/xhr-results/%25p2%25">
<article id="vehicleMDX-P5DTN6HJ" class="vehicle" data-link="/es/ocasion/honda/civic/executive-cvt-p5dtn6hj">
<div class="font-bold uppercase h6 color-medium-gray">IVA incluido</div>
<div class="h3 font-bold line-height-reset">20.500&nbsp;&euro;</div>
<span class="t-gray" title="A&ntilde;o de matriculaci&oacute;n"><span>2020</span></span>
<ul class="unstyle">
<li class="data-db15" title="Kilometraje"><span class="data-label">Kilometraje</span><span class="data-value">116.648&nbsp;km</span></li>
<li class="data-db12" title="Combustible"><span class="data-label">Combustible</span><span class="data-value">Gasolina</span></li>
</ul></article>
<article id="vehicleMDX-S1DTJSZX" class="vehicle" data-link="/es/ocasion/toyota/yaris/active-s1dtjszx">
<div class="h6">IVA incluido</div><div class="h3 font-bold line-height-reset">14.900&nbsp;&euro;</div>
<ul class="unstyle">
<li title="Kilometraje"><span class="data-label">Kilometraje</span><span class="data-value">60.000&nbsp;km</span></li>
<li title="Combustible"><span class="data-label">Combustible</span><span class="data-value">H&iacute;brido</span></li>
</ul></article>
</div>
"""


def test_found():
    assert honda_found(ART) == 28
    assert honda_found("<div>nope</div>") == 0


def test_parse_cards():
    cars = parse_honda_cards(ART, "mcar-madrid.honda.es")
    assert len(cars) == 2
    c0 = next(c for c in cars if c["ref"] == "P5DTN6HJ")
    assert c0["make"] == "Honda" and c0["model"] == "Civic" and c0["year"] == 2020
    assert c0["km"] == 116648 and c0["price"] == 20500.0 and c0["fuel"] == "Gasolina"
    assert c0["url"] == "https://mcar-madrid.honda.es/es/ocasion/honda/civic/executive-cvt-p5dtn6hj"
    # multi-brand trade-in (allBrands): make derives from the data-link brand segment
    c1 = next(c for c in cars if c["ref"] == "S1DTJSZX")
    assert c1["make"] == "Toyota" and c1["model"] == "Yaris" and c1["price"] == 14900.0
    assert c1["km"] == 60000 and c1["fuel"] == "Híbrido"


def test_empty():
    assert parse_honda_cards("<html>no articles</html>", "x.honda.es") == []

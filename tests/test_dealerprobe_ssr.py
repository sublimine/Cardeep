"""DealerProbe component 3 — SSR-card extractor (fallback when no JSON-LD/microdata).

Recon: 6/35 detectable dealers expose inventory only via server-rendered listing cards
(palaciocasion detalles.php?vehiculo=, automotordursan /coches-segunda-mano/<m>/.. cards).
The generic move: pull every per-vehicle LINK (reuses classify_loc) + the price/km/year that
sit inline in that card's window. make/model are best-effort (the PDP fills them). No JS, no
per-dealer selectors.
"""
import pytest

from pipeline.platform.dealerprobe import extract_vehicle_links, parse_ssr_cards

pytestmark = pytest.mark.unit


LISTING = """
<div class="grid">
  <article class="card">
    <a href="/coches-segunda-mano/bmw/x5/3-0d-2019-90000-17769">BMW X5 3.0d</a>
    <span class="price">29.990 €</span><span class="km">90.000 km</span><span class="y">2019</span>
  </article>
  <article class="card">
    <a href="/coches-segunda-mano/audi/a4/2-0-tdi-2018-60000-17770">Audi A4 2.0 TDI</a>
    <span class="price">21.500 €</span><span class="km">60.000 km</span><span class="y">2018</span>
  </article>
  <a href="/coches-ocasion/">Ver todos los coches</a>
  <a href="/contacto">Contacto</a>
</div>
"""

DETALLES_PHP = """
<ul>
  <li><a href="detalles.php?vehiculo=12345-v-bmw-serie-3">BMW Serie 3</a> <b>18.900 €</b></li>
  <li><a href="detalles.php?vehiculo=12346-v-seat-leon">Seat Leon</a> <b>14.500 €</b></li>
</ul>
"""


def test_extract_vehicle_links_only_per_vehicle():
    links = extract_vehicle_links(LISTING, "https://x.es/coches/")
    assert len(links) == 2
    assert all(l.startswith("https://x.es/coches-segunda-mano/") for l in links)
    # category (/coches-ocasion/) and other (/contacto) are excluded
    assert not any("coches-ocasion" in l or "contacto" in l for l in links)


def test_parse_ssr_cards_links_and_inline_specs():
    cards = parse_ssr_cards(LISTING, "https://x.es/coches/")
    assert len(cards) == 2
    c0 = cards[0]
    assert c0["url"].endswith("17769")
    assert c0["price"] == 29990.0 and c0["km"] == 90000 and c0["year"] == 2019
    c1 = cards[1]
    assert c1["url"].endswith("17770")
    assert c1["price"] == 21500.0 and c1["km"] == 60000 and c1["year"] == 2018


def test_parse_ssr_cards_detalles_php_query_detail():
    cards = parse_ssr_cards(DETALLES_PHP, "https://palaciocasion.es/coches/")
    assert len(cards) == 2
    assert all("detalles.php?vehiculo=" in c["url"] for c in cards)
    assert cards[0]["price"] == 18900.0


def test_parse_ssr_cards_no_links_is_empty():
    assert parse_ssr_cards("<div><a href='/contacto'>x</a><a href='/blog/post'>y</a></div>",
                           "https://x.es/") == []


def test_extract_vehicle_links_excludes_assets():
    # a car-named IMAGE path (palaciocasion home) must NOT be mistaken for a per-vehicle link
    html = """<a href="/wp-content/uploads/2023/11/coches-de-ocasion-asturias-4-1024x682.webp">img</a>
              <a href="/coches-segunda-mano/bmw/x5/2019-90000-17769">real car</a>"""
    links = extract_vehicle_links(html, "https://palaciocasion.es/")
    assert links == ["https://palaciocasion.es/coches-segunda-mano/bmw/x5/2019-90000-17769"]


def test_parse_ssr_cards_price_comma_thousands_and_mojibake():
    # grupobeniautos: comma thousands + '€' decoded to the mojibake replacement char '�'
    html = ('<a href="/listado/fiat-500-pop-555">Fiat 500</a><div class="precio">14,990�</div>'
            '<a href="/listado/citroen-c3-556">Citroen C3</a><b>9.990 &euro;</b>')
    cards = parse_ssr_cards(html, "https://grupobeniautos.com/")
    assert cards[0]["price"] == 14990.0          # comma thousands + mojibake currency
    assert cards[1]["price"] == 9990.0           # dot thousands + &euro; entity


def test_parse_ssr_cards_absolute_links_preserved():
    html = '<a href="https://other.es/coches-segunda-mano/kia/ceed/2021-30000-555">Kia</a> 17.000 €'
    cards = parse_ssr_cards(html, "https://x.es/")
    assert len(cards) == 1 and cards[0]["url"] == "https://other.es/coches-segunda-mano/kia/ceed/2021-30000-555"

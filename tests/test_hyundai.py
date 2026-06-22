"""Hyundai seminuevos connector — pure SSR card parser.

Fixture mirrors a real .ucar-container__item card captured live 2026-06-22. The stable per-car id
is the S3 stock code (the detalle href vid is a per-render token, deliberately NOT used).
"""
import pytest

from pipeline.platform.hyundai_used import parse_hyundai_cards

pytestmark = pytest.mark.unit


HTML = """
<div class="ucar-container__item"> <div class="ucar"> <a href="...detalle&amp;concesionario_id=14&amp;vid=PERRENDERTOKENa">
<figure><img src="https://hyundai-vo.s3.eu-west-3.amazonaws.com/public/stock/5192LYW/5192LYW-202-01.jpg"></figure></a>
<div class="ucar__info"><a href="...detalle&amp;concesionario_id=14&amp;vid=DIFFERENTtokenb" class="ucar__info__title">i20 1.0 TGDI N Line 48V 100</a>
<ul class="ucar__info__list"><li class="ucar__info__list__item"><img src="dgt-c.png"></li>
<li class="ucar__info__list__item">15.000km</li><li class="ucar__info__list__item">2023</li>
<li class="ucar__info__list__item">Manual</li></ul>
<div class="ucar__info__price"><p class="ucar__info__price__num">21.990</p></div></div></div></div>
<div class="ucar-container__item"> <div class="ucar"><a href="x"><figure><img
src="https://hyundai-vo.s3.eu-west-3.amazonaws.com/public/stock/9999ABC/9999ABC-1.jpg"></figure></a>
<div class="ucar__info"><a class="ucar__info__title">Tucson 1.6</a>
<ul class="ucar__info__list"><li class="ucar__info__list__item">40.000km</li>
<li class="ucar__info__list__item">2021</li></ul>
<div class="ucar__info__price"><p class="ucar__info__price__num">28.500</p></div></div></div></div>
"""


def test_parse_cards_stock_code_keyed():
    cars = parse_hyundai_cards(HTML)
    assert len(cars) == 2
    c0 = next(c for c in cars if c["ref"] == "5192LYW")
    assert c0["model"] == "i20 1.0 TGDI N Line 48V 100"
    assert c0["km"] == 15000 and c0["year"] == 2023 and c0["price"] == 21990.0
    assert c0["url"] == "https://www.hyundai.es/seminuevos/5192LYW"   # stable stock code, not vid
    assert c0["concesionario_id"] == "14"
    c1 = next(c for c in cars if c["ref"] == "9999ABC")
    assert c1["model"] == "Tucson 1.6" and c1["km"] == 40000 and c1["price"] == 28500.0


def test_parse_empty():
    assert parse_hyundai_cards("<html>no cards</html>") == []


def test_dedup_same_stock_code():
    dup = HTML + HTML
    cars = parse_hyundai_cards(dup)
    assert len({c["ref"] for c in cars}) == len(cars)   # stock code de-duplicated

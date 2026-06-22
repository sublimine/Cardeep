"""Mercedes ocasion connector — pure parser of the jscache JS document.

Fixture mirrors the real structure captured live 2026-06-22: const order fofisp -> fofili ->
fispor -> dbveda; rows are positional, decoded via fispor (column order) + fofisp (code->label).
"""
import pytest

from pipeline.platform.mercedes_ocasion import parse_mercedes_jscache

pytestmark = pytest.mark.unit


JS = (
    'fofisp={"DEFAULT":{'
    '"brandi":{"val":{"meb":"Mercedes-Benz","amg":"Mercedes-AMG"}},'
    '"modtyp":{"val":{"b180":"Clase B 180","cla35":"CLA 35"}},'
    '"seller":{"val":{"31":"Mercedes Madrid Centro","42":"Mercedes Sevilla"}}}}; '
    'const fofili={"DEFAULT":[]}; '
    'const fispor={"DEFAULT":["area","brandi","modtyp","seller","modyer","mileag","ofprgr","ordnbr"]}; '
    'const dbveda=[[0,"meb","b180","31",2023,25687,30900,"A12345"],'
    '[1,"amg","cla35","42",2022,40000,55900,"A67890"]];</script>'
)


def test_parse_decodes_positional_rows():
    vs = parse_mercedes_jscache(JS)
    assert len(vs) == 2
    v0 = next(v for v in vs if v["ref"] == "A12345")
    assert v0["make"] == "Mercedes-Benz" and v0["model"] == "Clase B 180"
    assert v0["year"] == 2023 and v0["km"] == 25687 and v0["price"] == 30900.0
    assert v0["dealer_name"] == "Mercedes Madrid Centro" and v0["seller_code"] == "31"
    assert v0["url"] == "https://ocasion.mercedes-benz.es/es/coche-ocasion/A12345"
    v1 = next(v for v in vs if v["ref"] == "A67890")
    assert v1["make"] == "Mercedes-AMG" and v1["price"] == 55900.0 and v1["seller_code"] == "42"


def test_parse_empty_or_garbage():
    assert parse_mercedes_jscache("") == []
    assert parse_mercedes_jscache("<html>no consts here</html>") == []

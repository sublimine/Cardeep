"""Offline unit tests for the Páginas Amarillas adapter promotion (§1.4)."""
from __future__ import annotations

import pytest

from pipeline.sources.paginas_amarillas import SOURCE_KEY, _province_of, record_to_entity


@pytest.mark.unit
def test_province_from_postcode_not_crawl_slug():
    # ceuta/melilla slugs fall back to NATIONAL results -> a Madrid listing crawled under the
    # 'ceuta' pass (prov_code='51') must resolve to Madrid (28) from its own postcode, never 51.
    assert _province_of({"postcode": "28038", "prov_code": "51"}) == "28"
    # legit Ceuta listing keeps 51
    assert _province_of({"postcode": "51001", "prov_code": "51"}) == "51"
    # no usable postcode -> fall back to the crawl code (geo still has the locality to try)
    assert _province_of({"postcode": None, "prov_code": "08"}) == "08"
    assert _province_of({"postcode": "00000", "prov_code": "28"}) == "28"


@pytest.mark.unit
def test_record_to_entity_canonical_identity():
    rec = {
        "name": "Talleres La Montaña", "address": "Calle Mayor 3",
        "locality": "Reinosa", "postcode": "39200", "prov_code": "39",
        "phone": "942000000", "website": "https://tallereslamontana.es",
        "activity": "compra venta de coches", "detail": "https://www.paginasamarillas.es/f/x.html",
        "kind": "compraventa", "rubro": "compra-venta-de-coches",
    }
    e = record_to_entity(rec)
    assert e.source_key == SOURCE_KEY
    assert e.kind == "compraventa"
    assert e.legal_name == "Talleres La Montaña"
    assert e.province_name == "39"
    assert e.municipality_name == "Reinosa"
    assert e.website == "https://tallereslamontana.es"   # real domain drives cdp dedup
    assert e.address == "Calle Mayor 3"
    assert e.phone == "942000000"
    assert e.source_ref == "https://www.paginasamarillas.es/f/x.html"
    assert e.extra["source_group"] == "directory"


@pytest.mark.unit
def test_record_to_entity_source_ref_fallback():
    e = record_to_entity({"name": "Desguace Sur", "locality": "Utrera",
                          "prov_code": "41", "kind": "desguace"})
    assert e.source_ref == "Desguace Sur|Utrera"   # no detail URL -> name|locality fallback
    assert e.kind == "desguace"

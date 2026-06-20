"""Offline unit tests for the autocasion CENSUS adapter (Vector 1).

No network, no DB: assert the sitemap dealer-slug filter, the ES phone normalization, and
the JSON-LD AutoDealer profile parse against committed fixtures, plus the identity-matching
invariant (address slot == 'profesional:{slug}') that makes the census dedup against the
wholesale dealers at the cdp_code level.
"""
from __future__ import annotations

import pytest

from pipeline.sources.autocasion_census import (
    AutocasionCensusAdapter,
    _norm_phone_es,
    _province_from_postcode,
    dealer_slugs_from_sitemap,
    parse_profile,
)

_SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
 <url><loc>https://www.autocasion.com/profesional</loc></url>
 <url><loc>https://www.autocasion.com/profesional/madrid</loc></url>
 <url><loc>https://www.autocasion.com/profesional/sta-c-de-tenerife</loc></url>
 <url><loc>https://www.autocasion.com/profesional/automoviles-san-jose-925563</loc></url>
 <url><loc>https://www.autocasion.com/profesional/autocenter-mallorca-adv-6a33fe6a383705</loc></url>
 <url><loc>https://www.autocasion.com/profesional/auto-sprint</loc></url>
</urlset>"""

_PROFILE = """<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"AutoDealer","name":"AUTOMOVILES SAN JOSE",
 "telephone":"+34 - 919374458",
 "url":"https://www.autocasion.com/profesional/automoviles-san-jose-925563",
 "address":{"@type":"PostalAddress","streetAddress":"Calle Caronte 1 bajo 1",
 "addressLocality":"Talavera de la Reina","postalCode":"45600"}}
</script></head><body>x</body></html>"""


@pytest.mark.unit
def test_sitemap_filters_province_pages_and_root():
    slugs = dealer_slugs_from_sitemap(_SITEMAP)
    # the 3 dealers survive; root + 2 province index pages are dropped.
    assert slugs == [
        "automoviles-san-jose-925563",
        "autocenter-mallorca-adv-6a33fe6a383705",
        "auto-sprint",
    ]


@pytest.mark.unit
@pytest.mark.parametrize("raw,expected", [
    ("+34 - 919374458", "+34919374458"),
    ("919 374 458", "+34919374458"),
    ("0034 600111222", "+34600111222"),
    ("+34 600 111 222", "+34600111222"),
    ("12345", None),            # too short -> rejected (no wrong number)
    ("+34 123456789", None),    # leading 1 is not a valid ES subscriber prefix
    (None, None),
])
def test_phone_normalization(raw, expected):
    assert _norm_phone_es(raw) == expected


@pytest.mark.unit
def test_province_from_postcode():
    assert _province_from_postcode("45600") == "45"
    assert _province_from_postcode("28001") == "28"
    assert _province_from_postcode("00123") is None   # 00 is not a valid INE province
    assert _province_from_postcode("ABCDE") is None
    assert _province_from_postcode(None) is None


@pytest.mark.unit
def test_parse_profile_extracts_autodealer():
    rec = parse_profile(_PROFILE)
    assert rec == {
        "name": "AUTOMOVILES SAN JOSE",
        "phone": "+34919374458",
        "street": "Calle Caronte 1 bajo 1",
        "city": "Talavera de la Reina",
        "postcode": "45600",
    }


@pytest.mark.unit
def test_parse_profile_none_without_autodealer():
    assert parse_profile("<html>no jsonld here</html>") is None


@pytest.mark.unit
def test_fetch_emits_identity_matching_entity(monkeypatch):
    # Drive the adapter with canned HTTP so fetch() is fully offline, and assert the
    # cdp-identity invariant: address == 'profesional:{slug}', website None, province from CP.
    import pipeline.sources.autocasion_census as mod

    def fake_get(url, timeout=30, retries=3):
        return _SITEMAP if url.endswith("stock.xml") else _PROFILE

    monkeypatch.setattr(mod, "_http_get", fake_get)
    a = AutocasionCensusAdapter(max_dealers=1, sleep_s=0)
    rows = a.fetch()
    assert a.declared_count() == 1
    assert len(rows) == 1
    e = rows[0]
    assert e.source_key == "autocasion_census"
    assert e.kind == "compraventa"
    assert e.address == "profesional:automoviles-san-jose-925563"  # dedup-matching slot
    assert e.website is None                                       # never the autocasion URL
    assert e.province_name == "45"
    assert e.municipality_name == "Talavera de la Reina"
    assert e.phone == "+34919374458"
    assert e.extra["vector"] == 1
    assert e.extra["street"] == "Calle Caronte 1 bajo 1"

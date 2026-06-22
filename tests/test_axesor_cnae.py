"""Offline unit tests for the axesor.es CNAE-4511/4520 census adapter (Vector 4b).

No network, no DB. The parser is exercised against three REAL committed ficha fixtures
captured live 2026-06-22:

  * axesor_4511_35motormadrid.html — CNAE 4511 (venta de automóviles) -> KEPT, compraventa
  * axesor_4520_17garage.html      — CNAE 4520 (reparación de vehículos) -> KEPT, garaje
  * axesor_6831_realestate.html    — CNAE 6831 (real estate)            -> DROPPED

plus the frontier helpers (ficha-link / municipality-slug / last-page extraction), the
postcode->province rule, and an end-to-end offline fetch() driven by canned HTTP that
asserts the seal-critical invariant: municipality_name is populated, CIF/CNAE/geo carried,
website never set to the axesor profile URL.
"""
from __future__ import annotations

import pathlib

import pytest

from pipeline.sources.axesor_cnae import (
    AxesorCnaeAdapter,
    _ficha_urls,
    _last_page,
    _municipality_slugs,
    _province_from_postcode,
    parse_axesor_ficha,
)

_FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def _load(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Pure parser — real fichas
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_parse_4511_kept_as_compraventa():
    rec = parse_axesor_ficha(_load("axesor_4511_35motormadrid.html"))
    assert rec is not None
    assert rec["cnae"] == "4511"
    assert rec["kind"] == "compraventa"
    assert rec["name"].lower() == "35motormadrid sl"
    assert rec["cif"] == "B67818450"
    assert rec["locality"] == "Coslada"        # addressLocality -> municipality (seal-critical)
    assert rec["region"] == "Madrid"           # addressRegion
    assert rec["postcode"] == "28821"
    assert rec["street"] and "CONSTITUCION" in rec["street"].upper()
    assert rec["lat"] == pytest.approx(40.4270607)
    assert rec["lon"] == pytest.approx(-3.560975)


@pytest.mark.unit
def test_parse_4520_kept_as_garaje():
    rec = parse_axesor_ficha(_load("axesor_4520_17garage.html"))
    assert rec is not None
    assert rec["cnae"] == "4520"
    assert rec["kind"] == "garaje"
    assert rec["name"].lower() == "17 garage sl"
    assert rec["cif"] == "B87860037"
    assert rec["locality"] == "Mostoles"
    assert rec["region"] == "Madrid"
    assert rec["postcode"] == "28935"
    assert rec["lat"] is not None and rec["lon"] is not None


@pytest.mark.unit
def test_parse_non_automotive_dropped():
    # CNAE 6831 (real estate) is not in {4511,4520} -> must be dropped, not mis-kept.
    rec = parse_axesor_ficha(_load("axesor_6831_realestate.html"))
    assert rec is None


@pytest.mark.unit
def test_parse_no_cnae_row_returns_none():
    assert parse_axesor_ficha("<html><body>no cnae, no jsonld</body></html>") is None


@pytest.mark.unit
def test_parse_automotive_cnae_but_no_org_block_returns_none():
    # A CNAE row in scope but no Organization JSON-LD -> useless for the seal -> None.
    html = '<table><tr><th>CNAE</th><td class="x">4511 Venta</td></tr></table>'
    assert parse_axesor_ficha(html) is None


# ---------------------------------------------------------------------------
# Frontier helpers
# ---------------------------------------------------------------------------

_LISTING = """
<a href="//www.axesor.es/Informes-Empresas/9168257/17_GARAGE_SL.html">17 Garage</a>
<a href="/Informes-Empresas/10455540/35MOTORMADRID_SL.html">35</a>
<a href="/Informes-Empresas/9168257/17_GARAGE_SL.html">dup</a>
<a href="//www.axesor.es/directorio-informacion-empresas/empresas-de-Madrid/informacion-empresas-de-Mostoles/1">p1</a>
<a href="//www.axesor.es/directorio-informacion-empresas/empresas-de-Madrid/informacion-empresas-de-Mostoles/2">p2</a>
<a href="//www.axesor.es/directorio-informacion-empresas/empresas-de-Madrid/informacion-empresas-de-Mostoles/173">last</a>
<a href="//www.axesor.es/directorio-informacion-empresas/empresas-de-Madrid/informacion-empresas-de-Getafe/1">other</a>
"""


@pytest.mark.unit
def test_ficha_urls_distinct_absolute():
    urls = _ficha_urls(_LISTING)
    assert urls == [
        "https://www.axesor.es/Informes-Empresas/9168257/17_GARAGE_SL.html",
        "https://www.axesor.es/Informes-Empresas/10455540/35MOTORMADRID_SL.html",
    ]


@pytest.mark.unit
def test_municipality_slugs_distinct():
    assert _municipality_slugs(_LISTING) == ["Mostoles", "Getafe"]


@pytest.mark.unit
def test_last_page_takes_advertised_max():
    assert _last_page(_LISTING, "Mostoles") == 173
    assert _last_page(_LISTING, "Getafe") == 1
    assert _last_page("<html>nada</html>", "Nowhere") == 1


@pytest.mark.unit
@pytest.mark.parametrize("pc,expected", [
    ("28821", "28"), ("28935", "28"), ("01001", "01"),
    ("00123", None), ("ABCDE", None), (None, None),
])
def test_province_from_postcode(pc, expected):
    assert _province_from_postcode(pc) == expected


# ---------------------------------------------------------------------------
# Offline end-to-end fetch() — canned HTTP, no network
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_fetch_keeps_only_automotive_and_populates_municipality(monkeypatch):
    import pipeline.sources.axesor_cnae as mod

    prov_root = (
        '<a href="/directorio-informacion-empresas/empresas-de-Madrid'
        '/informacion-empresas-de-Coslada/1">Coslada</a>')
    muni_p1 = (
        '<a href="/Informes-Empresas/10455540/35MOTORMADRID_SL.html">4511</a>'
        '<a href="/Informes-Empresas/9168257/17_GARAGE_SL.html">4520</a>'
        '<a href="/Informes-Empresas/10386921/13J7_CONSULTING_SL.html">6831</a>'
        '<a href="/directorio-informacion-empresas/empresas-de-Madrid'
        '/informacion-empresas-de-Coslada/1">p1</a>')

    f4511 = _load("axesor_4511_35motormadrid.html")
    f4520 = _load("axesor_4520_17garage.html")
    f6831 = _load("axesor_6831_realestate.html")

    def fake_get(url, *, timeout=30, retries=3):
        if url.endswith("/empresas-de-Madrid"):
            return prov_root
        if url.endswith("/informacion-empresas-de-Coslada/1"):
            return muni_p1
        if "10455540" in url:
            return f4511
        if "9168257" in url:
            return f4520
        if "10386921" in url:
            return f6831
        return None  # any page past the listing -> 404-equivalent

    monkeypatch.setattr(mod, "_http_get", fake_get)

    a = AxesorCnaeAdapter(
        provinces=["Madrid"], max_prov=1, max_fichas=50,
        max_muni=4, max_pages=1, sleep_s=0)
    rows = a.fetch()

    # 3 fichas fetched, 6831 dropped -> 2 kept (4511 + 4520).
    assert a._fichas_seen == 3
    assert a.excluded_count == 1
    assert len(rows) == 2

    by_cnae = {e.cnae: e for e in rows}
    assert set(by_cnae) == {"4511", "4520"}

    e = by_cnae["4511"]
    assert e.source_key == "axesor_cnae"
    assert e.kind == "compraventa"
    assert e.legal_name.lower() == "35motormadrid sl"
    assert e.cif == "B67818450"
    assert e.municipality_name == "Coslada"     # SEAL-CRITICAL: must be populated
    assert e.province_name == "28"              # from postcode 28821 (authoritative)
    assert e.postcode == "28821"
    assert e.lat == pytest.approx(40.4270607)
    assert e.website is None                    # never the axesor profile URL
    assert e.source_ref.endswith("35MOTORMADRID_SL.html")
    assert e.extra["registry"] == "axesor"

    g = by_cnae["4520"]
    assert g.kind == "garaje"
    assert g.municipality_name == "Mostoles"
    assert g.province_name == "28"


@pytest.mark.unit
def test_isolation_when_offline(monkeypatch):
    import pipeline.sources.axesor_cnae as mod
    monkeypatch.setattr(mod, "_http_get", lambda *a, **k: None)
    a = AxesorCnaeAdapter(provinces=["Madrid"], max_prov=1, sleep_s=0)
    rows = a.fetch()
    assert rows == []
    assert a._isolated is not None

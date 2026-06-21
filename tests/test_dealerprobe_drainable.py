"""DealerProbe --from-db noise filter — `_drainable_website`.

The un-harvested compraventa population is heavily polluted: OEM brand-network pages (the stock
lives on the brand platform, not a generic own-site), national marketplaces, SEO directory
placeholders, social profiles, and malformed URLs. Draining those would inflate "probed" with
junk. The filter is conservative — only CLEAR noise is dropped; unknown domains pass. Fixtures
are the exact shapes seen live in the DB sample.
"""
import pytest

from pipeline.platform.dealerprobe_wholesale import _drainable_website

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("url", [
    "https://www.opelalginet.com/es",            # real dealer own-site (brand name in domain, not OEM host)
    "http://vicanmotor.com/es/",
    "https://www.mgvalladolid.com/es/",
    "https://crestanevada.es",
    "https://grupobeniautos.com/",
    "https://autodeniamotors.com/",
])
def test_drainable_keeps_real_ownsites(url):
    assert _drainable_website(url) is True


@pytest.mark.parametrize("url", [
    "http://red.nissan.es/adenaumotor",                          # OEM network
    "https://concesionario.renault.es/intercargirona-girona.html",
    "https://redoficial.citroen.es/sant-boi-de-llobregat-psa-retail",
    "https://redcomercial.peugeot.es/psa-retail-barcelona-sant-feliu",
    "http://concesionario.bmw.es/autopremier-alcala/es_ES/equipo.html",
    "https://www.kia.com/es/concesionarios/ulsanmotor/",
    "https://www.clicars.com/coches-segunda-mano-ocasion",       # national marketplace
    "https://www.beedigital.es/planes/",                          # SEO placeholder
    "https://www.facebook.com/PalaciOcasion-1653923284830197/",  # social
    "http://www.https://www.lexusmadrid.com",                    # malformed double scheme
    "",                                                           # empty
    "notaurl",                                                    # no host
])
def test_drainable_drops_noise(url):
    assert _drainable_website(url) is False

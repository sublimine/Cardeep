"""Golden tests for the cdp_pair() refactor (audit P2 B-canonical-key).

Guarantees the cdp_code() output is byte-identical after extracting cdp_pair(), and that cdp_pair
exposes the canonical_key pre-image. If the hash ever drifted, the live-code assertions fail loud.
"""
from services.api.codes import canonical_key, cdp_code, cdp_pair


class TestCdpPairGolden:
    def test_byte_identical_to_live_codes(self):
        # cdp_pair must reproduce known LIVE cdp_codes — proves the refactor did not change the hash.
        assert cdp_pair(province_code="50", particular_platform="coches.net",
                        particular_seller_id="50")[1] == "CDP-ES-50-FPB3W1R6"
        assert cdp_pair(province_code="04", particular_platform="milanuncios",
                        particular_seller_id="109905688")[1] == "CDP-ES-04-CR8NMA86"
        assert cdp_pair(province_code="45", particular_platform="wallapop",
                        particular_seller_id="dqjwpv3enezo")[1] == "CDP-ES-45-84ZNGKZR"

    def test_cdp_code_delegates_to_pair(self):
        # cdp_code() == cdp_pair()[1] across a kwarg matrix (no drift from the refactor).
        matrix = [
            dict(province_code="28", domain="ford.es"),
            dict(province_code="08", name="Talleres X", municipality_code="08019"),
            dict(province_code="28", name="Garaje Y"),
            dict(province_code="50", particular_platform="coches.net", particular_seller_id="50"),
            dict(province_code="28", cif="B12345678"),
        ]
        for kw in matrix:
            assert cdp_code(**kw) == cdp_pair(**kw)[1]

    def test_cdp_pair_exposes_canonical_key(self):
        key, _ = cdp_pair(province_code="28", domain="ford.es")
        assert key == canonical_key(province_code="28", domain="ford.es") == "domain:ford.es"
        assert cdp_pair(province_code="50", particular_platform="coches.net",
                        particular_seller_id="50")[0] == "particular:cochesnet:50"

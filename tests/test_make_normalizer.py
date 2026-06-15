"""Unit tests for the canonical make normalizer (audit P2 A-make-model-null-parse)."""
from pipeline.identity.make_normalizer import canonical_make, make_from_title, normalize_make


class TestCanonicalMake:
    def test_casing_consolidated(self):
        assert canonical_make("VOLKSWAGEN") == "Volkswagen"
        assert canonical_make("volkswagen") == "Volkswagen"
        assert canonical_make("Volkswagen") == "Volkswagen"
        assert canonical_make("vw") == "Volkswagen"
        assert canonical_make("MERCEDES-BENZ") == "Mercedes-Benz"
        assert canonical_make("Mercedes") == "Mercedes-Benz"
        assert canonical_make("seat") == "SEAT"
        assert canonical_make("CUPRA") == "CUPRA"

    def test_unknown_or_empty_returns_none(self):
        assert canonical_make("NotARealBrand") is None
        assert canonical_make("") is None
        assert canonical_make(None) is None


class TestMakeFromTitle:
    def test_extracts_leading_brand(self):
        assert make_from_title("Volkswagen Golf 1.4 TSI 122 CV - 2010") == "Volkswagen"
        assert make_from_title("BMW Serie 3") == "BMW"
        assert make_from_title("ford focus") == "Ford"
        assert make_from_title("alfa romeo giulia 2.0") == "Alfa Romeo"   # leading token 'alfa'
        assert make_from_title("land-rover defender") == "Land Rover"

    def test_non_brand_leading_token_is_none(self):
        assert make_from_title("Vendo SEAT Altea 2006 XL") is None        # 'Vendo' not a brand
        assert make_from_title("stock disponible") is None
        assert make_from_title("caravana 2018") is None
        assert make_from_title("") is None
        assert make_from_title(None) is None


class TestNormalizeMake:
    def test_known_make_casing_normalized(self):
        assert normalize_make("VOLKSWAGEN", None) == "Volkswagen"
        assert normalize_make("citroen", None) == "Citroen"

    def test_null_make_recovered_from_title(self):
        assert normalize_make(None, "Ford Focus 1.6 TDCi") == "Ford"
        assert normalize_make("", "Opel Corsa -C") == "Opel"

    def test_unknown_make_preserved_never_guessed(self):
        # A non-empty unknown brand is kept verbatim — Law I: never guess identity.
        assert normalize_make("SomeKitCarMaker", "SomeKitCarMaker X") == "SomeKitCarMaker"

    def test_null_make_non_brand_title_stays_null(self):
        assert normalize_make(None, "Vendo coche barato urge") is None
        assert normalize_make(None, None) is None

    def test_known_make_wins_over_title(self):
        # An already-known make is normalized; the title is only a fallback for empty makes.
        assert normalize_make("bmw", "Audi A3") == "BMW"

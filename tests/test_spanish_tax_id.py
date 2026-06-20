"""P06 CAPA-0: pure-stdlib Spanish tax-ID (NIF / NIE / CIF) checksum validator.

The €0 alternative to python-stdnum (es.nif/es.cif — absent, an install gate): the deterministic-
first hard key P06 requires. A CIF/NIF that fails its OFFICIAL checksum must NOT become an identity
key (it would mint identity off corrupt data and inflate the dealer denominator). The algorithm is
fully specified by the BOE, so it is exhaustively verifiable offline — every vector below is computed
from the official rule, not scraped.
"""
import pytest

from services.api.tax_id import (
    canonical_tax_id,
    is_valid_cif,
    is_valid_nie,
    is_valid_nif,
    is_valid_tax_id,
)

pytestmark = pytest.mark.unit


class TestNIF:
    # 8 digits + control letter "TRWAGMYFPDXBNJZSQVHLCKE"[n % 23].
    @pytest.mark.parametrize("nif", ["12345678Z", "12345678-Z", "12345678 z", "00000000T"])
    def test_valid(self, nif):
        assert is_valid_nif(nif)

    @pytest.mark.parametrize(
        "nif", ["12345678A", "00000000A", "1234567Z", "123456789Z", "ABCDEFGHZ", "", "12345678"]
    )
    def test_invalid(self, nif):
        assert not is_valid_nif(nif)


class TestNIE:
    # X/Y/Z -> 0/1/2, then the NIF mod-23 letter.
    @pytest.mark.parametrize("nie", ["X1234567L", "Y1234567X", "Z1234567R"])
    def test_valid(self, nie):
        assert is_valid_nie(nie)

    @pytest.mark.parametrize("nie", ["X1234567A", "X0000000A", "W1234567L", "1234567L", ""])
    def test_invalid(self, nie):
        assert not is_valid_nie(nie)


class TestCIF:
    # Org letter + 7 digits + control (digit for ABEH, letter for KPQS, either otherwise).
    @pytest.mark.parametrize(
        "cif",
        [
            "A58818501",   # A -> digit control
            "B58818501",   # B -> digit control (same middle)
            "Q2826000H",   # Q -> letter control
            "F12345674",   # F -> either: digit form
            "F1234567D",   # F -> either: letter form
        ],
    )
    def test_valid(self, cif):
        assert is_valid_cif(cif)

    @pytest.mark.parametrize(
        "cif",
        [
            "A58818500",   # wrong control digit
            "Q2826000A",   # wrong control letter
            "A1234567D",   # ABEH must use the DIGIT, not the letter
            "Q12345674",   # KPQS must use the LETTER, not the digit
            "I1234567D",   # I is not a valid org-type letter
            "12345678Z",   # that is a NIF, not a CIF
            "",
        ],
    )
    def test_invalid(self, cif):
        assert not is_valid_cif(cif)


class TestDispatch:
    @pytest.mark.parametrize("tid", ["12345678Z", "X1234567L", "A58818501", "Q2826000H"])
    def test_is_valid_tax_id_accepts_all_families(self, tid):
        assert is_valid_tax_id(tid)

    def test_canonical_strips_and_uppercases(self):
        assert canonical_tax_id(" a-58.818.501 ") == "A58818501"
        assert canonical_tax_id("12345678z") == "12345678Z"

    @pytest.mark.parametrize("bad", ["A58818500", "garbage", "", "   ", None])
    def test_canonical_returns_none_for_invalid(self, bad):
        assert canonical_tax_id(bad) is None

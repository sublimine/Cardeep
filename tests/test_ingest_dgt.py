"""Unit tests for pipeline/market/ingest_dgt.py — pure parsing functions, no DB,
no network (the real download is exercised once, manually, per F4's verification
report — re-hitting the live DGT server on every test run would be slow and
disrespectful of a public government service, not because it's untested)."""
from __future__ import annotations

from datetime import date

import pytest

from pipeline.market.dgt_provinces import DGT_NON_GEOGRAPHIC_CODES, DGT_PROVINCE_TO_INE, map_province
from pipeline.market.ingest_dgt import (
    COD_TIPO_TURISMO,
    RECORD_LENGTH,
    build_url,
    parse_line,
    parse_records,
)

# A real 200-byte prefix of an actual downloaded record (2026-07-18,
# export_mensual_trf_202606.zip, first data row) — enough to cover every field
# this module slices (all offsets end at or before byte 157).
_REAL_SAMPLE_PREFIX = (
    "16062004001062026SUZUKI                        AN 400                "
    "1JS1BW11110***********500  385  2.84   197   390  2    0101          "
    "              BIBI20106202648530        ND         B0048083ORT"
)


class TestBuildUrl:
    def test_month_not_zero_padded(self) -> None:
        """Verified live 2026-07-18: the real DGT URL uses '6', not '06', for June —
        a zero-padded URL 404s."""
        assert build_url(2026, 6) == (
            "https://www.dgt.es/microdatos/salida/2026/6/vehiculos/transferencias/"
            "export_mensual_trf_202606.zip"
        )

    def test_year_and_zip_name_are_zero_padded_month_number(self) -> None:
        assert build_url(2026, 12) == (
            "https://www.dgt.es/microdatos/salida/2026/12/vehiculos/transferencias/"
            "export_mensual_trf_202612.zip"
        )


class TestParseLine:
    def test_real_sample_line_parses_correctly(self) -> None:
        """Every field verified against the actual downloaded bytes (2026-07-18):
        COD_PROVINCIA_VEH='BI' (Bizkaia, a real DGT alpha code), CLAVE_TRAMITE='2'
        (Transferencia — the file's whole purpose), BASTIDOR_ITV truncated to 8 real
        chars + asterisks (VIN restriction, carta §2 DGT row)."""
        row = parse_line(_REAL_SAMPLE_PREFIX)
        assert row is not None
        assert row["fec_tramitacion"] == date(2026, 6, 1)
        assert row["marca"] == "SUZUKI"
        assert row["modelo"] == "AN 400"
        assert row["cod_provincia_dgt"] == "BI"
        assert row["province_code"] == "48"  # Bizkaia's real INE code
        assert row["clave_tramite"] == "2"

    def test_too_short_line_returns_none(self) -> None:
        assert parse_line("short") is None

    def test_malformed_date_returns_none(self) -> None:
        bad = "X" * 9 + "AAAAAAAA" + " " * (157 - 17)
        assert parse_line(bad) is None

    def test_unmapped_province_code_is_none_not_guessed(self) -> None:
        """A DGT sentinel (DS/EX) or any code absent from the Anexo I table must
        yield province_code=None, never a fallback guess."""
        line = list(_REAL_SAMPLE_PREFIX)
        line[152:154] = list("DS")
        row = parse_line("".join(line))
        assert row is not None
        assert row["cod_provincia_dgt"] == "DS"
        assert row["province_code"] is None


class TestParseRecords:
    def test_multiple_lines_parsed(self) -> None:
        text = (_REAL_SAMPLE_PREFIX + "\r\n") * 3
        rows, n_bad = parse_records(text.encode("latin-1"))
        assert len(rows) == 3
        assert n_bad == 0

    def test_blank_lines_skipped_silently(self) -> None:
        text = _REAL_SAMPLE_PREFIX + "\r\n\r\n" + _REAL_SAMPLE_PREFIX
        rows, n_bad = parse_records(text.encode("latin-1"))
        assert len(rows) == 2
        assert n_bad == 0

    def test_malformed_line_counted_not_dropped_silently(self) -> None:
        text = _REAL_SAMPLE_PREFIX + "\r\n" + "garbage\r\n"
        rows, n_bad = parse_records(text.encode("latin-1"))
        assert len(rows) == 1
        assert n_bad == 1


class TestCodTipoConstant:
    def test_turismo_code_is_40(self) -> None:
        """Per Anexo I §1.3.4 COD_TIPO table: '40' = TURISMO (passenger car)."""
        assert COD_TIPO_TURISMO == "40"


class TestProvinceMapping:
    def test_exactly_52_geographic_provinces_mapped(self) -> None:
        """52 Spanish provinces total (Ceuta+Melilla included); DS/EX are
        non-geographic sentinels, deliberately excluded from the mapping dict."""
        assert len(DGT_PROVINCE_TO_INE) == 52
        values = set(DGT_PROVINCE_TO_INE.values())
        assert len(values) == 52  # every value distinct (no two DGT codes collide)
        assert values == {f"{i:02d}" for i in range(1, 53)}

    def test_madrid_and_barcelona(self) -> None:
        assert DGT_PROVINCE_TO_INE["M"] == "28"
        assert DGT_PROVINCE_TO_INE["B"] == "08"

    def test_non_geographic_sentinels_excluded_from_mapping(self) -> None:
        for code in DGT_NON_GEOGRAPHIC_CODES:
            assert code not in DGT_PROVINCE_TO_INE

    def test_map_province_returns_none_for_sentinel(self) -> None:
        assert map_province("DS") is None
        assert map_province("EX") is None

    def test_map_province_returns_none_for_unknown(self) -> None:
        assert map_province("ZZ") is None

    def test_map_province_none_input(self) -> None:
        assert map_province(None) is None

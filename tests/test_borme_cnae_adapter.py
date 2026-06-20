"""Offline unit tests for the V4 BORME-CNAE registry SourceAdapter.

No network: the CIF checksum, the automotive objeto-social classifier, and the
BORME-A XML act parser are exercised on a fixed fixture, asserting the contract
the geo-resolver and VAM gate rely on.
"""
from __future__ import annotations

import pytest

from pipeline.sources import borme_cnae as bc
from pipeline.sources.borme_cnae import BormeCnaeAdapter

_XML = """<?xml version="1.0" encoding="UTF-8"?>
<documento><texto>
<p class="articulo">291665 - CULTIVA IBERIA 5, S.L.</p>
<p class="parrafo">Constitución. Objeto social: Desarrollo de explotaciones agrícolas.
 Domicilio: C/ ARANZABAL 9 01008 (VITORIA-GASTEIZ). Capital: 3.000,00 Euros.</p>
<p class="articulo">291666 - ALMOGAVERS MOTION, S.L.</p>
<p class="parrafo">Constitución. Objeto social: Compraventa de vehículos automóviles y recambios.
 Domicilio: AV ROMA 12 43001 (TARRAGONA). Capital: 5.000,00 Euros.</p>
<p class="articulo">291667 - DESGUACES DEL EBRO S.L.</p>
<p class="parrafo">Constitución. Objeto social: Descontaminación de vehículos al final de su vida útil.
 Domicilio: POL IND 5 50297 (ZARAGOZA). Capital: 10.000,00 Euros.</p>
<p class="articulo">291668 - REFORMAS GARCIA S.L.</p>
<p class="parrafo">Constitución. Objeto social: Reparación de electrodomésticos del hogar.
 Domicilio: C/ SOL 1 28001 (MADRID). Capital: 3.000,00 Euros.</p>
<p class="articulo">291669 - VENDIDA YA S.L.</p>
<p class="parrafo">Otros actos. Nombramientos. Adm. Único: PEREZ JUAN.</p>
</texto></documento>"""


@pytest.mark.unit
@pytest.mark.parametrize("cif,ok", [
    ("A58818501", True),     # valid control digit
    ("B00000001", False),    # bad checksum
    ("X1234567L", False),    # NIE, not a CIF format
])
def test_cif_checksum(cif, ok):
    assert bc._cif_control_ok(cif) is ok


@pytest.mark.unit
def test_classifier():
    assert bc._classify("Compraventa de vehículos") == "compraventa"
    assert bc._classify("Descontaminación de vehículos al final de su vida útil") == "desguace"
    assert bc._classify("Concesionario oficial de automóviles") == "concesionario_oficial"
    # generic repair with no vehicle term -> not automotive
    assert bc._classify("Reparación de electrodomésticos") is None
    assert bc._classify("Restauración y hostelería") is None


@pytest.mark.unit
def test_parse_keeps_only_automotive_constituciones():
    a = BormeCnaeAdapter()
    rows = a._parse_province(_XML, "TARRAGONA", set())
    names = sorted(e.legal_name for e in rows)
    # agrícola + electrodomésticos + non-constitución act are excluded; 2 automotive remain
    assert names == ["ALMOGAVERS MOTION, S.L.", "DESGUACES DEL EBRO S.L."]
    by_name = {e.legal_name: e for e in rows}
    assert by_name["ALMOGAVERS MOTION, S.L."].kind == "compraventa"
    assert by_name["ALMOGAVERS MOTION, S.L."].province_name == "43"   # from postcode
    assert by_name["ALMOGAVERS MOTION, S.L."].municipality_name == "TARRAGONA"
    assert by_name["DESGUACES DEL EBRO S.L."].kind == "desguace"
    assert by_name["DESGUACES DEL EBRO S.L."].province_name == "50"
    for e in rows:
        assert e.source_key == "borme_cnae"
        assert e.extra["vector"] == 4
        assert e.cnae == "4511"


@pytest.mark.unit
def test_dedup_within_run():
    a = BormeCnaeAdapter()
    seen: set[str] = set()
    first = a._parse_province(_XML, "TARRAGONA", seen)
    second = a._parse_province(_XML, "TARRAGONA", seen)  # same regs -> all filtered
    assert len(first) == 2
    assert second == []

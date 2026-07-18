"""Tests for services/crm/lead_parsers.py (06-unified-crm-chat F4).

Pure unit tests, no DB, no network. Fixtures below are CONSTRUCTED bodies modeling the
publicly documented shape of each portal's lead-notification email (module docstring's
declared [ASUMIDO] — no real captured .eml sample was available in this environment).
They exist to prove the parser ARCHITECTURE — portal detection by sender domain,
deterministic extraction when markers match, honest degradation to the generic
extractor when they do not — not to certify byte-exact production templates.
"""
from __future__ import annotations

from services.crm.lead_parsers import detect_portal, parse_lead, strip_html


class TestDetectPortal:
    def test_cochesnet_domain(self) -> None:
        assert detect_portal("notificaciones@coches.net") == "coches.net"

    def test_wallapop_domain(self) -> None:
        assert detect_portal("no-reply@wallapop.com") == "wallapop"

    def test_milanuncios_domain(self) -> None:
        assert detect_portal("leads@milanuncios.com") == "milanuncios"

    def test_unknown_domain_is_manual(self) -> None:
        assert detect_portal("juan.perez@gmail.com") == "manual"

    def test_empty_address_is_manual(self) -> None:
        assert detect_portal("") == "manual"
        assert detect_portal(None) == "manual"  # type: ignore[arg-type]


class TestCochesNetExtractor:
    def test_matches_deterministic_template(self) -> None:
        body = "Nombre: Juan Pérez\nTeléfono: 612 345 678\nMensaje: Me interesa el BMW, sigue disponible?"
        lead = parse_lead("BMW 320d 2019 - 18.900€", body, "notificaciones@coches.net", "coches.net")
        assert lead.source_platform == "coches.net"
        assert lead.extraction_method == "deterministic"
        assert lead.contact_name == "Juan Pérez"
        assert lead.contact_phone == "612 345 678"
        assert "sigue disponible" in lead.message_body
        assert lead.vehicle_reference == "BMW 320d 2019 - 18.900€"

    def test_degrades_to_generic_when_no_markers(self) -> None:
        body = "Hola, quisiera mas info sobre el coche del anuncio. Mi tel es 611222333"
        lead = parse_lead("Consulta", body, "notificaciones@coches.net", "coches.net")
        assert lead.source_platform == "coches.net"
        assert lead.extraction_method == "generic"
        assert lead.contact_phone == "611222333"


class TestWallapopExtractor:
    def test_matches_deterministic_template(self) -> None:
        body = "De: Maria Lopez\nMensaje: Hola, esta disponible el coche?"
        lead = parse_lead("Nuevo mensaje en Wallapop", body, "no-reply@wallapop.com", "Wallapop")
        assert lead.source_platform == "wallapop"
        assert lead.extraction_method == "deterministic"
        assert lead.contact_name == "Maria Lopez"
        assert "esta disponible" in lead.message_body

    def test_degrades_to_generic_when_no_message_marker(self) -> None:
        body = "Alguien ha comentado tu anuncio"
        lead = parse_lead("Actividad en tu anuncio", body, "no-reply@wallapop.com", "Wallapop")
        assert lead.extraction_method == "generic"


class TestMilanunciosExtractor:
    def test_matches_deterministic_template(self) -> None:
        body = "Nombre: Pedro Gomez\nTeléfono: +34 622 111 222\nQuiero verlo este finde"
        lead = parse_lead("Interesado en tu anuncio", body, "leads@milanuncios.com", "Milanuncios")
        assert lead.source_platform == "milanuncios"
        assert lead.extraction_method == "deterministic"
        assert lead.contact_name == "Pedro Gomez"
        assert lead.contact_phone is not None and "622" in lead.contact_phone

    def test_degrades_to_generic_when_no_markers(self) -> None:
        body = "Hola buenas, esta disponible?"
        lead = parse_lead("Consulta", body, "leads@milanuncios.com", "Milanuncios")
        assert lead.extraction_method == "generic"


class TestGenericFallback:
    def test_unknown_portal_with_phone_in_body(self) -> None:
        body = "Hola, soy Ana, mi numero es 655443322, un saludo"
        lead = parse_lead("Interesada", body, "ana.particular@gmail.com", "Ana")
        assert lead.source_platform == "manual"
        assert lead.extraction_method == "generic"
        assert lead.contact_phone == "655443322"
        assert lead.contact_email == "ana.particular@gmail.com"
        assert lead.contact_name == "Ana"

    def test_never_raises_on_empty_body(self) -> None:
        lead = parse_lead("", "", "", None)
        assert lead.extraction_method == "generic"
        assert lead.message_body == ""

    def test_never_fabricates_a_phone_when_absent(self) -> None:
        lead = parse_lead("Hola", "Sin telefono aqui", "x@y.com", "X")
        assert lead.contact_phone is None


class TestStripHtml:
    def test_removes_tags_and_collapses_whitespace(self) -> None:
        html = "<html><body><p>Hola   <b>Juan</b></p><br/>Interesado</body></html>"
        assert strip_html(html) == "Hola Juan Interesado"

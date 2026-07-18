"""Unit tests for pipeline/terminal/ingest_news.py's pure functions (09-trading-terminal Fase 5).

No DB, no network — these test the RSS parsing, content-hash, and keyword-classification logic
in isolation. The live-fetch/DB-write path is exercised operationally (this session's real
ingestion run: 60 items from ANFAC+GANVAM, 58/60 V5-verified — see docs/architecture/
09-TERMINAL-METHODOLOGY.md), not re-mocked here.
"""
from __future__ import annotations

from pipeline.terminal.ingest_news import _content_hash, _match_symbol_keys, _parse_feed

_SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>Test Feed</title>
<item>
  <title>El mercado de BMW crece un 10% en julio</title>
  <link>https://example.test/bmw-crece</link>
  <description>Las ventas de BMW suben en Espana.</description>
  <pubDate>Thu, 16 Jul 2026 14:32:53 +0000</pubDate>
</item>
<item>
  <title>Sin link, se descarta</title>
  <description>Item malformado</description>
</item>
</channel></rss>
""".encode("utf-8")


class TestParseFeed:
    def test_parses_well_formed_items(self) -> None:
        items = _parse_feed(_SAMPLE_RSS)
        assert len(items) == 1  # the linkless item is dropped
        assert items[0]["title"] == "El mercado de BMW crece un 10% en julio"
        assert items[0]["link"] == "https://example.test/bmw-crece"
        assert items[0]["pub_date"] is not None
        assert items[0]["pub_date"].year == 2026

    def test_malformed_xml_returns_empty_list_not_raise(self) -> None:
        assert _parse_feed(b"not xml at all <<<") == []

    def test_empty_channel_returns_empty_list(self) -> None:
        assert _parse_feed(b"<rss><channel></channel></rss>") == []


class TestContentHash:
    def test_same_input_same_hash(self) -> None:
        assert _content_hash("Title", "Desc") == _content_hash("Title", "Desc")

    def test_different_input_different_hash(self) -> None:
        assert _content_hash("Title A", "Desc") != _content_hash("Title B", "Desc")


class TestMatchSymbolKeys:
    def test_matches_make_present_in_title(self) -> None:
        matched = _match_symbol_keys("El mercado de BMW crece", "", ["BMW", "Audi", "Seat"])
        assert matched == ["BMW"]

    def test_no_match_returns_empty(self) -> None:
        assert _match_symbol_keys("Noticia genérica del sector", "", ["BMW", "Audi"]) == []

    def test_word_boundary_avoids_substring_false_positive(self) -> None:
        # "Seat" must not match inside "reasseat" or similar — word-boundary regex guards this.
        assert _match_symbol_keys("una reaseatación cualquiera", "", ["Seat"]) == []

    def test_matches_in_description_too(self) -> None:
        matched = _match_symbol_keys("Titular genérico", "Se habla de Audi en el texto", ["Audi"])
        assert matched == ["Audi"]

"""Unit tests for the Das WeltAuto declared-total parser (B9 coverage instrumentation).

Pure string tests — no DB, no network. The connector drains by exhaustion, but each province SRP
declares its result count in an inline JS config object (numberOfResults). This is the site-declared
total fed to verify_coverage (the B9 gate). The parser must extract THAT and never confuse it with a
facet count (e.g. data-key="puertas" 1.037), which is a different number that can coincide.
"""
from __future__ import annotations

from pipeline.platform.dasweltauto_wholesale import _parse_declared_total

# Real shape observed live on /esp/coches-de-segunda-mano-en-madrid (page 1):
_CONFIG = '...filter = {"SortOrder":"Novelty - descending","filterlist":[],"numberOfResults":"1037","source":"Result List"};'
# A facet anchor — the SAME number can appear here; it must NOT be parsed as the total.
_FACET = '<li> <a data-value="5" data-key="puertas" class=" "> 5 <span> 1.037 </span> </a></li>'


class TestParseDeclaredTotal:
    def test_extracts_number_of_results(self) -> None:
        assert _parse_declared_total(_CONFIG) == 1037

    def test_facet_count_is_not_the_total(self) -> None:
        # No numberOfResults key -> None, even though "1.037" (a facet) is present.
        assert _parse_declared_total(_FACET) is None

    def test_config_wins_when_both_present(self) -> None:
        # The real page has both; only the config's numberOfResults is the declared total.
        assert _parse_declared_total(_FACET + _CONFIG) == 1037

    def test_unquoted_value_variant(self) -> None:
        assert _parse_declared_total('{"numberOfResults":2048,"x":1}') == 2048

    def test_absent_returns_none(self) -> None:
        assert _parse_declared_total("<html>no results count here</html>") is None
        assert _parse_declared_total("") is None

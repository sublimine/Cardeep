"""Regression tests for the Motorflash dealer-index sitemap parser.

2026-06-22 outage root cause: the concesionarios sitemap stopped emitting the
`coches-segunda-mano` segment and now lists each dealer under per-stock-type
segments (`coches-km0`, `coches-nuevos`, `coches-seminuevos`). The old regex was
pinned to `coches-segunda-mano` -> 0 dealers parsed -> 0 rows. These tests lock the
new grammar and the de-dup-by-id invariant so a future segment rename fails loudly.
"""
from __future__ import annotations

from pipeline.platform.motorflash_wholesale import parse_dealer_index

# A faithful slice of the LIVE sitemap grammar (verified 2026-06-22): three segment
# tokens, the same dealer repeated across segments with one stable native id.
_LIVE_SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://www.motorflash.com/concesionarios/</loc></url>
<url><loc>https://www.motorflash.com/concesionario/alcala-534-peugeot/coches-km0/119384/</loc></url>
<url><loc>https://www.motorflash.com/concesionario/alcala-534-peugeot/coches-nuevos/119384/</loc></url>
<url><loc>https://www.motorflash.com/concesionario/alcala-534-peugeot/coches-seminuevos/119384/</loc></url>
<url><loc>https://www.motorflash.com/concesionario/adarsa-zamora/coches-km0/4222/</loc></url>
<url><loc>https://www.motorflash.com/concesionario/adarsa-zamora/coches-seminuevos/4222/</loc></url>
</urlset>"""


def test_parses_new_segment_grammar_and_dedups_by_dealer_id() -> None:
    """Each dealer yields exactly one DealerRef regardless of segment count."""
    # Arrange / Act
    dealers = parse_dealer_index(_LIVE_SITEMAP)

    # Assert: two distinct dealers, not six segment rows; ids/slugs preserved.
    by_id = {d.mf_dealer_id: d for d in dealers}
    assert set(by_id) == {"119384", "4222"}
    assert by_id["119384"].slug == "alcala-534-peugeot"
    assert by_id["4222"].slug == "adarsa-zamora"
    # The header row /concesionarios/ (no id) is never a dealer.
    assert all(d.mf_dealer_id for d in dealers)


def test_legacy_segunda_mano_segment_still_parses() -> None:
    """Backward-compat: if a dealer is ever re-listed under the old segment, it
    must still parse (the regex is segment-agnostic, not km0-pinned)."""
    legacy = (
        '<loc>https://www.motorflash.com/concesionario/m-conde/'
        'coches-segunda-mano/999/</loc>'
    )
    dealers = parse_dealer_index(legacy)
    assert len(dealers) == 1
    assert dealers[0].mf_dealer_id == "999"
    assert dealers[0].slug == "m-conde"


def test_empty_or_unmatched_sitemap_yields_no_dealers() -> None:
    """An empty body (e.g. a swallowed fetch failure) must yield zero dealers,
    not raise — the harvester treats 0 dealers as a no-op proof slice."""
    assert parse_dealer_index("") == []
    assert parse_dealer_index("<urlset></urlset>") == []

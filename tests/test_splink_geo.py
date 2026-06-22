"""Geo-proximity entity resolution for the Splink cross-source merge (§V6).

The second orthogonal MSE list (Páginas Amarillas / DIR) overlaps the GEO list by
geocoding PA addresses and collapsing them onto the same physical dealer when the
coordinates coincide (~<150 m), even though the names differ. Two pieces make that
work and are asserted here as pure unit tests (no DB, no network, no full dedupe):

  1. ``_geocell`` rounds (lat, lon) into the coarse blocking key.
  2. ``_build_settings`` includes a geo blocking rule on that key AND a haversine
     distance comparison, ADDITIVE to the existing name/phone/website logic.

The DIR list itself is registered in the taxonomy (lists.py); that is asserted in
test_exhaustiveness_vector_lists.py — here we only cover the geo machinery.
"""
from __future__ import annotations

import pytest

from pipeline.exhaustiveness import lists, splink_merge


@pytest.mark.unit
def test_geocell_rounds_to_three_decimals():
    # 3 dp ~ 111 m: the proven PA<->Overture match radius collapses into one cell.
    assert splink_merge._geocell(40.41678, -3.70379) == "40.417,-3.704"


@pytest.mark.unit
def test_geocell_collapses_nearby_points_into_same_cell():
    # Two dealers ~tens of metres apart share a cell -> become a candidate pair.
    a = splink_merge._geocell(40.4167, -3.7037)
    b = splink_merge._geocell(40.41672, -3.70374)
    assert a == b


@pytest.mark.unit
def test_geocell_separates_distant_points():
    near = splink_merge._geocell(40.4167, -3.7037)
    far = splink_merge._geocell(40.4200, -3.7037)
    assert near != far


@pytest.mark.unit
@pytest.mark.parametrize("lat,lon", [(None, -3.70), (40.41, None), (None, None)])
def test_geocell_none_when_coords_missing(lat, lon):
    # Ungeocoded dealers must NOT share a (None) block.
    assert splink_merge._geocell(lat, lon) is None


@pytest.mark.unit
def test_geocell_accepts_string_coords():
    # entity.lat/lon may arrive as Decimal/str from psycopg2; float() coerces.
    assert splink_merge._geocell("40.41678", "-3.70379") == "40.417,-3.704"


@pytest.mark.unit
def test_dir_list_is_orthogonal_and_geo_matched():
    # The second list is genuinely orthogonal (directory capture mechanism).
    assert lists.bucket_for("paginas_amarillas") == "DIR"
    assert "DIR" in lists.ORTHOGONAL_LISTS
    cls, desc = lists.LIST_METADATA["DIR"]
    assert cls == "commercial_directory"
    assert "Páginas Amarillas" in desc


def _blocking_rule_sqls(settings) -> list[str]:
    """Real SQL of each blocking rule (Splink 4.0 DuckDB dialect)."""
    return [
        br.get_blocking_rule("duckdb").blocking_rule_sql
        for br in settings.blocking_rules_to_generate_predictions
    ]


@pytest.mark.unit
def test_settings_include_geo_blocking_rule():
    if not splink_merge.splink_available():
        pytest.skip("splink not installed")
    settings = splink_merge._build_settings()
    sqls = _blocking_rule_sqls(settings)
    # The geocell block must be present...
    assert any('"geocell"' in sql for sql in sqls), sqls
    # ...and it must be ADDITIVE: the existing blocks survive.
    assert any('"municipality_code"' in sql and '"name_prefix"' in sql for sql in sqls)
    assert any(sql == 'l."phone" = r."phone"' for sql in sqls)
    assert any(sql == 'l."website_host" = r."website_host"' for sql in sqls)


@pytest.mark.unit
def test_settings_include_geo_distance_comparison():
    if not splink_merge.splink_available():
        pytest.skip("splink not installed")
    settings = splink_merge._build_settings()
    dicts = [c.create_comparison_dict("duckdb") for c in settings.comparisons]
    descs = [d.get("comparison_description") for d in dicts]
    outputs = [d.get("output_column_name") for d in dicts]
    # haversine distance comparison on lat/lon is present (the geo signal)...
    assert "DistanceInKMAtThresholds" in descs, descs
    assert "lat_lon" in outputs, outputs
    # ...without dropping the name signal (geo is additive).
    assert any(o == "name" for o in outputs), outputs

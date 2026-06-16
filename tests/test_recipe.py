"""Q4/R2/R3 (green-review): write_recipe must produce PARSEABLE YAML (the old hand-rolled dumper
broke on ': ' values), round-trip-check what it writes, and log a semantic clobber. Uses tmp_path
via monkeypatch — no real recipe files are touched.
"""
from __future__ import annotations

import logging

import pytest
import yaml

from pipeline import recipe


def test_recipe_with_colon_space_value_is_parseable(tmp_path, monkeypatch):
    # Q4: 'FACET partition (depth-cap fix): seller_type' has a ': ' that the old _yaml_dump emitted
    # bare, producing a YAML ScannerError. yaml.dump quotes it; the file must round-trip.
    monkeypatch.setattr(recipe, "ROOT", tmp_path)
    r = {"version": 1, "source": "wallapop",
         "enumeration": "FACET partition (depth-cap fix): seller_type then brand",
         "field_map": {"price": "tracking.price", "note": "see: the map"}}
    path = recipe.write_recipe("CDP-ES-28-TSTYAML1", r)
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert loaded == r


def test_recipe_rejects_truthy_non_dict(tmp_path, monkeypatch):
    # R2: a non-dict (truthy) recipe is rejected, not silently written.
    monkeypatch.setattr(recipe, "ROOT", tmp_path)
    with pytest.raises(ValueError):
        recipe.write_recipe("CDP-ES-28-TSTYAML2", recipe=["not", "a", "dict"])  # type: ignore[arg-type]


def test_recipe_clobber_logs_warning(tmp_path, monkeypatch, caplog):
    # R3: overwriting an existing cdp_code with a semantically different recipe is logged.
    monkeypatch.setattr(recipe, "ROOT", tmp_path)
    recipe.write_recipe("CDP-ES-28-TSTYAML3", {"version": 1, "source": "alpha"})
    with caplog.at_level(logging.WARNING, logger="pipeline.recipe"):
        recipe.write_recipe("CDP-ES-28-TSTYAML3", {"version": 1, "source": "beta"})
    assert any("overwriting" in rec.message.lower() for rec in caplog.records)


def test_recipe_same_content_no_clobber_warning(tmp_path, monkeypatch, caplog):
    # Re-writing the IDENTICAL recipe must NOT warn (idempotent updates are normal).
    monkeypatch.setattr(recipe, "ROOT", tmp_path)
    r = {"version": 1, "source": "alpha"}
    recipe.write_recipe("CDP-ES-28-TSTYAML4", r)
    with caplog.at_level(logging.WARNING, logger="pipeline.recipe"):
        recipe.write_recipe("CDP-ES-28-TSTYAML4", r)
    assert not any("overwriting" in rec.message.lower() for rec in caplog.records)

"""P05 fase 2: the shared bulk SQL statements live in ONE place (pipeline/platform/_core/sql.py).

Many connectors had hand-copied these statements byte-identical; they now import the single core
constant (aliased to their local name). This guard is self-maintaining: a connector is an offender if
it re-declares an inline literal whose normalized form EQUALS the canonical core constant — i.e. it
duplicated the canonical instead of importing it. Connectors whose statement genuinely differs keep a
DIFFERENT inline literal on purpose; those never match the canonical, so they are never flagged.
"""
from __future__ import annotations

import glob
import hashlib
import os
import re

import pytest

from pipeline.platform._core.sql import (
    BULK_INSERT_EVENTS,
    BULK_INSERT_VEHICLES,
    BULK_TOUCH_VEHICLES,
    BULK_UPSERT_DEALERS,
    BULK_UPSERT_EDGES,
    BULK_UPSERT_ENTITY_SOURCE,
)

pytestmark = pytest.mark.unit

# local connector name -> the canonical core constant it must import (never re-declare inline).
_LOCAL_TO_CORE = {
    "_BULK_INSERT_VEHICLES": BULK_INSERT_VEHICLES,
    "_BULK_UPSERT_OWNER_SOURCES": BULK_UPSERT_ENTITY_SOURCE,
    "_BULK_UPSERT_DEALER_SOURCES": BULK_UPSERT_ENTITY_SOURCE,
    "_BULK_TOUCH_VEHICLES": BULK_TOUCH_VEHICLES,
    "_BULK_INSERT_EVENTS": BULK_INSERT_EVENTS,
    "_BULK_UPSERT_EDGES": BULK_UPSERT_EDGES,
    "_BULK_UPSERT_DEALERS": BULK_UPSERT_DEALERS,
}

# Names with NO legitimate divergent variant: every user collapsed, so NO inline literal may remain.
_FULLY_COLLAPSED = frozenset({
    "_BULK_UPSERT_OWNER_SOURCES", "_BULK_UPSERT_DEALER_SOURCES",
    "_BULK_TOUCH_VEHICLES", "_BULK_INSERT_EVENTS",
})


def _norm(body: str) -> str:
    return hashlib.sha256(
        "\n".join(line.strip() for line in body.strip().splitlines()).encode()).hexdigest()


def _connector_files() -> list[str]:
    return glob.glob("pipeline/platform/*.py")


def test_core_constants_have_expected_shapes() -> None:
    assert "transmission" in BULK_INSERT_VEHICLES
    assert "ON CONFLICT (entity_ulid, deep_link) DO NOTHING" in BULK_INSERT_VEHICLES
    assert "INSERT INTO entity_source" in BULK_UPSERT_ENTITY_SOURCE
    assert "DO UPDATE SET seen_at = now()" in BULK_UPSERT_ENTITY_SOURCE
    assert "UPDATE vehicle" in BULK_TOUCH_VEHICLES and "last_seen = now()" in BULK_TOUCH_VEHICLES
    assert "INSERT INTO vehicle_event" in BULK_INSERT_EVENTS and "'NEW'" in BULK_INSERT_EVENTS
    assert "INSERT INTO platform_listing" in BULK_UPSERT_EDGES and "xmax = 0" in BULK_UPSERT_EDGES
    assert "INSERT INTO entity" in BULK_UPSERT_DEALERS and "oem_vo_portal" in BULK_UPSERT_DEALERS


def test_no_connector_duplicates_a_canonical_statement_inline() -> None:
    # An inline literal equal to the canonical core constant means a connector re-copied it instead of
    # importing — exactly the drift the strangler removed. Divergent literals differ and are allowed.
    offenders = []
    for path in _connector_files():
        src = open(path, encoding="utf-8").read()
        for name, core in _LOCAL_TO_CORE.items():
            m = re.search(rf'{name}\s*=\s*"""(.*?)"""', src, re.S)
            if m and _norm(m.group(1)) == _norm(core):
                offenders.append(f"{os.path.basename(path)}:{name}")
    assert not offenders, f"these duplicate a _core.sql canonical inline — import it instead: {offenders}"


def test_fully_collapsed_names_have_no_inline_literal() -> None:
    offenders = []
    for path in _connector_files():
        src = open(path, encoding="utf-8").read()
        for name in _FULLY_COLLAPSED:
            if re.search(rf'{name}\s*=\s*"""', src):
                offenders.append(f"{os.path.basename(path)}:{name}")
    assert not offenders, f"fully-collapsed names must import from _core.sql, never declare inline: {offenders}"

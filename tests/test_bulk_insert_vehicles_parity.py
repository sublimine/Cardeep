"""P05 fase 2: the bulk vehicle upsert SQL lives in ONE place (_core.sql.BULK_INSERT_VEHICLES).

27 connectors had hand-copied this statement byte-for-byte; they now import the single core constant.
This guard (a) pins the canonical SQL shape and (b) fails if a connector re-introduces an inline copy
of the canonical statement instead of importing it — so the drift the strangler removed cannot creep
back. The 8 connectors whose vehicle row genuinely differs (no transmission / price NULL / scalar
entity_ulid / fewer columns) keep their own literal on purpose and are listed explicitly.
"""
from __future__ import annotations

import glob
import hashlib
import re

import pytest

from pipeline.platform._core.sql import (
    BULK_INSERT_EVENTS,
    BULK_INSERT_VEHICLES,
    BULK_TOUCH_VEHICLES,
    BULK_UPSERT_ENTITY_SOURCE,
)

pytestmark = pytest.mark.unit

# Local names that were collapsed to a single _core.sql constant — none may be re-declared inline.
_COLLAPSED_LOCAL_NAMES = (
    "_BULK_UPSERT_OWNER_SOURCES",
    "_BULK_UPSERT_DEALER_SOURCES",
    "_BULK_TOUCH_VEHICLES",
    "_BULK_INSERT_EVENTS",
)

# sha256 (whitespace-normalized) of the canonical variant-A statement.
_CANON_HASH = "42622b75e6"
_INLINE = re.compile(r'_BULK_INSERT_VEHICLES\s*=\s*"""(.*?)"""', re.S)

# Connectors whose vehicle row is genuinely different — they keep a bespoke literal on purpose.
_KNOWN_DIVERGENT = frozenset({
    "family_cms_wordpress_dominated__wholesale.py",
    "family_dealerk_wholesale.py",
    "family_dms_vendor_platforms__wholesale.py",
    "family_generic_custom_wholesale.py",
    "family_unreachable_wholesale.py",
    "localizavo_wholesale.py",
    "miclasico_wholesale.py",
    "subastacar_wholesale.py",
})


def _norm_hash(body: str) -> str:
    norm = "\n".join(line.strip() for line in body.strip().splitlines())
    return hashlib.sha256(norm.encode()).hexdigest()[:10]


def test_core_constant_is_the_canonical_statement() -> None:
    assert _norm_hash(BULK_INSERT_VEHICLES) == _CANON_HASH
    assert "ON CONFLICT (entity_ulid, deep_link) DO NOTHING" in BULK_INSERT_VEHICLES
    assert "transmission" in BULK_INSERT_VEHICLES  # the 14-column (full) shape


def test_no_connector_reintroduces_the_canonical_inline() -> None:
    offenders = []
    for path in glob.glob("pipeline/platform/*.py"):
        fname = path.replace("\\", "/").split("/")[-1]
        src = open(path, encoding="utf-8").read()
        m = _INLINE.search(src)
        if not m:
            continue  # imports the core constant (alias) or doesn't use it
        # An inline literal is only allowed for the genuinely-divergent connectors.
        if _norm_hash(m.group(1)) == _CANON_HASH:
            offenders.append(fname)  # re-introduced the canonical inline -> must import _core instead
        elif fname not in _KNOWN_DIVERGENT:
            offenders.append(f"{fname} (unexpected divergent inline literal)")
    assert not offenders, f"connectors must import BULK_INSERT_VEHICLES from _core.sql: {offenders}"


def test_core_constants_have_expected_shapes() -> None:
    # entity_source upsert (owner/dealer synonyms collapse here)
    assert "INSERT INTO entity_source" in BULK_UPSERT_ENTITY_SOURCE
    assert ("ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()"
            in BULK_UPSERT_ENTITY_SOURCE)
    # touch (refresh last_seen + mark available)
    assert "UPDATE vehicle" in BULK_TOUCH_VEHICLES and "last_seen = now()" in BULK_TOUCH_VEHICLES
    # NEW vehicle_event emit
    assert "INSERT INTO vehicle_event" in BULK_INSERT_EVENTS and "'NEW'" in BULK_INSERT_EVENTS


def test_no_connector_redeclares_a_collapsed_statement_inline() -> None:
    # Every collapsed local name must be an import alias of a _core.sql constant — never an inline
    # literal — so the drift the strangler removed cannot creep back in any of the four statements.
    patterns = {n: re.compile(rf'{n}\s*=\s*"""') for n in _COLLAPSED_LOCAL_NAMES}
    offenders = []
    for path in glob.glob("pipeline/platform/*.py"):
        src = open(path, encoding="utf-8").read()
        fname = path.replace("\\", "/").split("/")[-1]
        for name, pat in patterns.items():
            if pat.search(src):
                offenders.append(f"{fname}:{name}")
    assert not offenders, f"these must import from _core.sql instead of declaring inline: {offenders}"

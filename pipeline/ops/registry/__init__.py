"""Harvest registry — the motor↔pack split (COUNTRY-PACK-CONTRACT.md §4, PIECE 4).

The harvest registry maps every ``source_key`` to the connector module + CLI args the
scheduler launches for it. Historically this lived INLINE in ``pipeline/ops/scheduler.py``
as a hard-coded dict of ~50 ES entries — i.e. **pack data baked into the motor**. The
átomo-review 09 / contract §4 prescribe extracting it so the motor (this package) stays
country-invariant while each country's entries live in their own pack module
``registry/<cc>.py``.

Public API (consumed by the scheduler):

    SourceEntry                         the registry record (source_key, module, extra_args)
    get_harvest_registry(country_code)  -> list[SourceEntry]   (the country's entries, [] if not active)
    active_countries()                  -> list[str]           (the tenants the scheduler harvests)

Byte-identity guarantee: ``active_countries() == ['ES']`` and ``get_harvest_registry('ES')``
returns the ES entries VERBATIM in their original order, so the post-split scheduler harvests
exactly the same sources as before. Pinned by ``tests/test_registry_split.py``.

``SourceEntry`` is DEFINED here (not in the scheduler) so country packs can import it without
a circular dependency back on the scheduler; the scheduler re-exports the name for backward
compatibility (``pipeline.ops.scheduler.SourceEntry`` stays importable).
"""
from __future__ import annotations

from typing import NamedTuple


class SourceEntry(NamedTuple):
    source_key: str
    module: str            # python -m <module>
    extra_args: list[str]  # additional CLI args for that specific source_key


# Country packs are imported AFTER SourceEntry is bound so their
# ``from pipeline.ops.registry import SourceEntry`` resolves during package init.
from pipeline.ops.registry import es as _es  # noqa: E402


# Country-code → ordered harvest entries. The motor knows only the mapping; the
# entries themselves are 100% pack-owned (registry/<cc>.py).
_COUNTRY_REGISTRIES: dict[str, list[SourceEntry]] = {
    "ES": _es.ENTRIES,
}


def active_countries() -> list[str]:
    """Return the tenants the scheduler currently harvests.

    Today only Spain is active, so this is ``['ES']`` and the scheduler's behaviour is
    byte-identical to the pre-split inline registry. Onboarding a second country adds its
    code here (and a ``registry/<cc>.py``) — no scheduler change.
    """
    return ["ES"]


def get_harvest_registry(country_code: str) -> list[SourceEntry]:
    """Return the ordered harvest entries for ``country_code``.

    A fresh list is returned on every call (callers may sort/filter without corrupting the
    canonical pack). An unknown or non-active country yields ``[]`` — never a guess.
    """
    return list(_COUNTRY_REGISTRIES.get(country_code, ()))


__all__ = ["SourceEntry", "active_countries", "get_harvest_registry"]

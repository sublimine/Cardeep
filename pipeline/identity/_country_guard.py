"""Shared country-proof SECOND belt for the deterministic clusterers (T1.2, plans/road-to-13).

Every clusterer's block-keys already carry country (the FIRST belt: indices keyed by
(value, muni, country)). This module is the SECOND belt — a post-clustering assertion that fails
CLOSED if any cluster spans more than one country, so a present-or-future edge-builder that ever
omits country in a key can NEVER silently serve a cross-border merge. Used by both
cluster_dealers and cross_source_dedup; mirrors resolve_entities._assert_no_cross_country_clusters.
The THIRD belt (a DB constraint on entity_cluster) is T1.2-execution (DB-gated)."""
from __future__ import annotations

from typing import Any


class CrossCountryClusterError(ValueError):
    """Raised when a cluster spans more than one country — the country-proof invariant violated.

    Subclasses ValueError (project convention) so an existing ``except ValueError`` still catches it.
    """


def assert_single_country_clusters(
    components: dict[str, list[str]], entity_by_ulid: dict[str, Any]
) -> None:
    """Every cluster MUST be single-country. Empty/None country_codes are ignored (the column is
    DEFAULT 'ES' NOT NULL in the schema; a missing value cannot create a cross-country span).
    Raises :class:`CrossCountryClusterError` on the first multi-country cluster."""
    for root, members in components.items():
        countries = {
            (entity_by_ulid[m].get("country_code") or "").strip().upper()
            for m in members if m in entity_by_ulid
        }
        countries.discard("")
        if len(countries) > 1:
            raise CrossCountryClusterError(
                f"cross-country cluster {root!r} spans {sorted(countries)} "
                f"({len(members)} members) — country-proof violated"
            )

"""P05 — the platform-connector contract (strangler core).

PlatformSpec absorbs the per-module constants that 29 hand-copied ensure_platform_entity
functions hardcoded (trade_name, website, waf, source_key, the platform_meta surface...). One
spec per platform feeds the single ensure_platform_entity in _core/persistence.py — killing the
29-way drift the audit flagged (P05) by turning a copy-paste body into one parametrized callable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PlatformSpec:
    """Identity + data-surface of a platform entity; parametrizes _core.ensure_platform_entity.

    Fields map 1:1 to the columns the legacy per-connector copies wrote:
      entity:        cdp_code, trade_name (-> legal_name too), website, website_waf, is_tier1,
                     first_discovered_source = source_key.
      entity_source: source_key, source_ref.
      platform_meta: data_surface, surface_detail (JSONB), requires_creds, is_platform_like.
    """
    cdp_code: str                  # platform-level cdp_code (precomputed, deterministic)
    trade_name: str
    website: str
    source_key: str
    source_ref: str                # entity_source.source_ref (usually the bare domain)
    data_surface: str              # platform_meta.data_surface (schema-valid literal)
    surface_detail: dict[str, Any] = field(default_factory=dict)
    kind: str = "plataforma"       # entity.kind (almost always 'plataforma')
    legal_name: str | None = None  # entity.legal_name; None -> falls back to trade_name
    website_waf: str | None = None
    is_tier1: bool = False
    requires_creds: bool = False
    is_platform_like: bool = False
    sells_cars: bool | None = None  # entity.sells_cars; None -> NULL (the default the 27 platforms relied on)
    # Optional multi-axis classification columns (migrations/0016); set only by the connectors
    # that use them (e.g. autocasion). Absent -> written NULL == the legacy copy that omitted them.
    defense_tier: str | None = None
    source_group: str | None = None
    role: str | None = None
    family: str | None = None          # platform_meta.family (only some connectors)
    # Entity columns to refresh on cdp_code conflict, BESIDES last_seen. Per-connector: it mirrors
    # the legacy ON CONFLICT DO UPDATE set EXACTLY, so a re-run never wipes a column the legacy left
    # untouched. Members must be in _core.persistence._ALLOWED_REFRESH (allowlist, no injection).
    conflict_refresh: tuple[str, ...] = ()

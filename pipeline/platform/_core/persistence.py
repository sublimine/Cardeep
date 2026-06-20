"""P05 — the single ensure_platform_entity (strangler core).

ONE parametrized form of the 29 byte-divergent hand-copies. Behaviour-preserving: it issues the
exact same entity / entity_source / platform_meta upserts the copies did, with the per-platform
constants lifted into a PlatformSpec. Two values the copies hardcoded as SQL literals (is_tier1,
data_surface) become spec-driven bind params here so one body serves every platform; for any given
spec the rows written are identical to its legacy copy.
"""
from __future__ import annotations

import json

import asyncpg

from pipeline.ids import ulid
from pipeline.platform._core.contract import PlatformSpec

_ENTITY_UPSERT = """
    INSERT INTO entity (entity_ulid, cdp_code, kind, legal_name, trade_name,
           province_code, website, website_waf, is_tier1, status, kind_source,
           first_discovered_source, last_seen)
    VALUES ($1,$2,'plataforma',$3,$3,NULL,$4,$5,$6,'active','platform_label',$7, now())
    ON CONFLICT (cdp_code) DO UPDATE SET last_seen = now(),
        is_tier1 = EXCLUDED.is_tier1, website_waf = EXCLUDED.website_waf
"""

_ENTITY_SOURCE_UPSERT = """
    INSERT INTO entity_source (entity_ulid, source_key, source_ref) VALUES ($1,$2,$3)
    ON CONFLICT (entity_ulid, source_key) DO UPDATE SET seen_at = now()
"""

_PLATFORM_META_UPSERT = """
    INSERT INTO platform_meta (entity_ulid, data_surface, surface_detail,
           requires_creds, is_platform_like)
    VALUES ($1,$2,$3::jsonb,$4,$5)
    ON CONFLICT (entity_ulid) DO UPDATE SET data_surface = EXCLUDED.data_surface,
        surface_detail = EXCLUDED.surface_detail
"""


async def ensure_platform_entity(conn: asyncpg.Connection, spec: PlatformSpec) -> str:
    """Idempotently ensure a platform entity + its entity_source + platform_meta exist.

    Returns the platform entity_ulid. The single parametrized replacement for the 29 copies.
    """
    eulid = ulid()
    await conn.execute(
        _ENTITY_UPSERT, eulid, spec.cdp_code, spec.trade_name, spec.website,
        spec.website_waf, spec.is_tier1, spec.source_key)
    eulid = await conn.fetchval(
        "SELECT entity_ulid FROM entity WHERE cdp_code=$1", spec.cdp_code)
    await conn.execute(
        _ENTITY_SOURCE_UPSERT, eulid, spec.source_key, spec.source_ref)
    await conn.execute(
        _PLATFORM_META_UPSERT, eulid, spec.data_surface, json.dumps(spec.surface_detail),
        spec.requires_creds, spec.is_platform_like)
    return eulid

"""Shared dependencies for the Cardeep API routers.

Contains: DSN, authentication dependency, response helpers, ClusterInfo, resolve_cluster.
Imported by all routers — keeps core logic out of route modules.
"""
from __future__ import annotations

import os
from typing import Any

import asyncpg
from fastapi import Header, HTTPException
from fastapi.responses import JSONResponse

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")


# ---------------------------------------------------------------------------
# B3.5 — API key authentication (backward-compatible).
#
# Behaviour:
#   CARDEEP_API_KEY not set in environment  ->  public mode; all callers pass
#   CARDEEP_API_KEY set in environment      ->  protected mode; X-API-Key required
#
# Applied via Depends(require_api_key) on data endpoints only.
# NOT applied to /health so that liveness probes always reach it.
# ---------------------------------------------------------------------------

def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """FastAPI dependency: enforce the API key when CARDEEP_API_KEY is set."""
    configured_key = os.environ.get("CARDEEP_API_KEY")
    if configured_key is None:
        return
    if x_api_key != configured_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def ok(data: Any, **meta: Any) -> JSONResponse:
    return JSONResponse({"ok": True, "data": data, "error": None, "meta": meta or None})


def err(message: str, status: int = 404) -> JSONResponse:
    return JSONResponse({"ok": False, "data": None, "error": message, "meta": None}, status_code=status)


# ---------------------------------------------------------------------------
# Cluster resolution helper (CAMPAIGN B1.5)
# ---------------------------------------------------------------------------

class ClusterInfo:
    """Result of resolving a cdp_code to its canonical cluster."""

    __slots__ = (
        "canonical_cdp_code",
        "canonical_ulid",
        "member_ulids",
        "member_cdp_codes",
    )

    def __init__(
        self,
        canonical_cdp_code: str,
        canonical_ulid: str,
        member_ulids: list[str],
        member_cdp_codes: list[str],
    ) -> None:
        self.canonical_cdp_code = canonical_cdp_code
        self.canonical_ulid = canonical_ulid
        self.member_ulids = member_ulids
        self.member_cdp_codes = member_cdp_codes


async def resolve_cluster(conn: asyncpg.Connection, cdp_code: str) -> ClusterInfo | None:
    """Resolve *cdp_code* to its canonical and return the full cluster membership.

    Algorithm
    ---------
    1. Look up the entity for *cdp_code* — return None if it does not exist.
    2. Compute the canonical_ulid using v_dealer_resolved (transitive VAM-verified
       clusters), falling back to the entity's own ulid for non-clustered entities.
    3. Collect ALL entities whose canonical (via the same COALESCE logic) equals
       that canonical_ulid — those form the complete cluster.

    Note: uses v_dealer_resolved instead of the deprecated v_canonical so that
    resolution is consistent with the sealed B1 dealer count (40 016).
    """
    entity_row = await conn.fetchrow(
        """
        SELECT e.entity_ulid,
               COALESCE(vdr.resolved_ulid, e.entity_ulid)     AS canonical_ulid,
               COALESCE(vdr.resolved_cdp_code, e.cdp_code)    AS canonical_cdp_code
          FROM entity e
          LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid = e.entity_ulid
         WHERE e.cdp_code = $1
        """,
        cdp_code,
    )
    if entity_row is None:
        return None

    canonical_ulid: str = entity_row["canonical_ulid"]
    canonical_cdp_code: str = entity_row["canonical_cdp_code"]

    member_rows = await conn.fetch(
        """
        SELECT e.entity_ulid,
               e.cdp_code
          FROM entity e
          LEFT JOIN v_dealer_resolved vdr ON vdr.entity_ulid = e.entity_ulid
         WHERE COALESCE(vdr.resolved_ulid, e.entity_ulid) = $1
        """,
        canonical_ulid,
    )
    member_ulids = [r["entity_ulid"] for r in member_rows]
    member_cdp_codes = [r["cdp_code"] for r in member_rows]

    return ClusterInfo(
        canonical_cdp_code=canonical_cdp_code,
        canonical_ulid=canonical_ulid,
        member_ulids=member_ulids,
        member_cdp_codes=member_cdp_codes,
    )

"""Seed chain organizations and fix the kind='cadena' ontology violation (SU-0.5).

Per the entity ontology (decision D-11), a chain is NOT a leaf kind: it is an
`organization`. The live DB had 4 entities mis-kinded as 'cadena' (Clicars, Carplus,
Flexicar, OcasionPlus) and an empty `organization` table. This script:

  1. Creates one `organization` (org_type='chain_compraventa') per VO chain.
  2. Reassigns each chain ROOT entity from kind='cadena' to kind='compraventa'
     (it owns the centrally-scraped stock) and links it to its org via org_id.
  3. Links every chain BRANCH (source_group='chain') to its org via
     first_discovered_source (all 185 branches resolve to Flexicar).
  4. Refreshes organization.branch_count = count(entity WHERE org_id = org).

Idempotent: re-running converges (ON CONFLICT on org_code; the kind reassignment is
guarded by kind='cadena'). cdp_code is never rewritten (immutable invariant #1). Entity
inventory attribution is preserved (entity_ulid unchanged). No vehicle row is touched.

Usage:  python scripts/seed_chain_organizations.py
"""
from __future__ import annotations

import asyncio
import hashlib
import os
import pathlib
import sys

# Make the repo root importable regardless of the caller's cwd.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import asyncpg

from pipeline.ids import ulid
from services.api.codes import _base32  # reuse the exact Crockford-base32 minting primitive

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

# (source_tag, name, domain) — the four VO chains currently mis-kinded as 'cadena'.
# source_tag matches entity.first_discovered_source = 'group_vo_chains_{tag}'.
CHAINS: list[tuple[str, str, str]] = [
    ("flexicar", "Flexicar", "flexicar.es"),
    ("ocasionplus", "OcasionPlus", "ocasionplus.com"),
    ("clicars", "Clicars", "clicars.com"),
    ("carplus", "Carplus", "carplus.es"),
]


def org_code(domain: str) -> str:
    """ORG-ES-{8 x Crockford-base32(sha256('domain:'+host))} — mirrors the cdp_code domain key."""
    key = f"domain:{domain.lower().strip()}"
    return f"ORG-ES-{_base32(hashlib.sha256(key.encode('utf-8')).digest())}"


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        async with conn.transaction():
            for tag, name, domain in CHAINS:
                src = f"group_vo_chains_{tag}"
                org_ulid = await conn.fetchval(
                    """
                    INSERT INTO organization (org_ulid, org_code, name, org_type, website)
                    VALUES ($1, $2, $3, 'chain_compraventa', $4)
                    ON CONFLICT (org_code) DO UPDATE SET last_seen = now()
                    RETURNING org_ulid
                    """,
                    ulid(), org_code(domain), name, domain,
                )
                # Root: cadena -> compraventa (it owns the central chain stock), linked to org.
                await conn.execute(
                    "UPDATE entity SET kind = 'compraventa', org_id = $1 "
                    "WHERE first_discovered_source = $2 AND kind = 'cadena'",
                    org_ulid, src,
                )
                # All chain POS (root + branches) for this source link to the org.
                await conn.execute(
                    "UPDATE entity SET org_id = $1 "
                    "WHERE source_group = 'chain' AND first_discovered_source = $2 "
                    "AND org_id IS DISTINCT FROM $1",
                    org_ulid, src,
                )
                await conn.execute(
                    "UPDATE organization SET branch_count = "
                    "(SELECT count(*) FROM entity WHERE org_id = $1) WHERE org_ulid = $1",
                    org_ulid,
                )

        # Verification (orthogonal read after the transaction commits).
        cadena_left = await conn.fetchval("SELECT count(*) FROM entity WHERE kind = 'cadena'")
        orgs = await conn.fetch(
            "SELECT name, org_code, branch_count FROM organization ORDER BY name"
        )
        print(f"kind='cadena' remaining: {cadena_left}")
        for r in orgs:
            print(f"  {r['name']:<12} {r['org_code']}  branch_count={r['branch_count']}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())

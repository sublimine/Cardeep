"""Seed chain organizations and fix the kind='cadena' ontology violation (SU-0.5).

Per the entity ontology (decision D-11), a chain is NOT a leaf kind: it is an
`organization`. The live DB had 4 entities mis-kinded as 'cadena' (Clicars, Carplus,
Flexicar, OcasionPlus) and an empty `organization` table. This script:

  1. Creates one `organization` (org_type='chain_compraventa') per VO chain.
  2. Reassigns each chain ROOT entity from kind='cadena' to kind='compraventa'
     (it owns the centrally-scraped stock) and links it to its org via org_id.
  3. Links every chain BRANCH (source_group='chain') to its org via
     first_discovered_source (all 185 branches resolve to Flexicar).
  4. [NEW] Links ANY entity whose website host matches a chain domain to its org,
     regardless of first_discovered_source. This covers AS24/OSM-discovered
     branches that were not caught by step 3.
  5. [NEW] Re-kinds chain-domain entities that are mis-typed as 'concesionario_oficial'
     to 'compraventa' (they are used-car chains, not OEM concessionaires). Marks
     kind_source='platform_label' (existing ENUM value, closest semantic fit for
     an authoritative chain override).
  6. Refreshes organization.branch_count = count(entity WHERE org_id = org).

Idempotent: re-running converges (ON CONFLICT on org_code; the kind reassignment
guards are condition-scoped; org_id link uses IS DISTINCT FROM). cdp_code is never
rewritten (immutable invariant #1). Entity inventory attribution is preserved
(entity_ulid unchanged). No vehicle row is touched.

Usage:  python scripts/seed_chain_organizations.py
"""
from __future__ import annotations

import asyncio
import hashlib
import os
import pathlib
import re
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

_RE_SCHEME = re.compile(r"^https?://", re.IGNORECASE)
_RE_WWW = re.compile(r"^www\.", re.IGNORECASE)


def org_code(domain: str) -> str:
    """ORG-ES-{8 x Crockford-base32(sha256('domain:'+host))} — mirrors the cdp_code domain key."""
    key = f"domain:{domain.lower().strip()}"
    return f"ORG-ES-{_base32(hashlib.sha256(key.encode('utf-8')).digest())}"


def _bare_host(website: str | None) -> str | None:
    """Strip scheme + www, return bare lowercase host (no path/query)."""
    if not website or not isinstance(website, str) or not website.strip():
        return None
    h = website.strip().lower()
    h = _RE_SCHEME.sub("", h)
    h = _RE_WWW.sub("", h)
    h = h.split("/")[0].split("?")[0].strip()
    return h if h else None


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        async with conn.transaction():
            for tag, name, domain in CHAINS:
                src = f"group_vo_chains_{tag}"

                # ── Step 1: upsert the organization row ──────────────────────────
                org_ulid = await conn.fetchval(
                    """
                    INSERT INTO organization (org_ulid, org_code, name, org_type, website)
                    VALUES ($1, $2, $3, 'chain_compraventa', $4)
                    ON CONFLICT (org_code) DO UPDATE SET last_seen = now()
                    RETURNING org_ulid
                    """,
                    ulid(), org_code(domain), name, domain,
                )

                # ── Step 2: root cadena entity → compraventa ─────────────────────
                await conn.execute(
                    "UPDATE entity SET kind = 'compraventa', org_id = $1 "
                    "WHERE first_discovered_source = $2 AND kind = 'cadena'",
                    org_ulid, src,
                )

                # ── Step 3: chain POS via first_discovered_source ─────────────────
                await conn.execute(
                    "UPDATE entity SET org_id = $1 "
                    "WHERE source_group = 'chain' AND first_discovered_source = $2 "
                    "AND org_id IS DISTINCT FROM $1",
                    org_ulid, src,
                )

                # ── Step 4 [NEW]: link by website domain match ────────────────────
                # Any entity whose website host == chain domain (or is a subdomain of it)
                # gets linked to this org. Covers AS24/OSM-discovered branches and
                # subdomains like "concesionarios.ocasionplus.com".
                # We match the bare host by stripping scheme+www, then require:
                #   host == domain  OR  host ends with '.' + domain
                # Examples:
                #   "https://www.flexicar.es/coches-madrid/..." → host "flexicar.es" matches
                #   "https://concesionarios.ocasionplus.com"    → host "concesionarios.ocasionplus.com" matches
                linked_by_domain_rows = await conn.fetch(
                    """
                    WITH matched AS (
                        SELECT entity_ulid
                        FROM entity
                        WHERE website IS NOT NULL
                          AND (
                            -- bare host exactly = domain (with optional path suffix)
                            regexp_replace(
                              lower(regexp_replace(website, $2, '', 'i')),
                              $3, '', 'i'
                            ) ~ ('^' || $4 || '(/|\\?|$)')
                            OR
                            -- subdomain of chain domain
                            regexp_replace(
                              lower(regexp_replace(website, $2, '', 'i')),
                              $3, '', 'i'
                            ) ~ ('\\.' || $4 || '(/|\\?|$)')
                          )
                          AND org_id IS DISTINCT FROM $1
                    )
                    UPDATE entity SET org_id = $1
                    WHERE entity_ulid IN (SELECT entity_ulid FROM matched)
                    RETURNING entity_ulid
                    """,
                    org_ulid,
                    r"^https?://",   # $2 strip scheme
                    r"^www\.",        # $3 strip www
                    domain,           # $4 bare domain to match
                )
                print(f"  [{name}] linked by domain: {len(linked_by_domain_rows)} entities")

                # ── Step 5 [NEW]: re-kind chain-domain concesionario_oficial ────
                # Entities of these chains discovered as 'concesionario_oficial'
                # are mis-classified (they are used-car chains). Override to
                # 'compraventa' and mark kind_source='platform_label' as the
                # most accurate available ENUM value for an authoritative chain
                # classification (there is no 'chain_override' value in kind_source).
                rekinded_rows = await conn.fetch(
                    """
                    WITH matched AS (
                        SELECT entity_ulid
                        FROM entity
                        WHERE org_id = $1
                          AND kind = 'concesionario_oficial'
                    )
                    UPDATE entity
                    SET kind = 'compraventa',
                        kind_source = 'platform_label'
                    WHERE entity_ulid IN (SELECT entity_ulid FROM matched)
                    RETURNING entity_ulid
                    """,
                    org_ulid,
                )
                print(f"  [{name}] re-kinded concesionario_oficial->compraventa: {len(rekinded_rows)}")

                # ── Step 6: refresh branch_count ────────────────────────────────
                await conn.execute(
                    "UPDATE organization SET branch_count = "
                    "(SELECT count(*) FROM entity WHERE org_id = $1) WHERE org_ulid = $1",
                    org_ulid,
                )

        # ── Verification (read after commit) ─────────────────────────────────────
        cadena_left = await conn.fetchval("SELECT count(*) FROM entity WHERE kind = 'cadena'")
        orgs = await conn.fetch(
            "SELECT name, org_code, branch_count FROM organization ORDER BY name"
        )
        # Entities of chain domains still without org_id (should be 0)
        unlinked = await conn.fetchval(
            """
            SELECT count(*)
            FROM entity
            WHERE org_id IS NULL
              AND website IS NOT NULL
              AND (
                website ILIKE '%flexicar.es%'
                OR website ILIKE '%ocasionplus.com%'
                OR website ILIKE '%clicars.com%'
                OR website ILIKE '%carplus.es%'
              )
            """
        )
        # Concesionario_oficial entries among chain-domain entities (should be 0)
        still_misclassified = await conn.fetchval(
            """
            SELECT count(*)
            FROM entity e
            JOIN organization o ON o.org_ulid = e.org_id
            WHERE o.org_type = 'chain_compraventa'
              AND e.kind = 'concesionario_oficial'
            """
        )

        print(f"\nkind='cadena' remaining: {cadena_left}")
        print(f"Chain-domain entities without org_id (must be 0): {unlinked}")
        print(f"Chain org entities still concesionario_oficial (must be 0): {still_misclassified}")
        for r in orgs:
            print(f"  {r['name']:<12} {r['org_code']}  branch_count={r['branch_count']}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())

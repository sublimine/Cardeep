"""seed_demo_dealer.py — 03-garage-fleet F1: seed the GYATA demo dealer account.

Why a seed script instead of a real POST /auth/claim-dealer call: GYATA
(CDP-ES-28-YCZB8JYW) has no `cif` on record — verified live against cardeep-pg
2026-07-18 (`SELECT cif FROM entity WHERE cdp_code='CDP-ES-28-YCZB8JYW'` returns
an empty string). ``claim_dealer`` (services/api/routers/auth.py) requires a
checksum-valid tax ID that matches ``entity.cif`` for the claimed cdp_code — with
no cif on record that endpoint always 409s ("no verifiable tax id on record"),
by design (anti dealer-disfrazado control). Faking a cif to pass the real flow
would corrupt census data for a real, non-fictional entity. So the demo account
is seeded directly here, exactly as it will end up in the DB after a real claim
(same app_user + dealer_membership shape, same password hashing primitives) —
never bypassing a security check, just skipping a precondition (a populated cif)
that this specific seed entity does not have.

Idempotent: safe to run multiple times. Does not touch `entity`/`vehicle`/
`vehicle_event` (append-only census) — only `app_user` + `dealer_membership`.

Usage:
    python -m scripts.seed_demo_dealer
"""
from __future__ import annotations

import asyncio
import os

import asyncpg

from pipeline.ids import ulid
from services.api.auth_security import hash_password

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")

DEMO_EMAIL = "demo@cardeep.local"
DEMO_PASSWORD = "CardeepDemo2026!"  # meets validate_password_policy (>=10 chars); demo-only account
DEMO_NAME = "GYATA Demo"
DEMO_DEALER_CDP = "CDP-ES-28-YCZB8JYW"  # GYATA, servicio oficial Ford (Madrid) — see pages/inventory/config.ts


async def seed(conn: asyncpg.Connection) -> str:
    entity_row = await conn.fetchrow(
        "SELECT entity_ulid FROM entity WHERE cdp_code = $1", DEMO_DEALER_CDP
    )
    if entity_row is None:
        raise RuntimeError(f"seed_demo_dealer: entity {DEMO_DEALER_CDP} not found in live census")
    entity_ulid = entity_row["entity_ulid"]

    user_row = await conn.fetchrow(
        "SELECT user_ulid, role FROM app_user WHERE email_lower = lower($1)", DEMO_EMAIL
    )
    if user_row is None:
        user_ulid = ulid()
        await conn.execute(
            """
            INSERT INTO app_user (user_ulid, email, password_hash, name, role)
            VALUES ($1, $2, $3, $4, 'dealer')
            """,
            user_ulid, DEMO_EMAIL, hash_password(DEMO_PASSWORD), DEMO_NAME,
        )
        print(f"created app_user {user_ulid} ({DEMO_EMAIL})")
    else:
        user_ulid = user_row["user_ulid"]
        if user_row["role"] != "dealer":
            await conn.execute(
                "UPDATE app_user SET role = 'dealer', updated_at = now() WHERE user_ulid = $1",
                user_ulid,
            )
        print(f"app_user {user_ulid} already exists ({DEMO_EMAIL})")

    await conn.execute(
        """
        INSERT INTO dealer_membership (user_ulid, entity_ulid, role_in_entity)
        VALUES ($1, $2, 'owner')
        ON CONFLICT (user_ulid, entity_ulid) DO NOTHING
        """,
        user_ulid, entity_ulid,
    )
    print(f"dealer_membership ensured: {user_ulid} -> {entity_ulid} ({DEMO_DEALER_CDP})")
    return user_ulid


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        user_ulid = await seed(conn)
        print(f"\nDemo dealer login ready:\n  email:    {DEMO_EMAIL}\n  password: {DEMO_PASSWORD}\n  user_ulid: {user_ulid}\n  tenant:   {DEMO_DEALER_CDP} (GYATA)")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())

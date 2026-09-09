"""Create or reset the workspace operator account safely.

The operation is deliberately explicit: database location, login and password
must all be supplied by the caller. There are no committed credential defaults,
and neither the password nor the DSN is printed.

Required environment variables:

* ``CARDEEP_DSN``
* ``CARDEEP_ADMIN_USER``
* ``CARDEEP_ADMIN_PASSWORD``

The password must satisfy the same policy as normal registration. The account
uses the existing ``staff`` role and ``enterprise`` plan; no new privilege level
is invented. Re-running the command resets the password and reasserts the role,
plan and active status while touching only ``app_user``.

Usage::

    python -m scripts.seed_admin_user
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass

import asyncpg

from pipeline.ids import ulid
from services.api.auth_security import hash_password, validate_password_policy


@dataclass(frozen=True, slots=True)
class AdminConfig:
    """Validated runtime-only configuration for the operator account."""

    dsn: str
    login: str
    password: str
    name: str = "Administrador"
    role: str = "staff"
    plan: str = "enterprise"


_REQUIRED_ENV = (
    "CARDEEP_DSN",
    "CARDEEP_ADMIN_USER",
    "CARDEEP_ADMIN_PASSWORD",
)


def load_config() -> AdminConfig:
    """Load required settings without embedding or disclosing credentials."""
    missing = [name for name in _REQUIRED_ENV if not os.environ.get(name, "").strip()]
    if missing:
        raise RuntimeError(
            "missing required environment variables: " + ", ".join(missing)
        )

    password = os.environ["CARDEEP_ADMIN_PASSWORD"]
    policy_error = validate_password_policy(password)
    if policy_error is not None:
        raise ValueError(policy_error)

    return AdminConfig(
        dsn=os.environ["CARDEEP_DSN"],
        login=os.environ["CARDEEP_ADMIN_USER"].strip(),
        password=password,
    )


async def seed(
    conn: asyncpg.Connection, config: AdminConfig
) -> tuple[str, bool]:
    """Create or reset the operator account. Return ``(user_ulid, created)``."""
    row = await conn.fetchrow(
        "SELECT user_ulid FROM app_user WHERE email_lower = lower($1)", config.login
    )

    password_hash = hash_password(config.password)
    if row is None:
        user_ulid = ulid()
        await conn.execute(
            """
            INSERT INTO app_user (user_ulid, email, password_hash, name, role, plan, status)
            VALUES ($1, $2, $3, $4, $5, $6, 'active')
            """,
            user_ulid,
            config.login,
            password_hash,
            config.name,
            config.role,
            config.plan,
        )
        return user_ulid, True

    user_ulid = row["user_ulid"]
    await conn.execute(
        """
        UPDATE app_user
           SET password_hash = $2, role = $3, plan = $4, status = 'active', updated_at = now()
         WHERE user_ulid = $1
        """,
        user_ulid,
        password_hash,
        config.role,
        config.plan,
    )
    return user_ulid, False


async def main() -> None:
    config = load_config()
    conn = await asyncpg.connect(config.dsn)
    try:
        user_ulid, created = await seed(conn, config)
    finally:
        await conn.close()

    print(f"{'created' if created else 'reset'} app_user {user_ulid}")
    print(
        f"Operator login ready for {config.login} "
        f"(role={config.role}, plan={config.plan})"
    )


if __name__ == "__main__":
    asyncio.run(main())

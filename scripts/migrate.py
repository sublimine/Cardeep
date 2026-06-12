"""Cardeep migration runner.

Applies numbered SQL migrations from migrations/ in order, tracking applied
versions in a schema_migrations ledger. Idempotent: re-running skips applied
migrations. Each migration file carries its own `-- Rollback:` block (commented)
for manual E2E verification.

Usage:
    python -m scripts.migrate up          # apply all pending
    python -m scripts.migrate status      # show ledger
"""
from __future__ import annotations

import asyncio
import hashlib
import os
import re
import sys
from pathlib import Path

import asyncpg

DSN = os.environ.get("CARDEEP_DSN", "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep")
MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"
_FILENAME_RE = re.compile(r"^(\d{4})_.*\.sql$")

LEDGER_DDL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version    TEXT PRIMARY KEY,
    filename   TEXT NOT NULL,
    sha256     TEXT NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def discover() -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        m = _FILENAME_RE.match(path.name)
        if m:
            found.append((m.group(1), path))
    return found


def strip_rollback(sql: str) -> str:
    """Return only the forward DDL (everything before the `-- Rollback:` marker)."""
    idx = sql.find("-- Rollback:")
    return sql if idx == -1 else sql[:idx]


async def up() -> int:
    conn = await asyncpg.connect(DSN)
    try:
        await conn.execute(LEDGER_DDL)
        applied = {r["version"] for r in await conn.fetch("SELECT version FROM schema_migrations")}
        pending = [(v, p) for v, p in discover() if v not in applied]
        if not pending:
            print("Nothing to apply; schema is up to date.")
            return 0
        for version, path in pending:
            sql = path.read_text(encoding="utf-8")
            forward = strip_rollback(sql)
            sha = hashlib.sha256(sql.encode("utf-8")).hexdigest()
            async with conn.transaction():
                await conn.execute(forward)
                await conn.execute(
                    "INSERT INTO schema_migrations (version, filename, sha256) VALUES ($1, $2, $3)",
                    version, path.name, sha,
                )
            print(f"applied {version} {path.name}")
        return len(pending)
    finally:
        await conn.close()


async def status() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        await conn.execute(LEDGER_DDL)
        rows = await conn.fetch("SELECT version, filename, applied_at FROM schema_migrations ORDER BY version")
        if not rows:
            print("No migrations applied yet.")
        for r in rows:
            print(f"  {r['version']}  {r['filename']}  @ {r['applied_at']}")
        all_versions = [v for v, _ in discover()]
        pending = [v for v in all_versions if v not in {r["version"] for r in rows}]
        print(f"applied={len(rows)} pending={len(pending)} {pending or ''}")
    finally:
        await conn.close()


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "up"
    if cmd == "up":
        n = asyncio.run(up())
        print(f"done: {n} migration(s) applied")
    elif cmd == "status":
        asyncio.run(status())
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main()

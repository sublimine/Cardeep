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
from typing import Iterator

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


def split_statements(sql: str) -> Iterator[str]:
    """Split a SQL migration into individual statements.

    Handles $$ dollar-quoting so semicolons inside function/trigger bodies are
    not treated as statement terminators. Empty or comment-only chunks are
    skipped. This works around an asyncpg bug where executing a large multi-
    statement DDL block as a single call raises AttributeError on NoneType when
    the server emits a mix of NOTICE messages and CommandComplete packets for
    complex DDL sequences (CREATE OR REPLACE FUNCTION + DROP/CREATE TRIGGER in
    the same batch).
    """
    in_dollar = False
    current: list[str] = []

    for line in sql.splitlines():
        stripped = line.rstrip()
        # Count $$ occurrences to track dollar-quote nesting (simple, no nested $$)
        count = stripped.count("$$")
        if count % 2 == 1:
            in_dollar = not in_dollar

        current.append(line)

        if not in_dollar and stripped.endswith(";"):
            stmt = "\n".join(current).strip()
            if stmt and not all(l.lstrip().startswith("--") for l in stmt.splitlines() if l.strip()):
                yield stmt
            current = []

    # Flush any trailing content without a trailing semicolon
    if current:
        stmt = "\n".join(current).strip()
        if stmt and not all(l.lstrip().startswith("--") for l in stmt.splitlines() if l.strip()):
            yield stmt


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
            stmts = list(split_statements(forward))
            async with conn.transaction():
                for stmt in stmts:
                    await conn.execute(stmt)
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

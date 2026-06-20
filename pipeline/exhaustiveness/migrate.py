"""Idempotent applier for the exhaustiveness migration (0048).

Applies the SQL (which is itself idempotent: CREATE IF NOT EXISTS / CREATE OR
REPLACE) and registers it in schema_migrations with the real file sha256, the
same contract the existing migrations follow.
"""

from __future__ import annotations

import hashlib
import pathlib

import psycopg2

DSN = "postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep"
MIGRATION = pathlib.Path(__file__).resolve().parents[2] / "migrations" / "0048_discovery_capture.sql"
VERSION = "0048"


def apply(dsn: str = DSN) -> None:
    sql = MIGRATION.read_text(encoding="utf-8")
    sha = hashlib.sha256(sql.encode("utf-8")).hexdigest()
    conn = psycopg2.connect(dsn)
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql)
            cur.execute(
                """
                INSERT INTO schema_migrations (version, filename, sha256)
                VALUES (%s, %s, %s)
                ON CONFLICT (version) DO UPDATE SET sha256 = EXCLUDED.sha256,
                                                    filename = EXCLUDED.filename
                """,
                (VERSION, MIGRATION.name, sha),
            )
        print(f"migration {VERSION} applied (sha256={sha[:12]}...)")
    finally:
        conn.close()


if __name__ == "__main__":
    apply()

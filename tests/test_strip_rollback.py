"""Regression tests for scripts/migrate.py::strip_rollback.

Recurring bug: a `-- Rollback:` mention in a migration's HEADER comment caused
strip_rollback to truncate the forward DDL to 0 bytes (it cut at the FIRST
occurrence of the marker). This silently bit migrations 0026 and 0031 — the
runner registered them as applied while executing zero DDL.

Fix: use the LAST occurrence (rfind = the trailing rollback block) and guard
against truncating to empty (return full SQL when no DDL keyword survives).
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from scripts.migrate import strip_rollback


def test_normal_trailing_rollback_block() -> None:
    sql = "CREATE TABLE foo (id int);\n\n-- Rollback:\n-- DROP TABLE foo;\n"
    out = strip_rollback(sql)
    assert "CREATE TABLE foo" in out
    assert "DROP TABLE foo" not in out


def test_header_rollback_mention_does_not_truncate_ddl() -> None:
    """A 'Rollback:' mention in the header must NOT eat the DDL (0026/0031 bug)."""
    sql = (
        "-- 0099_x.sql — does X.\n"
        "-- Rollback: drops the table on revert.\n"  # header mention = the trap
        "CREATE TABLE bar (id int);\n"
        "-- Rollback:\n"
        "-- DROP TABLE bar;\n"
    )
    out = strip_rollback(sql)
    assert "CREATE TABLE bar" in out, "DDL must survive a header 'Rollback:' mention"
    assert "DROP TABLE bar" not in out


def test_header_rollback_only_no_trailing_block_returns_full() -> None:
    """Header mentions 'Rollback:' with no trailing block -> guard returns full SQL."""
    sql = "-- header with a -- Rollback: note\nCREATE TABLE baz (id int);\n"
    out = strip_rollback(sql)
    assert "CREATE TABLE baz" in out, "guard must never truncate to 0 bytes of DDL"


def test_no_rollback_marker_returns_full() -> None:
    sql = "CREATE TABLE q (id int);\n"
    assert strip_rollback(sql) == sql

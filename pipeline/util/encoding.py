"""Canonical stdout/stderr encoding guard.

Windows consoles and pipes default to cp1252, which cannot encode non-ASCII
characters such as the Greek sigma (U+03A3), em-dash (U+2014), or accented
Spanish letters found in car titles and connector progress output.  A raw
print() on cp1252 raises UnicodeEncodeError and aborts the process mid-harvest.

Usage (call once, at the very top of any entry point or harvest function):

    from pipeline.util.encoding import force_utf8_stdout
    force_utf8_stdout()

The scheduler subprocess environment already sets PYTHONIOENCODING=utf-8 for
all child processes, so this guard is belt-and-suspenders insurance for direct
invocations (developer shell, CI, cron outside the scheduler).  The 35
existing per-file copies of _force_utf8_stdout() are intentionally left in
place as compatible no-ops once PYTHONIOENCODING is set; they are catalogued
as minor debt but pose zero runtime risk after the scheduler env fix.
"""
from __future__ import annotations

import sys


def force_utf8_stdout() -> None:
    """Reconfigure sys.stdout and sys.stderr to UTF-8 with errors='replace'.

    Idempotent: if both streams are already UTF-8 the function returns
    immediately without touching either stream.  Safe to call multiple times
    (from harvest() and from main() without double-reconfiguration side
    effects).

    Silently swallows AttributeError (Python < 3.7 TextIOWrapper without
    reconfigure, or wrapped streams without the method) and ValueError (stream
    closed or already detached).
    """
    already_utf8 = all(
        getattr(s, "encoding", "").lower().replace("-", "") == "utf8"
        for s in (sys.stdout, sys.stderr)
    )
    if already_utf8:
        return

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass

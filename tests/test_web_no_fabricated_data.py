"""Guardrail: the web portal must NEVER ship fabricated or stale data values.

Born from the frontend data-integrity audit (workflow wyp2ucequ): the Landing page shipped a
hardcoded FALLBACK Stats object (vehicles_unique_available=1_704_968, dealers=61_729, events=0)
and a frozen public/geo/seal-snapshot.json that had drifted from the live API (6 province verdicts
flipped) — both were displayed as if they were live data. The owner caught the portal showing
1.704.968 cars while /stats served 1.841.679.

This test fails if that bug CLASS reappears, so every data point on the portal comes from the live
API and a fabricated literal can never silently drift again. DB-free (pure file scan) -> runs in the
CI unit job on every push.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_REPO = Path(__file__).resolve().parent.parent
_WEB_SRC = _REPO / "web" / "src"
_WEB_PUBLIC = _REPO / "web" / "public"

# Legitimate big-number CONFIG constants (NOT displayed data). Extend deliberately, with a reason.
_ALLOWED_BIG_NUMERICS: dict[str, set[str]] = {
    "main.tsx": {"60_000"},  # TanStack Query staleTime in ms — a config knob, never shown to a user
}


def _code_lines(path: Path):
    """Yield (lineno, code) for non-comment lines (drops // and block-comment lines, strips trailing //)."""
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        s = raw.strip()
        if s.startswith("//") or s.startswith("*") or s.startswith("/*"):
            continue
        yield i, raw.split("//", 1)[0]


def _ts_files():
    if not _WEB_SRC.exists():
        return []
    return [p for p in _WEB_SRC.rglob("*.ts*") if p.is_file()]


def test_no_frozen_seal_snapshot_file():
    snap = _WEB_PUBLIC / "geo" / "seal-snapshot.json"
    assert not snap.exists(), (
        f"{snap} is a FROZEN fabricated data file — it drifted from the live seal and painted wrong "
        "province verdicts when the API was down. The map must read /geo/seal live; delete this file."
    )


def test_no_typed_fabricated_data_object():
    """No const typed as a live API type assigned a hardcoded object literal (the FALLBACK antipattern)."""
    # Negative lookahead skips EMPTY initializers (`= {}` / `= { }`) — only a NON-empty literal with
    # hardcoded fields is the fabrication antipattern.
    pat = re.compile(r":\s*(Stats|GeoSeal|SealMap|Exhaustiveness|ProvinceCoverage)\s*=\s*\{(?!\s*\})")
    offenders = []
    for f in _ts_files():
        for ln, code in _code_lines(f):
            if pat.search(code):
                offenders.append(f"{f.relative_to(_REPO)}:{ln}: {code.strip()}")
    assert not offenders, (
        "Fabricated data object(s) typed as a live API type — render from the live API, never a "
        "hardcoded snapshot:\n" + "\n".join(offenders)
    )


def test_no_unexplained_big_underscore_numerics():
    """Underscore-separated big literals (e.g. 1_704_968) smell of a fabricated count. Whitelist config only."""
    pat = re.compile(r"\b\d{1,3}(?:_\d{3})+\b")
    offenders = []
    for f in _ts_files():
        allowed = _ALLOWED_BIG_NUMERICS.get(f.name, set())
        for ln, code in _code_lines(f):
            for m in pat.findall(code):
                if m not in allowed:
                    offenders.append(f"{f.relative_to(_REPO)}:{ln}: {m}")
    assert not offenders, (
        "Underscore-separated big numeric literal(s) in web/src (smell of a fabricated count). If it is "
        "a displayed data value, read it from the live API; if it is a config constant, add it to "
        "_ALLOWED_BIG_NUMERICS with a reason:\n" + "\n".join(offenders)
    )

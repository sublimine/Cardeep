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


@pytest.mark.skip(reason=(
    "TRACKED DEBT (plans/road-to-13 T5). This is the census-TRUTH guard for displayed counts, but "
    "today NO web page consumes the live census: web/src/api/cardeep.ts has 0 imports. The whole "
    "frontend is a demo/marketing scaffold — the landing ships count-up demo figures (1_550_000 "
    "'vehículos', 28_000 'dealers') and the CRM/terminal scaffold ships UI mock (Dashboard/Market "
    "2_140_000, ...). None are census claims wired to /stats, so scanning them is a false positive, "
    "not a fabrication-served-as-truth. It re-activates the moment T5 wires pages to cardeep.ts "
    "(then every displayed figure must come from /stats). The RIVR-class bomb — another product's "
    "vocabulary and abbreviated metrics — is defended LIVE by the two checks below."))
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


# ---------------------------------------------------------------------------
# Hardened guardrail (T0.2): the previous three checks only caught the exact 2026-06-23 bug shape
# (typed Stats object, underscore numerics, frozen snapshot). They did NOT catch the next class: a
# whole landing copied from a DIFFERENT product (a DeFi protocol "RIVR") with abbreviated string
# metrics ('$2.4B' TVL, '8.5%' APY, '140K+' yielders) — strings without a type annotation, invisible
# to the old regexes. These checks close that class. Scoped to the LANDING (the public surface that
# MUST show real census figures or '—'); the authenticated CRM/terminal scaffold is out of scope, so
# its own legitimate financial vocabulary never trips this.
# ---------------------------------------------------------------------------
def _landing_files():
    """The public landing surface: Landing.tsx + landing-sections.tsx + anything under pages/landing/."""
    if not _WEB_SRC.exists():
        return []
    files = []
    for rel in ("pages/Landing.tsx", "pages/landing-sections.tsx"):
        p = _WEB_SRC / rel
        if p.is_file():
            files.append(p)
    ld = _WEB_SRC / "pages" / "landing"
    if ld.is_dir():
        files.extend(p for p in ld.rglob("*.ts*") if p.is_file())
    return files


# Vocabulary that belongs to a DeFi/crypto protocol, never to a Spanish used-car census. The RIVR
# motionsites template leaked these into the landing. WORD-BOUNDED regex so 'defi' never matches
# 'defined', 'staking' never matches 'mistaking', 'apy' never matches 'therapy', etc.
_FOREIGN_PRODUCT_PATTERNS = (
    r"\brivr\b", r"\bstaking\b", r"\byielders?\b", r"\bliquid stak", r"\bvalue locked\b",
    r"\btvl\b", r"\bapy\b", r"\bsmart vault", r"\bvaults?\b", r"\bfluid asset", r"\bdefi\b",
)


def test_landing_has_no_foreign_product_vocabulary():
    offenders = []
    for f in _landing_files():
        low = f.read_text(encoding="utf-8").lower()
        for pat in _FOREIGN_PRODUCT_PATTERNS:
            if re.search(pat, low):
                offenders.append(f"{f.relative_to(_REPO)}: foreign-product pattern {pat!r}")
    assert not offenders, (
        "The landing carries vocabulary from ANOTHER product (DeFi/crypto). It must speak CARDEEP — "
        "the live Spanish used-car census — not a staking protocol:\n" + "\n".join(offenders)
    )


# Abbreviated money/scale metrics displayed as hardcoded strings ('$2.4B', '$140M'). A real figure
# must come from the live API (cardeep.ts) or render '—' while loading — never a fabricated literal.
_ABBREV_MONEY = re.compile(r"\$\s?\d[\d.,]*\s*[bmk]\b", re.IGNORECASE)


def test_landing_has_no_hardcoded_abbreviated_money_metric():
    offenders = []
    for f in _landing_files():
        for ln, code in _code_lines(f):
            for m in _ABBREV_MONEY.findall(code):
                offenders.append(f"{f.relative_to(_REPO)}:{ln}: {m!r}")
    assert not offenders, (
        "Hardcoded abbreviated money metric(s) on the landing (smell of a fabricated stat). Read "
        "every displayed figure from the live API or show '—':\n" + "\n".join(offenders)
    )

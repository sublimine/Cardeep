"""Repository-level guards against runtime coupling to sibling projects."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_ROOTS = ("pipeline", "scripts", "services", "workspace")
SOURCE_SUFFIXES = {".go", ".js", ".mjs", ".py", ".ps1", ".sh", ".ts", ".tsx"}
CARDEX_OWNED_OPERATIONS = re.compile(
    r"(?i)\b(?:cardex-pipeline|cardex-scraper|python-scraper)\b"
)
SIBLING_CHECKOUT = re.compile(
    r"(?ix)(?:"
    r"[a-z]:[\\/](?:users[\\/][^\\/]+[\\/])?(?:projects[\\/])?(?:cardex|cardeex)(?:[\\/]|\b)"
    r"|/(?:home[\\/][^\\/]+[\\/])?(?:projects?[\\/])?(?:cardex|cardeex)(?:[\\/]|\b)"
    r")"
)


def test_active_code_has_no_hard_coded_sibling_checkout() -> None:
    offenders: list[str] = []
    for root_name in ACTIVE_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if SIBLING_CHECKOUT.search(text):
                offenders.append(path.relative_to(ROOT).as_posix())

    assert offenders == [], f"runtime code depends on a sibling project checkout: {offenders}"


def test_cardeep_docs_do_not_prescribe_cardex_owned_agents_or_skills() -> None:
    offenders: list[str] = []
    for path in (ROOT / "docs").rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if CARDEX_OWNED_OPERATIONS.search(text):
            offenders.append(path.relative_to(ROOT).as_posix())

    assert offenders == [], f"Cardeep docs prescribe CARDEX-owned operations: {offenders}"


def test_raw_third_party_aecs_page_is_not_versioned() -> None:
    assert not (ROOT / "docs/research/associations/aecs_raw.html").exists()

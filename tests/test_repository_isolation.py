"""Repository-level guards against runtime coupling to sibling projects."""

from __future__ import annotations

import json
import re
import subprocess
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
WINDOWS_PROFILE = re.compile(rb"(?i)[a-z]:[\\/]+users[\\/]+")
POSIX_USER_PROFILE = re.compile(rb"(?:/[A-Za-z]/" + rb"Users/|/" + rb"Users/)")
ENCODED_WINDOWS_PROFILE = re.compile(rb"(?i)[a-z]%3a%5c" + rb"users%5c")
CONSUMER_EMAIL = re.compile(
    rb"(?i)[a-z0-9._%+-]+@(?:gmail|hotmail|outlook|icloud|protonmail|yahoo)\.[a-z]{2,}"
)
PINTEREST_PROFILE_URL = re.compile(
    rb"(?i)(?:https?://)?(?:[a-z]{2}\.)?pinterest\.com/[a-z0-9._-]+/"
)
CARDEX_BRANDED_RUNTIME_EXAMPLE = re.compile(
    rb"(?i)(?:session[-_]?cardex|postgresql(?:\+asyncpg)?://[^\s\"']*cardex)"
)


def _tracked_paths() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / item.decode("utf-8") for item in output.split(b"\0") if item]


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


def test_cardeep_docs_have_no_cardex_branded_runtime_examples() -> None:
    offenders = [
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "docs").rglob("*.md")
        if CARDEX_BRANDED_RUNTIME_EXAMPLE.search(path.read_bytes())
    ]

    assert offenders == [], f"Cardeep docs contain CARDEX-branded runtime examples: {offenders}"


def test_raw_third_party_aecs_page_is_not_versioned() -> None:
    assert not (ROOT / "docs/research/associations/aecs_raw.html").exists()


def test_tracked_tree_has_no_absolute_windows_profile_paths() -> None:
    offenders = [
        path.relative_to(ROOT).as_posix()
        for path in _tracked_paths()
        if WINDOWS_PROFILE.search(path.read_bytes())
        or POSIX_USER_PROFILE.search(path.read_bytes())
        or ENCODED_WINDOWS_PROFILE.search(path.read_bytes())
    ]

    assert offenders == [], f"tracked files expose a local Windows profile path: {offenders}"


def test_deployment_runbooks_have_no_personal_consumer_email() -> None:
    runbooks = (
        ROOT / "docs/runbook/DEPLOY_OPENSHIP.md",
        ROOT / "docs/runbook/DEPLOY_VERCEL.md",
    )
    offenders = [
        path.relative_to(ROOT).as_posix()
        for path in runbooks
        if CONSUMER_EMAIL.search(path.read_bytes())
    ]

    assert offenders == [], f"deployment runbooks expose a personal email: {offenders}"


def test_docs_have_no_person_specific_pinterest_profile_url() -> None:
    offenders = [
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "docs").rglob("*.md")
        if PINTEREST_PROFILE_URL.search(path.read_bytes())
    ]

    assert offenders == [], f"docs expose a Pinterest profile URL: {offenders}"


def test_executable_workflows_do_not_depend_on_profile_placeholders() -> None:
    roots = (ROOT / ".wf", ROOT / "pipeline", ROOT / "scripts", ROOT / "plans")
    offenders: list[str] = []
    for root in roots:
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES:
                if b"<USERPROFILE>" in path.read_bytes().upper():
                    offenders.append(path.relative_to(ROOT).as_posix())
    settings = ROOT / ".claude/settings.json"
    if b"<USERPROFILE>" in settings.read_bytes().upper():
        offenders.append(settings.relative_to(ROOT).as_posix())

    assert offenders == [], f"executable workflows retain a profile placeholder: {offenders}"


def test_session_hook_is_rooted_in_claude_project_directory() -> None:
    settings = json.loads(
        (ROOT / ".claude/settings.json").read_text(encoding="utf-8")
    )
    command = settings["hooks"]["SessionEnd"][0]["hooks"][0]["command"]

    assert "$CLAUDE_PROJECT_DIR/.claude/hooks/session_log.py" in command
    assert (ROOT / ".claude/hooks/session_log.py").is_file()

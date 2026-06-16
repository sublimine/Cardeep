"""One-shot: quote prose recipe-YAML values containing an embedded ': ' (colon-space), which YAML
mis-parses as a nested mapping (audit Q3).

30 hand-authored tier1/platform/chain recipes (recipe_version=NULL) bypassed write_recipe()'s
round-trip guard and are YAML-unparseable (e.g. `ownership: PER-DEALER-BY-NAME: the card...`). The
LIVE pipeline is unaffected (the G3 completion gate reads the DB recipe_version, never parses these
YAMLs; the executable recipe for these connectors lives in code), but a recipe must be readable as a
re-scrape spec for "cualquiera pueda retomarlo". This quotes the offending scalar values (quoting a
scalar is always valid YAML and preserves the human-readable meaning). Idempotent: files that already
parse are skipped. Verifies EACH candidate fix re-parses before writing; anything it cannot fix
safely is reported for manual repair (never silently mangled).

Usage:
    python scripts/fix_recipe_yaml.py            # DRY-RUN (reports, writes nothing)
    python scripts/fix_recipe_yaml.py --apply     # write the fixes
"""
from __future__ import annotations

import glob
import os
import re
import sys

import yaml

APPLY = "--apply" in sys.argv
CHECK = "--check" in sys.argv  # CI lint: exit 1 if any recipe.yaml is unparseable (no writes)
ROOT = os.path.join(os.path.dirname(__file__), "..")
# key: value  — value a non-empty scalar; quote it only when it carries a colon-space (the
# YAML-confusing pattern) and is not already quoted / a flow collection / a block scalar.
_LINE = re.compile(r"^(\s*)([\w_/.\-]+): (\S.*)$")
_SKIP_FIRST = ('"', "'", "{", "[", "|", ">", "&", "*", "#")


def fix_text(raw: str) -> str:
    out = []
    for ln in raw.split("\n"):
        m = _LINE.match(ln)
        if m:
            val = m.group(3)
            # Quote when the value carries a colon-space (mis-read as a nested mapping) OR starts
            # with a YAML reserved indicator (backtick/@/%) that voids a plain scalar.
            if (": " in val or val[0] in ("`", "@", "%")) and val[0] not in _SKIP_FIRST:
                esc = val.replace("\\", "\\\\").replace('"', '\\"')
                out.append(f'{m.group(1)}{m.group(2)}: "{esc}"')
                continue
        out.append(ln)
    return "\n".join(out)


def _parses(text: str) -> bool:
    try:
        yaml.safe_load(text)
        return True
    except Exception:
        return False


def main() -> None:
    files = glob.glob(os.path.join(ROOT, "countries/ES/**/recipe.yaml"), recursive=True)
    if CHECK:
        broken = [os.path.relpath(f, ROOT) for f in files
                  if not _parses(open(f, encoding="utf-8").read())]
        print(f"recipe files={len(files)} unparseable={len(broken)}")
        for b in broken:
            print(f"  BROKEN: {b}")
        sys.exit(1 if broken else 0)
    bad = fixed = 0
    unfixable = []
    for f in files:
        raw = open(f, encoding="utf-8").read()
        if _parses(raw):
            continue
        bad += 1
        new = fix_text(raw)
        if not _parses(new):
            unfixable.append((os.path.relpath(f, ROOT), "still unparseable after quoting"))
            continue
        if APPLY:
            open(f, "w", encoding="utf-8").write(new)
        fixed += 1
    print(f"recipe files={len(files)} unparseable={bad} fixable={fixed} unfixable={len(unfixable)}")
    for rel, why in unfixable:
        print(f"  UNFIXABLE (manual): {rel}: {why}")
    if APPLY:
        still = [os.path.relpath(f, ROOT) for f in files if not _parses(open(f, encoding="utf-8").read())]
        print(f"after apply: still-unparseable={len(still)}")
        assert not still, f"files still broken after apply: {still}"
    else:
        print("DRY-RUN — re-run with --apply to write.")


if __name__ == "__main__":
    main()

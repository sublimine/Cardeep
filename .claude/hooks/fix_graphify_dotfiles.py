#!/usr/bin/env python3
"""Post-process fixup for graphify's Obsidian export: Obsidian treats any
file/folder starting with "." as hidden (same convention as .git/, .obsidian/
elsewhere in this repo) — confirmed empirically via the REST API's directory
listing endpoint, which silently omits them. graphify's safe_name() sanitizer
does not strip a leading dot (common when an AST label is a chained method
call like ".acquire()"), so a meaningful fraction of the exported vault
(~9% measured on 2026-07-15) is invisible to Obsidian's file explorer, graph
view, and search despite existing on disk and being readable by direct path.

This rewrites every offending filename (drops the leading dot; resolves any
resulting collision with a numeric suffix) and rewrites every [[wikilink]]
across the export directory that pointed at the old name, so backlinks keep
resolving after the rename.

Idempotent — safe to run after every `graphify export obsidian`, including
via the post-commit hook. Never touches non-dot files or graphify's own
manifest.
"""
import os
import re
import sys

TARGET_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "docs", "second-brain", "gf",
)

MANIFEST_NAME = ".graphify_obsidian_manifest.json"


def main():
    if not os.path.isdir(TARGET_DIR):
        return
    os.chdir(TARGET_DIR)

    all_files = []
    for dirpath, _, filenames in os.walk("."):
        for fn in filenames:
            rel = os.path.normpath(os.path.join(dirpath, fn)).replace("\\", "/")
            if rel.startswith("./"):
                rel = rel[2:]
            all_files.append(rel)

    existing = set(all_files)
    rename_map = {}  # old basename (no dir, with ext) -> new basename

    for rel in all_files:
        base = os.path.basename(rel)
        if base == MANIFEST_NAME:
            continue
        if not base.startswith("."):
            continue
        new_base = base.lstrip(".")
        if not new_base:
            new_base = "unnamed" + os.path.splitext(base)[1]
        new_rel = os.path.join(os.path.dirname(rel), new_base).replace("\\", "/")
        # Resolve collisions deterministically.
        n = 1
        candidate = new_rel
        while candidate in existing and candidate != rel:
            stem, ext = os.path.splitext(new_rel)
            candidate = f"{stem}_{n}{ext}"
            n += 1
        existing.discard(rel)
        existing.add(candidate)
        rename_map[rel] = candidate
        rename_map[base] = os.path.basename(candidate)
        stem_old, _ext_old = os.path.splitext(base)
        stem_new, _ext_new = os.path.splitext(os.path.basename(candidate))
        rename_map[stem_old] = stem_new

    if not rename_map:
        print("fix_graphify_dotfiles: no dot-prefixed files found, nothing to do")
        return

    file_renames = {k: v for k, v in rename_map.items() if "/" in k or os.path.sep in k or k in all_files}
    # Perform the actual filesystem renames (only for real relative paths).
    renamed_count = 0
    for rel in all_files:
        if rel in rename_map and rename_map[rel] != rel:
            new_rel = rename_map[rel]
            os.makedirs(os.path.dirname(new_rel) or ".", exist_ok=True)
            os.replace(rel, new_rel)
            renamed_count += 1

    # Rewrite wikilinks in every remaining .md file. Single combined
    # alternation regex + dict lookup = one pass per file (O(files)), not
    # one regex substitution per rename target per file (O(files*targets) —
    # 26k files x 2.4k targets was still running after 5+ minutes and had to
    # be killed; this is the fix for that).
    link_targets = sorted(
        (k for k in rename_map if not k.endswith((".md", ".canvas", ".json"))),
        key=len, reverse=True,
    )
    if link_targets:
        combined = re.compile(
            r"\[\[(" + "|".join(re.escape(k) for k in link_targets) + r")(\||\]|#)"
        )

        def _replace(m):
            return f"[[{rename_map[m.group(1)]}{m.group(2)}"

        updated_files = 0
        for dirpath, _, filenames in os.walk("."):
            for fn in filenames:
                if not fn.endswith(".md"):
                    continue
                path = os.path.normpath(os.path.join(dirpath, fn)).replace("\\", "/")
                if path.startswith("./"):
                    path = path[2:]
                try:
                    text = open(path, encoding="utf-8").read()
                except Exception:
                    continue
                new_text = combined.sub(_replace, text)
                if new_text != text:
                    open(path, "w", encoding="utf-8").write(new_text)
                    updated_files += 1
    else:
        updated_files = 0

    print(f"fix_graphify_dotfiles: renamed {renamed_count} file(s), rewrote links in {updated_files} note(s)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""SessionEnd hook: auto-capture deterministic session metadata into the
Obsidian second-brain vault (docs/second-brain/sessions/).

Fires once per real Claude Code session end (SessionEnd, not Stop — Stop
fires per turn and would spam a note per response). Writes nothing when
nothing changed since the last captured checkpoint (new commits or a
different uncommitted-changes fingerprint), so /clear-without-work or a
repeated SessionEnd never produces empty or duplicate notes.

Never raises — a broken logger must not block session end.
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def git(repo_root, *args):
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True, text=True, timeout=15,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def main():
    raw = sys.stdin.read()
    payload = json.loads(raw) if raw.strip() else {}

    session_id = payload.get("session_id", "unknown")
    cwd = payload.get("cwd") or str(Path(__file__).resolve().parents[2])
    exit_reason = payload.get("exit_reason", "unknown")
    final_turn_count = payload.get("final_turn_count", "?")

    repo_root_str = git(cwd, "rev-parse", "--show-toplevel")
    if not repo_root_str:
        return  # not inside a git repo — nothing sane to log
    repo_root = Path(repo_root_str)

    marker_path = repo_root / ".claude" / "second-brain-session-marker.json"
    marker = {"last_commit": None, "last_diff_hash": ""}
    if marker_path.exists():
        try:
            marker = json.loads(marker_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    current_commit = git(repo_root, "rev-parse", "HEAD")
    status_text = git(repo_root, "status", "--porcelain")
    current_diff_hash = hashlib.sha256(status_text.encode("utf-8")).hexdigest()

    last_commit = marker.get("last_commit")
    last_diff_hash = marker.get("last_diff_hash", "")

    if last_commit is None:
        # First run: establish baseline only, no note (avoids dumping
        # the whole repo history into a single "session" note).
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        marker_path.write_text(json.dumps({
            "last_commit": current_commit,
            "last_diff_hash": current_diff_hash,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }, indent=2), encoding="utf-8")
        return

    new_commits_text = git(repo_root, "log", f"{last_commit}..HEAD", "--oneline") if last_commit else ""
    new_commits = [l for l in new_commits_text.splitlines() if l.strip()]
    status_lines = [l for l in status_text.splitlines() if l.strip()]

    changed = bool(new_commits) or (current_diff_hash != last_diff_hash and bool(status_lines))
    if not changed:
        return  # nothing real happened — no note, no marker churn

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    stamp = now.strftime("%Y-%m-%d-%H%M%S")
    short_id = session_id[:8] if session_id else "unknown"

    lines = []
    lines.append("---")
    lines.append("type: session")
    lines.append("status: ASUMIDO")
    lines.append(f"date: {date_str}")
    lines.append("tags: [session-log, auto-generated]")
    lines.append("---")
    lines.append("")
    lines.append(f"# Sesión {date_str} {now.strftime('%H:%M')} — auto-generada")
    lines.append("")
    lines.append("## Qué se hizo (capturado automáticamente por el hook SessionEnd)")
    lines.append("")
    if new_commits:
        lines.append("**Commits nuevos:**")
        for c in new_commits:
            lines.append(f"- `{c}`")
        lines.append("")
    if status_lines:
        lines.append("**Cambios sin comitear al terminar la sesión:**")
        for s in status_lines:
            lines.append(f"- `{s}`")
        lines.append("")
    lines.append("## Decisiones")
    lines.append("")
    lines.append("_No capturado automáticamente — completar a mano si aplica._")
    lines.append("")
    lines.append("## Pendientes")
    lines.append("")
    lines.append("_No capturado automáticamente — completar a mano si aplica._")
    lines.append("")
    lines.append("---")
    lines.append(f"_Metadata: session_id={session_id}, exit_reason={exit_reason}, "
                  f"turns={final_turn_count}, commit_range={last_commit[:8] if last_commit else '?'}..{current_commit[:8]}_")
    lines.append("")

    sessions_dir = repo_root / "docs" / "second-brain" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    note_path = sessions_dir / f"{stamp}-{short_id}.md"
    note_path.write_text("\n".join(lines), encoding="utf-8")

    # Re-snapshot AFTER writing: the note itself is now an untracked file in
    # the working tree (this hook never auto-commits, by design — see the
    # original vault spec's rationale against an auto-commit plugin). If the
    # marker recorded the pre-write hash, the note's own existence would look
    # like "new uncommitted change" on the very next run and spam another
    # note forever. Baselining post-write makes the note part of the
    # accepted baseline instead.
    post_write_status = git(repo_root, "status", "--porcelain")
    post_write_diff_hash = hashlib.sha256(post_write_status.encode("utf-8")).hexdigest()

    marker_path.write_text(json.dumps({
        "last_commit": current_commit,
        "last_diff_hash": post_write_diff_hash,
        "last_note": str(note_path.relative_to(repo_root)).replace("\\", "/"),
        "updated_at": now.isoformat(timespec="seconds"),
    }, indent=2), encoding="utf-8")

    print(json.dumps({
        "systemMessage": f"Second brain: nota de sesión creada en docs/second-brain/sessions/{note_path.name}"
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # never block or noisy-fail session end
    sys.exit(0)

"""Virtual display (Xvfb) so a HEADFUL browser runs on a server with no monitor.

Vía #1 needs a headful browser (DataDome flags headless instantly). On a desktop
that is a real screen; on a headless VPS there is none, so a headful launch would
fail. Xvfb gives the browser a real X11 display in memory — the WAF sees a genuine
headful Chrome/Firefox, not headless, with no physical monitor.

This is wired and tested locally even though the VPS is a deferred phase: the
DECISION LOGIC (when to spin Xvfb) is unit-tested, and on this Windows host the
context manager is a clean no-op (Windows draws headful to a real desktop already).

Activation rule (`should_use_virtual_display`): only on Linux, only when a headful
browser is requested, only when no DISPLAY is already exported, and only when an
Xvfb binary (or pyvirtualdisplay) is actually available. Otherwise: no-op.

Implementation order: pyvirtualdisplay if installed (handles edge cases), else a
raw Xvfb subprocess managed with stdlib only (no new hard dependency).
"""
from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import sys
import time


def xvfb_available() -> bool:
    return shutil.which("Xvfb") is not None


def pyvirtualdisplay_available() -> bool:
    try:
        import pyvirtualdisplay  # noqa: F401
        return True
    except Exception:  # noqa: BLE001
        return False


def should_use_virtual_display(*, headful: bool,
                               platform: str | None = None,
                               display_env: str | None = "__unset__",
                               has_xvfb: bool | None = None) -> bool:
    """Decide whether a virtual display is needed (pure, unit-testable).

    True only when: Linux + headful requested + no DISPLAY already set + Xvfb (or
    pyvirtualdisplay) available. Args are injectable so the rule is testable from
    any host (e.g. simulate Linux from Windows).
    """
    plat = platform if platform is not None else sys.platform
    if not headful:
        return False
    if not plat.startswith("linux"):
        return False  # Windows/macOS draw headful to the real desktop
    disp = os.environ.get("DISPLAY") if display_env == "__unset__" else display_env
    if disp:
        return False  # a display is already available
    avail = has_xvfb if has_xvfb is not None else (xvfb_available() or pyvirtualdisplay_available())
    return bool(avail)


@contextlib.contextmanager
def virtual_display(*, headful: bool = True, width: int = 1920, height: int = 1080):
    """Context manager that provides a display for a headful browser when needed.

    No-op (yields immediately) when a virtual display is not required (Windows, an
    existing DISPLAY, headless, or no Xvfb). When required, prefers pyvirtualdisplay
    and falls back to a raw Xvfb subprocess, restoring the prior DISPLAY on exit.
    """
    if not should_use_virtual_display(headful=headful):
        yield None
        return

    # Preferred: pyvirtualdisplay (robust display-number allocation).
    if pyvirtualdisplay_available():
        from pyvirtualdisplay import Display  # type: ignore
        disp = Display(visible=False, size=(width, height))
        disp.start()
        try:
            yield disp
        finally:
            with contextlib.suppress(Exception):
                disp.stop()
        return

    # Fallback: raw Xvfb subprocess (stdlib only).
    prior = os.environ.get("DISPLAY")
    disp_num = _pick_display_number()
    proc = subprocess.Popen(
        ["Xvfb", f":{disp_num}", "-screen", "0", f"{width}x{height}x24", "-nolisten", "tcp"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.environ["DISPLAY"] = f":{disp_num}"
    _await_display(proc)
    try:
        yield proc
    finally:
        with contextlib.suppress(Exception):
            proc.terminate()
            proc.wait(timeout=5)
        if prior is None:
            os.environ.pop("DISPLAY", None)
        else:
            os.environ["DISPLAY"] = prior


def _pick_display_number() -> int:
    # 99 is the conventional Xvfb display; bump if a lock file already exists.
    for n in range(99, 120):
        if not os.path.exists(f"/tmp/.X{n}-lock"):
            return n
    return 99


def _await_display(proc: subprocess.Popen, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError("Xvfb exited before the display was ready")
        # The lock file appears once Xvfb has the display up.
        disp = os.environ.get("DISPLAY", ":99").lstrip(":").split(".")[0]
        if os.path.exists(f"/tmp/.X{disp}-lock"):
            return
        time.sleep(0.1)

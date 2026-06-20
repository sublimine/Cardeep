"""Virtual-display (Xvfb) decision logic — wired for the VPS, testable on any host."""
from pipeline.engine.tier1 import display


def test_no_virtual_display_when_headless():
    assert display.should_use_virtual_display(
        headful=False, platform="linux", display_env=None, has_xvfb=True) is False


def test_no_virtual_display_on_windows():
    # Windows draws headful to the real desktop — never Xvfb.
    assert display.should_use_virtual_display(
        headful=True, platform="win32", display_env=None, has_xvfb=True) is False


def test_no_virtual_display_on_macos():
    assert display.should_use_virtual_display(
        headful=True, platform="darwin", display_env=None, has_xvfb=True) is False


def test_virtual_display_needed_on_headless_linux_with_xvfb():
    # The VPS case: Linux, headful wanted, no DISPLAY, Xvfb present -> spin Xvfb.
    assert display.should_use_virtual_display(
        headful=True, platform="linux", display_env=None, has_xvfb=True) is True


def test_no_virtual_display_when_display_already_set():
    # A real X server is already there (e.g. Linux desktop) -> no Xvfb.
    assert display.should_use_virtual_display(
        headful=True, platform="linux", display_env=":0", has_xvfb=True) is False


def test_no_virtual_display_when_xvfb_missing():
    # Linux headless but no Xvfb binary -> cannot, returns False (caller decides).
    assert display.should_use_virtual_display(
        headful=True, platform="linux", display_env=None, has_xvfb=False) is False


def test_virtual_display_contextmanager_is_noop_here():
    # On this Windows host the context manager must be a clean no-op.
    with display.virtual_display(headful=True) as d:
        assert d is None

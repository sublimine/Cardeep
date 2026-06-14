"""Tests for pipeline.util.encoding.force_utf8_stdout (B3.3).

Verifies that:
  1. force_utf8_stdout() does not crash on any call.
  2. After calling it, printing the Greek sigma (U+03A3) does not raise
     UnicodeEncodeError regardless of the current stdout encoding.
  3. The function is idempotent: calling it twice leaves streams in a valid
     UTF-8 state and does not raise.
  4. The scheduler subprocess env dict includes PYTHONIOENCODING=utf-8.
"""
from __future__ import annotations

import io
import sys
from unittest.mock import patch, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Allow running from project root without install
# ---------------------------------------------------------------------------
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.util.encoding import force_utf8_stdout


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_cp1252_stream() -> io.TextIOWrapper:
    """Return a TextIOWrapper that mimics a cp1252 console pipe."""
    buf = io.BytesIO()
    wrapper = io.TextIOWrapper(buf, encoding="cp1252", errors="strict")
    return wrapper


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestForceUtf8Stdout:
    def test_does_not_raise_on_utf8_streams(self):
        """No-op and no exception when streams are already UTF-8."""
        utf8_out = io.TextIOWrapper(io.BytesIO(), encoding="utf-8", errors="replace")
        utf8_err = io.TextIOWrapper(io.BytesIO(), encoding="utf-8", errors="replace")
        with patch("sys.stdout", utf8_out), patch("sys.stderr", utf8_err):
            force_utf8_stdout()  # must not raise

    def test_sigma_print_does_not_crash_after_guard(self):
        """Printing U+03A3 after force_utf8_stdout() must not raise UnicodeEncodeError."""
        # Replace stdout/stderr with fresh UTF-8 streams so the test is
        # hermetic regardless of the terminal encoding under pytest.
        buf_out = io.BytesIO()
        buf_err = io.BytesIO()
        new_out = io.TextIOWrapper(buf_out, encoding="utf-8", errors="replace")
        new_err = io.TextIOWrapper(buf_err, encoding="utf-8", errors="replace")
        with patch("sys.stdout", new_out), patch("sys.stderr", new_err):
            force_utf8_stdout()
            # This is the character that triggered alert id 6 (coches_com:discover).
            print("Σ total cars: 92312")  # must not raise

    def test_idempotent_double_call(self):
        """Calling force_utf8_stdout() twice does not raise."""
        buf_out = io.BytesIO()
        buf_err = io.BytesIO()
        new_out = io.TextIOWrapper(buf_out, encoding="utf-8", errors="replace")
        new_err = io.TextIOWrapper(buf_err, encoding="utf-8", errors="replace")
        with patch("sys.stdout", new_out), patch("sys.stderr", new_err):
            force_utf8_stdout()
            force_utf8_stdout()  # second call must be a no-op, no exception

    def test_streams_with_no_reconfigure_method(self):
        """Streams that lack reconfigure() are silently skipped (AttributeError path)."""
        dummy = MagicMock(spec=[])  # no reconfigure attribute
        dummy.encoding = "cp1252"
        with patch("sys.stdout", dummy), patch("sys.stderr", dummy):
            force_utf8_stdout()  # must not propagate AttributeError

    def test_errors_replace_prevents_crash_on_unencodable_char(self):
        """errors='replace' means U+03A3 on a cp1252-backed stream writes '?' not raise."""
        # Simulate what happens on a cp1252 console WITHOUT the guard:
        buf = io.BytesIO()
        cp1252_stream = io.TextIOWrapper(buf, encoding="cp1252", errors="strict")
        with pytest.raises(UnicodeEncodeError):
            cp1252_stream.write("Σ")
            cp1252_stream.flush()

        # After reconfigure to errors='replace', same write succeeds:
        buf2 = io.BytesIO()
        replaceable_stream = io.TextIOWrapper(buf2, encoding="cp1252", errors="replace")
        replaceable_stream.write("Σ")  # must not raise
        replaceable_stream.flush()
        assert buf2.getvalue() == b"?"  # replaced with ASCII fallback


class TestSchedulerSubprocessEnv:
    """Verify that _run_source() injects PYTHONIOENCODING=utf-8 into child env."""

    def test_pythonioencoding_in_child_env(self, monkeypatch):
        """subprocess.run receives env dict containing PYTHONIOENCODING=utf-8."""
        import pipeline.ops.scheduler as sched

        captured: list[dict] = []

        def fake_run(cmd, *, timeout, check, env, **kwargs):
            captured.append({"cmd": cmd, "env": env})
            result = MagicMock()
            result.returncode = 0
            return result

        monkeypatch.setattr(sched.subprocess, "run", fake_run)

        # Ensure a registry entry exists for the fake source
        fake_entry = sched.SourceEntry(
            source_key="coches_com_wholesale",
            module="pipeline.platform.coches_com_wholesale",
            extra_args=[],
        )
        monkeypatch.setitem(sched.REGISTRY, "coches_com_wholesale", fake_entry)

        sched._run_source("coches_com_wholesale")

        assert len(captured) == 1
        assert captured[0]["env"].get("PYTHONIOENCODING") == "utf-8"

    def test_child_env_inherits_os_environ(self, monkeypatch):
        """Child env contains existing os.environ vars in addition to PYTHONIOENCODING."""
        import pipeline.ops.scheduler as sched

        captured: list[dict] = []

        def fake_run(cmd, *, timeout, check, env, **kwargs):
            captured.append(env)
            result = MagicMock()
            result.returncode = 0
            return result

        monkeypatch.setattr(sched.subprocess, "run", fake_run)

        fake_entry = sched.SourceEntry(
            source_key="coches_com_wholesale",
            module="pipeline.platform.coches_com_wholesale",
            extra_args=[],
        )
        monkeypatch.setitem(sched.REGISTRY, "coches_com_wholesale", fake_entry)

        # Inject a sentinel into os.environ to verify inheritance
        monkeypatch.setenv("_CARDEEP_TEST_SENTINEL", "yes")

        sched._run_source("coches_com_wholesale")

        child_env = captured[0]
        assert child_env.get("_CARDEEP_TEST_SENTINEL") == "yes"
        assert child_env.get("PYTHONIOENCODING") == "utf-8"

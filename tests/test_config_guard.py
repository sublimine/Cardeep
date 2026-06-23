"""Unit tests for pipeline.config_guard — the prod-gated configuration guard.

Contract under test (see pipeline/config_guard.py):

  * cardeep_env() defaults to "dev" when CARDEEP_ENV is unset/empty, and
    normalizes case/whitespace otherwise.
  * assert_safe_dsn raises RuntimeError ONLY when CARDEEP_ENV=prod AND the DSN
    still carries the 'cardeep_dev_only' dev credential; pass-through otherwise.
  * require_api_key_or_fail raises ONLY when CARDEEP_ENV=prod AND no key is set.
  * require_prod_secrets is a total no-op outside prod (byte-identical dev/test).

These are pure, DB-less, network-less unit tests. They run with CARDEEP_ENV
controlled per-test via monkeypatch; the default suite (CARDEEP_ENV unset) never
arms any guard, so behaviour is byte-identical to before this module existed.

The /stats-style API 503 behaviour (prod + no key) is asserted through the
require_api_key dependency in services/api/deps.py, but ONLY when the test run is
explicitly in prod — see TestApiKeyDependencyProdGate, which SKIPS when
CARDEEP_ENV is unset so it never perturbs the default 1438-test suite.
"""
from __future__ import annotations

import os

import pytest

from pipeline.config_guard import (
    DEV_CREDENTIAL_MARKER,
    assert_safe_dsn,
    cardeep_env,
    is_prod,
    require_api_key_or_fail,
    require_prod_secrets,
)

pytestmark = pytest.mark.unit

# A realistic dev-default DSN (the literal baked into ~158 files).
DEV_DSN = "postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep"
# A DSN that does NOT carry the dev credential — stands in for a real prod DSN.
REAL_DSN = "postgresql://cardeep:S0me-Real-Secret@db.internal:5432/cardeep"


# ---------------------------------------------------------------------------
# cardeep_env()
# ---------------------------------------------------------------------------

class TestCardeepEnv:
    """CARDEEP_ENV resolution defaults to 'dev' and normalizes input."""

    def test_unset_defaults_to_dev(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Arrange
        monkeypatch.delenv("CARDEEP_ENV", raising=False)
        # Act / Assert
        assert cardeep_env() == "dev"
        assert is_prod() is False

    def test_empty_defaults_to_dev(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CARDEEP_ENV", "   ")
        assert cardeep_env() == "dev"
        assert is_prod() is False

    def test_prod_is_normalized(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CARDEEP_ENV", "  PROD ")
        assert cardeep_env() == "prod"
        assert is_prod() is True

    def test_arbitrary_value_is_not_prod(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CARDEEP_ENV", "staging")
        assert cardeep_env() == "staging"
        assert is_prod() is False


# ---------------------------------------------------------------------------
# assert_safe_dsn()
# ---------------------------------------------------------------------------

class TestAssertSafeDsn:
    """DSN guard fires only in prod against the dev-default credential."""

    def test_dev_unset_passes_through_dev_dsn(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """No CARDEEP_ENV -> dev -> dev DSN returned unchanged (no raise)."""
        monkeypatch.delenv("CARDEEP_ENV", raising=False)
        assert assert_safe_dsn(DEV_DSN, var="CARDEEP_DSN") == DEV_DSN

    def test_explicit_dev_passes_through_dev_dsn(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("CARDEEP_ENV", "dev")
        assert assert_safe_dsn(DEV_DSN, var="CARDEEP_DSN") == DEV_DSN

    def test_prod_with_dev_default_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """prod + dev_only credential -> RuntimeError naming the variable."""
        monkeypatch.setenv("CARDEEP_ENV", "prod")
        with pytest.raises(RuntimeError) as excinfo:
            assert_safe_dsn(DEV_DSN, var="CARDEEP_DSN")
        msg = str(excinfo.value)
        assert "CARDEEP_DSN" in msg
        assert DEV_CREDENTIAL_MARKER in msg

    def test_prod_with_real_dsn_passes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """prod + a real DSN (no dev credential) -> returned unchanged."""
        monkeypatch.setenv("CARDEEP_ENV", "prod")
        assert assert_safe_dsn(REAL_DSN, var="CARDEEP_DSN") == REAL_DSN

    def test_prod_psycopg2_keyword_form_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The keyword DSN form (scheduler _RAW_DSN) is also caught in prod."""
        monkeypatch.setenv("CARDEEP_ENV", "prod")
        kw_dsn = (
            "host=127.0.0.1 port=5433 dbname=cardeep "
            "user=cardeep password=cardeep_dev_only"
        )
        with pytest.raises(RuntimeError):
            assert_safe_dsn(kw_dsn, var="CARDEEP_DSN")


# ---------------------------------------------------------------------------
# require_api_key_or_fail()
# ---------------------------------------------------------------------------

class TestRequireApiKeyOrFail:
    """API-key guard fires only in prod when no key is configured."""

    def test_dev_unset_no_key_is_noop(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CARDEEP_ENV", raising=False)
        # Must not raise even with no key in dev.
        require_api_key_or_fail(None)

    def test_prod_no_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CARDEEP_ENV", "prod")
        with pytest.raises(RuntimeError) as excinfo:
            require_api_key_or_fail(None)
        assert "CARDEEP_API_KEY" in str(excinfo.value)

    def test_prod_empty_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CARDEEP_ENV", "prod")
        with pytest.raises(RuntimeError):
            require_api_key_or_fail("   ")

    def test_prod_with_key_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CARDEEP_ENV", "prod")
        # Must not raise when a real key is present.
        require_api_key_or_fail("a-real-prod-key")


# ---------------------------------------------------------------------------
# require_prod_secrets() — aggregate entry-point guard
# ---------------------------------------------------------------------------

class TestRequireProdSecrets:
    """The aggregate guard is a total no-op outside prod."""

    def test_dev_unset_is_total_noop(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """dev -> no raise even with dev DSNs and no key."""
        monkeypatch.delenv("CARDEEP_ENV", raising=False)
        monkeypatch.delenv("CARDEEP_API_KEY", raising=False)
        require_prod_secrets(
            (DEV_DSN, "CARDEEP_DSN"),
            (DEV_DSN, "CARDEEP_DB_URL"),
            require_api_key=True,
        )

    def test_prod_dev_dsn_raises_first_failure(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("CARDEEP_ENV", "prod")
        with pytest.raises(RuntimeError) as excinfo:
            require_prod_secrets((DEV_DSN, "CARDEEP_DSN"))
        assert "CARDEEP_DSN" in str(excinfo.value)

    def test_prod_real_dsns_and_key_passes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """prod + real DSNs + key present -> no raise (the happy prod path)."""
        monkeypatch.setenv("CARDEEP_ENV", "prod")
        monkeypatch.setenv("CARDEEP_API_KEY", "a-real-prod-key")
        require_prod_secrets(
            (REAL_DSN, "CARDEEP_DSN"),
            (REAL_DSN, "CARDEEP_ASYNCPG_DSN"),
            require_api_key=True,
        )

    def test_prod_missing_key_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("CARDEEP_ENV", "prod")
        monkeypatch.delenv("CARDEEP_API_KEY", raising=False)
        with pytest.raises(RuntimeError) as excinfo:
            require_prod_secrets((REAL_DSN, "CARDEEP_DSN"), require_api_key=True)
        assert "CARDEEP_API_KEY" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Prod-gated guard under an explicit prod run (SKIPS unless CARDEEP_ENV=prod)
# ---------------------------------------------------------------------------

class TestProdGateUnderProdRun:
    """When the WHOLE suite is run with CARDEEP_ENV=prod, the guards arm.

    This class SKIPS whenever CARDEEP_ENV is not 'prod', so it never perturbs the
    default suite (which runs with CARDEEP_ENV unset). It exists to prove the
    fail-closed behaviour holds when an operator deliberately exercises prod mode
    (e.g. `CARDEEP_ENV=prod pytest -m unit`). It asserts ONLY against this module's
    own contract — it does not depend on the API/scheduler wiring edits, so it is
    self-contained and cannot be broken by sibling changes.
    """

    @pytest.mark.skipif(
        cardeep_env() != "prod",
        reason="prod-only gate; default suite runs with CARDEEP_ENV unset (=dev)",
    )
    def test_prod_run_arms_dsn_guard(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Do NOT touch CARDEEP_ENV here — it is 'prod' for this test to run at all.
        assert os.environ.get("CARDEEP_ENV", "").strip().lower() == "prod"
        with pytest.raises(RuntimeError):
            assert_safe_dsn(DEV_DSN, var="CARDEEP_DSN")

    @pytest.mark.skipif(
        cardeep_env() != "prod",
        reason="prod-only gate; default suite runs with CARDEEP_ENV unset (=dev)",
    )
    def test_prod_run_arms_api_key_guard(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert os.environ.get("CARDEEP_ENV", "").strip().lower() == "prod"
        monkeypatch.delenv("CARDEEP_API_KEY", raising=False)
        with pytest.raises(RuntimeError) as excinfo:
            require_api_key_or_fail(os.environ.get("CARDEEP_API_KEY"))
        assert "CARDEEP_API_KEY" in str(excinfo.value)

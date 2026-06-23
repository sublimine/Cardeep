"""Prod-gated configuration guard — single source of truth for fail-fast checks.

Why this module exists
----------------------
The dev credential ``cardeep_dev_only`` is hardcoded as the DSN default in ~158
files (the ``CARDEEP_DSN`` / ``CARDEEP_DB_URL`` / ``CARDEEP_ASYNCPG_DSN`` env
fallbacks). In development that is exactly what we want; in production it is a
silent foot-gun: a daemon started without a real DSN would happily connect to a
dev database (or fail confusingly), and a missing ``CARDEEP_API_KEY`` would serve
every data endpoint publicly. Rewriting all 158 literals is risky and pointless —
the resolved value is what matters. Instead this module exposes ONE validated
gate that is wired at the few real startup seams (API lifespan + both schedulers).

Design contract (must stay byte-identical for dev/test)
-------------------------------------------------------
* ``cardeep_env()`` reads ``CARDEEP_ENV`` (default ``"dev"``). ``CARDEEP_ENV``
  appears nowhere in the codebase today except plans/docs, so the default ``dev``
  means current behaviour is 100% preserved — every guard below is a no-op
  pass-through unless an operator explicitly sets ``CARDEEP_ENV=prod``.
* ``assert_safe_dsn(dsn, var=...)`` raises ``RuntimeError`` ONLY when
  ``cardeep_env() == "prod"`` AND the resolved ``dsn`` still carries the
  ``cardeep_dev_only`` dev credential. In any non-prod env it returns ``dsn``
  unchanged.
* ``require_api_key_or_fail(configured_key)`` raises ``RuntimeError`` ONLY when
  ``cardeep_env() == "prod"`` AND no API key is configured. Non-prod: no-op.
* ``require_prod_secrets(...)`` is the convenience aggregate the entry points call
  at startup: it validates any DSNs passed and, optionally, the API key, all under
  the same prod gate.

Nothing here imports anything beyond the standard library, so it can be imported
from both the ``services.api`` package and the ``pipeline`` package without
creating an import cycle.
"""
from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: The literal dev credential baked into the ~158 DSN defaults. Its presence in a
#: RESOLVED DSN while running in prod is the signal that no real DSN was supplied.
DEV_CREDENTIAL_MARKER: str = "cardeep_dev_only"

#: The single production sentinel value of CARDEEP_ENV that arms every guard.
PROD_ENV: str = "prod"

#: Default environment when CARDEEP_ENV is unset — preserves current behaviour.
DEFAULT_ENV: str = "dev"


# ---------------------------------------------------------------------------
# Environment resolution
# ---------------------------------------------------------------------------

def cardeep_env() -> str:
    """Return the normalized runtime environment.

    Reads ``CARDEEP_ENV`` and lower-cases / strips it. Returns ``"dev"`` when the
    variable is unset or empty, so dev and the test suite (which never set
    ``CARDEEP_ENV``) keep their exact current behaviour.
    """
    return os.environ.get("CARDEEP_ENV", DEFAULT_ENV).strip().lower() or DEFAULT_ENV


def is_prod() -> bool:
    """True only when the runtime environment is production."""
    return cardeep_env() == PROD_ENV


# ---------------------------------------------------------------------------
# DSN guard
# ---------------------------------------------------------------------------

def assert_safe_dsn(dsn: str, *, var: str) -> str:
    """Fail-fast on the dev-default DSN in production; pass through otherwise.

    Parameters
    ----------
    dsn:
        The RESOLVED connection string (after env lookup + default fallback).
    var:
        Name of the env var the DSN came from — used only for the error message
        so an operator immediately knows which variable to set.

    Returns
    -------
    str
        ``dsn`` unchanged when the check passes (always, in non-prod).

    Raises
    ------
    RuntimeError
        Only when ``cardeep_env() == "prod"`` AND ``dsn`` still contains the
        ``cardeep_dev_only`` dev credential — i.e. no real DSN was supplied in
        production.
    """
    if not is_prod():
        return dsn
    if DEV_CREDENTIAL_MARKER in dsn:
        raise RuntimeError(
            f"CARDEEP_ENV=prod but {var} still uses the {DEV_CREDENTIAL_MARKER} "
            "dev default; set a real DSN"
        )
    return dsn


# ---------------------------------------------------------------------------
# API-key guard
# ---------------------------------------------------------------------------

def require_api_key_or_fail(configured_key: str | None) -> None:
    """Fail-fast when no API key is configured in production; no-op otherwise.

    Parameters
    ----------
    configured_key:
        The value of ``CARDEEP_API_KEY`` (``None`` when unset).

    Raises
    ------
    RuntimeError
        Only when ``cardeep_env() == "prod"`` AND ``configured_key`` is ``None``
        or empty — in prod the data endpoints must never be silently public.
    """
    if not is_prod():
        return
    if configured_key is None or configured_key.strip() == "":
        raise RuntimeError(
            "CARDEEP_ENV=prod but CARDEEP_API_KEY is not configured; "
            "set CARDEEP_API_KEY so data endpoints are not served publicly"
        )


# ---------------------------------------------------------------------------
# Aggregate entry-point guard
# ---------------------------------------------------------------------------

def require_prod_secrets(
    *dsns: tuple[str, str],
    require_api_key: bool = False,
) -> None:
    """Validate prod secrets at a startup seam under the single prod gate.

    A convenience aggregate so an entry point can validate everything it owns in
    one call. In any non-prod env this is a total no-op (every sub-check returns
    immediately), so dev/test startup is byte-identical.

    Parameters
    ----------
    *dsns:
        Zero or more ``(dsn, var_name)`` pairs to validate via
        :func:`assert_safe_dsn`.
    require_api_key:
        When ``True``, also enforce that ``CARDEEP_API_KEY`` is set in prod via
        :func:`require_api_key_or_fail`. Defaults to ``False`` because the
        schedulers do not serve HTTP and therefore need no API key.

    Raises
    ------
    RuntimeError
        Propagated from the first failing sub-check, only in prod.
    """
    if not is_prod():
        return
    for dsn, var in dsns:
        assert_safe_dsn(dsn, var=var)
    if require_api_key:
        require_api_key_or_fail(os.environ.get("CARDEEP_API_KEY"))

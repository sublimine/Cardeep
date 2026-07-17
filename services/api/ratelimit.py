"""SU-D2: In-memory rate-limiting via slowapi.

Design
------
- Uses ``slowapi.Limiter`` with the default ``memory://`` storage backend
  (pure in-process dict, zero infra coupling, €0, no Redis).
- Key function   = client IP extracted from the request (``get_remote_address``).
- Default limit  = RATE_DEFAULT (module constant, global fallback).
- Tight limits   = applied on expensive DB-heavy endpoints that must not be
  hammered: inventory, geo-tree, geo-completeness, platform inventory.
- Test gate      = env var ``CARDEEP_API_RATELIMIT_ENABLED`` (default "1").
  Set to "0" to disable enforcement — the limiter is still wired but all
  limits resolve to a no-op string "9999/second" that the test suite cannot
  reach, keeping the 89 existing tests green without any fixture changes.

429 envelope
------------
slowapi's default 429 handler returns plain text. We replace it with the
project's consistent envelope:

    {
        "ok":    false,
        "data":  null,
        "error": "rate_limit_exceeded",
        "meta":  {"detail": "<slowapi message>", "retry_after": <int|null>}
    }

HTTP status: 429. ``Retry-After`` header is preserved from slowapi.

Wiring (in main.py)
-------------------
    from services.api.ratelimit import limiter, rate_limit_handler
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

Per-endpoint usage
------------------
    from services.api.ratelimit import limiter, RATE_EXPENSIVE

    @router.get("/entities/{cdp_code}/inventory")
    @limiter.limit(RATE_EXPENSIVE)
    async def get_inventory(request: Request, ...):
        ...

Note: the ``request: Request`` parameter MUST be present in the function
signature for slowapi to inject the limit key — FastAPI routes already have it.
"""
from __future__ import annotations

import os
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# ---------------------------------------------------------------------------
# Module-level constants — all limit strings live here, none inline.
# ---------------------------------------------------------------------------

# NOTE (audit P2 E-ratelimit): _ENABLED and the RATE_* limits below are read ONCE at import and
# baked into the Limiter — unlike require_api_key, which reads os.environ per request. Toggling
# CARDEEP_API_RATELIMIT_ENABLED (or changing a limit) in an already-running process has NO effect;
# it requires a process restart. The default (enabled) is the safe state.
_ENABLED: bool = os.environ.get("CARDEEP_API_RATELIMIT_ENABLED", "1") != "0"

# When disabled (test mode), use an astronomically high limit that no
# test run will hit.  slowapi requires a syntactically valid limit string
# even for no-ops.
_NOOP_LIMIT: str = "9999/second"

RATE_DEFAULT: str = "120/minute" if _ENABLED else _NOOP_LIMIT
"""Global fallback limit applied to all decorated endpoints not given a tighter one."""

RATE_EXPENSIVE: str = "30/minute" if _ENABLED else _NOOP_LIMIT
"""Tight limit for expensive endpoints: inventory, geo-tree, geo-completeness,
platform-inventory.  These trigger multi-join queries over 500 k + rows."""

RATE_HEALTH: str = "300/minute" if _ENABLED else _NOOP_LIMIT
"""Generous limit for the /health liveness probe — must never block monitors."""

RATE_AUTH: str = "10/minute" if _ENABLED else _NOOP_LIMIT
"""AUTH-0: tight limit for credential-guessing surfaces (login/register/claim-dealer).
Deliberately tighter than RATE_DEFAULT — these endpoints spend an argon2 hash per call
(expensive by design) and are the highest-value bruteforce/enumeration target in the API."""

# ---------------------------------------------------------------------------
# Limiter singleton — imported by routers and wired into the FastAPI app.
# ---------------------------------------------------------------------------

limiter: Limiter = Limiter(
    key_func=get_remote_address,
    # ``default_limits`` applies to every route that carries a ``@limiter.limit``
    # decorator.  Routes with no decorator are unrestricted (ops/health use
    # their own explicit decorators).
    default_limits=[RATE_DEFAULT],
    # ``storage_uri="memory://"`` is the slowapi default (in-process dict).
    # Never change this to Redis — cardeep-redis is a different project.
    storage_uri="memory://",
)


# ---------------------------------------------------------------------------
# Custom 429 exception handler — project envelope compliant.
# ---------------------------------------------------------------------------

def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Return HTTP 429 in the project envelope ``{ok, data, error, meta}``.

    slowapi raises ``RateLimitExceeded``; we convert it to the consistent
    envelope shape instead of slowapi's default plain-text response.

    ``Retry-After`` is extracted from the exception's ``retry_after``
    attribute when available (integer seconds) and included in meta.
    """
    retry_after: int | None = getattr(exc, "retry_after", None)
    meta: dict[str, Any] = {"detail": str(exc.detail)}
    if retry_after is not None:
        meta["retry_after"] = retry_after

    headers: dict[str, str] = {}
    if retry_after is not None:
        headers["Retry-After"] = str(retry_after)

    return JSONResponse(
        content={
            "ok": False,
            "data": None,
            "error": "rate_limit_exceeded",
            "meta": meta,
        },
        status_code=429,
        headers=headers,
    )

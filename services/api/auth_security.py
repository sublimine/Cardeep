"""AUTH-0: password hashing, opaque session tokens, dealer-role verification.

Resolution: 00-MASTER.md §2 C-3. This module is the security core consumed by
``services/api/routers/auth.py`` — kept separate from the router so the
security-sensitive primitives (hashing, token minting, timing-safe verification)
have one obvious file to review and test in isolation.

Design decisions (see plans/cardeep-omni/AUTH-0.md for the full record):
  * Passwords: argon2id via argon2-cffi's ``PasswordHasher`` (its own defaults are the
    OWASP-recommended argon2id parameters). Never truncated, never re-hashed with a
    weaker scheme.
  * Sessions: opaque, high-entropy bearer tokens. The RAW token is returned to the
    client exactly once (register/login/refresh response); only its SHA-256 hash is
    ever persisted, logged, or compared. This is deliberately NOT a JWT — a bare JWT
    has no server-side revocation path, and 08-forum-community's carta explicitly
    requires "cero JWT sin revocación".
  * Dealer-role claims: a user may only be attached (via ``dealer_membership``) to an
    `entity` whose registered `cif` matches a tax ID the caller can produce AND that
    passes its official BOE checksum (``services/api/tax_id.py``). This is the anti
    dealer-disfrazado control from 08-forum-community §4.7 — claiming somebody else's
    dealer profile requires knowing their real, checksum-valid tax ID.
"""
from __future__ import annotations

import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_hasher = PasswordHasher()  # library defaults = current OWASP-recommended argon2id params

MIN_PASSWORD_LENGTH = 10
"""NIST SP 800-63B favors length over composition rules; 10 chars is this product's floor."""

MAX_PASSWORD_LENGTH = 128
"""Upper bound so a client cannot submit a multi-megabyte string into the KDF (DoS guard)."""

# Precomputed once at import time so verify_password() takes the SAME code path (and a
# comparable wall-clock cost) whether or not the target account exists — mitigates
# user-enumeration via login timing (OWASP ASVS 2.2 quotient).
_DUMMY_HASH: str = _hasher.hash(secrets.token_urlsafe(32))


def hash_password(raw: str) -> str:
    """Hash *raw* with argon2id. Caller is responsible for length validation beforehand."""
    return _hasher.hash(raw)


def verify_password(raw: str, stored_hash: str | None) -> bool:
    """Return True iff *raw* matches *stored_hash*.

    When *stored_hash* is None (account does not exist), verification still runs against
    a fixed dummy hash so the response time does not leak account existence, and the
    function still returns False (never True) in that branch.
    """
    target = stored_hash if stored_hash is not None else _DUMMY_HASH
    try:
        _hasher.verify(target, raw)
    except (VerifyMismatchError, InvalidHash):
        return False
    return stored_hash is not None


def needs_rehash(stored_hash: str) -> bool:
    """True when *stored_hash* was minted with weaker-than-current argon2id parameters."""
    return _hasher.check_needs_rehash(stored_hash)


def validate_password_policy(raw: str) -> str | None:
    """Return an error message if *raw* violates the password policy, else None."""
    if len(raw) < MIN_PASSWORD_LENGTH:
        return f"password must be at least {MIN_PASSWORD_LENGTH} characters"
    if len(raw) > MAX_PASSWORD_LENGTH:
        return f"password must be at most {MAX_PASSWORD_LENGTH} characters"
    return None


# ---------------------------------------------------------------------------
# Opaque session tokens
# ---------------------------------------------------------------------------

ACCESS_TOKEN_TTL_SECONDS: int = 24 * 60 * 60
"""24h. web/src/api/client.ts proactively calls /auth/refresh once <5 min remain, so this
is a rolling session in practice, not a hard 24h logout."""


def new_raw_token() -> str:
    """256 bits of CSPRNG entropy, URL-safe — this is what the client stores and sends."""
    return secrets.token_urlsafe(32)


def hash_token(raw: str) -> str:
    """SHA-256 of the raw token — this, never the raw value, is what user_session stores."""
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

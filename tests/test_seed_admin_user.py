"""Unit tests for the explicit, non-disclosing admin seed helper."""

from __future__ import annotations

import asyncio

import pytest

from scripts import seed_admin_user
from services.api.auth_security import MIN_PASSWORD_LENGTH, verify_password


pytestmark = pytest.mark.unit


REQUIRED_ENV = (
    "CARDEEP_DSN",
    "CARDEEP_ADMIN_USER",
    "CARDEEP_ADMIN_PASSWORD",
)


def _set_valid_env(monkeypatch: pytest.MonkeyPatch) -> str:
    password = "unit-test-only-" + ("x" * MIN_PASSWORD_LENGTH)
    monkeypatch.setenv("CARDEEP_DSN", "postgresql://localhost/cardeep")
    monkeypatch.setenv("CARDEEP_ADMIN_USER", "operator")
    monkeypatch.setenv("CARDEEP_ADMIN_PASSWORD", password)
    return password


def test_load_config_requires_explicit_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in REQUIRED_ENV:
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(RuntimeError) as exc_info:
        seed_admin_user.load_config()

    for name in REQUIRED_ENV:
        assert name in str(exc_info.value)


def test_load_config_enforces_shared_password_policy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_valid_env(monkeypatch)
    monkeypatch.setenv("CARDEEP_ADMIN_PASSWORD", "short")

    with pytest.raises(ValueError, match=f"at least {MIN_PASSWORD_LENGTH}"):
        seed_admin_user.load_config()


def test_seed_hashes_password_before_write(monkeypatch: pytest.MonkeyPatch) -> None:
    password = _set_valid_env(monkeypatch)
    config = seed_admin_user.load_config()

    class ExistingUserConnection:
        execute_args: tuple[object, ...] | None = None

        async def fetchrow(self, *_args: object) -> dict[str, str]:
            return {"user_ulid": "usr_test"}

        async def execute(self, *args: object) -> None:
            self.execute_args = args

    conn = ExistingUserConnection()
    user_ulid, created = asyncio.run(seed_admin_user.seed(conn, config))

    assert (user_ulid, created) == ("usr_test", False)
    assert conn.execute_args is not None
    persisted_hash = conn.execute_args[2]
    assert isinstance(persisted_hash, str)
    assert password not in conn.execute_args
    assert verify_password(password, persisted_hash)


def test_main_never_prints_password(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    password = _set_valid_env(monkeypatch)

    class ExistingUserConnection:
        async def fetchrow(self, *_args: object) -> dict[str, str]:
            return {"user_ulid": "usr_test"}

        async def execute(self, *_args: object) -> None:
            return None

        async def close(self) -> None:
            return None

    async def connect(_dsn: str) -> ExistingUserConnection:
        return ExistingUserConnection()

    monkeypatch.setattr(seed_admin_user.asyncpg, "connect", connect)

    asyncio.run(seed_admin_user.main())

    output = capsys.readouterr().out
    assert password not in output
    assert "operator" in output

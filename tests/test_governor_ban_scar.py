"""P03 (record_ban wiring): el ban SEMANTICO debe cicatrizar el host in-memory.

Antes: RateGovernor.record_ban era un no-op sin backend, pese a que su docstring prometia
una cicatriz in-memory "stricter per-host override" — maquillaje (doc miente sobre el codigo).
Ademas el Verdict.BANNED del ban_detector nunca llegaba al governor (solo reaccionaba el
breaker por http_status). Fix: record_ban marca un cooldown per-host que acquire() honra, y
wrap_fetch_text alimenta el last_verdict del engine al governor.

Tests puros (sin red, sin DB, sin browser)."""
from __future__ import annotations

import asyncio
import time

import pytest

from pipeline.engine.governor import RateGovernor


@pytest.mark.unit
def test_record_ban_sets_inmemory_scar_without_backend() -> None:
    gov = RateGovernor()
    asyncio.run(gov.record_ban("x.test", 5.0))
    assert "x.test" in gov._ban_until  # cicatriz in-memory, sin backend


@pytest.mark.unit
def test_acquire_waits_out_the_ban_cooldown() -> None:
    async def go():
        gov = RateGovernor()
        await gov.record_ban("x.test", 0.25)
        t0 = time.monotonic()
        waited = await gov.acquire("x.test")
        return time.monotonic() - t0, waited

    elapsed, waited = asyncio.run(go())
    assert elapsed >= 0.2, f"acquire no respeto el cooldown del ban (elapsed={elapsed:.3f})"
    assert waited >= 0.2


@pytest.mark.unit
def test_scar_clears_after_cooldown() -> None:
    async def go():
        gov = RateGovernor()
        await gov.record_ban("x.test", 0.05)
        await asyncio.sleep(0.12)
        waited = await gov.acquire("x.test")  # scar elapsed -> sin espera extra
        return waited, gov._ban_until.get("x.test")

    waited, still = asyncio.run(go())
    assert waited < 0.1
    assert still is None  # cicatriz limpiada al expirar


@pytest.mark.unit
def test_wrap_records_ban_on_banned_verdict() -> None:
    class _V:  # duck-typed Verdict.BANNED (sin importar el enum)
        name = "BANNED"

    class _Engine:
        last_verdict = _V()

        def fetch_text(self, url, **kw):  # no usado: pasamos fetch_callable explicito
            return ""

    async def go():
        gov = RateGovernor()
        governed = gov.wrap_fetch_text(lambda url, **kw: "<html>", engine=_Engine())
        await governed("https://walled.test/x")
        return "walled.test" in gov._ban_until

    assert asyncio.run(go()) is True

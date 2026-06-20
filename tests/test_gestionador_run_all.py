"""P10: el runner del gestionador despierta TODOS los detectores reales (no solo price_trap).

run.run_all itera detect.DETECTORS, SALTA detect.STUB_DETECTORS (inertes sin sus tablas), rutea
cada detector con su propio actor, agrega un resumen y aisla fallos por-detector (uno que revienta
no aborta el resto). Offline: fake conn + detectores + route_anomalies monkeypatched (sin DB).
"""
from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from pipeline.gestionador import detect, run


class _FakeConn:
    async def execute(self, *a, **k):  # set_config(...) -> no-op
        return "SET"

    async def close(self):
        return None


def _anom(side=None):
    return SimpleNamespace(measured={"side": side} if side else {})


@pytest.mark.unit
def test_run_all_runs_every_real_detector_and_skips_stubs(monkeypatch):
    called: list[str] = []
    routed_actors: list[str] = []

    def _mk(name, n):
        async def _fn(conn):
            called.append(name)
            return [_anom() for _ in range(n)]
        return _fn

    fake_registry = [
        ("count_inflation", _mk("count_inflation", 1)),
        ("price_trap", _mk("price_trap", 2)),
        ("geo_resolution_drift", _mk("geo_resolution_drift", 99)),  # stub -> debe saltarse
        ("classifier_drift", _mk("classifier_drift", 99)),          # stub -> debe saltarse
    ]
    monkeypatch.setattr(detect, "DETECTORS", fake_registry)

    async def _fake_route(conn, anomalies, *, actor):
        routed_actors.append(actor)
        return list(range(len(anomalies)))

    monkeypatch.setattr(run, "route_anomalies", _fake_route)

    summary = asyncio.run(run.run_all(_FakeConn()))

    assert set(called) == {"count_inflation", "price_trap"}  # los stubs NO corren
    assert set(summary["skipped"]) == {"geo_resolution_drift", "classifier_drift"}
    assert summary["total_flagged"] == 3 and summary["total_items"] == 3
    assert summary["detectors"]["price_trap"]["flagged"] == 2
    assert "gestionador:count_inflation" in routed_actors
    assert "gestionador:price_trap" in routed_actors


@pytest.mark.unit
def test_run_all_isolates_a_failing_detector(monkeypatch):
    async def _ok(conn):
        return [_anom()]

    async def _boom(conn):
        raise RuntimeError("db blew up")

    monkeypatch.setattr(detect, "DETECTORS",
                        [("count_inflation", _boom), ("price_trap", _ok)])

    async def _fake_route(conn, anomalies, *, actor):
        return list(range(len(anomalies)))

    monkeypatch.setattr(run, "route_anomalies", _fake_route)

    summary = asyncio.run(run.run_all(_FakeConn()))

    assert summary["detectors"]["count_inflation"]["flagged"] == -1  # fallo aislado
    assert "count_inflation" in summary["errors"]
    assert summary["detectors"]["price_trap"]["flagged"] == 1        # el resto corre


@pytest.mark.unit
def test_real_registry_has_nine_detectors_two_stubs():
    # Guard de regresion: el registro vivo y los stubs no se descuadran en silencio.
    assert len(detect.DETECTORS) == 9
    assert detect.STUB_DETECTORS == {"geo_resolution_drift", "classifier_drift"}
    names = {n for n, _ in detect.DETECTORS}
    assert detect.STUB_DETECTORS <= names

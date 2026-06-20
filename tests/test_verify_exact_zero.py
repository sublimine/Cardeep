"""P09-S1 regresion: cerrar la mentira EXACT_ZERO en record_count_verdict.

Bug vivo (verify.py): un claim con paths {db:0, fetched:0, source_declared:0} (tres
familias ortogonales coincidiendo en 0 por AUSENCIA de datos) producia modal_ok +
has_independence -> verdict TRUSTWORTHY. Un cero por ausencia se certificaba como verdad
(10 recetas web_generic FAILED llevaban vam_verdict TRUSTWORTHY con fetched:0).

Fix: un cero modal NO certifica TRUSTWORTHY salvo que el caller pase
measured_by_observation=True (la fuente devolvio un conjunto vacio OBSERVADO, no ausencia).
Por defecto False => todos los callers existentes obtienen el comportamiento seguro.

Todas las escrituras corren en una transaccion rolled-back (no persiste nada).
"""
from __future__ import annotations

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DSN = "postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"


async def _ping() -> bool:
    try:
        import asyncpg
        conn = await asyncpg.connect(DSN, timeout=3)
        await conn.close()
        return True
    except Exception:
        return False


def _db_available() -> bool:
    try:
        import asyncpg  # noqa: F401
        return asyncio.run(_ping())
    except Exception:
        return False


DB_AVAILABLE = _db_available()


class _Rollback(Exception):
    """Forces rollback — nothing persists."""


async def _verdict_for(paths, **kw) -> str:
    import asyncpg
    from pipeline.verify import record_count_verdict
    conn = await asyncpg.connect(DSN)
    captured = {}
    try:
        async with conn.transaction():
            captured["v"] = await record_count_verdict(
                conn, subject_type="__test_exact_zero__", subject_key="x",
                claim="exact-zero regression", paths=paths, **kw,
            )
            raise _Rollback
    except _Rollback:
        pass
    finally:
        await conn.close()
    return captured["v"]


@pytest.mark.skipif(not DB_AVAILABLE, reason="cardeep-pg not reachable at 127.0.0.1:5433")
class TestExactZero:
    def test_all_zero_absence_is_not_trustworthy(self) -> None:
        # 3 familias ortogonales en 0 por AUSENCIA -> NUNCA TRUSTWORTHY (la mentira cerrada).
        v = asyncio.run(_verdict_for({"db_ingested": 0, "fetched": 0, "source_declared": 0}))
        assert v != "TRUSTWORTHY", "un cero por ausencia NO puede certificarse"
        assert v == "UNVERIFIED"

    def test_measured_zero_can_be_trustworthy(self) -> None:
        # Inventario VACIO OBSERVADO (la fuente devolvio 0 de verdad) si certifica.
        v = asyncio.run(_verdict_for(
            {"db_ingested": 0, "fetched": 0, "source_declared": 0},
            measured_by_observation=True))
        assert v == "TRUSTWORTHY"

    def test_nonzero_modal_quorum_still_trustworthy(self) -> None:
        # No-regresion: el quorum normal con valor no-cero sigue certificando.
        v = asyncio.run(_verdict_for(
            {"db_ingested": 140, "fetched": 140, "source_declared": 140}))
        assert v == "TRUSTWORTHY"

    def test_divergent_still_refuted(self) -> None:
        v = asyncio.run(_verdict_for(
            {"db_ingested": 140, "fetched": 900, "source_declared": 50}))
        assert v == "REFUTED"

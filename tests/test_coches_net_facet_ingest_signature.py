"""Regresion P05-S0: el harvester canonico de coches.net (facet) DEBE llamar al
_ingest_window compartido con la arity EXACTA de su firma.

Bug vivo cazado (HEAD 9a9c34c): coches_net_facet.py:295 llamaba _ingest_window con 7
args posicionales contra una firma de 8 (prov_names en posicion 3, anadido al wholesale
en 9e36df9 sin actualizar el call-site del facet). El scheduler agenda coches_net_wholesale
-> modulo facet, asi que el harvester Tier-1 NACIONAL agendado crasheaba en cada run.

Contract-test estatico (AST), sin DB: falla si CUALQUIER call-site de _ingest_window en
los modulos coches_net no concuerda con la firma canonica. Barato y deterministico.
"""
import ast
import inspect
import pathlib

import pytest

from pipeline.platform import coches_net_wholesale as W
from pipeline.platform import coches_net_facet as F


def _ingest_window_calls(module):
    src = pathlib.Path(module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_ingest_window"
    ]


@pytest.mark.unit
def test_facet_ingest_window_arity_matches_signature():
    expected = len(inspect.signature(W._ingest_window).parameters)
    calls = _ingest_window_calls(F)
    assert calls, "no _ingest_window call found in coches_net_facet (test target moved?)"
    for call in calls:
        assert not call.keywords, "facet must call _ingest_window positionally"
        got = len(call.args)
        assert got == expected, (
            f"coches_net_facet calls _ingest_window with {got} positional args "
            f"but the canonical signature has {expected} params "
            f"(line {call.lineno}). Arg-shift crash regression (P05-S0)."
        )

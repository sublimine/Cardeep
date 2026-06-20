"""P03-S3: el motor Tier-1 por DEFECTO no debe ser AGPL.

nodriver/zendriver son AGPL-3.0 (network copyleft): si CARDEEP expone su API publica
con nodriver en la ruta por defecto, la AGPL puede forzar publicar el codigo del servicio
(riesgo existencial marcado por la revision adversarial). El default permisivo es camoufox
(MPL-2.0, file-level copyleft, seguro en un servicio de red); nodriver NO se elimina, queda
como opt-in explicito (tier1_engine='nodriver') bajo decision legal del owner.

Tests puros (sin red, sin browser real)."""
from __future__ import annotations

import pytest

from pipeline.engine import fetch as fetchmod
from pipeline.engine.fetch import FetchEngine

_AGPL_ENGINES = {"nodriver", "zendriver"}


@pytest.mark.unit
def test_default_tier1_engine_constant_is_permissive() -> None:
    assert fetchmod._TIER1_ENGINE not in _AGPL_ENGINES, (
        f"_TIER1_ENGINE={fetchmod._TIER1_ENGINE!r} es AGPL; el default debe ser permisivo "
        f"(camoufox MPL-2.0)")


@pytest.mark.unit
def test_default_tier1_chain_runs_no_agpl_engine() -> None:
    eng = FetchEngine(impersonate="chrome131", use_proxy_pool=False)
    assert not (_AGPL_ENGINES & set(eng._tier1_engines)), (
        f"la cadena Tier-1 por defecto {eng._tier1_engines} corre un motor AGPL")


@pytest.mark.unit
def test_nodriver_still_available_as_explicit_optin() -> None:
    # No se elimina nodriver: el owner puede exigirlo explicitamente (con su decision legal).
    eng = FetchEngine(impersonate="chrome131", use_proxy_pool=False, tier1_engine="nodriver")
    assert "nodriver" in eng._tier1_engines

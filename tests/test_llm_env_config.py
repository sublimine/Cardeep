"""4.1 (autonomy-e2e): the LLM rung's model + URL are ENV-CONFIGURABLE.

CARDEEP_OLLAMA_URL lets a containerised autopilot daemon reach the HOST's Ollama (a container's
"localhost" is the container, not the host); CARDEEP_LLM_MODEL lets the owner swap the model without
editing code. Pure @unit — never touches a real Ollama daemon.
"""
from __future__ import annotations

import importlib

import pytest

pytestmark = pytest.mark.unit


def test_llm_model_and_url_are_env_configurable(monkeypatch):
    import pipeline.recipe_extract_llm as m

    monkeypatch.setenv("CARDEEP_LLM_MODEL", "test-model-xyz")
    monkeypatch.setenv("CARDEEP_OLLAMA_URL", "http://test-host:9/api/generate")
    importlib.reload(m)
    try:
        assert m._OLLAMA_MODEL == "test-model-xyz"
        assert m._OLLAMA_URL == "http://test-host:9/api/generate"
    finally:
        monkeypatch.delenv("CARDEEP_LLM_MODEL", raising=False)
        monkeypatch.delenv("CARDEEP_OLLAMA_URL", raising=False)
        importlib.reload(m)  # restore module defaults for any other test

    # Default preserved when the env is absent (behaviour-preserving).
    assert m._OLLAMA_MODEL == "qwen2.5:7b"
    assert m._OLLAMA_URL == "http://localhost:11434/api/generate"

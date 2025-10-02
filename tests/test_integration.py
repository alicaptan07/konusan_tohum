"""Konuşan Tohum entegrasyon katmanının web araması, API istemcisi ve AI köprülerini birlikte doğrulayan senaryolar."""

import builtins
import importlib
import sys
import types
from unittest.mock import patch

if "transformers" not in sys.modules:
    transformers_stub = types.ModuleType("transformers")

    def _stub_pipeline(*args, **kwargs):
        def _generator(*_args, **_kwargs):
            return [{"generated_text": "stub"}]

        return _generator

    transformers_stub.pipeline = _stub_pipeline
    sys.modules["transformers"] = transformers_stub

from konusan_tohum.integration.api_connector import AIConnector, call_api
from konusan_tohum.integration.web_search_mod import search


def test_web_search():
    results = search("Antalya hava durumu")
    assert isinstance(results, list)
    print("✅ WebSearchMod test edildi.")


def test_api_connector():
    response = call_api("https://api.example.com", {"q": "test"})
    assert response is not None
    print("✅ APIConnector test edildi.")


def test_ai_connector_offline_fallback(monkeypatch):
    connector = AIConnector()
    connector.provider = "offline"
    connector.keys = {}

    monkeypatch.setattr(
        "konusan_tohum.integration.api_connector.generate_response",
        lambda message: "offline yanıt",
    )

    result = connector.chat("Merhaba")

    assert isinstance(result, str)
    assert result == "offline yanıt"


def test_integration_ai_connector_without_requests(monkeypatch):
    monkeypatch.delitem(sys.modules, "konusan_tohum.integration.ai_connector", raising=False)

    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "requests":
            raise ImportError("No module named 'requests'")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        module = importlib.import_module("konusan_tohum.integration.ai_connector")

    monkeypatch.setattr(
        module,
        "generate_response",
        lambda message: "offline yanıt (requests yok)"
    )

    connector = module.AIConnector()
    connector.api_key_openai = "dummy"

    result = connector.chat("Merhaba", provider="openai")

    assert result == "offline yanıt (requests yok)"

    importlib.reload(module)

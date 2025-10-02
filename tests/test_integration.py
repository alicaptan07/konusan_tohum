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

import pytest

from integration import api_connector as connector_module
from integration.web_search_mod import search
from integration.api_connector import AIConnector, HTTPSettings, _build_http_session, call_api


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
        "integration.api_connector.generate_response", lambda message: "offline yanıt"
    )

    result = connector.chat("Merhaba")

    assert isinstance(result, str)
    assert result == "offline yanıt"


def test_http_session_applies_retry_configuration():
    session = _build_http_session(HTTPSettings(timeout=2, max_retries=4, backoff_factor=1.5))
    if session is None:  # pragma: no cover - requests missing
        pytest.skip("requests library not available")

    adapter = session.get_adapter("https://")
    retry = getattr(adapter, "max_retries", None)

    assert retry is not None
    assert retry.total == 4
    assert retry.backoff_factor == 1.5


def test_call_api_timeout_surface_error(monkeypatch):
    if connector_module.requests is None:
        pytest.skip("requests library not available")

    class TimeoutSession:
        def get(self, *args, **kwargs):
            raise connector_module.requests.Timeout("boom")

    monkeypatch.setattr(connector_module, "_build_http_session", lambda *_args, **_kwargs: TimeoutSession())

    result = call_api("https://timeout.test", {"foo": "bar"})

    assert result["status"] == "timeout"
    assert "timed out" in result["error"].lower()


def test_search_falls_back_when_client_errors():
    class FailingClient:
        def get(self, *args, **kwargs):
            raise RuntimeError("network down")

    results = search("Antalya hava durumu", http_client=FailingClient())

    assert results  # offline dataset populated
    assert all(isinstance(item, str) for item in results)


def test_ai_connector_openai_timeout_message(monkeypatch):
    if connector_module.requests is None:
        pytest.skip("requests library not available")

    connector = AIConnector()
    connector.provider = "openai"
    connector.keys = {"openai": "dummy"}

    class TimeoutSession:
        def post(self, *args, **kwargs):
            raise connector_module.requests.Timeout("boom")

    monkeypatch.setattr(
        "integration.api_connector._build_http_session",
        lambda *_args, **_kwargs: TimeoutSession(),
    )

    message = connector.chat("Merhaba", user_memory="", context="")

    assert "timed out" in message.lower()


def test_integration_ai_connector_without_requests(monkeypatch):
    monkeypatch.delitem(sys.modules, "integration.ai_connector", raising=False)

    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "requests":
            raise ImportError("No module named 'requests'")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        module = importlib.import_module("integration.ai_connector")

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

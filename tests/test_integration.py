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


def test_api_connector(monkeypatch):
    class _DummyResponse:
        headers = {"Content-Type": "application/json"}

        @staticmethod
        def raise_for_status():
            return None

        @staticmethod
        def json():
            return {"message": "ok"}

    def _dummy_get(url, params=None, timeout=None):
        return _DummyResponse()

    dummy_requests = types.SimpleNamespace(get=_dummy_get)
    monkeypatch.setitem(sys.modules, "requests", dummy_requests)

    response = call_api("https://api.example.com", {"q": "test"}, timeout=3)

    assert response["status"] == "ok"
    assert response["data"] == {"message": "ok"}
    assert response["params"] == {"q": "test"}
    print("✅ APIConnector test edildi.")


def test_call_api_retries_return_stub(monkeypatch):
    attempts = []

    def _failing_get(url, params=None, timeout=None):
        attempts.append({"timeout": timeout, "params": params})
        raise RuntimeError("boom")

    dummy_requests = types.SimpleNamespace(get=_failing_get)
    monkeypatch.setitem(sys.modules, "requests", dummy_requests)

    sleeps = []
    monkeypatch.setattr(
        "konusan_tohum.integration.api_connector.time.sleep",
        lambda duration: sleeps.append(duration),
    )

    response = call_api(
        "https://api.example.com",
        {"q": "retry"},
        timeout=7,
        retries=2,
        backoff_factor=0.1,
    )

    assert response == {
        "status": "stub",
        "url": "https://api.example.com",
        "params": {"q": "retry"},
        "data": "stub-response-for-https://api.example.com",
    }
    assert len(attempts) == 3
    assert all(call["timeout"] == 7 for call in attempts)
    assert sleeps == [0.1, 0.2]


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

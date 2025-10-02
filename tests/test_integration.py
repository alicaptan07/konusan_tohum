import builtins
import importlib
import sys
import types
from unittest.mock import patch

import pytest

if "transformers" not in sys.modules:
    transformers_stub = types.ModuleType("transformers")

    def _stub_pipeline(*args, **kwargs):
        def _generator(*_args, **_kwargs):
            return [{"generated_text": "stub"}]

        return _generator

    transformers_stub.pipeline = _stub_pipeline
    sys.modules["transformers"] = transformers_stub

from integration.web_search_mod import search
from integration.api_connector import call_api, AIConnector


def test_web_search():
    results = search("Antalya hava durumu")
    assert isinstance(results, list)
    print("✅ WebSearchMod test edildi.")


def test_api_connector():
    response = call_api("https://api.example.com", {"q": "test"})
    assert response is not None
    print("✅ APIConnector test edildi.")


class _DummyResponse:
    def __init__(self, status_code, data, headers=None):
        self.status_code = status_code
        self._data = data
        self.headers = headers or {}
        self.text = data if isinstance(data, str) else ""

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


@pytest.mark.parametrize(
    "side_effects, expected_status, expected_calls",
    [
        ([
            _DummyResponse(200, {"result": "ok"}, {"Content-Type": "application/json"})
        ], "ok", 1),
        ([
            _DummyResponse(404, "not-found", {"Content-Type": "text/plain"})
        ], "stub", 1),
        ([
            TimeoutError("boom"),
            TimeoutError("boom"),
            TimeoutError("boom"),
        ], "stub", 3),
    ],
)
def test_call_api_retry_logic(monkeypatch, side_effects, expected_status, expected_calls):
    calls = []

    class _RequestsStub:
        class exceptions:
            Timeout = TimeoutError

        Timeout = TimeoutError

        @staticmethod
        def get(url, params=None, timeout=5):
            index = len(calls)
            if index >= len(side_effects):
                raise AssertionError("Unexpected extra API call")
            effect = side_effects[index]
            calls.append((url, params, timeout))
            if isinstance(effect, Exception):
                raise effect
            return effect

    monkeypatch.setitem(sys.modules, "requests", _RequestsStub)
    sleep_calls = []
    monkeypatch.setattr("integration.api_connector.time.sleep", lambda duration: sleep_calls.append(duration))

    response = call_api("https://example.com/api", {"payload": 1})

    assert response["status"] == expected_status
    assert len(calls) == expected_calls
    if expected_status == "ok":
        assert response["data"] == {"result": "ok"}
    else:
        assert response["data"].startswith("stub-response-for")

    if expected_calls > 1:
        assert sleep_calls, "Retry backoff should trigger sleep calls"
    else:
        assert not sleep_calls


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

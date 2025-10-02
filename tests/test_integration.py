import builtins
import importlib
import sys
import types
from unittest.mock import MagicMock, call, patch

if "requests" not in sys.modules:
    requests_stub = types.ModuleType("requests")

    class RequestException(Exception):
        pass

    class HTTPError(RequestException):
        pass

    class Timeout(RequestException):
        pass

    requests_stub.exceptions = types.SimpleNamespace(
        RequestException=RequestException,
        HTTPError=HTTPError,
        Timeout=Timeout,
    )
    requests_stub.get = lambda *args, **kwargs: None
    sys.modules["requests"] = requests_stub

import requests

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


def test_call_api_success_response_structure():
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.headers = {"Content-Type": "application/json; charset=utf-8"}
    mock_response.json.return_value = {"message": "ok"}

    with patch("requests.get", return_value=mock_response) as mock_get, patch(
        "konusan_tohum.integration.api_connector.time.sleep"
    ) as mock_sleep:
        result = call_api("https://api.example.com/data", {"q": "value"})

    assert result == {
        "status": "ok",
        "url": "https://api.example.com/data",
        "params": {"q": "value"},
        "data": {"message": "ok"},
    }
    mock_get.assert_called_once_with(
        "https://api.example.com/data", params={"q": "value"}, timeout=5
    )
    mock_sleep.assert_not_called()


def test_call_api_http_error_retries_and_stub():
    error_response = MagicMock()
    error_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
    error_response.headers = {}
    error_response.text = ""

    with patch("requests.get", return_value=error_response) as mock_get, patch(
        "konusan_tohum.integration.api_connector.time.sleep"
    ) as mock_sleep:
        result = call_api("https://api.example.com/not-found", {"b": 2, "a": 1})

    assert result == {
        "status": "stub",
        "url": "https://api.example.com/not-found",
        "params": {"a": 1, "b": 2},
        "data": "stub-response-for-https://api.example.com/not-found",
    }
    assert mock_get.call_count == 3
    mock_sleep.assert_has_calls([call(0.5), call(1.0)])


def test_call_api_timeout_retries_and_stub():
    with patch("requests.get", side_effect=requests.exceptions.Timeout("timeout")) as mock_get, patch(
        "konusan_tohum.integration.api_connector.time.sleep"
    ) as mock_sleep:
        result = call_api("https://api.example.com/slow", {"k": "v"})

    assert result == {
        "status": "stub",
        "url": "https://api.example.com/slow",
        "params": {"k": "v"},
        "data": "stub-response-for-https://api.example.com/slow",
    }
    assert mock_get.call_count == 3
    mock_sleep.assert_has_calls([call(0.5), call(1.0)])


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

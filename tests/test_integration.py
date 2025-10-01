import sys
import types

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

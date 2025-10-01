from integration.web_search_mod import search
from integration.api_connector import call_api
from integration.ai_connector import AIConnector


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
    connector.api_key_openai = ""
    connector.api_key_openrouter = ""

    monkeypatch.setattr("integration.ai_connector.generate_response", lambda message: "offline yanıt")

    result = connector.chat("Merhaba")

    assert isinstance(result, str)
    assert result == "offline yanıt"

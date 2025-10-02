"""Konuşan Tohum AI bağlayıcısı, OpenAI ve OpenRouter sağlayıcılarıyla konuşmaları yöneten ve gerekirse çevrimdışı üreticiye dönen bir soyutlama sunar."""

# integration/ai_connector.py
try:
    import requests
except ImportError:  # pragma: no cover - optional dependency
    requests = None

from konusan_tohum.core.config_manager import ConfigManager
from konusan_tohum.dialog.response_generator import generate_response

class AIConnector:
    def __init__(self):
        self.config = ConfigManager()
        self.provider = self.config.get("api.provider", "openai")
        self.api_key_openai = self.config.get("api_keys.openai")
        self.api_key_openrouter = self.config.get("api_keys.openrouter")
        self.model_openai = self.config.get("models.online", "gpt-4o-mini")
        self.model_openrouter = self.config.get("models.openrouter", "openai/gpt-3.5-turbo")

    def chat(self, message, provider=None):
        response = None
        provider = (provider or self.provider or "offline").lower()

        if provider == "openrouter" and self.api_key_openrouter:
            if requests is None:
                return generate_response(message)
            try:
                headers = {"Authorization": f"Bearer {self.api_key_openrouter}"}
                payload = {
                    "model": self.model_openrouter,
                    "messages": [{"role": "system", "content": "Sen akıllı bir asistanısın."},
                                 {"role": "user", "content": message}]
                }
                r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
                if r.status_code == 200:
                    response = r.json()["choices"][0]["message"]["content"]
                    return response
            except Exception as e:
                print(f"[AIConnector] OpenRouter hatası: {e}")
        if provider == "openrouter":
            provider = "offline"

        if provider == "openai" and self.api_key_openai:
            if requests is None:
                return generate_response(message)
            try:
                headers = {"Authorization": f"Bearer {self.api_key_openai}"}
                payload = {
                    "model": self.model_openai,
                    "messages": [{"role": "system", "content": "Sen akıllı bir asistanısın."},
                                 {"role": "user", "content": message}]
                }
                r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
                if r.status_code == 200:
                    response = r.json()["choices"][0]["message"]["content"]
                    return response
            except Exception as e:
                print(f"[AIConnector] OpenAI hatası: {e}")
        if provider == "openai":
            provider = "offline"

        if provider == "offline" or not response:
            return generate_response(message)

        return "Üzgünüm, şu anda cevap üretemiyorum."

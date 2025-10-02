"""Bridges chat requests to the configured AI provider or offline fallback.

The :class:`AIConnector` consults the central configuration to determine which
provider should receive chat prompts.  Supported keys include
``api.provider`` (``openai``, ``openrouter`` or ``offline``), ``api_keys`` for
credential management and ``models`` for choosing the concrete model IDs.  When
network access or third-party dependencies are not available the connector
routes the request to :func:`dialog.response_generator.generate_response`,
making the behaviour reproducible within CI pipelines while still exercising
logging hooks in the surrounding orchestration.
"""

# integration/ai_connector.py
try:
    import requests
except ImportError:  # pragma: no cover - optional dependency
    requests = None

from core.config_manager import ConfigManager
from dialog.response_generator import generate_response

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

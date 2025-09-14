# integration/ai_connector.py
import requests
from core.config_manager import ConfigManager

class AIConnector:
    def __init__(self):
        self.config = ConfigManager()
        self.api_key_openai = self.config.get("api_keys.openai")
        self.api_key_openrouter = self.config.get("api_keys.openrouter")
        self.model_openai = self.config.get("models.online", "gpt-4o-mini")
        self.model_openrouter = self.config.get("models.openrouter", "openai/gpt-3.5-turbo")

    def chat(self, message, provider="openai"):
        response = None

        if provider == "openrouter" and self.api_key_openrouter:
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

        if provider == "openai" and self.api_key_openai:
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

        return "Üzgünüm, şu anda cevap üretemiyorum."

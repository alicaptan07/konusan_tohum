import openai
import requests

from core.config_manager import ConfigManager
from dialog.response_generator import generate_response


def call_api(url, params=None):
    """Basit bir GET isteği yapan yardımcı."""
    try:
        response = requests.get(url, params=params or {}, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return response.json()
        return response.text
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


class AIConnector:
    def __init__(self):
        config = ConfigManager()
        self.provider = config.get("api.provider", "openai")
        self.keys = config.get("api_keys", {})
        self.models = config.get("models", {})

    def chat(self, message, user_memory="", context=""):
        try:
            if self.provider == "openai":
                openai.api_key = self.keys.get("openai", "")
                messages = [
                    {"role": "system", "content": "You are Konuşan Tohum AI."},
                    {"role": "system", "content": f"User memory: {user_memory}"},
                    {"role": "system", "content": f"Context: {context}"},
                    {"role": "user", "content": message},
                ]
                response = openai.ChatCompletion.create(
                    model=self.models.get("online", ""),
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300,
                )
                return response.choices[0].message.content

            else:
                # Offline veya başka provider fallback
                return generate_response(message)
        except Exception as e:
            return f"⚠️ API hatası: {str(e)}"

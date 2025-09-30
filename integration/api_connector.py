import importlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from integration.web_search_mod import search_duckduckgo

__all__ = ["AIConnector", "call_api"]

_DEFAULT_CONFIG: Dict[str, Any] = {
    "api": {"provider": "offline"},
    "api_keys": {},
    "models": {},
}

_openai_spec = importlib.util.find_spec("openai")
_openai = importlib.import_module("openai") if _openai_spec is not None else None


def _load_configuration() -> Dict[str, Any]:
    settings_path = Path("settings/settings.yaml")
    if not settings_path.exists():
        return dict(_DEFAULT_CONFIG)

    yaml_spec = importlib.util.find_spec("yaml")
    if yaml_spec is None:
        return dict(_DEFAULT_CONFIG)

    yaml = importlib.import_module("yaml")
    try:
        with settings_path.open("r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
    except Exception:  # noqa: BLE001 - yapılandırma hatalarında varsayılana dön
        return dict(_DEFAULT_CONFIG)

    if isinstance(config, dict):
        return config
    return dict(_DEFAULT_CONFIG)


def _generate_offline_response(message: str, context: str = "") -> str:
    context_part = f" | Ek bilgi: {context}" if context else ""
    return f"Yanıt: {message}{context_part}".strip()


class AIConnector:
    def __init__(self):
        config = _load_configuration()
        api_config = config.get("api", {}) if isinstance(config, dict) else {}
        self.provider = api_config.get("provider", "offline")
        self.keys = config.get("api_keys", {}) if isinstance(config, dict) else {}
        self.models = config.get("models", {}) if isinstance(config, dict) else {}

    def chat(self, message: str, user_memory: str = "", context: str = "") -> str:
        try:
            if self.provider == "openai" and _openai is not None:
                api_key = self.keys.get("openai", "")
                if not api_key:
                    raise ValueError("OpenAI API anahtarı eksik.")

                _openai.api_key = api_key
                messages = [
                    {"role": "system", "content": "You are Konuşan Tohum AI."},
                    {"role": "system", "content": f"User memory: {user_memory}"},
                    {"role": "system", "content": f"Context: {context}"},
                    {"role": "user", "content": message},
                ]
                response = _openai.ChatCompletion.create(
                    model=self.models.get("online", "gpt-3.5-turbo"),
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300,
                )
                return response.choices[0].message.content

            external_info = search_duckduckgo(message)
            return _generate_offline_response(message, context or external_info)
        except Exception as exc:  # noqa: BLE001 - kullanıcıya anlaşılır hata ilet
            return f"⚠️ API hatası: {exc}" if exc else "⚠️ API hatası oluştu."


def call_api(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Basit API çağrısı yardımcı fonksiyonu."""

    params = params or {}
    query = urlencode(params)
    url = f"{endpoint}?{query}" if query else endpoint

    try:
        with urlopen(url, timeout=10) as response:  # noqa: S310 - harici API denemesi
            payload = response.read().decode("utf-8")
    except (URLError, TimeoutError):
        return {"endpoint": endpoint, "params": params, "status": "unavailable"}

    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {"endpoint": endpoint, "params": params, "raw": payload}

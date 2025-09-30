from typing import Any, Dict, Optional

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    openai = None  # type: ignore

from core.config_manager import load_config
from dialog.response_generator import generate_response
from integration.web_search_mod import search_duckduckgo


def _build_stub_response(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return a deterministic offline response for API calls."""

    params = params or {}
    ordered_params = {key: params[key] for key in sorted(params)}
    return {
        "status": "stub",
        "url": url,
        "params": ordered_params,
        "data": f"stub-response-for-{url}",
    }


def call_api(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Lightweight API helper that gracefully falls back to a stub response.

    The function attempts to perform a real HTTP GET using the requests library.
    When the client library is unavailable or a network error occurs, the
    function returns a deterministic stub response so that tests can run
    without external dependencies.
    """

    params = params or {}

    try:
        import requests  # Local import to avoid mandatory dependency.
    except ImportError:
        return _build_stub_response(url, params)

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        payload: Any
        if content_type.startswith("application/json"):
            payload = response.json()
        else:
            payload = response.text

        return {
            "status": "ok",
            "url": url,
            "params": params,
            "data": payload,
        }
    except Exception:
        return _build_stub_response(url, params)

class AIConnector:
    def __init__(self):
        config = load_config()
        self.provider = config["api"]["provider"]
        self.keys = config["api_keys"]
        self.models = config["models"]

    def chat(self, message, user_memory="", context=""):
        try:
            if (
                self.provider == "openai"
                and openai
                and isinstance(self.keys, dict)
                and self.keys.get("openai")
            ):
                openai.api_key = self.keys["openai"]
                messages = [
                    {"role":"system", "content":"You are Konuşan Tohum AI."},
                    {"role":"system", "content":f"User memory: {user_memory}"},
                    {"role":"system", "content":f"Context: {context}"},
                    {"role":"user", "content":message}
                ]
                response = openai.ChatCompletion.create(
                    model=self.models["online"],
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300
                )
                return response.choices[0].message.content

            else:
                # Offline veya başka provider fallback
                return generate_response(message, intent=None, entities=None, context=context)
        except Exception as e:
            return f"⚠️ API hatası: {str(e)}"
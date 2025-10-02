from typing import Any, Dict, Optional

import time

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    openai = None  # type: ignore

from konusan_tohum.core.config_manager import load_config
from konusan_tohum.dialog.response_generator import generate_response


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


def call_api(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    *,
    timeout: float = 5,
    retries: int = 0,
    backoff_factor: float = 0.5,
) -> Dict[str, Any]:
    """Lightweight API helper that gracefully falls back to a stub response.

    Parameters
    ----------
    url:
        Target endpoint for the HTTP GET request.
    params:
        Query parameters forwarded to the remote endpoint. The mapping is also
        used to build the deterministic stub payload when network access is not
        possible.
    timeout:
        Per-request timeout value passed directly to ``requests.get``. Defaults
        to ``5`` seconds to keep backward compatibility.
    retries:
        The number of retry attempts when the HTTP call fails. Retries use an
        exponential backoff controlled by ``backoff_factor``. ``0`` preserves
        the previous behaviour and performs a single request attempt.
    backoff_factor:
        The base delay in seconds for exponential backoff. Each retry waits for
        ``backoff_factor * (2 ** attempt_index)`` seconds before retrying. The
        value is ignored when ``retries`` is set to ``0``.

    Returns
    -------
    Dict[str, Any]
        Successful responses contain the raw payload returned by ``requests``.
        When the client library is unavailable or network errors persist after
        exhausting the configured retries, the function returns a deterministic
        stub response so that tests can run without external dependencies.
    """

    params = params or {}

    # Guard against negative retry values to keep behaviour predictable.
    if retries < 0:
        retries = 0

    try:
        import requests  # Local import to avoid mandatory dependency.
    except ImportError:
        return _build_stub_response(url, params)

    for attempt in range(retries + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout)
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
            if attempt < retries:
                # Exponential backoff with deterministic timing for tests.
                delay = backoff_factor * (2**attempt)
                if delay > 0:
                    time.sleep(delay)
                continue
            return _build_stub_response(url, params)

class AIConnector:
    def __init__(self):
        config = load_config() or {}

        api_config = config.get("api") if isinstance(config, dict) else None
        if not isinstance(api_config, dict):
            api_config = {}

        self.provider = api_config.get("provider", "offline")
        self.keys = config.get("api_keys", {}) if isinstance(config, dict) else {}
        self.models = config.get("models", {}) if isinstance(config, dict) else {}

        if not isinstance(self.keys, dict):
            self.keys = {}
        if not isinstance(self.models, dict):
            self.models = {}
        self.models.setdefault("online", "gpt-3.5-turbo")
        self.models.setdefault("offline", "konusan-tohum-offline")

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
                return generate_response(message)
        except Exception as e:
            return f"⚠️ API hatası: {str(e)}"

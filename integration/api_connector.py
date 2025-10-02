from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    openai = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import requests
    from requests.adapters import HTTPAdapter
except ImportError:  # pragma: no cover - gracefully handle missing requests
    requests = None  # type: ignore
    HTTPAdapter = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from urllib3.util import Retry
except ImportError:  # pragma: no cover - gracefully handle missing urllib3
    Retry = None  # type: ignore

from core.config_manager import load_config
from dialog.response_generator import generate_response


@dataclass(frozen=True)
class HTTPSettings:
    """Configuration container for outbound HTTP calls."""

    timeout: float = 10.0
    max_retries: int = 3
    backoff_factor: float = 0.5


_SESSION_CACHE: Dict[HTTPSettings, "requests.Session"] = {}


def _get_http_settings() -> HTTPSettings:
    """Extract HTTP settings from configuration with sensible defaults."""

    config = load_config() or {}
    api_config = config.get("api") if isinstance(config, dict) else {}
    if not isinstance(api_config, dict):
        api_config = {}

    timeout = api_config.get("timeout", 10)
    retries = api_config.get("max_retries", 3)
    backoff = api_config.get("backoff_factor", 0.5)

    try:
        timeout_value = float(timeout)
    except (TypeError, ValueError):  # pragma: no cover - defensive branch
        timeout_value = 10.0

    try:
        retries_value = int(retries)
    except (TypeError, ValueError):  # pragma: no cover - defensive branch
        retries_value = 3

    try:
        backoff_value = float(backoff)
    except (TypeError, ValueError):  # pragma: no cover - defensive branch
        backoff_value = 0.5

    return HTTPSettings(
        timeout=max(timeout_value, 0.1),
        max_retries=max(retries_value, 0),
        backoff_factor=max(backoff_value, 0.0),
    )


def _build_http_session(settings: HTTPSettings) -> Optional["requests.Session"]:
    """Create (and cache) a requests session with retry/backoff configuration."""

    if requests is None:  # pragma: no cover - executed when requests missing
        return None

    session = _SESSION_CACHE.get(settings)
    if session is not None:
        return session

    session = requests.Session()

    if HTTPAdapter is not None:
        if Retry is not None:
            retry = Retry(
                total=settings.max_retries,
                connect=settings.max_retries,
                read=settings.max_retries,
                status=settings.max_retries,
                backoff_factor=settings.backoff_factor,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=("GET", "POST"),
                raise_on_status=False,
            )
            adapter = HTTPAdapter(max_retries=retry)
        else:  # pragma: no cover - urllib3 missing
            adapter = HTTPAdapter()

        session.mount("http://", adapter)
        session.mount("https://", adapter)

    _SESSION_CACHE[settings] = session
    return session


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
    """Lightweight API helper that gracefully falls back to a stub response."""

    params = params or {}

    settings = _get_http_settings()
    session = _build_http_session(settings)
    if session is None:  # pragma: no cover - requests missing
        return _build_stub_response(url, params)

    try:
        response = session.get(url, params=params, timeout=settings.timeout)
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
    except Exception as exc:
        if requests is not None and isinstance(exc, requests.Timeout):
            error_response = _build_stub_response(url, params)
            error_response.update(
                {
                    "status": "timeout",
                    "error": f"Request to {url} timed out after {settings.timeout} seconds.",
                }
            )
            return error_response
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
        self.models.setdefault("openrouter", "openai/gpt-3.5-turbo")

        self.http_settings = _get_http_settings()

    def chat(self, message, user_memory="", context=""):
        provider = (self.provider or "offline").lower()
        session = _build_http_session(self.http_settings)

        def _compose_messages() -> Dict[str, Any]:
            return {
                "model": self.models.get("online", "gpt-3.5-turbo"),
                "messages": [
                    {"role": "system", "content": "You are Konuşan Tohum AI."},
                    {"role": "system", "content": f"User memory: {user_memory}"},
                    {"role": "system", "content": f"Context: {context}"},
                    {"role": "user", "content": message},
                ],
                "temperature": 0.7,
                "max_tokens": 300,
            }

        def _handle_timeout(endpoint: str) -> str:
            return (
                f"⚠️ API hatası: Request to {endpoint} timed out after "
                f"{self.http_settings.timeout} seconds."
            )

        try:
            if provider == "openrouter" and self.keys.get("openrouter"):
                if session is None:
                    return generate_response(message)

                headers = {
                    "Authorization": f"Bearer {self.keys['openrouter']}",
                    "Content-Type": "application/json",
                }
                payload = _compose_messages()
                payload["model"] = self.models.get("openrouter", payload["model"])

                try:
                    response = session.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=self.http_settings.timeout,
                    )
                    response.raise_for_status()
                    data = response.json()
                    content = (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content")
                    )
                    if isinstance(content, str) and content.strip():
                        return content
                except Exception as exc:
                    if requests is not None and isinstance(exc, requests.Timeout):
                        return _handle_timeout("OpenRouter")
                    return f"⚠️ API hatası: {exc}"
                provider = "offline"

            if provider == "openai" and self.keys.get("openai"):
                if session is None and openai:
                    try:
                        openai.api_key = self.keys["openai"]
                        payload = _compose_messages()
                        messages = payload.pop("messages")
                        response = openai.ChatCompletion.create(
                            messages=messages,
                            **payload,
                        )
                        return response.choices[0].message.content
                    except Exception as exc:  # pragma: no cover - optional path
                        return f"⚠️ API hatası: {exc}"

                if session is None:
                    return generate_response(message)

                headers = {
                    "Authorization": f"Bearer {self.keys['openai']}",
                    "Content-Type": "application/json",
                }
                payload = _compose_messages()
                try:
                    response = session.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=self.http_settings.timeout,
                    )
                    response.raise_for_status()
                    data = response.json()
                    content = (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content")
                    )
                    if isinstance(content, str) and content.strip():
                        return content
                except Exception as exc:
                    if requests is not None and isinstance(exc, requests.Timeout):
                        return _handle_timeout("OpenAI")
                    return f"⚠️ API hatası: {exc}"
                provider = "offline"

            return generate_response(message)
        except Exception as exc:  # pragma: no cover - defensive
            return f"⚠️ API hatası: {exc}"

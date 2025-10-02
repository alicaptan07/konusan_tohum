import time
from typing import Any, Dict, Optional, Sequence

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    openai = None  # type: ignore

from core.config_manager import load_config
from dialog.response_generator import generate_response


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


_RETRYABLE_STATUS_CODES: Sequence[int] = (429, 500, 502, 503, 504, 522, 524)


def call_api(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    *,
    max_retries: int = 3,
    backoff_factor: float = 0.5,
) -> Dict[str, Any]:
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

    # Bazı ortamlar requests.Timeout yerine exceptions.Timeout kullanır.
    timeout_exceptions: Sequence[type] = tuple(
        exc
        for exc in (
            getattr(requests, "Timeout", None),
            getattr(getattr(requests, "exceptions", None), "Timeout", None),
        )
        if isinstance(exc, type)
    )

    last_error: Optional[Exception] = None
    delay = backoff_factor

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=5)
        except Exception as exc:  # pragma: no cover - farklı hata türleri
            last_error = exc
        else:
            status_code = getattr(response, "status_code", None)
            if isinstance(status_code, int) and 200 <= status_code < 300:
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

            if status_code in _RETRYABLE_STATUS_CODES:
                last_error = Exception(f"HTTP {status_code}")
            else:
                try:
                    response.raise_for_status()
                except Exception as exc:  # pragma: no cover - requests ayrıntıları
                    last_error = exc
                break

        # Başarısız denemeler için geri çekilme uygula.
        if attempt < max_retries - 1:
            if timeout_exceptions and last_error and isinstance(last_error, timeout_exceptions):
                pass
            # Geri çekilme sırasında bekleme yapılırken hatalara toleranslı ol.
            try:
                time.sleep(delay)
            except Exception:
                pass
            delay *= 2

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

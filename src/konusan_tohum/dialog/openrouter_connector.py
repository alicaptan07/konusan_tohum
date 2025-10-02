# dialog/openrouter_connector.py
try:
    import requests  # type: ignore
except ImportError:  # pragma: no cover - environment without requests
    requests = None
from konusan_tohum.core.config_manager import ConfigManager

config = ConfigManager()
api_keys = config.get("api_keys", {})
OPENROUTER_KEY = api_keys.get("openrouter")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_openrouter_api(prompt, model="openai/gpt-3.5-turbo"):
    if requests is None:
        raise RuntimeError(
            "The 'requests' library is required to call the OpenRouter API, but it is not installed."
        )
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}"}
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    r = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

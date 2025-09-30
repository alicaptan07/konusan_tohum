import json
from typing import List
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

__all__ = ["search_duckduckgo", "search"]

_DUCKDUCKGO_API_URL = "https://api.duckduckgo.com/"
_FALLBACK_MESSAGE = "Üzgünüm, bu konuda bilgi bulamadım."


def _fetch_duckduckgo_data(query: str) -> dict:
    params = {
        "q": query,
        "format": "json",
        "no_redirect": 1,
        "no_html": 1,
    }
    url = f"{_DUCKDUCKGO_API_URL}?{urlencode(params)}"
    try:
        with urlopen(url, timeout=10) as response:
            payload = response.read().decode("utf-8")
    except (URLError, TimeoutError):
        return {}

    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {}


def _extract_related_topics(topics: List[dict]) -> List[str]:
    results: List[str] = []
    for entry in topics or []:
        text = entry.get("Text")
        if text:
            results.append(text)
            continue

        nested = entry.get("Topics")
        if isinstance(nested, list):
            results.extend(_extract_related_topics(nested))
    return results


def search_duckduckgo(query: str, *, _data: dict | None = None) -> str:
    data = _data if _data is not None else _fetch_duckduckgo_data(query)
    if not data:
        return _FALLBACK_MESSAGE

    abstract = data.get("Abstract") or data.get("AbstractText")
    if abstract:
        return abstract

    related_results = _extract_related_topics(data.get("RelatedTopics", []))
    if related_results:
        return related_results[0]

    return _FALLBACK_MESSAGE


def search(query: str) -> List[str]:
    """Return DuckDuckGo search results as a list for integration tests."""

    data = _fetch_duckduckgo_data(query)
    results: List[str] = []

    primary = search_duckduckgo(query, _data=data)
    if primary:
        results.append(primary)

    if data:
        related_results = _extract_related_topics(data.get("RelatedTopics", []))
        for item in related_results:
            if item not in results:
                results.append(item)

    return results or [_FALLBACK_MESSAGE]

import requests


def search_duckduckgo(query):
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_redirect": 1,
        "no_html": 1,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    abstract = data.get("Abstract")
    if isinstance(abstract, str):
        abstract = abstract.strip()
    return abstract or None


def search(query):
    """Return DuckDuckGo search summaries as a list."""
    result = search_duckduckgo(query)
    if isinstance(result, str):
        cleaned = result.strip()
        if cleaned:
            return [cleaned]
    return []

import requests

def search_duckduckgo(query):
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_redirect": 1,
        "no_html": 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("Abstract", "Üzgünüm, bu konuda bilgi bulamadım.")
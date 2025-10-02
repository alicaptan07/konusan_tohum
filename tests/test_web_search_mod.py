"""Unit tests for the DuckDuckGo search helper module."""

from unittest.mock import patch

from konusan_tohum.integration import web_search_mod


def test_search_returns_online_result_when_available():
    """The online branch should take precedence when it yields a summary."""

    with patch.object(
        web_search_mod,
        "search_duckduckgo",
        return_value="  İnternet sonucu  ",
    ) as mock_search:
        results = web_search_mod.search("herhangi bir sorgu")

    mock_search.assert_called_once_with("herhangi bir sorgu")
    assert results == ["İnternet sonucu"]


def test_search_falls_back_to_offline_results_when_online_fails():
    """When the online lookup fails we should expose the offline dataset."""

    with patch.object(web_search_mod, "search_duckduckgo", return_value=None):
        results = web_search_mod.search("Antalya hava durumu")

    assert results == [
        "Antalya'da hava çoğunlukla güneşli olup mevsimine göre hafif rüzgarli.",
    ]

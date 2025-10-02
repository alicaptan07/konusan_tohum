"""Konuşan Tohum OpenRouter bağlayıcısının bağımlılık kontrollerini ve hata mesajlarını doğrulayan testler."""

import pytest

from konusan_tohum.dialog import openrouter_connector


def test_call_openrouter_api_without_requests(monkeypatch):
    monkeypatch.setattr(openrouter_connector, "requests", None)

    with pytest.raises(RuntimeError, match="requests"):
        openrouter_connector.call_openrouter_api("Hello")

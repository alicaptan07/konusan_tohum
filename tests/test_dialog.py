import pytest

from konusan_tohum.dialog.response_generator import (
    RULE_BASED_RESPONSES,
    generate,
    generate_response,
)


@pytest.mark.parametrize(
    "intent,expected_key",
    [
        ("greeting", "greeting"),
        ("ask_help", "help"),
        ("farewell", "goodbye"),
        ("thank_you", "thanks"),
    ],
)
def test_rule_based_responses(intent, expected_key):
    response = generate(intent, {}, [])
    assert response == RULE_BASED_RESPONSES[expected_key]


@pytest.mark.parametrize(
    "intent",
    ["ask_help", "farewell", "thank_you"],
)
def test_rule_based_aliases_present(intent):
    """Yeni niyet anahtarları için kural tabanlı yanıt döndürülmeli."""
    response = generate(intent, {}, [])
    assert isinstance(response, str)
    assert response


def test_generate_matches_generate_response(monkeypatch):
    """Serbest üretim akışında `generate` ve `generate_response` aynı çıktıyı vermeli."""

    from konusan_tohum.dialog import response_generator as rg

    class DummyGenerator:
        def __call__(self, prompt, **kwargs):
            return [{"generated_text": f"YANIT: {prompt}"}]

    dummy_generator = DummyGenerator()

    # Dış bağımlılıklar deterministik hale getiriliyor.
    monkeypatch.setattr(rg, "_GENERATOR", None, raising=False)
    monkeypatch.setattr(rg, "_get_generator", lambda: dummy_generator)

    message = "Merhaba dünya"
    expected = generate_response(message)
    context = [{"message": message}]

    result = generate(None, {}, context)

    assert result == expected

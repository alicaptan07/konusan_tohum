import pytest

from dialog import response_generator as response_module
from dialog.response_generator import RULE_BASED_RESPONSES, generate


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


def _stub_generator():
    def _generate(prompt, **kwargs):
        return [{"generated_text": f"echo::{prompt}"}]

    return _generate


def test_generate_response_alias(monkeypatch):
    monkeypatch.setattr(response_module, "_GENERATOR", _stub_generator())

    result = response_module.generate_response("merhaba")
    assert result == "echo::merhaba"


def test_generate_fallback_uses_generator(monkeypatch):
    monkeypatch.setattr(response_module, "_GENERATOR", _stub_generator())

    result = response_module.generate("bilinmeyen", {}, [], user_id="u1")
    # Intent bilinmeyen olduğunda generate_response tetiklenmeli
    assert result == "echo::bilinmeyen"

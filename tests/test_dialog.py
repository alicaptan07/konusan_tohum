import pytest

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

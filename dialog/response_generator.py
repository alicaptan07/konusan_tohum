# dialog/response_generator.py

try:
    from transformers import pipeline
except ImportError:  # pragma: no cover - çevrimdışı ortamlara uyum
    pipeline = None

from core.config_manager import ConfigManager

_GENERATOR = None


class _FallbackGenerator:
    """Dış bağımlılık olmadığında kullanılan basit üretici."""

    def __call__(self, prompt, **kwargs):
        return [{"generated_text": prompt}]


def _get_generator():
    """Modeli tek seferde oluşturup önbelleğe al."""
    global _GENERATOR
    if _GENERATOR is None:
        config = ConfigManager()
        model_name = config.get("models.offline", "gpt2")
        if pipeline is None:
            _GENERATOR = _FallbackGenerator()
        else:
            _GENERATOR = pipeline("text-generation", model=model_name)
    return _GENERATOR


def generate_response(message: str) -> str:
    """
    Kullanıcıdan gelen mesajı alır ve uygun bir yanıt üretir.
    :param message: Kullanıcı mesajı
    :return: Yapay zeka tarafından üretilen yanıt
    """
    try:
        generator = _get_generator()
        response = generator(
            message,
            max_length=100,
            num_return_sequences=1,
            do_sample=True,
            top_k=50,
            top_p=0.95
        )
        return response[0]["generated_text"]
    except Exception as e:
        return f"[Hata] Yanıt üretilemedi: {e}"


_BASE_RULE_RESPONSES = {
    "greeting": "Merhaba! Size nasıl yardımcı olabilirim?",
    "goodbye": "Görüşmek üzere! Yardıma ihtiyacınız olursa buradayım.",
    "thanks": "Rica ederim! Başka bir konuda destek ister misiniz?",
    "help": "Elbette, hangi konuda yardıma ihtiyacınız var?"
}

_INTENT_ALIASES = {
    "farewell": "goodbye",
    "thank_you": "thanks",
    "ask_help": "help",
}

RULE_BASED_RESPONSES = dict(_BASE_RULE_RESPONSES)
for alias, target in _INTENT_ALIASES.items():
    RULE_BASED_RESPONSES[alias] = _BASE_RULE_RESPONSES.get(target, "")


def _entity_summary(entities):
    if not entities:
        return ""

    if isinstance(entities, dict):
        items = [f"{key}: {value}" for key, value in entities.items()]
    else:
        items = [str(entity) for entity in entities]
    return ", ".join(items)


def generate(intent, entities, context, user_id=None):
    """Niyet, varlıklar ve bağlamı kullanarak yanıt üretir."""

    intent_key = (intent or "").lower()
    intent_key = _INTENT_ALIASES.get(intent_key, intent_key)

    if intent_key in RULE_BASED_RESPONSES:
        base_response = RULE_BASED_RESPONSES[intent_key]
        entity_text = _entity_summary(entities)
        if entity_text:
            base_response += f" (Belirttiğiniz bilgiler: {entity_text})"
        return base_response

    if context:
        latest_message = context[-1].get("message", "")
    else:
        latest_message = intent or "Merhaba"

    response = generate_response(latest_message)

    if isinstance(response, str):
        return response

    return str(response)


if __name__ == "__main__":
    # Test amaçlı
    test_input = "Merhaba, sen kimsin?"
    print("Kullanıcı:", test_input)
    print("Tohum AI:", generate_response(test_input))

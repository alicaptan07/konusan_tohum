# dialog/response_generator.py

from transformers import pipeline

# Hugging Face'ten hazır pipeline (örnek: küçük bir model ile test için)
# Daha güçlü bir model kullanmak istersen buradaki model adını değiştirebilirsin.
generator = pipeline("text-generation", model="gpt2")


def generate_response(message: str) -> str:
    """
    Kullanıcıdan gelen mesajı alır ve uygun bir yanıt üretir.
    :param message: Kullanıcı mesajı
    :return: Yapay zeka tarafından üretilen yanıt
    """
    try:
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


RULE_BASED_RESPONSES = {
    "greeting": "Merhaba! Size nasıl yardımcı olabilirim?",
    "goodbye": "Görüşmek üzere! Yardıma ihtiyacınız olursa buradayım.",
    "thanks": "Rica ederim! Başka bir konuda destek ister misiniz?",
    "help": "Elbette, hangi konuda yardıma ihtiyacınız var?"
}


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

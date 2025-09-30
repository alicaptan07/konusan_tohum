from nlp.intent_detector import detect_intent
from nlp.entity_extractor import extract_entities
from nlp.context_manager import update_context, get_context
from nlp.persona_builder import get_persona
from dialog.response_generator import generate
from dialog.tone_adjuster import adjust_tone


def process_message(user_id, message):
    # Mevcut bağlamı al
    context_history = get_context(user_id)

    # Niyet ve varlık çıkarımı
    intent = detect_intent(message)
    entities = extract_entities(message)

    # Bağlamı gerçek verilerle güncelle
    context_history = update_context(user_id, message, intent, entities)

    # Kişilik profili ve ton bilgisi
    persona_data = get_persona(user_id)
    if not isinstance(persona_data, dict):
        persona_data = {}
    else:
        persona_data = dict(persona_data)
    tone = persona_data.get("tone") or persona_data.get("default_tone") or "neutral"
    persona_data.setdefault("tone", tone)

    # Yanıt üretimi için zenginleştirilmiş bağlam
    conversation_context = {
        "history": context_history,
        "persona": persona_data,
        "tone": tone,
    }

    # Yanıt üretimi
    raw_response = generate(intent, entities, conversation_context)
    final_response = adjust_tone(user_id, raw_response)

    return final_response


def ping():
    return "OK"

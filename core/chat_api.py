from nlp.intent_detector import detect_intent
from nlp.entity_extractor import extract_entities
from nlp.context_manager import update_context, get_context
from nlp.persona_builder import build_persona
from dialog.response_generator import generate
from dialog.tone_adjuster import adjust

def process_message(user_id, message):
    # Bağlamı güncelle
    update_context(user_id, {"last_message": message})
    context = get_context(user_id)

    # Niyet ve varlık çıkarımı
    intent = detect_intent(message)
    entities = extract_entities(message)

    # Kişilik profili
    persona = build_persona(user_id)
    tone = persona.get("tone", "neutral")

    # Yanıt üretimi
    raw_response = generate(intent, entities, context)
    final_response = adjust(raw_response, tone)

    return final_response

def ping():
    return "OK"
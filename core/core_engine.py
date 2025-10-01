from nlp.intent_detector import detect_intent
from nlp.nlp_engine import preprocess_text
from nlp.entity_extractor import extract_entities
from nlp.context_manager import update_context
from dialog.response_generator import generate_response
from integration.web_search_mod import search


def process_message(user_id, message):
    if not message or not message.strip():
        return "⚠️ Lütfen geçerli bir mesaj yaz."

    # 1. Ön işleme
    clean_text = preprocess_text(message)

    # 2. Niyet ve varlık çıkarımı
    try:
        intent = detect_intent(clean_text)
    except Exception as e:
        intent = "unknown"

    try:
        entities = extract_entities(clean_text)
    except Exception as e:
        entities = {}

    # 3. Bağlam güncelleme
    try:
        context = update_context(user_id, message, intent, entities)
    except Exception as e:
        context = {}

    # 4. GPT tabanlı yanıt üretimi
    try:
        response = generate_response(clean_text, intent, entities, context)
    except Exception as e:
        response = f"⚠️ Yanıt üretilemedi: {str(e)}"

    # 5. Yanıt eksikse web aramasıyla destekle
    if not response or "bilgi yok" in response.lower():
        try:
            search_results = search(message)
            if search_results:
                response = f"{search_results[0]} (Kaynak: DuckDuckGo)"
            else:
                response = (response or "") + "\n⚠️ Web araması sonuç vermedi."
        except Exception:
            response = (response or "") + "\n⚠️ Web araması yapılamadı."

    return response

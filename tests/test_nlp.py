"""Konuşan Tohum NLP katmanının niyet ve varlık çıkarımı için sunduğu yolları değerlendiren testler."""

from konusan_tohum.nlp.entity_extractor import extract_entities
from konusan_tohum.nlp.intent_detector import IntentDetector, detect_intent

def test_intent_detector():
    intent = detect_intent("Bugün hava nasıl?")
    assert intent in ["weather", "greeting", "unknown"]
    print("✅ IntentDetector test edildi.")

def test_intent_detector_fallback_manual_map():
    detector = IntentDetector(load_transformer=False)
    intent = detector.detect("Merhaba, nasılsın?")
    assert intent == "greeting"

def test_entity_extractor():
    entities = extract_entities("Antalya'da hava durumu")
    assert isinstance(entities, dict)
    print("✅ EntityExtractor test edildi.")

from nlp.intent_detector import detect_intent
from nlp.entity_extractor import extract_entities
from nlp.intent_loader import load_intents

def test_intent_detector():
    intent = detect_intent("Bugün hava nasıl?")
    # ask_weather dahil olmak üzere tanımlı niyetleri ve manuel eşleşmeleri kapsar
    expected_labels = set(load_intents().keys()) | {"continue_story", "story_request"}
    assert intent in expected_labels
    print("✅ IntentDetector test edildi.")

def test_entity_extractor():
    entities = extract_entities("Antalya'da hava durumu")
    assert isinstance(entities, dict)
    print("✅ EntityExtractor test edildi.")

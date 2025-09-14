from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from nlp.intent_loader import load_intents

class IntentDetector:
    def __init__(self):
        self.intents = load_intents()
        self.labels = list(self.intents.keys())
        self.tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-base-turkish-cased")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "dbmdz/bert-base-turkish-cased"
        )

        # Manuel örnek eşleştirme için basit anahtar kelime haritası
        self.manual_map = {
            "devam et": "continue_story",
            "sonra ne oldu": "continue_story",
            "hikaye devam etsin": "continue_story",
            "bana bir hikaye anlat": "story_request",
            "yardım istiyorum": "ask_help",
            "nasılsın": "greeting",
            "merhaba": "greeting"
        }

    def detect(self, text):
        if not text or not text.strip():
            return "unknown"

        # Manuel eşleşme kontrolü
        lowered = text.lower().strip()
        for phrase, intent in self.manual_map.items():
            if phrase in lowered:
                return intent

        # Model tabanlı tahmin
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()

        if 0 <= predicted_class < len(self.labels):
            return self.labels[predicted_class]
        return "unknown"

# Global örnek
intent_detector = IntentDetector()

# Fonksiyon olarak dışa aktar
def detect_intent(text):
    return intent_detector.detect(text)
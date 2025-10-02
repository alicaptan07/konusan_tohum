"""Konuşan Tohum varlık çıkarıcısı, önceden tanımlı örneklerle kullanıcı mesajlarından anlamlı varlıklar tespit eder."""

import re
from konusan_tohum.nlp.entity_loader import load_entities

class EntityExtractor:
    def __init__(self):
        self.entities = load_entities()

    def extract(self, text):
        found_entities = {}
        for entity_type, info in self.entities.items():
            examples = info.get("examples", [])
            for example in examples:
                if re.search(rf"\b{re.escape(example)}\b", text, re.IGNORECASE):
                    found_entities[entity_type] = example
        return found_entities

# Global örnek
entity_extractor = EntityExtractor()

# Fonksiyon olarak dışa aktar
def extract_entities(text):
    return entity_extractor.extract(text)

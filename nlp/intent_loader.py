import os
import yaml

def load_intents(path=None):
    if path is None:
        # intent_loader.py'nin bulunduğu klasörü bul
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Oradan "data/intents.yaml" yolunu oluştur
        path = os.path.join(base_dir, "data", "intents.yaml")

    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ intents.yaml bulunamadı: {path}")

    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data["intents"]
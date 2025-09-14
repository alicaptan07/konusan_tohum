import os
import yaml

def load_entities(path=None):
    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "data", "entities.yaml")

    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ entities.yaml bulunamadı: {path}")

    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data["entities"]

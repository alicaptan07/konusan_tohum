import json
import os
from pathlib import Path


_PACKAGE_DIR = Path(__file__).resolve().parent
_DATA_DIR = _PACKAGE_DIR / "data"
MEMORY_FILE = _DATA_DIR / "user_memory.json"


def _ensure_memory_file(memory_file):
    path = Path(memory_file)
    os.makedirs(path.parent, exist_ok=True)
    if not path.exists():
        path.write_text("{}", encoding="utf-8")
    return path


_ensure_memory_file(MEMORY_FILE)


def load_user_memory(user_id, memory_file=MEMORY_FILE):
    """Kullanıcının hafızasını yükler."""
    path = _ensure_memory_file(memory_file)
    with open(path, "r", encoding="utf-8") as f:
        all_memory = json.load(f)
    return all_memory.get(user_id, {})


def save_memory(user_memory_dict, memory_file=MEMORY_FILE):
    """Tüm kullanıcı hafızasını kaydeder.
    user_memory_dict: {user_id: memory_data} şeklinde olmalı
    """
    path = _ensure_memory_file(memory_file)
    with open(path, "r", encoding="utf-8") as f:
        all_memory = json.load(f)

    # Hafızayı güncelle
    for uid, mem in user_memory_dict.items():
        all_memory[uid] = mem

    with open(path, "w", encoding="utf-8") as f:
        json.dump(all_memory, f, indent=2, ensure_ascii=False)


def auto_update_memory(user_id, message, intent=None, entities=None, memory_file=MEMORY_FILE):
    """Kullanıcı mesajını history'ye ekler."""
    memory_data = load_user_memory(user_id, memory_file=memory_file)
    if "history" not in memory_data:
        memory_data["history"] = []

    memory_data["history"].append({
        "message": message,
        "intent": intent,
        "entities": entities
    })

    # Maksimum geçmişi koru (isteğe göre)
    MAX_HISTORY = 20
    if len(memory_data["history"]) > MAX_HISTORY:
        memory_data["history"] = memory_data["history"][-MAX_HISTORY:]

    save_memory({user_id: memory_data}, memory_file=memory_file)


def get_user_memory(user_id, memory_file=MEMORY_FILE):
    """Kullanıcının tam hafızasını döner."""
    return load_user_memory(user_id, memory_file=memory_file)


def update_memory(user_id, message, response, memory_file=MEMORY_FILE):
    """Kullanıcının mesaj/yanıt geçmişini günceller ve JSON bütünlüğünü doğrular."""
    memory_data = load_user_memory(user_id, memory_file=memory_file)

    history = memory_data.get("history", [])
    history.append({
        "message": message,
        "response": response,
    })
    memory_data["history"] = history[-20:]

    save_memory({user_id: memory_data}, memory_file=memory_file)

    # JSON yapısının bozulmadığını doğrula
    path = _ensure_memory_file(memory_file)
    with open(path, "r", encoding="utf-8") as f:
        json.load(f)

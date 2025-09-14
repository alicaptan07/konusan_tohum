import json
import os

MEMORY_FILE = "memory/user_memory.json"

# Dosya yoksa oluştur
if not os.path.exists("memory"):
    os.makedirs("memory")

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=2, ensure_ascii=False)


def load_user_memory(user_id):
    """Kullanıcının hafızasını yükler."""
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        all_memory = json.load(f)
    return all_memory.get(user_id, {})


def save_memory(user_memory_dict):
    """Tüm kullanıcı hafızasını kaydeder.
    user_memory_dict: {user_id: memory_data} şeklinde olmalı
    """
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        all_memory = json.load(f)

    # Hafızayı güncelle
    for uid, mem in user_memory_dict.items():
        all_memory[uid] = mem

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(all_memory, f, indent=2, ensure_ascii=False)


def auto_update_memory(user_id, message, intent=None, entities=None):
    """Kullanıcı mesajını history'ye ekler."""
    memory_data = load_user_memory(user_id)
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

    save_memory({user_id: memory_data})


def get_user_memory(user_id):
    """Kullanıcının tam hafızasını döner."""
    return load_user_memory(user_id)

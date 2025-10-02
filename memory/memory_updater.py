import json
import os
import tempfile
import threading
from typing import Any, Dict

MEMORY_FILE = "memory/user_memory.json"

_MEMORY_LOCK = threading.Lock()


def _ensure_memory_file() -> None:
    """Ensure the backing memory file and its directory exist."""
    directory = os.path.dirname(MEMORY_FILE) or "."
    os.makedirs(directory, exist_ok=True)
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2, ensure_ascii=False)


def _atomic_write_json(data: Dict[str, Any], file_path: str) -> None:
    """Persist JSON data atomically using a temporary file and os.replace."""
    directory = os.path.dirname(file_path) or "."
    os.makedirs(directory, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=directory, delete=False
    ) as tmp_file:
        json.dump(data, tmp_file, indent=2, ensure_ascii=False)
        tmp_file.flush()
        os.fsync(tmp_file.fileno())
        temp_name = tmp_file.name
    os.replace(temp_name, file_path)


def _load_all_memory() -> Dict[str, Any]:
    _ensure_memory_file()
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


_ensure_memory_file()


def load_user_memory(user_id):
    """Kullanıcının hafızasını yükler."""
    all_memory = _load_all_memory()
    return all_memory.get(user_id, {})


def save_memory(user_memory_dict):
    """Tüm kullanıcı hafızasını kaydeder.
    user_memory_dict: {user_id: memory_data} şeklinde olmalı
    """
    with _MEMORY_LOCK:
        all_memory = _load_all_memory()

        # Hafızayı güncelle
        for uid, mem in user_memory_dict.items():
            all_memory[uid] = mem

        _atomic_write_json(all_memory, MEMORY_FILE)


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


def update_memory(user_id, message, response):
    """Kullanıcının mesaj/yanıt geçmişini günceller ve JSON bütünlüğünü doğrular."""
    with _MEMORY_LOCK:
        all_memory = _load_all_memory()
        memory_data = all_memory.get(user_id, {})

        history = memory_data.get("history", [])
        history.append({
            "message": message,
            "response": response,
        })
        memory_data["history"] = history[-20:]
        all_memory[user_id] = memory_data

        _atomic_write_json(all_memory, MEMORY_FILE)

        # JSON yapısının bozulmadığını doğrula
        _load_all_memory()

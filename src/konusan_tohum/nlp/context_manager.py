"""Konuşan Tohum bağlam yöneticisi, kullanıcı etkileşim geçmişini güncelleyip özetleyerek diyaloğu kişiselleştirir."""

from konusan_tohum.memory.memory_updater import (
    auto_update_memory,
    load_user_memory,
    save_memory,
)

MAX_HISTORY = 5  # Kaç mesaj saklanacak


def update_context(user_id, message, intent=None, entities=None, memory_file=None):
    """Kullanıcının bağlamını günceller ve hafızaya kaydeder."""
    if memory_file is None:
        memory_data = load_user_memory(user_id)
    else:
        memory_data = load_user_memory(user_id, memory_file=memory_file)

    if "context" not in memory_data:
        memory_data["context"] = []

    memory_data["context"].append({
        "message": message,
        "intent": intent,
        "entities": entities
    })

    # Maksimum geçmişi koru
    if len(memory_data["context"]) > MAX_HISTORY:
        memory_data["context"] = memory_data["context"][-MAX_HISTORY:]

    # Belleği kaydet
    if memory_file is None:
        save_memory({user_id: memory_data})
    else:
        save_memory({user_id: memory_data}, memory_file=memory_file)

    # Ayrıca otomatik hafızaya da işleyelim
    if memory_file is None:
        auto_update_memory(user_id, message, intent, entities)
    else:
        auto_update_memory(
            user_id, message, intent, entities, memory_file=memory_file
        )

    return memory_data["context"]


def get_context(user_id, memory_file=None):
    """Kullanıcının bağlamını döner."""
    if memory_file is None:
        memory_data = load_user_memory(user_id)
    else:
        memory_data = load_user_memory(user_id, memory_file=memory_file)
    return memory_data.get("context", [])


def get_context_summary(user_id, memory_file=None):
    """Kullanıcının bağlamının kısa özetini döner."""
    if memory_file is None:
        context = get_context(user_id)
    else:
        context = get_context(user_id, memory_file=memory_file)
    summary = "\n".join([f"{c['message']} ({c['intent']})" for c in context])
    return summary

from memory.memory_updater import load_user_memory, save_memory, auto_update_memory

MAX_HISTORY = 5  # Kaç mesaj saklanacak


def update_context(user_id, message, intent=None, entities=None):
    """Kullanıcının bağlamını günceller ve hafızaya kaydeder."""
    memory_data = load_user_memory(user_id)

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
    save_memory({user_id: memory_data})

    # Ayrıca otomatik hafızaya da işleyelim
    auto_update_memory(user_id, message, intent, entities)

    return memory_data["context"]


def get_context(user_id):
    """Kullanıcının bağlamını döner."""
    memory_data = load_user_memory(user_id)
    return memory_data.get("context", [])


def get_context_summary(user_id):
    """Kullanıcının bağlamının kısa özetini döner."""
    context = get_context(user_id)
    summary = "\n".join([f"{c['message']} ({c['intent']})" for c in context])
    return summary

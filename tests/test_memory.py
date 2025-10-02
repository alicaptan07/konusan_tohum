import json

from konusan_tohum.memory import update_memory
from konusan_tohum.memory.memory_updater import auto_update_memory


def test_update_memory_appends_history_and_persists_json(tmp_path):
    memory_file = tmp_path / "user_memory.json"
    user_id = "test-user"

    update_memory(user_id, "Selam", "Merhaba!", memory_file=memory_file)
    update_memory(user_id, "Nasılsın?", "İyiyim, teşekkürler!", memory_file=memory_file)

    with memory_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert user_id in data
    history = data[user_id]["history"]
    assert len(history) == 2
    assert history[0] == {"message": "Selam", "response": "Merhaba!"}
    assert history[1] == {"message": "Nasılsın?", "response": "İyiyim, teşekkürler!"}


def test_auto_update_memory_persists_intent_entities_and_limits_history(tmp_path):
    memory_file = tmp_path / "user_memory.json"
    user_id = "auto-user"

    auto_update_memory(
        user_id,
        "İlk mesaj",
        intent="selamlama",
        entities={"isim": "Ahmet"},
        memory_file=memory_file,
    )

    for i in range(25):
        auto_update_memory(
            user_id,
            f"Mesaj {i}",
            intent=f"intent_{i}",
            entities={"index": i},
            memory_file=memory_file,
        )

    with memory_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert user_id in data
    history = data[user_id]["history"]

    assert len(history) == 20
    assert history[0]["message"] == "Mesaj 5"
    assert history[-1] == {
        "message": "Mesaj 24",
        "intent": "intent_24",
        "entities": {"index": 24},
    }

    for entry in history:
        assert "intent" in entry
        assert "entities" in entry

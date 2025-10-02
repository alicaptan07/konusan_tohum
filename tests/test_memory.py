import json

from konusan_tohum.memory import update_memory


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

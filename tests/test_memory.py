import json
import threading

import pytest

from memory import memory_updater


def _configure_temporary_memory(monkeypatch, tmp_path):
    memory_file = tmp_path / "user_memory.json"
    monkeypatch.setattr(memory_updater, "MEMORY_FILE", str(memory_file), raising=False)
    memory_updater._ensure_memory_file()
    return memory_file


def test_update_memory_is_atomic_on_failure(monkeypatch, tmp_path):
    memory_file = _configure_temporary_memory(monkeypatch, tmp_path)
    user_id = "user"

    memory_updater.update_memory(user_id, "hello", "world")
    initial_state = json.loads(memory_file.read_text(encoding="utf-8"))

    def fail_atomic_write_json(*args, **kwargs):  # pragma: no cover - behaviour tested via exception
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(memory_updater, "_atomic_write_json", fail_atomic_write_json)

    with pytest.raises(RuntimeError):
        memory_updater.update_memory(user_id, "new", "response")

    assert json.loads(memory_file.read_text(encoding="utf-8")) == initial_state


def test_update_memory_concurrent_access(monkeypatch, tmp_path):
    _configure_temporary_memory(monkeypatch, tmp_path)

    user_id = "concurrent-user"
    message_count = 10

    def worker(idx: int) -> None:
        message = f"message-{idx}"
        response = f"response-{idx}"
        memory_updater.update_memory(user_id, message, response)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(message_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    history = memory_updater.load_user_memory(user_id).get("history", [])
    assert len(history) == message_count

    expected_pairs = {
        (f"message-{idx}", f"response-{idx}")
        for idx in range(message_count)
    }
    actual_pairs = {(item.get("message"), item.get("response")) for item in history}

    assert expected_pairs == actual_pairs

"""Konuşan Tohum masaüstü arayüzünün hafıza ve bağlam panellerini güncellemesini doğrulayan testler."""

import json
import chat_gui


class DummyText:
    def __init__(self):
        self.state = None
        self.content = ""

    def configure(self, state=None):
        if state is not None:
            self.state = state

    def delete(self, start, end):
        self.content = ""

    def insert(self, index, text):
        self.content += text


class DummyLabel:
    def __init__(self):
        self.configured = {}

    def config(self, **kwargs):
        self.configured.update(kwargs)


def test_update_side_panel_reflects_new_context(tmp_path, monkeypatch):
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    memory_file = memory_dir / "user_memory.json"
    memory_file.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(chat_gui, "MEMORY_FILE", str(memory_file))

    gui = chat_gui.ChatGUI.__new__(chat_gui.ChatGUI)
    gui.context_area = DummyText()
    gui.memory_area = DummyText()
    gui.status_text = DummyLabel()

    chat_gui.update_context(chat_gui.USER_ID, "Yeni mesaj", intent="test_intent")
    gui._update_side_panel()

    assert "- Yeni mesaj (test_intent)\n" in gui.context_area.content

    stored_memory = json.loads(memory_file.read_text(encoding="utf-8"))
    assert chat_gui.USER_ID in stored_memory
    assert stored_memory[chat_gui.USER_ID]["context"][0]["message"] == "Yeni mesaj"

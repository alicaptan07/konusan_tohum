import tkinter as tk
from tkinter import scrolledtext
import json
import os

USER_ID = "demo_user"
MEMORY_FILE = "memory/user_memory.json"
MAX_HISTORY = 5  # Bağlamda saklanacak maksimum mesaj sayısı

# -------------------- HAFIZA YÖNETİMİ --------------------
if not os.path.exists("memory"):
    os.makedirs("memory")

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=2, ensure_ascii=False)

def load_user_memory(user_id):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        all_memory = json.load(f)
    return all_memory.get(user_id, {})

def save_memory(user_memory_dict):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        all_memory = json.load(f)
    for uid, mem in user_memory_dict.items():
        all_memory[uid] = mem
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(all_memory, f, indent=2, ensure_ascii=False)

def auto_update_memory(user_id, message, intent=None, entities=None):
    memory_data = load_user_memory(user_id)
    if "history" not in memory_data:
        memory_data["history"] = []
    memory_data["history"].append({
        "message": message,
        "intent": intent,
        "entities": entities
    })
    if len(memory_data["history"]) > 20:
        memory_data["history"] = memory_data["history"][-20:]
    save_memory({user_id: memory_data})

def get_user_memory(user_id):
    return load_user_memory(user_id)

# -------------------- BAĞLAM YÖNETİMİ --------------------
def update_context(user_id, message, intent=None, entities=None):
    memory = load_user_memory(user_id)
    if "context" not in memory:
        memory["context"] = []

    memory["context"].append({
        "message": message,
        "intent": intent,
        "entities": entities
    })

    if len(memory["context"]) > MAX_HISTORY:
        memory["context"] = memory["context"][-MAX_HISTORY:]

    auto_update_memory(user_id, message, intent, entities)
    return memory["context"]

def get_context(user_id):
    memory = load_user_memory(user_id)
    return memory.get("context", [])

def get_context_summary(user_id):
    context = get_context(user_id)
    summary = "\n".join([f"{c['message']} ({c['intent']})" for c in context])
    return summary

# -------------------- BASİT BOT YANIT ÜRETİCİ --------------------
def handle_message(user_id, message):
    # Örnek intent algılama
    if "merhaba" in message.lower():
        intent = "greeting"
        response = "Merhaba! Sana nasıl yardımcı olabilirim?"
    elif "kedi" in message.lower():
        intent = "cats"
        response = "Komik kedi videolarını mı seviyorsun? Harika!"
    else:
        intent = "general"
        response = "Bunu anladım, devam edelim."

    update_context(user_id, message, intent)
    return response

# -------------------- TKINTER ARAYÜZÜ --------------------
class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Konuşan Tohum 🌱")

        # Çerçeveler
        self.left_frame = tk.Frame(root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(root, width=250, bg="#f5f5f5")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Sohbet alanı
        self.chat_area = scrolledtext.ScrolledText(self.left_frame, wrap=tk.WORD, state="disabled", height=25)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Girdi kutusu
        self.entry = tk.Entry(self.left_frame, width=80)
        self.entry.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.send_message)

        # Gönder butonu
        self.send_button = tk.Button(self.left_frame, text="Gönder", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Sağ panel başlıkları
        self.context_label = tk.Label(self.right_frame, text="Bağlam", bg="#f5f5f5", font=("Arial", 10, "bold"))
        self.context_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.context_area = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD, height=8, width=30, state="disabled")
        self.context_area.pack(padx=10, pady=5)

        self.memory_label = tk.Label(self.right_frame, text="Hafıza", bg="#f5f5f5", font=("Arial", 10, "bold"))
        self.memory_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.memory_area = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD, height=8, width=30, state="disabled")
        self.memory_area.pack(padx=10, pady=5)

        self.status_label = tk.Label(self.right_frame, text="Durum", bg="#f5f5f5", font=("Arial", 10, "bold"))
        self.status_label.pack(anchor="w", padx=10, pady=(10, 0))

        self.status_text = tk.Label(self.right_frame, text="", bg="#f5f5f5", justify="left")
        self.status_text.pack(anchor="w", padx=10, pady=5)

    def send_message(self, event=None):
        user_msg = self.entry.get().strip()
        if not user_msg:
            return
        self.entry.delete(0, tk.END)

        # Kullanıcı mesajını ekrana yaz
        self._update_chat("Sen", user_msg)

        # Bot yanıtı
        bot_response = handle_message(USER_ID, user_msg)
        self._update_chat("Tohum", bot_response)

        # Sağ paneli güncelle
        self._update_side_panel()

    def _update_chat(self, speaker, message):
        self.chat_area.configure(state="normal")
        self.chat_area.insert(tk.END, f"{speaker}: {message}\n")
        self.chat_area.configure(state="disabled")
        self.chat_area.yview(tk.END)

    def _update_side_panel(self):
        # Bağlam
        context = get_context(USER_ID)
        self.context_area.configure(state="normal")
        self.context_area.delete(1.0, tk.END)
        for entry in context:
            self.context_area.insert(tk.END, f"- {entry['message']} ({entry['intent']})\n")
        self.context_area.configure(state="disabled")

        # Hafıza
        memory = get_user_memory(USER_ID)
        self.memory_area.configure(state="normal")
        self.memory_area.delete(1.0, tk.END)
        for k, v in memory.items():
            self.memory_area.insert(tk.END, f"{k}: {v}\n")
        self.memory_area.configure(state="disabled")

        # Durum (sade örnek)
        status = "Ruh hali: bilinmiyor\nMod: default"
        self.status_text.config(text=status)

if __name__ == "__main__":
    root = tk.Tk()
    gui = ChatGUI(root)
    root.mainloop()

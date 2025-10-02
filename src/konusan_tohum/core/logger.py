"""Konuşan Tohum günlükleme yardımcı sınıfı, çekirdek akıştaki olayları zaman damgası ve önem seviyesiyle standart biçimde kayda geçirir."""

import datetime

class Logger:
    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().isoformat()
        print(f"[{level}] {timestamp} → {message}")

import datetime

class Logger:
    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().isoformat()
        print(f"[{level}] {timestamp} → {message}")
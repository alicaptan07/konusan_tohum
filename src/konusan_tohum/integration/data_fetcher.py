"""Konuşan Tohum veri toplayıcısı, yerel ve uzak örnek veri kaynaklarına tek noktadan erişim sağlar."""

def fetch(source):
    if source == "local":
        return {"data": "Yerel veri örneği"}
    elif source == "remote":
        return {"data": "Uzaktan veri örneği"}
    else:
        return {"error": "Kaynak tanımlı değil"}

def ping():
    return "OK"

"""Konuşan Tohum veri temizleyicisi, sohbet girdilerini XSS ve basit enjeksiyon risklerine karşı arındırır."""

import re

def sanitize(text):
    # Basit XSS temizliği
    clean = re.sub(r"<.*?>", "", text)
    clean = clean.replace("'", "").replace('"', "")
    return clean

def ping():
    return "OK"

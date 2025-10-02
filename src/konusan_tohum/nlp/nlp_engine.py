"""Konuşan Tohum NLP motoru, metin ön işleme ve temel analiz fonksiyonlarını düzenler."""

import re

def preprocess_text(text):
    """
    Metni temizler: küçük harfe çevirir, noktalama işaretlerini kaldırır, boşlukları sadeleştirir.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize(text):
    """
    Temizlenmiş metni kelimelere ayırır.
    """
    return text.split()

def analyze(text):
    """
    Metni analiz eder: orijinal, temizlenmiş, token listesi ve uzunluk bilgisi döner.
    """
    clean_text = preprocess_text(text)
    tokens = tokenize(clean_text)
    return {
        "original": text,
        "clean": clean_text,
        "tokens": tokens,
        "length": len(tokens)
    }

def ping():
    return "OK"

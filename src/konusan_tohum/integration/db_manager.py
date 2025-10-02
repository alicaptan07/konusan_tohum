"""Konuşan Tohum veritabanı yöneticisi, prototip aşamasındaki anahtar-değer saklama ihtiyaçları için hafif bir arayüz sunar."""

database = {}

def insert(key, value):
    database[key] = value

def query(key):
    return database.get(key, "Kayıt bulunamadı")

def ping():
    return "OK"

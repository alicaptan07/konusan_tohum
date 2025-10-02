"""Konuşan Tohum kimlik doğrulama yöneticisi, temel kullanıcı ve parola eşleşmeleriyle oturum doğruluğunu kontrol eder."""

users = {
    "admin": "1234",
    "guest": "0000"
}

def authenticate(username, password):
    return users.get(username) == password

def ping():
    return "OK"

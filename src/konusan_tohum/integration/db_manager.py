database = {}

def insert(key, value):
    database[key] = value

def query(key):
    return database.get(key, "Kayıt bulunamadı")

def ping():
    return "OK"
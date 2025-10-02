"""Konuşan Tohum izin denetleyicisi, rol bazlı eylem yetkilendirmesini doğrular."""

permissions = {
    "admin": ["read", "write", "delete"],
    "guest": ["read"]
}

def check(user_id, action):
    allowed = permissions.get(user_id, [])
    return action in allowed

def ping():
    return "OK"

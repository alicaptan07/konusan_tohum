# nlp/emotion_tracker.py

_emotions = {}

def set_emotion(user_id, emotion):
    """Kullanıcının ruh halini kaydeder"""
    _emotions[user_id] = emotion

def get_emotion(user_id):
    """Kullanıcının ruh halini döner"""
    return _emotions.get(user_id, None)

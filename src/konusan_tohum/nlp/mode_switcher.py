# nlp/mode_switcher.py

_modes = {}

def set_mode(user_id, mode):
    """Kullanıcı için mod kaydet"""
    _modes[user_id] = mode

def get_mode(user_id):
    """Kullanıcının mevcut modunu döner"""
    return _modes.get(user_id, "default")

def detect_mode(user_id, intent):
    """
    Kullanıcı niyetine göre modu belirle.
    """
    if intent in ["tell_story", "story_mode"]:
        mode = "story"
    elif intent in ["ask_help", "help_mode"]:
        mode = "help"
    elif intent in ["ask_suggestion", "suggestion_mode"]:
        mode = "suggestion"
    elif intent in ["privacy_query", "privacy_mode"]:
        mode = "privacy"
    else:
        mode = "chat"

    set_mode(user_id, mode)
    return mode

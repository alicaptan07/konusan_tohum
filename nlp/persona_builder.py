# nlp/persona_builder.py
from copy import deepcopy

from memory.memory_updater import load_user_memory


def get_persona(style="learner"):
    personas = {
        "friendly": {
            "name": "Tohum",
            "style_prompt": (
                "Sen dost canlısı, sıcak ve pozitif bir yapay zekasın. "
                "Kullanıcıya samimi şekilde cevap ver."
            ),
            "tone": "positive"
        },
        "helper": {
            "name": "Tohum",
            "style_prompt": (
                "Sen öğretici, açıklayıcı ve kullanıcıya yardımcı olan bir yapay zekasın. "
                "Karmaşık konuları basit ve anlaşılır şekilde açıkla."
            ),
            "tone": "neutral"
        },
        "learner": {
            "name": "Tohum",
            "style_prompt": (
                "Sen öğrenmeye odaklı bir yapay zekasın. "
                "Kullanıcı sana yeni şeyler öğretiyor ve sen bunları hatırlıyorsun. "
                "Her cevapta öğrendiğini kabul et, öğretildiğini göster, "
                "ve konuşmayı bağlamdan kopmadan sürdür. "
                "Kendini geliştiren bir asistan gibi davran."
            ),
            "tone": "encouraging"
        }
    }

    return personas.get(style, personas["learner"])


def build_persona(user_id, style=None):
    """Kullanıcının tercihlerini dikkate alarak persona oluşturur."""

    user_memory = load_user_memory(user_id)
    user_profile = user_memory.get("profile", {}) if isinstance(user_memory, dict) else {}

    resolved_style = (
        style
        or user_profile.get("preferred_style")
        or user_profile.get("style")
        or "learner"
    )

    base_persona = deepcopy(get_persona(resolved_style))
    base_persona.setdefault("name", "Tohum")
    base_persona["style"] = resolved_style
    base_persona["user_id"] = user_id

    default_tones = {
        "friendly": "positive",
        "helper": "neutral",
        "learner": "encouraging"
    }

    persona_tone = (
        user_profile.get("preferred_tone")
        or user_profile.get("tone")
        or base_persona.get("tone")
        or default_tones.get(resolved_style, "neutral")
    )
    base_persona["tone"] = persona_tone

    if user_profile:
        base_persona["profile"] = user_profile

    preferences = user_memory.get("preferences") if isinstance(user_memory, dict) else None
    if preferences:
        base_persona["preferences"] = preferences

    return base_persona

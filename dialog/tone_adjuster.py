# dialog/tone_adjuster.py
from nlp.emotion_tracker import get_emotion

class ToneAdjuster:
    def __init__(self):
        pass

    def adjust(self, user_id, text):
        emotion = get_emotion(user_id)
        if not emotion:
            return text

        if emotion == "pozitif":
            return text + " 😊"
        elif emotion == "negatif":
            return text + " 💭"
        return text

# Global örnek
tone_adjuster = ToneAdjuster()

def adjust_tone(user_id, text):
    return tone_adjuster.adjust(user_id, text)

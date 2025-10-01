# dialog/tone_adjuster.py


class ToneAdjuster:
    """Metni belirtilen tona göre ayarlayan yardımcı sınıf."""

    TONE_SUFFIXES = {
        "positive": " 😊",
        "encouraging": " 💪",
        "neutral": "",
        "empathetic": " 🤝",
        "negative": " 💭"
    }

    def adjust(self, text, tone):
        if not text:
            return ""

        if not tone:
            return text

        suffix = self.TONE_SUFFIXES.get(tone.lower())
        if suffix is None:
            return text

        return f"{text}{suffix}"


# Global örnek
tone_adjuster = ToneAdjuster()


def adjust(text, tone):
    """Kısa yol fonksiyon."""

    return tone_adjuster.adjust(text, tone)

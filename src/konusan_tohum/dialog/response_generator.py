# dialog/response_generator.py

try:
    from transformers import pipeline
except ImportError:  # pragma: no cover - çevrimdışı ortamlara uyum
    pipeline = None

from konusan_tohum.core.config_manager import ConfigManager

_GENERATOR = None


class _FallbackGenerator:
    """Dış bağımlılık olmadığında kullanılan basit üretici."""

    def __call__(self, prompt, **kwargs):
        return [{"generated_text": prompt}]


def _get_generator():
    """Modeli tek seferde oluşturup önbelleğe al."""
    global _GENERATOR
    if _GENERATOR is None:
        config = ConfigManager()
        model_name = config.get("models.offline", "gpt2")
        if pipeline is None:
            _GENERATOR = _FallbackGenerator()
        else:
            _GENERATOR = pipeline("text-generation", model=model_name)
    return _GENERATOR


def generate_response(message: str) -> str:
    """
    Kullanıcıdan gelen mesajı alır ve uygun bir yanıt üretir.
    :param message: Kullanıcı mesajı
    :return: Yapay zeka tarafından üretilen yanıt
    """
    try:
        generator = _get_generator()
        response = generator(
            message,
            max_length=100,
            num_return_sequences=1,
            do_sample=True,
            top_k=50,
            top_p=0.95
        )
        return response[0]["generated_text"]
    except Exception as e:
        return f"[Hata] Yanıt üretilemedi: {e}"


def generate(intent, entities, context, user_id=None):
    """`generate_response` çağrısı için geriye dönük uyumlu sarmalayıcı."""

    if context:
        latest_message = context[-1].get("message", "")
    else:
        latest_message = intent or ""

    return generate_response(latest_message)


if __name__ == "__main__":
    # Test amaçlı
    test_input = "Merhaba, sen kimsin?"
    print("Kullanıcı:", test_input)
    print("Tohum AI:", generate_response(test_input))

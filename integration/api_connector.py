import openai
from core.config_manager import load_config
from dialog.response_generator import generate_response

class AIConnector:
    def __init__(self):
        config = load_config()
        self.provider = config["api"]["provider"]
        self.keys = config["api_keys"]
        self.models = config["models"]

    def chat(self, message, user_memory="", context=""):
        try:
            if self.provider == "openai":
                openai.api_key = self.keys["openai"]
                messages = [
                    {"role":"system", "content":"You are Konuşan Tohum AI."},
                    {"role":"system", "content":f"User memory: {user_memory}"},
                    {"role":"system", "content":f"Context: {context}"},
                    {"role":"user", "content":message}
                ]
                response = openai.ChatCompletion.create(
                    model=self.models["online"],
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300
                )
                return response.choices[0].message.content

            else:
                # Offline veya başka provider fallback
                return generate_response(message, intent=None, entities=None, context=context)
        except Exception as e:
            return f"⚠️ API hatası: {str(e)}"

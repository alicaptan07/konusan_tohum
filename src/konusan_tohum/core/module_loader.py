import importlib
import logging

class ModuleLoader:
    def __init__(self, module_names):
        self.module_names = module_names
        self.modules = {}
        self.logger = logging.getLogger("ModuleLoader")

    def _ensure_generation_interface(self, name, target):
        has_generate = hasattr(target, "generate")
        has_generate_response = hasattr(target, "generate_response")

        if has_generate and not has_generate_response:
            setattr(target, "generate_response", getattr(target, "generate"))
            self.logger.debug(
                "Modül %s için 'generate' fonksiyonu 'generate_response' olarak aliaslandı.",
                name,
            )
        elif has_generate_response and not has_generate:
            setattr(target, "generate", getattr(target, "generate_response"))
            self.logger.debug(
                "Modül %s için 'generate_response' fonksiyonu 'generate' olarak aliaslandı.",
                name,
            )
        elif not has_generate and not has_generate_response:
            message = (
                f"{name} modülünde 'generate' ve 'generate_response' fonksiyonları tanımlı değil."
            )
            self.logger.error(message)
            raise AttributeError(message)

    def load_all(self):
        for name in self.module_names:
            try:
                module = importlib.import_module(name)
                if hasattr(module, "initialize"):
                    target = module.initialize()
                else:
                    target = module

                self._ensure_generation_interface(name, target)

                self.modules[name] = target
                self.logger.info(f"Modül yüklendi: {name}")
            except Exception as e:
                self.logger.error(f"Modül yüklenemedi: {name} → {e}")
                raise

    def get_module(self, name):
        return self.modules.get(name, None)

    def get_all_modules(self):
        return self.modules
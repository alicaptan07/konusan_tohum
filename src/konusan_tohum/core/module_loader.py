import importlib
import logging

class ModuleLoader:
    def __init__(self, module_names):
        self.module_names = module_names
        self.modules = {}
        self.logger = logging.getLogger("ModuleLoader")

    def load_all(self):
        for name in self.module_names:
            try:
                module = importlib.import_module(name)
                if hasattr(module, "initialize"):
                    self.modules[name] = module.initialize()
                else:
                    self.modules[name] = module
                self.logger.info(f"Modül yüklendi: {name}")
            except Exception as e:
                self.logger.error(f"Modül yüklenemedi: {name} → {e}")

    def get_module(self, name):
        return self.modules.get(name, None)

    def get_all_modules(self):
        return self.modules
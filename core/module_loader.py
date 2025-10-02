import importlib
import logging


class ModuleLoadError(ImportError):
    """Raised when a configured module cannot be imported."""

    def __init__(self, module_name, reason):
        message = f"Failed to load module '{module_name}': {reason}"
        super().__init__(message)
        self.module_name = module_name
        self.reason = reason

class ModuleLoader:
    def __init__(self, module_names):
        self.module_names = module_names
        self.modules = {}
        self.logger = logging.getLogger("ModuleLoader")

    def load_all(self):
        for name in self.module_names:
            if not isinstance(name, str) or not name.strip():
                raise ModuleLoadError(name, "module path must be a non-empty string")

            try:
                module = importlib.import_module(name)
                if hasattr(module, "initialize"):
                    self.modules[name] = module.initialize()
                else:
                    self.modules[name] = module
                self.logger.info(f"Modül yüklendi: {name}")
            except Exception as e:
                self.logger.error(f"Modül yüklenemedi: {name} → {e}")
                raise ModuleLoadError(name, str(e)) from e

    def get_module(self, name):
        return self.modules.get(name, None)

    def get_all_modules(self):
        return self.modules
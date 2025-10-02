from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


logger = logging.getLogger("ModuleLoader")


@dataclass
class ModuleImportError(Exception):
    module_name: str
    original: Exception

    def __str__(self) -> str:  # pragma: no cover - kolay okunurluk
        return f"{self.module_name} modülü yüklenemedi: {self.original}"


class ModuleLoadError(Exception):
    def __init__(self, errors: Iterable[ModuleImportError], loaded_modules: Optional[Dict[str, object]] = None):
        self.errors: List[ModuleImportError] = list(errors)
        self.loaded_modules = loaded_modules or {}
        message = "\n".join(str(error) for error in self.errors)
        super().__init__(message)


class ModuleLoader:
    def __init__(self, module_names):
        self.module_names = module_names
        self.modules: Dict[str, object] = {}

    def load_all(self):
        errors: List[ModuleImportError] = []
        for name in self.module_names:
            try:
                module = importlib.import_module(name)
                instance = module.initialize() if hasattr(module, "initialize") else module
                self.modules[name] = instance
                logger.info("Modül yüklendi: %s", name)
            except Exception as exc:
                error = ModuleImportError(name, exc)
                errors.append(error)
                logger.error(str(error))

        if errors:
            raise ModuleLoadError(errors, self.modules)

    def get_module(self, name):
        return self.modules.get(name, None)

    def get_all_modules(self):
        return self.modules
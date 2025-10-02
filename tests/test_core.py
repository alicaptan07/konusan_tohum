import sys
import types

import pytest

from konusan_tohum.core.config_manager import ConfigManager
from konusan_tohum.core.logger import Logger
from konusan_tohum.core.module_loader import ModuleLoader

def test_logger():
    logger = Logger()
    logger.log("Test mesajı", level="INFO")
    print("✅ Logger test edildi.")

def test_config_manager():
    config = ConfigManager()
    settings = config.load_config()
    assert isinstance(settings, dict)
    print("✅ ConfigManager test edildi.")


def test_module_loader_aliases_generate_to_generate_response():
    module_name = "tests.dummy.generate_only"
    module = types.ModuleType(module_name)

    def generate(*args, **kwargs):
        return "generated"

    module.generate = generate
    sys.modules[module_name] = module

    try:
        loader = ModuleLoader([module_name])
        loader.load_all()
        loaded = loader.get_module(module_name)
        assert loaded.generate is loaded.generate_response
        assert loaded.generate("test") == "generated"
    finally:
        sys.modules.pop(module_name, None)


def test_module_loader_aliases_generate_response_to_generate():
    module_name = "tests.dummy.response_only"
    module = types.ModuleType(module_name)

    class Generator:
        def generate_response(self, *args, **kwargs):
            return "response"

    def initialize():
        return Generator()

    module.initialize = initialize
    sys.modules[module_name] = module

    try:
        loader = ModuleLoader([module_name])
        loader.load_all()
        loaded = loader.get_module(module_name)
        assert hasattr(loaded, "generate")
        assert loaded.generate("test") == "response"
        assert loaded.generate.__func__ is loaded.generate_response.__func__
    finally:
        sys.modules.pop(module_name, None)


def test_module_loader_raises_when_generation_missing():
    module_name = "tests.dummy.missing_generation"
    module = types.ModuleType(module_name)
    sys.modules[module_name] = module

    try:
        loader = ModuleLoader([module_name])
        with pytest.raises(AttributeError):
            loader.load_all()
    finally:
        sys.modules.pop(module_name, None)

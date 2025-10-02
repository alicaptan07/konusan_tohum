from core.logger import Logger
import pytest

from core.config_manager import ConfigManager, InvalidActiveModulesError
from core.module_loader import ModuleLoader, ModuleLoadError

def test_logger():
    logger = Logger()
    logger.log("Test mesajı", level="INFO")
    print("✅ Logger test edildi.")

def test_config_manager():
    config = ConfigManager()
    settings = config.load_config()
    assert isinstance(settings, dict)
    print("✅ ConfigManager test edildi.")


def test_get_active_modules_rejects_invalid_type(monkeypatch):
    monkeypatch.setattr(
        ConfigManager,
        "_load_yaml",
        lambda self: {"modules": {"active": "dialog.response_generator"}},
    )

    manager = ConfigManager()
    with pytest.raises(InvalidActiveModulesError) as exc:
        manager.get_active_modules()

    assert "modules.active" in str(exc.value)


def test_get_active_modules_rejects_invalid_entries(monkeypatch):
    monkeypatch.setattr(
        ConfigManager,
        "_load_yaml",
        lambda self: {"modules": {"active": ["dialog.response_generator", ""]}},
    )

    manager = ConfigManager()
    with pytest.raises(InvalidActiveModulesError) as exc:
        manager.get_active_modules()

    assert "module import paths" in str(exc.value)


def test_module_loader_raises_for_invalid_entries():
    loader = ModuleLoader(["", "dialog.response_generator"])

    with pytest.raises(ModuleLoadError) as exc:
        loader.load_all()

    assert "module path" in str(exc.value)


def test_module_loader_raises_when_import_fails(monkeypatch):
    loader = ModuleLoader(["nonexistent.module"])

    def fake_import(name):
        raise ImportError("boom")

    monkeypatch.setattr("core.module_loader.importlib.import_module", fake_import)

    with pytest.raises(ModuleLoadError) as exc:
        loader.load_all()

    assert "nonexistent.module" in str(exc.value)
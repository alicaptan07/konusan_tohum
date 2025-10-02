import textwrap

import pytest

from core.config_manager import (
    ConfigManager,
    ConfigValidationError,
    ModuleValidationError,
)
from core.module_loader import ModuleLoadError, ModuleLoader


def _write_config(tmp_path, body: str):
    path = tmp_path / "settings.yaml"
    path.write_text(textwrap.dedent(body), encoding="utf-8")
    return path


def test_missing_required_field_raises_validation_error(tmp_path):
    config_body = textwrap.dedent(
        """
        api_keys:
          openai: ""
          openrouter: ""
          huggingface: ""
        """
    )
    config_path = _write_config(tmp_path, config_body)

    with pytest.raises(ConfigValidationError) as exc_info:
        ConfigManager(str(config_path))

    assert "'api' alanı zorunlu" in str(exc_info.value)


def test_invalid_modules_raise_module_validation_error(tmp_path):
    config_body = textwrap.dedent(
        """
        api:
          provider: "offline"

        api_keys:
          openai: ""
          openrouter: ""
          huggingface: ""

        models:
          online: "a"
          openrouter: "b"
          offline: "c"

        memory:
          path: "memory/data"

        context:
          max_history: 3

        gui:
          title: "Konuşan Tohum"
          theme: "light"

        modules:
          active:
            - tests.nonexistent_module
            - "  "
        """
    )
    config_path = _write_config(tmp_path, config_body)
    manager = ConfigManager(str(config_path))

    with pytest.raises(ModuleValidationError) as exc_info:
        manager.get_active_modules()

    message = str(exc_info.value)
    assert "'modules.active[1]'" in message
    assert "tests.nonexistent_module" in message


def test_module_loader_reports_failed_imports():
    loader = ModuleLoader(["math", "tests.missing_module_for_loader"])

    with pytest.raises(ModuleLoadError) as exc_info:
        loader.load_all()

    error = exc_info.value
    assert "tests.missing_module_for_loader" in str(error)
    assert "math" in loader.get_all_modules()

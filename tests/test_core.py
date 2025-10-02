"""Çekirdek bileşenler için birim testleri."""

from __future__ import annotations

from pathlib import Path

import pytest

from konusan_tohum.core.config_manager import ConfigManager
from konusan_tohum.core.logger import Logger


def test_logger():
    logger = Logger()
    logger.log("Test mesajı", level="INFO")
    print("✅ Logger test edildi.")


def test_config_manager():
    config = ConfigManager()
    settings = config.load_config()
    assert isinstance(settings, dict)
    print("✅ ConfigManager test edildi.")


def test_config_manager_invalid_yaml(tmp_path: Path):
    invalid_settings = tmp_path / "settings.yaml"
    invalid_settings.write_text("api: [unclosed", encoding="utf-8")

    with pytest.raises(ValueError):
        ConfigManager(config_path=invalid_settings)

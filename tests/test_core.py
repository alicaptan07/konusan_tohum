"""Konuşan Tohum çekirdek bileşenlerinin günlükleme ve yapılandırma davranışını doğrulayan birim testleri."""

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

from core.logger import Logger
from core.config_manager import ConfigManager

def test_logger():
    logger = Logger()
    logger.log("Test mesajı", level="INFO")
    print("✅ Logger test edildi.")

def test_config_manager():
    config = ConfigManager()
    settings = config.load_config()
    assert isinstance(settings, dict)
    print("✅ ConfigManager test edildi.")
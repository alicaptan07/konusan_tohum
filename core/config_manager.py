# core/config_manager.py
import yaml

class ConfigManager:
    def __init__(self, config_path="settings/settings.yaml"):
        self.config_path = config_path
        self.config = self._load_yaml()

    def _load_yaml(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[ConfigManager] YAML yüklenemedi: {e}")
            return {}

    def load_config(self):
        """Yüklü yapılandırma sözlüğünü döndür."""
        return self.config

    def get(self, key, default=None):
        keys = key.split(".")
        data = self.config
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return default
        return data

    def get_active_modules(self):
        """Yapılandırmadan etkin modül listesini döndür."""
        modules_section = self.config.get("modules", {}) if isinstance(self.config, dict) else {}
        active_modules = modules_section.get("active", []) if isinstance(modules_section, dict) else []
        return active_modules if isinstance(active_modules, list) else []


def load_config():
    """Yeni bir ConfigManager örneğinden yapılandırmayı döndür."""
    return ConfigManager().load_config()

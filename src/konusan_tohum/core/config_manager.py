# core/config_manager.py
from pathlib import Path

try:
    from yaml import YAMLError
except ImportError:  # pragma: no cover - çevrimdışı ortamlara uyum
    YAMLError = Exception

try:
    import yaml
except ImportError:  # pragma: no cover - çevrimdışı ortamlara uyum
    yaml = None


_DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent / "settings" / "settings.yaml"
)


class ConfigManager:
    def __init__(self, config_path=None):
        self.config_path = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH
        self.config = self._load_yaml()
        self._validate_config()

    def _load_yaml(self):
        if yaml is None:
            return {}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except FileNotFoundError as exc:  # pragma: no cover - gerçek dosya eksikliği
            raise FileNotFoundError(
                f"Yapılandırma dosyası bulunamadı: {self.config_path}"
            ) from exc
        except YAMLError as exc:
            raise ValueError("Yapılandırma dosyası geçerli bir YAML değil.") from exc
        except OSError as exc:  # pragma: no cover - IO hataları
            raise ValueError(f"Yapılandırma dosyası okunamadı: {exc}") from exc

        return data or {}

    def _validate_config(self):
        if not isinstance(self.config, dict):
            raise ValueError("Yapılandırma sözlük formatında olmalıdır.")

    def load_config(self):
        """Return the cached configuration dictionary."""
        return self.config or {}

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
        """Return the list of active modules from the configuration."""
        modules = self.get("modules.active", default=None)
        if isinstance(modules, list):
            return modules
        return []


def load_config():
    """Backward-compatible helper to load configuration settings."""
    return ConfigManager().load_config()

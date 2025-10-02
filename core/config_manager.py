# core/config_manager.py
try:
    import yaml
except ImportError:  # pragma: no cover - çevrimdışı ortamlara uyum
    yaml = None


class ConfigurationError(Exception):
    """Base exception for configuration issues."""


class InvalidActiveModulesError(ConfigurationError):
    """Raised when modules.active is missing or malformed."""

    def __init__(self, invalid_value):
        message = (
            "modules.active must be a list of module import paths, "
            f"received: {invalid_value!r}"
        )
        super().__init__(message)
        self.invalid_value = invalid_value

class ConfigManager:
    def __init__(self, config_path="settings/settings.yaml"):
        self.config_path = config_path
        self.config = self._load_yaml()

    def _load_yaml(self):
        try:
            if yaml is None:
                return {}
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[ConfigManager] YAML yüklenemedi: {e}")
            return {}

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
        if modules is None:
            return []

        if not isinstance(modules, list):
            raise InvalidActiveModulesError(modules)

        invalid_entries = [
            item for item in modules if not isinstance(item, str) or not item.strip()
        ]
        if invalid_entries:
            raise InvalidActiveModulesError(invalid_entries)

        return modules


def load_config():
    """Backward-compatible helper to load configuration settings."""
    return ConfigManager().load_config()

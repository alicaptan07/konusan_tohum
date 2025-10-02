"""Utilities for loading and validating Konuşan Tohum configuration.

The :class:`ConfigManager` is responsible for reading the main
``settings/settings.yaml`` file once, exposing read-only helpers for the rest of
the application.  The loader defends against missing optional dependencies
(``pyyaml``) and malformed files so that continuous integration jobs can
exercise the codebase without additional setup.  Modules consume the manager via
``ConfigManager.get`` to access feature flags (for example ``modules.active``),
API credentials, and model selection knobs such as ``models.offline`` or
``models.openai``.

Downstream components (connectors, dialog engines and diagnostics) rely on the
configuration data to decide whether to use online services, offline fallbacks
or additional logging.  When new configuration keys are introduced they should
be parsed through this module so that validation and default handling remain
centralised.
"""

# core/config_manager.py
try:
    import yaml
except ImportError:  # pragma: no cover - çevrimdışı ortamlara uyum
    yaml = None

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
        if isinstance(modules, list):
            return modules
        return []


def load_config():
    """Backward-compatible helper to load configuration settings."""
    return ConfigManager().load_config()

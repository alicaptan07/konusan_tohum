# core/config_manager.py
from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, MutableMapping, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover - çevrimdışı ortamlara uyum
    yaml = None


class ConfigError(Exception):
    """Base sınıf."""


class ConfigLoadError(ConfigError):
    """YAML dosyası okunamazsa fırlatılır."""


@dataclass
class ConfigValidationError(ConfigError):
    errors: List[str]

    def __str__(self) -> str:  # pragma: no cover - küçük yardımcı
        joined = "\n - ".join(self.errors)
        return f"Ayar dosyası doğrulanamadı:\n - {joined}" if joined else "Ayar dosyası doğrulanamadı."


@dataclass
class ModuleValidationError(ConfigError):
    errors: List[str]

    def __str__(self) -> str:  # pragma: no cover - küçük yardımcı
        joined = "\n - ".join(self.errors)
        return f"Modül yapılandırması hatalı:\n - {joined}" if joined else "Modül yapılandırması hatalı."


_CONFIG_SCHEMA: Dict[str, Any] = {
    "api": {
        "required": True,
        "type": dict,
        "schema": {"provider": {"type": str, "required": True}},
    },
    "api_keys": {
        "required": True,
        "type": dict,
        "schema": {
            "openai": {"type": str, "required": True},
            "openrouter": {"type": str, "required": True},
            "huggingface": {"type": str, "required": True},
        },
    },
    "models": {
        "required": True,
        "type": dict,
        "schema": {
            "online": {"type": str, "required": True},
            "openrouter": {"type": str, "required": True},
            "offline": {"type": str, "required": True},
        },
    },
    "memory": {
        "required": True,
        "type": dict,
        "schema": {"path": {"type": str, "required": True}},
    },
    "context": {
        "required": True,
        "type": dict,
        "schema": {"max_history": {"type": int, "required": True}},
    },
    "gui": {
        "required": True,
        "type": dict,
        "schema": {
            "title": {"type": str, "required": True},
            "theme": {"type": str, "required": True},
        },
    },
    "modules": {
        "required": False,
        "type": dict,
        "schema": {
            "active": {
                "type": list,
                "required": False,
                "item_type": str,
            }
        },
    },
}


def _strip_inline_comment(line: str) -> str:
    result: List[str] = []
    in_single = False
    in_double = False
    for char in line:
        if char == "'" and not in_double:
            in_single = not in_single
            result.append(char)
            continue
        if char == '"' and not in_single:
            in_double = not in_double
            result.append(char)
            continue
        if char == "#" and not in_single and not in_double:
            break
        result.append(char)
    return "".join(result).rstrip()


def _parse_scalar(value: str) -> Any:
    if value in ("[]", "{}"):
        return [] if value == "[]" else {}
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.isdigit():
        try:
            return int(value)
        except ValueError:
            pass
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    return value


def _peek_next(lines: List[str], start: int) -> Optional[Tuple[int, str]]:
    for index in range(start, len(lines)):
        candidate = _strip_inline_comment(lines[index])
        if candidate.strip():
            indent = len(lines[index]) - len(lines[index].lstrip(" "))
            return indent, candidate.lstrip()
    return None


def _simple_yaml_load(text: str) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    stack: List[Tuple[int, Any]] = [(-1, root)]
    lines = text.splitlines()

    for idx, raw_line in enumerate(lines):
        processed = _strip_inline_comment(raw_line)
        if not processed.strip():
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()

        container = stack[-1][1]
        line = processed.lstrip()

        if line.startswith("- "):
            if not isinstance(container, list):
                raise ConfigLoadError("Liste öğesi beklenmeyen bir konumda bulundu.")
            value_part = line[2:].strip()
            container.append(_parse_scalar(value_part))
            continue

        key, sep, remainder = line.partition(":")
        if not sep:
            raise ConfigLoadError(f"Geçersiz satır: {line}")
        key = key.strip()
        value = remainder.strip()

        if not value:
            next_info = _peek_next(lines, idx + 1)
            if next_info and next_info[0] > indent and next_info[1].startswith("- "):
                new_container: Any = []
            else:
                new_container = {}
            if isinstance(container, dict):
                container[key] = new_container
            else:
                raise ConfigLoadError("Liste öğesine doğrudan anahtar atanamaz.")
            stack.append((indent, new_container))
        else:
            parsed = _parse_scalar(value)
            if isinstance(container, dict):
                container[key] = parsed
            else:
                raise ConfigLoadError("Liste öğesine doğrudan anahtar atanamaz.")

    return root


def _validate_schema(schema: Dict[str, Any], data: MutableMapping[str, Any], path: str = "") -> List[str]:
    errors: List[str] = []

    for field, rules in schema.items():
        field_path = f"{path}.{field}" if path else field
        required = rules.get("required", False)
        if field not in data or data[field] is None:
            if required:
                errors.append(f"'{field_path}' alanı zorunlu.")
            continue

        value = data[field]
        expected_type = rules.get("type")
        if expected_type and not isinstance(value, expected_type):
            errors.append(
                f"'{field_path}' alanı {expected_type.__name__} olmalı ancak {type(value).__name__} bulundu."
            )
            continue

        nested_schema = rules.get("schema")
        if nested_schema and isinstance(value, MutableMapping):
            errors.extend(_validate_schema(nested_schema, value, field_path))

        item_type = rules.get("item_type")
        if item_type and isinstance(value, Iterable):
            for index, item in enumerate(value):
                if not isinstance(item, item_type):
                    errors.append(
                        f"'{field_path}[{index}]' {item_type.__name__} olmalı ancak {type(item).__name__} bulundu."
                    )

    return errors


class ConfigManager:
    def __init__(self, config_path="settings/settings.yaml"):
        self.config_path = config_path
        self.config = self._load_yaml()

    def _load_yaml(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                raw_content = f.read()
            if yaml is None:
                loaded = _simple_yaml_load(raw_content)
            else:
                loaded = yaml.safe_load(raw_content) or {}
        except FileNotFoundError as exc:  # pragma: no cover - temel IO
            raise ConfigLoadError(f"Yapılandırma dosyası bulunamadı: {self.config_path}") from exc
        except Exception as exc:  # pragma: no cover - yaml parse hataları
            raise ConfigLoadError(f"Yapılandırma dosyası okunamadı: {exc}") from exc

        if not isinstance(loaded, dict):
            raise ConfigValidationError(["YAML içeriği geçerli bir sözlük değil."])

        errors = _validate_schema(_CONFIG_SCHEMA, loaded)
        if errors:
            raise ConfigValidationError(errors)

        return loaded

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
        modules = self.get("modules.active", default=[])
        if modules is None:
            return []
        if not isinstance(modules, list):
            raise ModuleValidationError(["'modules.active' bir liste olmalıdır."])

        errors: List[str] = []
        validated: List[str] = []
        for index, module_name in enumerate(modules):
            if not isinstance(module_name, str) or not module_name.strip():
                errors.append(
                    f"'modules.active[{index}]' boş olmayan bir modül yolu olmalıdır."
                )
                continue
            try:
                importlib.import_module(module_name)
            except Exception as exc:
                errors.append(f"'{module_name}' modülü yüklenemedi: {exc}")
            else:
                validated.append(module_name)

        if errors:
            raise ModuleValidationError(errors)

        return validated


def load_config():
    """Backward-compatible helper to load configuration settings."""
    return ConfigManager().load_config()

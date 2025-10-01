"""Minimal YAML helpers tailored to the project's fixture files."""

from __future__ import annotations

from typing import Dict, List


class SimpleYAMLError(ValueError):
    """Raised when the ad-hoc YAML parser encounters an unexpected format."""


def parse_mapping_with_examples(
    content: str, *, root_key: str
) -> Dict[str, Dict[str, List[str]]]:
    """Parse a very small subset of YAML used by the NLP fixtures.

    The supported structure looks like::

        root_key:
          item_name:
            description: Some text
            examples:
              - foo
              - bar

    Parameters
    ----------
    content:
        Raw YAML text.
    root_key:
        Name of the expected top-level mapping.
    """

    data: Dict[str, Dict[str, List[str]]] = {}
    current_item: str | None = None
    current_list_key: str | None = None
    seen_root = False

    for raw_line in content.splitlines():
        if not raw_line.strip():
            continue

        indent = len(raw_line) - len(raw_line.lstrip())
        line = raw_line.strip()

        if indent == 0 and line.endswith(":"):
            key = line[:-1]
            if key != root_key:
                raise SimpleYAMLError(f"Beklenmeyen üst seviye anahtar: {key}")
            seen_root = True
            continue

        if indent == 2 and line.endswith(":"):
            if not seen_root:
                raise SimpleYAMLError("Kök anahtar tanımlanmadan öğe bulundu")
            current_item = line[:-1]
            data[current_item] = {"description": "", "examples": []}
            current_list_key = None
            continue

        if indent == 4 and ":" in line:
            if current_item is None:
                raise SimpleYAMLError("Özellik eklenmeden önce öğe adı gerekli")

            key, value = [part.strip() for part in line.split(":", 1)]
            if value:
                data[current_item][key] = value
                current_list_key = None
            else:
                current_list_key = key
            continue

        if indent == 6 and line.startswith("- "):
            if current_item is None or current_list_key is None:
                raise SimpleYAMLError("Liste öğesi eklemek için aktif anahtar gerekli")
            data[current_item].setdefault(current_list_key, []).append(line[2:].strip())
            continue

        raise SimpleYAMLError(f"Satır çözümlenemedi: {raw_line}")

    return data

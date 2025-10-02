"""Konuşan Tohum varlık yükleyicisi, YAML tabanlı tanımları okuyarak çıkarım motoruna besler."""

from __future__ import annotations

import os
from typing import Dict, List

from .yaml_utils import parse_mapping_with_examples


def load_entities(path: str | None = None) -> Dict[str, Dict[str, List[str]]]:
    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "data", "entities.yaml")

    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ entities.yaml bulunamadı: {path}")

    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

    return parse_mapping_with_examples(content, root_key="entities")

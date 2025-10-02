"""Deterministic data fetch helpers used by optional integration modules.

The production system is expected to source records from local caches or remote
services depending on configuration.  During automated testing we avoid making
network calls and instead rely on predictable stub payloads.  Integrators can
wire this module through ``modules.active`` entries in ``settings.yaml`` and
swap the simple functions with richer implementations while keeping the public
API intact.
"""

from __future__ import annotations

from typing import Dict

_LOCAL_SAMPLE: Dict[str, str] = {"data": "Yerel veri örneği"}
_REMOTE_SAMPLE: Dict[str, str] = {"data": "Uzaktan veri örneği"}


def fetch(source: str) -> Dict[str, str]:
    """Return canned dataset samples for the requested source."""

    if source == "local":
        return dict(_LOCAL_SAMPLE)
    if source == "remote":
        return dict(_REMOTE_SAMPLE)
    return {"error": "Kaynak tanımlı değil"}


def ping() -> str:
    """Expose a lightweight health check used by diagnostics."""

    return "OK"

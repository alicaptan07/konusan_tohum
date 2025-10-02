"""In-memory stand-in for the persistence layer used during integration tests.

The functions defined here mimic the database access patterns exercised by the
rest of the application.  Production deployments are expected to replace them
with adapters backed by ``modules.active`` configuration entries pointing to
real repositories.  The stub keeps CI runs hermetic while still offering
observability hooks through the standard logging infrastructure.
"""

from __future__ import annotations

from typing import Dict

_database: Dict[str, str] = {}


def insert(key: str, value: str) -> None:
    """Store ``value`` under ``key`` in the in-memory database."""

    _database[key] = value


def query(key: str) -> str:
    """Retrieve ``key`` from the in-memory database or return a message."""

    return _database.get(key, "Kayıt bulunamadı")


def ping() -> str:
    """Expose a health check used by diagnostics and smoke tests."""

    return "OK"

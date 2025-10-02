"""Application logging utilities."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Final


LOG_DIRECTORY: Final[Path] = Path("logs")
LOG_FILE: Final[Path] = LOG_DIRECTORY / "application.log"
LOG_FORMAT: Final[str] = "[%(levelname)s] %(asctime)s → %(message)s"
DATE_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%S"


class Logger:
    """Simple wrapper around Python's :mod:`logging` package.

    The logger writes both INFO and ERROR level messages to a file located in the
    runtime generated ``logs/`` directory while mirroring the output to the
    console.
    """

    def __init__(self, name: str = "konusan_tohum") -> None:
        self._logger = logging.getLogger(name)
        self._ensure_configured()

    def _ensure_configured(self) -> None:
        """Configure the underlying logger once."""

        if self._logger.handlers:
            return

        LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

        self._logger.setLevel(logging.INFO)

        formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self._logger.addHandler(stream_handler)

        self._logger.propagate = False

    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message at the requested severity level."""

        normalized_level = level.upper()
        if normalized_level == "ERROR":
            self._logger.error(message)
        else:
            self._logger.info(message)

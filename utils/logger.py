"""Central logging configuration for console and file output."""

from __future__ import annotations

import logging
from pathlib import Path

_DEFAULT_LOG_PATH = Path(__file__).resolve().parents[1] / "logs" / "repair_center_ai.log"
_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def get_logger(name: str, log_file: str | Path | None = None) -> logging.Logger:
    """Return a logger with timestamped console and file handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    target = Path(log_file) if log_file is not None else _DEFAULT_LOG_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(_LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(target, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger

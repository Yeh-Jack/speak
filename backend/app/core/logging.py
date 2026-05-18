"""Centralized logging configuration for the application."""

import logging
import logging.handlers
import os
import sys
from enum import Enum


class LogLevel(str, Enum):
    """Log level enumeration matching standard logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEBUG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"


def get_log_level(env_value: str | None = None) -> int:
    """Get log level from environment variable or provided value.

    Args:
        env_value: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging level integer
    """
    if env_value is None:
        env_value = os.getenv("LOG_LEVEL", "INFO")

    level = getattr(logging, env_value.upper(), logging.INFO)
    return level


def is_verbose() -> bool:
    """Check if verbose mode is enabled via environment variable."""
    verbose = os.getenv("VERBOSE", "").lower()
    return verbose in ("true", "1", "yes")


def setup_logging(log_level: str | None = None, verbose: bool | None = None) -> None:
    """Configure application-wide logging.

    Args:
        log_level: Log level string (default: INFO, verbose: DEBUG)
        verbose: If True, sets log level to DEBUG regardless of log_level
    """
    if verbose is None:
        verbose = is_verbose()

    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")

    if verbose:
        level = logging.DEBUG
        log_format = DEBUG_FORMAT
    else:
        level = get_log_level(log_level)
        log_format = DEFAULT_FORMAT

    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=_get_handlers(level, log_format),
    )

    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def _get_handlers(level: int, log_format: str) -> list[logging.Handler]:
    """Get logging handlers based on environment.

    Args:
        level: The logging level configured
        log_format: Log format string to use

    Returns:
        List of logging handlers
    """
    handlers = [logging.StreamHandler(sys.stdout)]

    log_dir = os.getenv("LOG_DIR")
    if log_dir:
        from pathlib import Path

        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.TimedRotatingFileHandler(
            when="midnight",
            interval=1,
            backupCount=7,
            filename=log_path / "app.log",
            encoding="utf-8",
        )
        file_handler.setFormatter(logging.Formatter(DEBUG_FORMAT))
        file_handler.setLevel(level)
        handlers.append(file_handler)

    return handlers


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the standard format.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

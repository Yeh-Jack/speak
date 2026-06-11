"""Tests for logging module."""

import logging
import pytest
from unittest.mock import patch, MagicMock

from app.core.logging import (
    get_log_level,
    is_verbose,
    setup_logging,
    get_logger,
    LogLevel,
    DEFAULT_FORMAT,
    DEBUG_FORMAT,
)


class TestGetLogLevel:
    """Tests for get_log_level function."""

    def test_get_log_level_debug(self):
        """Should return logging.DEBUG for 'DEBUG' input."""
        assert get_log_level("DEBUG") == logging.DEBUG

    def test_get_log_level_info(self):
        """Should return logging.INFO for 'INFO' input."""
        assert get_log_level("INFO") == logging.INFO

    def test_get_log_level_warning(self):
        """Should return logging.WARNING for 'WARNING' input."""
        assert get_log_level("WARNING") == logging.WARNING

    def test_get_log_level_error(self):
        """Should return logging.ERROR for 'ERROR' input."""
        assert get_log_level("ERROR") == logging.ERROR

    def test_get_log_level_critical(self):
        """Should return logging.CRITICAL for 'CRITICAL' input."""
        assert get_log_level("CRITICAL") == logging.CRITICAL

    def test_get_log_level_lowercase(self):
        """Should handle lowercase input."""
        assert get_log_level("debug") == logging.DEBUG

    def test_get_log_level_invalid_returns_info(self):
        """Should return INFO for invalid input."""
        assert get_log_level("INVALID") == logging.INFO

    def test_get_log_level_none_uses_env(self):
        """Should use LOG_LEVEL env var when None."""
        with patch("os.getenv", return_value="WARNING"):
            level = get_log_level(None)
        assert level == logging.WARNING

    def test_get_log_level_explicit_none_overrides_env(self):
        """Explicit env_value should override env var."""
        with patch("os.getenv") as mock_getenv:
            level = get_log_level("ERROR")
            mock_getenv.assert_not_called()
        assert level == logging.ERROR


class TestIsVerbose:
    """Tests for is_verbose function."""

    def test_is_verbose_true_string(self):
        """Should return True for 'true'."""
        with patch("os.getenv", return_value="true"):
            assert is_verbose() is True

    def test_is_verbose_one_string(self):
        """Should return True for '1'."""
        with patch("os.getenv", return_value="1"):
            assert is_verbose() is True

    def test_is_verbose_yes_string(self):
        """Should return True for 'yes'."""
        with patch("os.getenv", return_value="yes"):
            assert is_verbose() is True

    def test_is_verbose_false_string(self):
        """Should return False for 'false'."""
        with patch("os.getenv", return_value="false"):
            assert is_verbose() is False

    def test_is_verbose_no_string(self):
        """Should return False for 'no'."""
        with patch("os.getenv", return_value="no"):
            assert is_verbose() is False

    def test_is_verbose_empty_string(self):
        """Should return False for empty string."""
        with patch("os.getenv", return_value=""):
            assert is_verbose() is False


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_sets_debug_format_when_verbose(self):
        """Should use DEBUG_FORMAT when verbose is True."""
        with patch(
            "app.core.logging.is_verbose", return_value=True
        ), patch("app.core.logging._get_handlers") as mock_handlers:
            mock_handlers.return_value = [logging.StreamHandler()]
            setup_logging(verbose=True)
            mock_handlers.assert_called_once()
            call_args = mock_handlers.call_args
            assert call_args[0][1] == DEBUG_FORMAT

    def test_setup_logging_uses_default_format_when_not_verbose(self):
        """Should use DEFAULT_FORMAT when verbose is False."""
        with patch(
            "app.core.logging.is_verbose", return_value=False
        ), patch(
            "app.core.logging.get_log_level", return_value=logging.INFO
        ), patch(
            "app.core.logging._get_handlers"
        ) as mock_handlers:
            mock_handlers.return_value = [logging.StreamHandler()]
            setup_logging(verbose=False)
            call_args = mock_handlers.call_args
            assert call_args[0][1] == DEFAULT_FORMAT

    def test_setup_logging_uses_explicit_log_level(self):
        """Should use explicit log_level over env var."""
        with patch(
            "app.core.logging.is_verbose", return_value=False
        ), patch(
            "app.core.logging.get_log_level", return_value=logging.WARNING
        ), patch(
            "app.core.logging._get_handlers"
        ) as mock_handlers:
            mock_handlers.return_value = [logging.StreamHandler()]
            setup_logging(log_level="WARNING")
            mock_handlers.assert_called_once()
            call_args = mock_handlers.call_args
            assert call_args[0][0] == logging.WARNING

    def test_setup_logging_sets_third_party_loggers_to_warning(self):
        """Should set httpx and urllib3 to WARNING."""
        with patch(
            "app.core.logging.is_verbose", return_value=False
        ), patch(
            "app.core.logging.get_log_level", return_value=logging.INFO
        ), patch(
            "app.core.logging._get_handlers"
        ) as mock_handlers:
            mock_handlers.return_value = [logging.StreamHandler()]
            setup_logging()
            assert logging.getLogger("httpx").level == logging.WARNING
            assert logging.getLogger("urllib3").level == logging.WARNING


class TestGetHandlers:
    """Tests for _get_handlers function."""

    def test_get_handlers_includes_stream_handler(self):
        """Should always include StreamHandler for stdout."""
        from app.core.logging import _get_handlers

        handlers = _get_handlers(logging.INFO, DEFAULT_FORMAT)
        assert len(handlers) >= 1
        assert any(isinstance(h, logging.StreamHandler) for h in handlers)

    def test_get_handlers_adds_file_handler_when_log_dir_set(self):
        """Should add file handler when LOG_DIR is set."""
        with patch("os.getenv", return_value="/tmp/logs"):
            from app.core.logging import _get_handlers

            handlers = _get_handlers(logging.INFO, DEBUG_FORMAT)
            file_handlers = [h for h in handlers if isinstance(h, logging.handlers.TimedRotatingFileHandler)]
            assert len(file_handlers) == 1


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_logger_instance(self):
        """Should return a logger instance."""
        logger = get_logger("test")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_sets_correct_name(self):
        """Should set the logger name correctly."""
        logger = get_logger("app.services.test")
        assert logger.name == "app.services.test"


class TestLogLevel:
    """Tests for LogLevel enum."""

    def test_log_level_values(self):
        """LogLevel should have correct string values."""
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.CRITICAL.value == "CRITICAL"

    def test_log_level_is_string(self):
        """LogLevel should be usable as string."""
        level = LogLevel.INFO
        assert level.value == "INFO"
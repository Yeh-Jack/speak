"""Tests for config module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.core import config


class TestModuleLevelConstants:
    """Tests for module-level constants."""

    def test_project_root_is_path(self):
        """PROJECT_ROOT should be a Path object."""
        assert isinstance(config.PROJECT_ROOT, Path)

    def test_data_dir_relative_to_project_root(self):
        """DATA_DIR should be PROJECT_ROOT / 'data'."""
        assert config.DATA_DIR == config.PROJECT_ROOT / "data"

    def test_database_url_is_sqlite(self):
        """DATABASE_URL should be SQLite with aiosqlite."""
        assert "sqlite" in config.DATABASE_URL
        assert "aiosqlite" in config.DATABASE_URL

    def test_storage_base_path_equals_data_dir(self):
        """STORAGE_BASE_PATH should equal DATA_DIR."""
        assert config.STORAGE_BASE_PATH == config.DATA_DIR

    def test_llm_model_path(self):
        """LLM_MODEL_PATH should be DATA_DIR / 'models'."""
        assert config.LLM_MODEL_PATH == config.DATA_DIR / "models"

    def test_subtitles_dir(self):
        """SUBTITLES_DIR should be DATA_DIR / 'subtitles'."""
        assert config.SUBTITLES_DIR == config.DATA_DIR / "subtitles"

    def test_sentence_snap_enabled(self):
        """SENTENCE_SNAP should be True."""
        assert config.SENTENCE_SNAP is True


class TestSettings:
    """Tests for Settings class."""

    def test_settings_has_default_model(self):
        """Settings should have DEFAULT_MODEL."""
        assert hasattr(config.settings, "DEFAULT_MODEL")
        assert config.settings.DEFAULT_MODEL == "Qwen3.5-2B-Q4_K_M.gguf"

    def test_settings_llm_gpu_layers(self):
        """Settings should have LLM_GPU_LAYERS."""
        assert hasattr(config.settings, "LLM_GPU_LAYERS")
        assert config.settings.LLM_GPU_LAYERS == "-1"

    def test_settings_llm_context_size(self):
        """Settings should have LLM_CONTEXT_SIZE."""
        assert hasattr(config.settings, "LLM_CONTEXT_SIZE")
        assert config.settings.LLM_CONTEXT_SIZE == 8192

    def test_settings_llm_threads(self):
        """Settings should have LLM_THREADS as positive int."""
        assert hasattr(config.settings, "LLM_THREADS")
        assert isinstance(config.settings.LLM_THREADS, int)
        assert config.settings.LLM_THREADS > 0

    def test_settings_youtube_download_quality(self):
        """Settings should have YOUTUBE_DOWNLOAD_QUALITY."""
        assert hasattr(config.settings, "YOUTUBE_DOWNLOAD_QUALITY")
        assert config.settings.YOUTUBE_DOWNLOAD_QUALITY == 720

    def test_settings_youtube_audio_quality(self):
        """Settings should have YOUTUBE_AUDIO_QUALITY."""
        assert hasattr(config.settings, "YOUTUBE_AUDIO_QUALITY")
        assert config.settings.YOUTUBE_AUDIO_QUALITY == "128k"

    def test_settings_chunk_duration(self):
        """Settings should have CHUNK_DURATION as positive int."""
        assert hasattr(config.settings, "CHUNK_DURATION")
        assert isinstance(config.settings.CHUNK_DURATION, int)
        assert config.settings.CHUNK_DURATION > 0

    def test_settings_environment(self):
        """Settings should have ENVIRONMENT."""
        assert hasattr(config.settings, "ENVIRONMENT")
        assert config.settings.ENVIRONMENT in ["development", "production", "test"]

    def test_settings_debug_default(self):
        """Settings should have DEBUG defaulting to True."""
        assert hasattr(config.settings, "DEBUG")
        assert config.settings.DEBUG is True

    def test_settings_log_level_default(self):
        """Settings should have LOG_LEVEL defaulting to INFO."""
        assert hasattr(config.settings, "LOG_LEVEL")
        assert config.settings.LOG_LEVEL == "INFO"


class TestSettingsEnvOverride:
    """Tests for Settings environment variable override."""

    def test_llm_gpu_layers_env_override(self):
        """LLM_GPU_LAYERS should be overridable via env var."""
        with patch.dict("os.environ", {"LLM_GPU_LAYERS": "0"}):
            from importlib import reload
            from app.core import config as config_module
            reload(config_module)
            assert config_module.settings.LLM_GPU_LAYERS == "0"

    def test_chunk_duration_env_override(self):
        """CHUNK_DURATION should be overridable via env var."""
        with patch.dict("os.environ", {"CHUNK_DURATION": "600"}):
            from importlib import reload
            from app.core import config as config_module
            reload(config_module)
            assert config_module.settings.CHUNK_DURATION == 600

    def test_environment_env_override(self):
        """ENVIRONMENT should be overridable via env var."""
        with patch.dict("os.environ", {"ENVIRONMENT": "production"}):
            from importlib import reload
            from app.core import config as config_module
            reload(config_module)
            assert config_module.settings.ENVIRONMENT == "production"
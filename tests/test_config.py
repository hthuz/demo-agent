"""Tests for configuration module."""

import os
import pytest
from unittest.mock import patch

from agent.config import Config, get_config


class TestConfig:
    """Test Config class."""

    def test_config_defaults(self):
        """Test default configuration values."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            config = Config()

            assert config.openai_api_key == "test-key"
            assert config.model_name == "gpt-4"
            assert config.temperature == 0.7
            assert config.max_tokens == 2000
            assert config.max_iterations == 10
            assert config.verbose is True
            assert config.file_reader_base_path == "."
            assert config.file_reader_max_size == 10000
            assert config.directory_base_path == "."

    def test_config_from_env(self):
        """Test loading configuration from environment variables."""
        env_vars = {
            "OPENAI_API_KEY": "custom-key",
            "MODEL_NAME": "gpt-3.5-turbo",
            "TEMPERATURE": "0.5",
            "MAX_TOKENS": "1500",
            "MAX_ITERATIONS": "5",
            "VERBOSE": "false",
            "FILE_READER_BASE_PATH": "/custom/path",
            "FILE_READER_MAX_SIZE": "5000",
            "DIRECTORY_BASE_PATH": "/custom/dir",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = Config()

            assert config.openai_api_key == "custom-key"
            assert config.model_name == "gpt-3.5-turbo"
            assert config.temperature == 0.5
            assert config.max_tokens == 1500
            assert config.max_iterations == 5
            assert config.verbose is False
            assert config.file_reader_base_path == "/custom/path"
            assert config.file_reader_max_size == 5000
            assert config.directory_base_path == "/custom/dir"

    def test_config_verbose_variations(self):
        """Test different verbose value formats."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("off", False),
        ]

        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test", "VERBOSE": env_value}, clear=True):
                config = Config()
                assert config.verbose == expected, f"Failed for VERBOSE={env_value}"

    def test_config_validation_success(self):
        """Test successful configuration validation."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            config = Config()
            is_valid, errors = config.validate()

            assert is_valid is True
            assert len(errors) == 0

    def test_config_validation_missing_api_key(self):
        """Test validation fails when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            is_valid, errors = config.validate()

            assert is_valid is False
            assert len(errors) == 1
            assert "OPENAI_API_KEY" in errors[0]

    def test_config_validation_invalid_temperature(self):
        """Test validation fails for invalid temperature."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test", "TEMPERATURE": "3.0"}, clear=True):
            config = Config()
            is_valid, errors = config.validate()

            assert is_valid is False
            assert any("TEMPERATURE" in error for error in errors)

    def test_config_validation_invalid_max_tokens(self):
        """Test validation fails for invalid max_tokens."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test", "MAX_TOKENS": "-10"}, clear=True):
            config = Config()
            is_valid, errors = config.validate()

            assert is_valid is False
            assert any("MAX_TOKENS" in error for error in errors)

    def test_config_validation_invalid_max_iterations(self):
        """Test validation fails for invalid max_iterations."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test", "MAX_ITERATIONS": "0"}, clear=True):
            config = Config()
            is_valid, errors = config.validate()

            assert is_valid is False
            assert any("MAX_ITERATIONS" in error for error in errors)

    def test_config_validation_multiple_errors(self):
        """Test validation reports multiple errors."""
        with patch.dict(os.environ, {
            "TEMPERATURE": "5.0",
            "MAX_TOKENS": "-1",
        }, clear=True):
            config = Config()
            is_valid, errors = config.validate()

            assert is_valid is False
            assert len(errors) >= 2  # At least missing API key and one other error

    def test_config_invalid_numeric_values(self):
        """Test handling of invalid numeric environment variables."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test",
            "TEMPERATURE": "invalid",
            "MAX_TOKENS": "not-a-number",
            "MAX_ITERATIONS": "abc",
        }, clear=True):
            config = Config()

            # Should fall back to defaults
            assert config.temperature == 0.7
            assert config.max_tokens == 2000
            assert config.max_iterations == 10

    def test_get_config_singleton(self):
        """Test get_config returns singleton instance."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}, clear=True):
            config1 = get_config()
            config2 = get_config()

            assert config1 is config2

    def test_get_config_reload(self):
        """Test get_config reload functionality."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test1"}, clear=True):
            config1 = get_config()
            assert config1.openai_api_key == "test1"

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test2"}, clear=True):
            config2 = get_config(reload=True)
            assert config2.openai_api_key == "test2"

    def test_config_repr(self):
        """Test Config string representation."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            config = Config()
            repr_str = repr(config)

            assert "Config" in repr_str
            assert "gpt-4" in repr_str
            assert "0.7" in repr_str
            assert "10" in repr_str
            # API key should not be in repr
            assert "test-key" not in repr_str

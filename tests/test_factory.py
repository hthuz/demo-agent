"""Tests for model factory."""

import os
import pytest
from unittest.mock import patch

from agent.models.factory import create_model
from agent.models.openai_model import OpenAIModel
from agent.models.deepseek_model import DeepSeekModel
from agent.config import Config


class TestModelFactory:
    """Test model factory function."""

    def test_create_openai_model(self):
        """Test creating OpenAI model."""
        with patch.dict(os.environ, {
            "MODEL_PROVIDER": "openai",
            "OPENAI_API_KEY": "test-key",
        }, clear=True):
            config = Config(load_env=False)
            model = create_model(config=config)
            assert isinstance(model, OpenAIModel)
            assert model.api_key == "test-key"

    def test_create_deepseek_model(self):
        """Test creating DeepSeek model."""
        with patch.dict(os.environ, {
            "MODEL_PROVIDER": "deepseek",
            "DEEPSEEK_API_KEY": "test-key",
        }, clear=True):
            config = Config(load_env=False)
            model = create_model(config=config)
            assert isinstance(model, DeepSeekModel)
            assert model.api_key == "test-key"

    def test_create_model_default_config(self):
        """Test creating model with default config."""
        with patch.dict(os.environ, {
            "MODEL_PROVIDER": "openai",
            "OPENAI_API_KEY": "test-key",
        }, clear=True):
            model = create_model()
            assert isinstance(model, OpenAIModel)

    def test_create_model_unsupported_provider(self):
        """Test error for unsupported provider."""
        with patch.dict(os.environ, {
            "MODEL_PROVIDER": "unsupported",
            "OPENAI_API_KEY": "test-key",
        }, clear=True):
            config = Config(load_env=False)
            with pytest.raises(ValueError) as exc_info:
                create_model(config=config)
            assert "Unsupported MODEL_PROVIDER" in str(exc_info.value)
            assert "unsupported" in str(exc_info.value)
            assert "openai" in str(exc_info.value)
            assert "deepseek" in str(exc_info.value)

    def test_create_model_case_insensitive(self):
        """Test that provider selection is case insensitive."""
        with patch.dict(os.environ, {
            "MODEL_PROVIDER": "OpenAI",
            "OPENAI_API_KEY": "test-key",
        }, clear=True):
            config = Config(load_env=False)
            model = create_model(config=config)
            assert isinstance(model, OpenAIModel)

    def test_create_model_with_custom_model_name(self):
        """Test creating model with custom model name."""
        with patch.dict(os.environ, {
            "MODEL_PROVIDER": "deepseek",
            "DEEPSEEK_API_KEY": "test-key",
            "MODEL_NAME": "deepseek-v4-pro",
        }, clear=True):
            config = Config(load_env=False)
            model = create_model(config=config)
            assert isinstance(model, DeepSeekModel)
            assert model.model == "deepseek-v4-pro"

    def test_create_model_missing_api_key(self):
        """Test error when API key is missing for selected provider."""
        with patch.dict(os.environ, {
            "MODEL_PROVIDER": "openai",
        }, clear=True):
            config = Config(load_env=False)
            with pytest.raises(ValueError) as exc_info:
                create_model(config=config)
            assert "API key" in str(exc_info.value)

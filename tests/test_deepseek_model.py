"""Tests for DeepSeek model implementation."""

import os
import pytest
from unittest.mock import patch, Mock, MagicMock

from agent.models.deepseek_model import DeepSeekModel
from agent.config import Config


class TestDeepSeekModel:
    """Test DeepSeekModel class."""

    def test_init_with_explicit_api_key(self):
        """Test initialization with explicit API key."""
        model = DeepSeekModel(api_key="test-key", model="deepseek-chat")
        assert model.api_key == "test-key"
        assert model.model == "deepseek-chat"

    def test_init_from_config(self):
        """Test initialization from config."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "env-key"}, clear=True):
            config = Config(load_env=False)
            model = DeepSeekModel(config=config)
            assert model.api_key == "env-key"

    def test_init_missing_api_key(self):
        """Test initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config(load_env=False)
            with pytest.raises(ValueError) as exc_info:
                DeepSeekModel(config=config)
            assert "DEEPSEEK_API_KEY" in str(exc_info.value)

    def test_init_custom_model_preserved(self):
        """Test that custom model names are preserved."""
        model = DeepSeekModel(api_key="test-key", model="deepseek-coder")
        assert model.model == "deepseek-coder"

    def test_init_parameters(self):
        """Test initialization with custom parameters."""
        model = DeepSeekModel(
            api_key="test-key",
            model="deepseek-chat",
            temperature=0.5,
            max_tokens=1000,
        )
        assert model.temperature == 0.5
        assert model.max_tokens == 1000

    def test_init_base_url(self):
        """Test custom base URL."""
        model = DeepSeekModel(
            api_key="test-key",
            base_url="https://custom.api.com/v1",
        )
        assert model.base_url == "https://custom.api.com/v1"

    @patch("agent.models.deepseek_model.OpenAI")
    def test_generate_success(self, mock_openai_class):
        """Test successful generation."""
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock the response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Generated response"))]
        mock_client.chat.completions.create.return_value = mock_response

        # Create model and generate
        model = DeepSeekModel(api_key="test-key")
        result = model.generate("Test prompt")

        assert result == "Generated response"
        mock_client.chat.completions.create.assert_called_once()

    @patch("agent.models.deepseek_model.OpenAI")
    def test_generate_with_kwargs(self, mock_openai_class):
        """Test generation with custom parameters."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_response

        model = DeepSeekModel(api_key="test-key", temperature=0.7, max_tokens=2000)
        model.generate("Test", temperature=0.3, max_tokens=500)

        # Verify the call used the override parameters
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["temperature"] == 0.3
        assert call_kwargs["max_tokens"] == 500

    @patch("agent.models.deepseek_model.OpenAI")
    def test_generate_empty_response(self, mock_openai_class):
        """Test handling of empty response."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=None))]
        mock_client.chat.completions.create.return_value = mock_response

        model = DeepSeekModel(api_key="test-key")
        result = model.generate("Test")

        assert result == ""

    @patch("agent.models.deepseek_model.OpenAI")
    def test_generate_api_error(self, mock_openai_class):
        """Test handling of API errors."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_client.chat.completions.create.side_effect = Exception("API Error")

        model = DeepSeekModel(api_key="test-key")
        with pytest.raises(RuntimeError) as exc_info:
            model.generate("Test")

        assert "DeepSeek API error" in str(exc_info.value)

    def test_repr(self):
        """Test string representation."""
        model = DeepSeekModel(api_key="test-key", model="deepseek-chat")
        repr_str = repr(model)

        assert "DeepSeekModel" in repr_str
        assert "deepseek-chat" in repr_str

    @patch("agent.models.deepseek_model.OpenAI")
    def test_client_initialized_with_correct_params(self, mock_openai_class):
        """Test that OpenAI client is initialized with correct parameters."""
        model = DeepSeekModel(
            api_key="test-key",
            base_url="https://api.deepseek.com/v1",
        )

        mock_openai_class.assert_called_once_with(
            api_key="test-key",
            base_url="https://api.deepseek.com/v1",
        )

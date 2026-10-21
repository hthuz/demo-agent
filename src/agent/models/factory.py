"""Model factory for creating LLM instances based on configuration."""

from typing import Optional

from agent.config import Config, get_config
from agent.models.base import LLMBase


def create_model(config: Optional[Config] = None) -> LLMBase:
    """Create and return the appropriate model based on configuration.

    Args:
        config: Configuration instance (if None, uses global config)

    Returns:
        LLMBase: Initialized model instance

    Raises:
        ValueError: If MODEL_PROVIDER is not supported or configuration is invalid
    """
    if config is None:
        config = get_config()

    provider = config.model_provider

    if provider == "openai":
        from agent.models.openai_model import OpenAIModel
        return OpenAIModel(config=config)
    elif provider == "deepseek":
        from agent.models.deepseek_model import DeepSeekModel
        return DeepSeekModel(config=config)
    else:
        raise ValueError(
            f"Unsupported MODEL_PROVIDER: '{provider}'. "
            f"Supported providers: 'openai', 'deepseek'"
        )

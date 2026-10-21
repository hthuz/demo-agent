"""DeepSeek model implementation."""

from typing import Optional

from openai import OpenAI

from agent.models.base import LLMBase
from agent.config import Config, get_config


class DeepSeekModel(LLMBase):
    """DeepSeek model implementation (OpenAI-compatible API)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        config: Optional[Config] = None,
        base_url: str = "https://api.deepseek.com/v1",
    ):
        """Initialize DeepSeek model.

        Args:
            api_key: DeepSeek API key (if None, reads from config/env)
            model: Model name (if None, reads from config, default: deepseek-flash)
            temperature: Sampling temperature (if None, reads from config)
            max_tokens: Maximum tokens in response (if None, reads from config)
            config: Config instance (if None, uses global config)
            base_url: DeepSeek API base URL
        """
        # Get configuration
        if config is None:
            config = get_config()

        # Set parameters (explicit args override config)
        self.api_key = api_key or config.deepseek_api_key
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key not provided. Set DEEPSEEK_API_KEY environment "
                "variable or pass api_key parameter."
            )

        self.model = model or config.model_name
        self.temperature = temperature if temperature is not None else config.temperature
        self.max_tokens = max_tokens if max_tokens is not None else config.max_tokens
        self.base_url = base_url

        print("deepseek used")

        # Initialize OpenAI client with DeepSeek endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using DeepSeek API.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Generated text response
        """
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"DeepSeek API error: {str(e)}")

    def __repr__(self) -> str:
        return f"<DeepSeekModel: {self.model}>"

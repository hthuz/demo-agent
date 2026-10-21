"""Base class for LLM models."""

from abc import ABC, abstractmethod


class LLMBase(ABC):
    """Abstract base class for Language Model implementations."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the model.

        Args:
            prompt: Input prompt for the model
            **kwargs: Additional model-specific parameters

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """String representation of the model."""
        pass

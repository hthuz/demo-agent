"""Configuration management for ReAct Agent.

All configuration values are read from environment variables (.env file).
"""

import os
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv


class Config:
    """Central configuration class for the ReAct Agent."""

    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration.

        Args:
            env_file: Path to .env file (if None, searches default locations)
        """
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to load from common locations
            load_dotenv()  # Load from current directory
            load_dotenv(Path.home() / ".env")  # Load from home directory

    # ============================================================================
    # LLM Configuration
    # ============================================================================

    @property
    def openai_api_key(self) -> Optional[str]:
        """OpenAI API key."""
        return os.getenv("OPENAI_API_KEY")

    @property
    def model_name(self) -> str:
        """LLM model name to use."""
        return os.getenv("MODEL_NAME", "gpt-4")

    @property
    def temperature(self) -> float:
        """LLM temperature (0.0-2.0)."""
        try:
            return float(os.getenv("TEMPERATURE", "0.7"))
        except ValueError:
            return 0.7

    @property
    def max_tokens(self) -> int:
        """Maximum tokens in LLM response."""
        try:
            return int(os.getenv("MAX_TOKENS", "2000"))
        except ValueError:
            return 2000

    # ============================================================================
    # Agent Configuration
    # ============================================================================

    @property
    def max_iterations(self) -> int:
        """Maximum number of ReAct loop iterations."""
        try:
            return int(os.getenv("MAX_ITERATIONS", "10"))
        except ValueError:
            return 10

    @property
    def verbose(self) -> bool:
        """Whether to print verbose output during agent execution."""
        return os.getenv("VERBOSE", "true").lower() in ("true", "1", "yes", "on")

    # ============================================================================
    # Tool Configuration
    # ============================================================================

    @property
    def file_reader_base_path(self) -> str:
        """Base path for FileReader tool (security constraint)."""
        return os.getenv("FILE_READER_BASE_PATH", ".")

    @property
    def file_reader_max_size(self) -> int:
        """Maximum file size to read (in characters)."""
        try:
            return int(os.getenv("FILE_READER_MAX_SIZE", "10000"))
        except ValueError:
            return 10000

    @property
    def directory_base_path(self) -> str:
        """Base path for Directory tool (security constraint)."""
        return os.getenv("DIRECTORY_BASE_PATH", ".")

    # ============================================================================
    # Validation
    # ============================================================================

    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required fields
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required but not set")

        # Validate ranges
        if not 0.0 <= self.temperature <= 2.0:
            errors.append(f"TEMPERATURE must be between 0.0 and 2.0, got {self.temperature}")

        if self.max_tokens < 1:
            errors.append(f"MAX_TOKENS must be positive, got {self.max_tokens}")

        if self.max_iterations < 1:
            errors.append(f"MAX_ITERATIONS must be positive, got {self.max_iterations}")

        if self.file_reader_max_size < 1:
            errors.append(f"FILE_READER_MAX_SIZE must be positive, got {self.file_reader_max_size}")

        return len(errors) == 0, errors

    def __repr__(self) -> str:
        """String representation (hiding sensitive data)."""
        return (
            f"<Config: model={self.model_name}, "
            f"temperature={self.temperature}, "
            f"max_iterations={self.max_iterations}, "
            f"verbose={self.verbose}>"
        )


# Global default config instance
_default_config: Optional[Config] = None


def get_config(reload: bool = False) -> Config:
    """Get the global configuration instance.

    Args:
        reload: If True, reload configuration from environment

    Returns:
        Config instance
    """
    global _default_config
    if _default_config is None or reload:
        _default_config = Config()
    return _default_config

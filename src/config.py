"""Configuration management for the video frame description tool."""

import os
from dotenv import load_dotenv
from .exceptions import ConfigurationError


def load_config() -> dict:
    """Load and validate configuration from environment variables.

    Returns:
        dict: Configuration dictionary with all required and optional settings.

    Raises:
        ConfigurationError: If required configuration is missing.
    """
    load_dotenv()

    # Required configuration
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ConfigurationError(
            "ANTHROPIC_API_KEY not set. Please create a .env file with your API key. "
            "See .env.example for reference."
        )

    # Optional configuration with defaults
    config = {
        "anthropic_api_key": api_key,
        "mongodb_uri": os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
        "mongodb_database": os.getenv("MONGODB_DATABASE", "video_analysis"),
        "mongodb_collection": os.getenv("MONGODB_COLLECTION", "frame_descriptions"),
        "claude_model": os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5"),
        "max_tokens": int(os.getenv("MAX_TOKENS", "1024"))
    }

    return config

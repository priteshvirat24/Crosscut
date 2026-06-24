"""LLM provider factory — creates the appropriate provider from config."""

from __future__ import annotations

from functools import lru_cache

from app.config import LLMProvider as LLMProviderEnum, get_settings
from app.llm.provider import LLMProvider


def create_llm_provider(provider_name: str | None = None) -> LLMProvider:
    """Create an LLM provider instance based on configuration.

    Args:
        provider_name: Override provider name. If None, uses config default.

    Returns:
        Configured LLM provider instance.

    Raises:
        ValueError: If provider is unknown or API key is missing.
    """
    settings = get_settings()
    name = provider_name or settings.llm_provider.value

    if name == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
        from app.llm.openai import OpenAIProvider

        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )

    elif name == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")
        from app.llm.anthropic import AnthropicProvider

        return AnthropicProvider(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
        )

    elif name == "google":
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required for Google provider")
        from app.llm.google import GoogleProvider

        return GoogleProvider(
            api_key=settings.google_api_key,
            model=settings.google_model,
        )

    else:
        raise ValueError(f"Unknown LLM provider: {name}")


@lru_cache
def get_default_provider() -> LLMProvider:
    """Get the default LLM provider (cached singleton)."""
    return create_llm_provider()

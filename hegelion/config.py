"""Environment-driven configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from .backends import (
    AnthropicLLMBackend,
    CustomHTTPLLMBackend,
    LLMBackend,
    OllamaLLMBackend,
    OpenAILLMBackend,
)


class ConfigurationError(RuntimeError):
    """Raised when the server is misconfigured."""


@dataclass(frozen=True)
class EngineSettings:
    """Runtime configuration for the dialectical engine."""

    model: str
    synthesis_threshold: float
    max_tokens_per_phase: int


def _get_env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ConfigurationError(f"Environment variable {name} must be a float.") from exc


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ConfigurationError(f"Environment variable {name} must be an integer.") from exc


DEFAULT_ANTHROPIC_BASE_URL = "https://api.anthropic.com"


@lru_cache(maxsize=1)
def get_backend_from_env() -> LLMBackend:
    """Instantiate the configured backend."""

    provider = os.getenv("HEGELION_PROVIDER", "anthropic").lower()
    model = os.getenv("HEGELION_MODEL", "claude-4.5-sonnet-latest")

    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_base_url = os.getenv("ANTHROPIC_BASE_URL", DEFAULT_ANTHROPIC_BASE_URL)
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    custom_base_url = os.getenv("CUSTOM_API_BASE_URL")
    custom_api_key = os.getenv("CUSTOM_API_KEY")
    custom_timeout = _get_env_float("CUSTOM_API_TIMEOUT", 60.0)

    # Default priority: Anthropic first (recommended), then OpenAI
    if provider in {"anthropic", "auto"} and anthropic_key:
        return AnthropicLLMBackend(
            model=model,
            api_key=anthropic_key,
            base_url=anthropic_base_url,
        )

    if provider in {"openai", "auto"} and openai_key:
        return OpenAILLMBackend(
            model=model,
            api_key=openai_key,
            base_url=os.getenv("OPENAI_BASE_URL"),
            organization=os.getenv("OPENAI_ORG_ID"),
        )

    if provider == "ollama":
        return OllamaLLMBackend(model=model, base_url=ollama_url)

    if provider == "custom_http":
        if not custom_base_url:
            raise ConfigurationError(
                "CUSTOM_API_BASE_URL must be set when HEGELION_PROVIDER=custom_http"
            )
        return CustomHTTPLLMBackend(
            model=model,
            api_base_url=custom_base_url,
            api_key=custom_api_key,
            timeout=custom_timeout,
        )

    raise ConfigurationError(
        "Unable to configure LLM backend. Set HEGELION_PROVIDER to one of: anthropic, openai, "
        "ollama, custom_http, or auto with the corresponding API keys."
    )


def get_engine_settings_from_env() -> EngineSettings:
    """Load engine configuration values from environment variables."""

    return EngineSettings(
        model=os.getenv("HEGELION_MODEL", "claude-4.5-sonnet-latest"),
        synthesis_threshold=_get_env_float("HEGELION_SYNTHESIS_THRESHOLD", 0.85),
        max_tokens_per_phase=_get_env_int("HEGELION_MAX_TOKENS_PER_PHASE", 10_000),
    )


__all__ = [
    "EngineSettings",
    "ConfigurationError",
    "get_backend_from_env",
    "get_engine_settings_from_env",
]

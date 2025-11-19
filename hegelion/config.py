"""Environment-driven configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Dict

from .backends import (
    AnthropicLLMBackend,
    CustomHTTPLLMBackend,
    GoogleLLMBackend,
    LLMBackend,
    OllamaLLMBackend,
    OpenAILLMBackend,
)


class ConfigurationError(RuntimeError):
    """Raised when the server is misconfigured."""


@dataclass
class EngineSettings:
    """Settings for the Hegelion engine."""

    model: str
    synthesis_threshold: float
    max_tokens_per_phase: int
    validate_results: bool
    cache_enabled: bool
    cache_ttl_seconds: int
    cache_dir: str


@dataclass
class Config:
    """Mutable runtime configuration for Hegelion."""

    provider: str
    model: str
    synthesis_threshold: float
    max_tokens_per_phase: int
    validate_results: bool
    cache_enabled: bool
    cache_ttl_seconds: int
    cache_dir: str

    # Backend-specific settings
    openai_key: str | None
    openai_base_url: str | None
    openai_org: str | None
    anthropic_key: str | None
    anthropic_base_url: str
    google_key: str | None
    google_base_url: str | None
    ollama_url: str
    custom_base_url: str | None
    custom_api_key: str | None
    custom_timeout: float

    debug: bool = False

    # Internal state
    _initial_env: Dict[str, Any] = field(default_factory=dict, repr=False)


def _get_env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigurationError(
            f"Environment variable {name} must be a float."
        ) from exc


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigurationError(
            f"Environment variable {name} must be an integer."
        ) from exc


def _get_env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no"}


DEFAULT_ANTHROPIC_BASE_URL = "https://api.anthropic.com"


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Return the global, mutable configuration object."""
    return Config(
        provider=os.getenv("HEGELION_PROVIDER", "anthropic").lower(),
        model=os.getenv("HEGELION_MODEL", "claude-4.5-sonnet-latest"),
        synthesis_threshold=_get_env_float("HEGELION_SYNTHESIS_THRESHOLD", 0.85),
        max_tokens_per_phase=_get_env_int("HEGELION_MAX_TOKENS_PER_PHASE", 10_000),
        validate_results=_get_env_bool("HEGELION_VALIDATE_RESULTS", True),
        cache_enabled=_get_env_bool("HEGELION_CACHE", True),
        cache_ttl_seconds=_get_env_int("HEGELION_CACHE_TTL_SECONDS", 86_400),
        cache_dir=os.path.expanduser(
            os.getenv("HEGELION_CACHE_DIR", "~/.cache/hegelion")
        ),
        openai_key=os.getenv("OPENAI_API_KEY"),
        openai_base_url=os.getenv("OPENAI_BASE_URL"),
        openai_org=os.getenv("OPENAI_ORG_ID"),
        anthropic_key=os.getenv("ANTHROPIC_API_KEY"),
        anthropic_base_url=os.getenv("ANTHROPIC_BASE_URL", DEFAULT_ANTHROPIC_BASE_URL),
        google_key=os.getenv("GOOGLE_API_KEY"),
        google_base_url=os.getenv("GOOGLE_API_BASE_URL"),
        ollama_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        custom_base_url=os.getenv("CUSTOM_API_BASE_URL"),
        custom_api_key=os.getenv("CUSTOM_API_KEY"),
        custom_timeout=_get_env_float("CUSTOM_API_TIMEOUT", 60.0),
    )


def set_config_value(key: str, value: Any) -> None:
    """Update a value in the global configuration."""
    config = get_config()
    if hasattr(config, key):
        setattr(config, key, value)
        # When backend-related config changes, we must clear the backend cache
        if key in {"provider", "model", "openai_key", "anthropic_key", "google_key"}:
            get_backend_from_env.cache_clear()
    else:
        raise AttributeError(f"'{type(config).__name__}' has no attribute '{key}'")


def resolve_backend_for_model(model: str) -> LLMBackend:
    """Resolve an LLM backend based on the model name."""
    lowered = model.lower()
    config = get_config()

    if "claude" in lowered:
        if not config.anthropic_key:
            raise ConfigurationError("ANTHROPIC_API_KEY must be set.")
        return AnthropicLLMBackend(
            model=model,
            api_key=config.anthropic_key,
            base_url=config.anthropic_base_url,
        )

    if lowered.startswith(("gpt-", "o1-")) or "glm" in lowered:
        if not config.openai_key:
            raise ConfigurationError("OPENAI_API_KEY must be set.")
        return OpenAILLMBackend(
            model=model,
            api_key=config.openai_key,
            base_url=config.openai_base_url,
            organization=config.openai_org,
        )

    if "gemini" in lowered or lowered.startswith("g-"):
        if not config.google_key:
            raise ConfigurationError("GOOGLE_API_KEY must be set.")
        return GoogleLLMBackend(
            model=model, api_key=config.google_key, base_url=config.google_base_url
        )

    if lowered.startswith("local-"):
        actual_model = model.split("local-", 1)[1] or "llama3.3"
        return OllamaLLMBackend(model=actual_model, base_url=config.ollama_url)

    raise ConfigurationError(f"Cannot infer backend for model '{model}'.")


@lru_cache(maxsize=1)
def get_backend_from_env() -> LLMBackend:
    """Instantiate the configured backend from the global config."""
    config = get_config()

    if config.provider in {"anthropic", "auto"} and config.anthropic_key:
        return AnthropicLLMBackend(
            model=config.model,
            api_key=config.anthropic_key,
            base_url=config.anthropic_base_url,
        )

    if config.provider in {"openai", "auto"} and config.openai_key:
        return OpenAILLMBackend(
            model=config.model,
            api_key=config.openai_key,
            base_url=config.openai_base_url,
            organization=config.openai_org,
        )

    if config.provider in {"google", "auto"} and config.google_key:
        return GoogleLLMBackend(
            model=config.model,
            api_key=config.google_key,
            base_url=config.google_base_url,
        )

    if config.provider == "ollama":
        return OllamaLLMBackend(model=config.model, base_url=config.ollama_url)

    if config.provider == "custom_http":
        if not config.custom_base_url:
            raise ConfigurationError(
                "CUSTOM_API_BASE_URL must be set for custom_http provider."
            )
        return CustomHTTPLLMBackend(
            model=config.model,
            api_base_url=config.custom_base_url,
            api_key=config.custom_api_key,
            timeout=config.custom_timeout,
        )

    raise ConfigurationError(
        "Unable to configure LLM backend. Set HEGELION_PROVIDER and corresponding API keys."
    )


def get_engine_settings() -> EngineSettings:
    """Load engine configuration values from the global config."""
    config = get_config()
    return EngineSettings(
        model=config.model,
        synthesis_threshold=config.synthesis_threshold,
        max_tokens_per_phase=config.max_tokens_per_phase,
        validate_results=config.validate_results,
        cache_enabled=config.cache_enabled,
        cache_ttl_seconds=config.cache_ttl_seconds,
        cache_dir=config.cache_dir,
    )


__all__ = [
    "Config",
    "EngineSettings",
    "ConfigurationError",
    "get_config",
    "set_config_value",
    "get_backend_from_env",
    "get_engine_settings",
    "resolve_backend_for_model",
]

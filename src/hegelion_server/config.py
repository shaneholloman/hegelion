"""Environment-driven configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from .llm_backends import (
    AnthropicLLMBackend,
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


@lru_cache(maxsize=1)
def get_backend_from_env() -> LLMBackend:
    """Instantiate the configured backend."""

    provider = os.getenv("HEGELION_PROVIDER", "auto").lower()
    model = os.getenv("HEGELION_MODEL", "gpt-4.1-mini")

    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    if provider in {"openai", "auto"} and openai_key:
        return OpenAILLMBackend(
            model=model,
            api_key=openai_key,
            base_url=os.getenv("OPENAI_BASE_URL"),
            organization=os.getenv("OPENAI_ORG_ID"),
        )

    if provider in {"anthropic", "auto"} and anthropic_key:
        return AnthropicLLMBackend(model=model, api_key=anthropic_key)

    if provider == "ollama":
        return OllamaLLMBackend(model=model, base_url=ollama_url)

    raise ConfigurationError(
        "Unable to configure LLM backend. "
        "Provide HEGELION_PROVIDER and associated API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY) "
        "or set HEGELION_PROVIDER=ollama."
    )


def get_engine_settings_from_env() -> EngineSettings:
    """Load engine configuration values from environment variables."""

    return EngineSettings(
        model=os.getenv("HEGELION_MODEL", "gpt-4.1-mini"),
        synthesis_threshold=_get_env_float("HEGELION_SYNTHESIS_THRESHOLD", 0.85),
        max_tokens_per_phase=_get_env_int("HEGELION_MAX_TOKENS_PER_PHASE", 10_000),
    )


__all__ = [
    "EngineSettings",
    "ConfigurationError",
    "get_backend_from_env",
    "get_engine_settings_from_env",
]

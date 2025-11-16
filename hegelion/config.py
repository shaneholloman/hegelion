"""Environment-driven configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

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


def _get_common_env() -> dict:
    """Collect common backend-related environment variables."""
    return {
        "model": os.getenv("HEGELION_MODEL", "claude-4.5-sonnet-latest"),
        "openai_key": os.getenv("OPENAI_API_KEY"),
        "openai_base_url": os.getenv("OPENAI_BASE_URL"),
        "openai_org": os.getenv("OPENAI_ORG_ID"),
        "anthropic_key": os.getenv("ANTHROPIC_API_KEY"),
        "anthropic_base_url": os.getenv("ANTHROPIC_BASE_URL", DEFAULT_ANTHROPIC_BASE_URL),
        "google_key": os.getenv("GOOGLE_API_KEY"),
        "google_base_url": os.getenv("GOOGLE_API_BASE_URL"),
        "ollama_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "custom_base_url": os.getenv("CUSTOM_API_BASE_URL"),
        "custom_api_key": os.getenv("CUSTOM_API_KEY"),
        "custom_timeout": _get_env_float("CUSTOM_API_TIMEOUT", 60.0),
    }


def resolve_backend_for_model(model: str) -> LLMBackend:
    """Resolve an LLM backend based on the model name.

    Heuristics:
    - Models containing \"claude\" → Anthropic
    - Models starting with \"gpt-\" or \"o1-\" or containing \"glm\" → OpenAI-compatible
    - Models containing \"gemini\" or starting with \"g-\" → Google Generative AI
    - Models starting with \"local-\" → Ollama (model name after prefix)

    Raises:
        ConfigurationError: if the required API keys or base URLs are not set.
    """
    lowered = model.lower()
    env = _get_common_env()

    # Anthropic
    if "claude" in lowered:
        if not env["anthropic_key"]:
            raise ConfigurationError(
                "ANTHROPIC_API_KEY must be set to use Anthropic models like 'claude-*'."
            )
        return AnthropicLLMBackend(
            model=model,
            api_key=env["anthropic_key"],
            base_url=env["anthropic_base_url"],
        )

    # OpenAI-compatible (including GLM-style)
    if lowered.startswith(("gpt-", "o1-")) or "glm" in lowered:
        if not env["openai_key"]:
            raise ConfigurationError(
                "OPENAI_API_KEY must be set to use OpenAI-compatible models like 'gpt-*', 'o1-*', or 'GLM-*'."
            )
        return OpenAILLMBackend(
            model=model,
            api_key=env["openai_key"],
            base_url=env["openai_base_url"],
            organization=env["openai_org"],
        )

    # Google Gemini
    if "gemini" in lowered or lowered.startswith("g-"):
        if not env["google_key"]:
            raise ConfigurationError(
                "GOOGLE_API_KEY must be set to use Gemini models like 'gemini-*' or 'g-*'."
            )
        return GoogleLLMBackend(
            model=model,
            api_key=env["google_key"],
            base_url=env["google_base_url"],
        )

    # Local Ollama
    if lowered.startswith("local-"):
        actual_model = model.split("local-", 1)[1] or "llama3.3"
        return OllamaLLMBackend(model=actual_model, base_url=env["ollama_url"])

    # Fallback: treat as env-configured provider using HEGELION_PROVIDER
    raise ConfigurationError(
        f"Cannot infer backend for model '{model}'. "
        "Either set HEGELION_PROVIDER/HEGELION_MODEL and use the default API, "
        "or choose a model name that clearly indicates its provider "
        "(e.g., 'claude-*', 'gpt-*', 'gemini-*', 'local-llama3.3')."
    )


@lru_cache(maxsize=1)
def get_backend_from_env() -> LLMBackend:
    """Instantiate the configured backend."""

    provider = os.getenv("HEGELION_PROVIDER", "anthropic").lower()
    env = _get_common_env()
    model = env["model"]

    # Default priority: Anthropic first (recommended), then OpenAI
    if provider in {"anthropic", "auto"} and env["anthropic_key"]:
        return AnthropicLLMBackend(
            model=model,
            api_key=env["anthropic_key"],
            base_url=env["anthropic_base_url"],
        )

    if provider in {"openai", "auto"} and env["openai_key"]:
        return OpenAILLMBackend(
            model=model,
            api_key=env["openai_key"],
            base_url=env["openai_base_url"],
            organization=env["openai_org"],
        )

    if provider in {"google", "auto"} and env["google_key"]:
        return GoogleLLMBackend(
            model=model,
            api_key=env["google_key"],
            base_url=env["google_base_url"],
        )

    if provider == "ollama":
        return OllamaLLMBackend(model=model, base_url=env["ollama_url"])

    if provider == "custom_http":
        if not env["custom_base_url"]:
            raise ConfigurationError(
                "CUSTOM_API_BASE_URL must be set when HEGELION_PROVIDER=custom_http"
            )
        return CustomHTTPLLMBackend(
            model=model,
            api_base_url=env["custom_base_url"],
            api_key=env["custom_api_key"],
            timeout=env["custom_timeout"],
        )

    raise ConfigurationError(
        "Unable to configure LLM backend. Set HEGELION_PROVIDER to one of: anthropic, openai, "
        "google, ollama, custom_http, or auto with the corresponding API keys."
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
    "resolve_backend_for_model",
]

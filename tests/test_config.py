"""Tests for configuration and environment variable parsing."""

import os
from unittest.mock import MagicMock, patch

import pytest

from hegelion.backends import (
    AnthropicLLMBackend,
    CustomHTTPLLMBackend,
    OllamaLLMBackend,
    OpenAILLMBackend,
)
from hegelion.config import (
    ConfigurationError,
    get_backend_from_env,
    get_config,
    get_engine_settings,
    resolve_backend_for_model,
)


class TestResolveBackendForModel:
    """Tests for resolve_backend_for_model function."""

    def test_resolve_claude_model(self, monkeypatch):
        """Test resolving Anthropic backend for Claude models."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        get_config.cache_clear()
        backend = resolve_backend_for_model("claude-3-opus-20240229")

        assert isinstance(backend, AnthropicLLMBackend)
        assert backend.model == "claude-3-opus-20240229"

    def test_resolve_claude_model_case_insensitive(self, monkeypatch):
        """Test resolving Claude model case-insensitively."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        get_config.cache_clear()
        backend = resolve_backend_for_model("CLAUDE-3-SONNET")

        assert isinstance(backend, AnthropicLLMBackend)

    def test_resolve_gpt_model(self, monkeypatch):
        """Test resolving OpenAI backend for GPT models."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        get_config.cache_clear()
        backend = resolve_backend_for_model("gpt-4")

        assert isinstance(backend, OpenAILLMBackend)
        assert backend.model == "gpt-4"

    def test_resolve_o1_model(self, monkeypatch):
        """Test resolving OpenAI backend for o1 models."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        get_config.cache_clear()
        backend = resolve_backend_for_model("o1-preview")

        assert isinstance(backend, OpenAILLMBackend)
        assert backend.model == "o1-preview"

    def test_resolve_glm_model(self, monkeypatch):
        """Test resolving OpenAI backend for GLM models."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        get_config.cache_clear()
        backend = resolve_backend_for_model("GLM-4.6")

        assert isinstance(backend, OpenAILLMBackend)
        assert backend.model == "GLM-4.6"

    def test_resolve_gemini_model(self, monkeypatch):
        """Test resolving Google backend for Gemini models."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

        with patch("hegelion.config.GoogleLLMBackend") as mock_google:
            mock_google.return_value = MagicMock()
            get_config.cache_clear()
            _ = resolve_backend_for_model("gemini-2.5-pro")

            mock_google.assert_called_once()
            assert mock_google.call_args[1]["model"] == "gemini-2.5-pro"

    def test_resolve_g_prefix_model(self, monkeypatch):
        """Test resolving Google backend for g-* models."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

        with patch("hegelion.config.GoogleLLMBackend") as mock_google:
            mock_google.return_value = MagicMock()
            get_config.cache_clear()
            _ = resolve_backend_for_model("g-2.0-flash")

            mock_google.assert_called_once()

    def test_resolve_local_ollama_model(self, monkeypatch):
        """Test resolving Ollama backend for local-* models."""
        get_config.cache_clear()
        backend = resolve_backend_for_model("local-llama3.3")

        assert isinstance(backend, OllamaLLMBackend)
        assert backend.model == "llama3.3"

    def test_resolve_local_model_default(self, monkeypatch):
        """Test resolving local model with default."""
        get_config.cache_clear()
        backend = resolve_backend_for_model("local-")

        assert isinstance(backend, OllamaLLMBackend)
        assert backend.model == "llama3.3"

    def test_resolve_unknown_model_raises(self, monkeypatch):
        """Test that unknown model raises ConfigurationError."""
        get_config.cache_clear()
        with pytest.raises(ConfigurationError) as exc_info:
            resolve_backend_for_model("unknown-model-xyz")

        assert "Cannot infer backend" in str(exc_info.value)

    def test_resolve_claude_missing_key_raises(self, monkeypatch):
        """Test that Claude model without API key raises error."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        get_config.cache_clear()
        with pytest.raises(ConfigurationError) as exc_info:
            resolve_backend_for_model("claude-3-opus")

        assert "ANTHROPIC_API_KEY" in str(exc_info.value)

    def test_resolve_gpt_missing_key_raises(self, monkeypatch):
        """Test that GPT model without API key raises error."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        get_config.cache_clear()
        with pytest.raises(ConfigurationError) as exc_info:
            resolve_backend_for_model("gpt-4")

        assert "OPENAI_API_KEY" in str(exc_info.value)

    def test_resolve_gemini_missing_key_raises(self, monkeypatch):
        """Test that Gemini model without API key raises error."""
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

        get_config.cache_clear()
        with pytest.raises(ConfigurationError) as exc_info:
            resolve_backend_for_model("gemini-2.5-pro")

        assert "GOOGLE_API_KEY" in str(exc_info.value)


class TestGetBackendFromEnv:
    """Tests for get_backend_from_env function."""

    def test_get_anthropic_backend(self, monkeypatch):
        """Test getting Anthropic backend from env."""
        monkeypatch.setenv("HEGELION_PROVIDER", "anthropic")
        monkeypatch.setenv("HEGELION_MODEL", "claude-3-opus")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        get_config.cache_clear()
        get_backend_from_env.cache_clear()
        backend = get_backend_from_env()

        assert isinstance(backend, AnthropicLLMBackend)
        assert backend.model == "claude-3-opus"

    def test_get_openai_backend(self, monkeypatch):
        """Test getting OpenAI backend from env."""
        monkeypatch.setenv("HEGELION_PROVIDER", "openai")
        monkeypatch.setenv("HEGELION_MODEL", "gpt-4")
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        get_config.cache_clear()
        get_backend_from_env.cache_clear()
        backend = get_backend_from_env()

        assert isinstance(backend, OpenAILLMBackend)
        assert backend.model == "gpt-4"

    def test_get_google_backend(self, monkeypatch):
        """Test getting Google backend from env."""
        monkeypatch.setenv("HEGELION_PROVIDER", "google")
        monkeypatch.setenv("HEGELION_MODEL", "gemini-2.5-pro")
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

        get_config.cache_clear()
        get_backend_from_env.cache_clear()

        with patch("hegelion.config.GoogleLLMBackend") as mock_google:
            mock_google.return_value = MagicMock()
            _ = get_backend_from_env()

            mock_google.assert_called_once()

    def test_get_ollama_backend(self, monkeypatch):
        """Test getting Ollama backend from env."""
        monkeypatch.setenv("HEGELION_PROVIDER", "ollama")
        monkeypatch.setenv("HEGELION_MODEL", "llama3.3")
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://custom:11434")

        get_config.cache_clear()
        get_backend_from_env.cache_clear()
        backend = get_backend_from_env()

        assert isinstance(backend, OllamaLLMBackend)
        assert backend.model == "llama3.3"
        assert backend.base_url == "http://custom:11434"

    def test_get_custom_http_backend(self, monkeypatch):
        """Test getting custom HTTP backend from env."""
        monkeypatch.setenv("HEGELION_PROVIDER", "custom_http")
        monkeypatch.setenv("HEGELION_MODEL", "custom-model")
        monkeypatch.setenv("CUSTOM_API_BASE_URL", "https://api.example.com/v1")
        monkeypatch.setenv("CUSTOM_API_KEY", "custom-key")

        get_config.cache_clear()
        get_backend_from_env.cache_clear()
        backend = get_backend_from_env()

        assert isinstance(backend, CustomHTTPLLMBackend)
        assert backend.model == "custom-model"
        assert backend.api_base_url == "https://api.example.com/v1"
        assert backend.api_key == "custom-key"

    def test_get_custom_http_missing_url_raises(self, monkeypatch):
        """Test that custom HTTP without base URL raises error."""
        monkeypatch.setenv("HEGELION_PROVIDER", "custom_http")
        monkeypatch.delenv("CUSTOM_API_BASE_URL", raising=False)

        get_config.cache_clear()
        get_backend_from_env.cache_clear()

        get_config.cache_clear()
        with pytest.raises(ConfigurationError) as exc_info:
            get_backend_from_env()

        assert "CUSTOM_API_BASE_URL" in str(exc_info.value)

    def test_get_auto_provider_anthropic_first(self, monkeypatch):
        """Test auto provider selects Anthropic when available."""
        monkeypatch.setenv("HEGELION_PROVIDER", "auto")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-2")

        get_config.cache_clear()
        get_backend_from_env.cache_clear()
        backend = get_backend_from_env()

        assert isinstance(backend, AnthropicLLMBackend)

    def test_get_auto_provider_openai_fallback(self, monkeypatch):
        """Test auto provider falls back to OpenAI."""
        monkeypatch.setenv("HEGELION_PROVIDER", "auto")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        get_config.cache_clear()
        get_backend_from_env.cache_clear()
        backend = get_backend_from_env()

        assert isinstance(backend, OpenAILLMBackend)

    def test_get_backend_no_provider_raises(self, monkeypatch):
        """Test that missing provider raises error."""
        monkeypatch.setenv("HEGELION_PROVIDER", "unknown")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        get_config.cache_clear()
        get_backend_from_env.cache_clear()

        get_config.cache_clear()
        with pytest.raises(ConfigurationError) as exc_info:
            get_backend_from_env()

        assert "Unable to configure" in str(exc_info.value)


class TestGetEngineSettingsFromEnv:
    """Tests for get_engine_settings function."""

    def test_default_settings(self, monkeypatch):
        """Test default settings when no env vars set."""
        # Clear all relevant env vars
        for key in [
            "HEGELION_MODEL",
            "HEGELION_SYNTHESIS_THRESHOLD",
            "HEGELION_MAX_TOKENS_PER_PHASE",
            "HEGELION_VALIDATE_RESULTS",
            "HEGELION_CACHE",
            "HEGELION_CACHE_TTL_SECONDS",
            "HEGELION_CACHE_DIR",
        ]:
            monkeypatch.delenv(key, raising=False)

        get_config.cache_clear()
        settings = get_engine_settings()

        assert settings.model == "claude-4.5-sonnet-latest"
        assert settings.synthesis_threshold == 0.85
        assert settings.max_tokens_per_phase == 10_000
        assert settings.validate_results is True
        assert settings.cache_enabled is True
        assert settings.cache_ttl_seconds == 86_400

    def test_custom_model(self, monkeypatch):
        """Test custom model setting."""
        monkeypatch.setenv("HEGELION_MODEL", "custom-model")

        get_config.cache_clear()
        settings = get_engine_settings()

        assert settings.model == "custom-model"

    def test_custom_synthesis_threshold(self, monkeypatch):
        """Test custom synthesis threshold."""
        monkeypatch.setenv("HEGELION_SYNTHESIS_THRESHOLD", "0.75")

        get_config.cache_clear()
        settings = get_engine_settings()

        assert settings.synthesis_threshold == 0.75

    def test_custom_max_tokens(self, monkeypatch):
        """Test custom max tokens."""
        monkeypatch.setenv("HEGELION_MAX_TOKENS_PER_PHASE", "5000")

        get_config.cache_clear()
        settings = get_engine_settings()

        assert settings.max_tokens_per_phase == 5000

    def test_validate_results_false(self, monkeypatch):
        """Test disabling validation."""
        monkeypatch.setenv("HEGELION_VALIDATE_RESULTS", "0")

        get_config.cache_clear()
        settings = get_engine_settings()

        assert settings.validate_results is False

    def test_validate_results_false_strings(self, monkeypatch):
        """Test validation disabled with various false strings."""
        for false_value in ["false", "no", "False", "NO"]:
            monkeypatch.setenv("HEGELION_VALIDATE_RESULTS", false_value)

            get_config.cache_clear()
            settings = get_engine_settings()

            assert settings.validate_results is False

    def test_cache_disabled(self, monkeypatch):
        """Test disabling cache."""
        monkeypatch.setenv("HEGELION_CACHE", "0")

        get_config.cache_clear()
        settings = get_engine_settings()

        assert settings.cache_enabled is False

    def test_custom_cache_ttl(self, monkeypatch):
        """Test custom cache TTL."""
        monkeypatch.setenv("HEGELION_CACHE_TTL_SECONDS", "3600")

        get_config.cache_clear()
        settings = get_engine_settings()

        assert settings.cache_ttl_seconds == 3600

    def test_custom_cache_dir(self, monkeypatch):
        """Test custom cache directory."""
        monkeypatch.setenv("HEGELION_CACHE_DIR", "/custom/cache/path")

        get_config.cache_clear()
        settings = get_engine_settings()

        assert settings.cache_dir == "/custom/cache/path"

    def test_invalid_float_raises(self, monkeypatch):
        """Test that invalid float raises ConfigurationError."""
        monkeypatch.setenv("HEGELION_SYNTHESIS_THRESHOLD", "not-a-float")

        get_config.cache_clear()
        with pytest.raises(ConfigurationError) as exc_info:
            get_engine_settings()

        assert "must be a float" in str(exc_info.value)

    def test_invalid_int_raises(self, monkeypatch):
        """Test that invalid int raises ConfigurationError."""
        monkeypatch.setenv("HEGELION_MAX_TOKENS_PER_PHASE", "not-an-int")

        get_config.cache_clear()
        with pytest.raises(ConfigurationError) as exc_info:
            get_engine_settings()

        assert "must be an integer" in str(exc_info.value)

    def test_cache_dir_expands_user(self, monkeypatch):
        """Test that cache dir expands ~."""
        monkeypatch.setenv("HEGELION_CACHE_DIR", "~/.custom_cache")

        get_config.cache_clear()
        settings = get_engine_settings()

        assert "~" not in settings.cache_dir
        assert os.path.expanduser(
            "~"
        ) in settings.cache_dir or settings.cache_dir.startswith("/")


class TestConfigurationError:
    """Tests for ConfigurationError exception."""

    def test_configuration_error_message(self):
        """Test ConfigurationError has helpful message."""
        error = ConfigurationError("Test error message")

        assert "Test error message" in str(error)
        assert isinstance(error, RuntimeError)

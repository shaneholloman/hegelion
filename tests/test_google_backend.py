import asyncio
import sys
import pytest

from hegelion import config
from hegelion.backends import GoogleLLMBackend


class _DummyResponse:
    def __init__(self, text: str = ""):
        self.text = text


class _RecordingAsyncModel:
    def __init__(self, model: str):
        self.model = model
        self.last_prompt = None
        self.last_kwargs = None

    async def generate_content(
        self, prompt, **kwargs
    ):  # pragma: no cover - exercised in tests
        self.last_prompt = prompt
        self.last_kwargs = kwargs
        return _DummyResponse(text="Generated from Google")


class _StubGenAI:
    def __init__(self):
        self.configured_with = None
        self.AsyncGenerativeModel = _RecordingAsyncModel

    def configure(self, **kwargs):  # pragma: no cover - exercised in tests
        self.configured_with = kwargs


def test_google_backend_generates_text(monkeypatch):
    stub = _StubGenAI()
    monkeypatch.setattr(sys.modules["hegelion.backends"], "genai", stub)

    backend = GoogleLLMBackend(
        model="gemini-2.5-pro",
        api_key="fake-key",
        base_url="https://custom.endpoint",
    )

    result = asyncio.run(
        backend.generate(
            "Hello Gemini",
            max_tokens=50,
            temperature=0.2,
            system_prompt="System message",
        )
    )

    assert result == "Generated from Google"
    assert stub.configured_with == {
        "api_key": "fake-key",
        "client_options": {"api_endpoint": "https://custom.endpoint"},
    }
    assert backend.client.last_prompt == "Hello Gemini"
    assert backend.client.last_kwargs["generation_config"] == {
        "max_output_tokens": 50,
        "temperature": 0.2,
    }
    assert backend.client.last_kwargs["system_instruction"] == "System message"


def test_google_backend_missing_key_raises(monkeypatch):
    monkeypatch.setenv("HEGELION_PROVIDER", "google")
    for env_name in (
        "HEGELION_MODEL",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
    ):
        monkeypatch.delenv(env_name, raising=False)

    config.get_backend_from_env.cache_clear()

    with pytest.raises(config.ConfigurationError):
        config.get_backend_from_env()

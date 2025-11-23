"""Backend abstractions for calling different LLM providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

import json
import inspect

import httpx

try:
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover - optional dependency
    AsyncOpenAI = None  # type: ignore

try:
    from anthropic import AsyncAnthropic
except ImportError:  # pragma: no cover - optional dependency
    AsyncAnthropic = None  # type: ignore

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional dependency
    genai = None  # type: ignore


class BackendNotAvailableError(RuntimeError):
    """Raised when a backend cannot be initialized."""


class LLMBackend(Protocol):
    """Minimal interface required by the dialectical engine."""

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1_000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str: ...


@dataclass
class OpenAILLMBackend:
    """Backend that targets OpenAI-compatible chat completion APIs."""

    model: str
    api_key: str
    base_url: Optional[str] = None
    organization: Optional[str] = None

    def __post_init__(self) -> None:
        if AsyncOpenAI is None:  # pragma: no cover - import guard
            raise BackendNotAvailableError(
                "openai package is not installed but OpenAI backend was requested."
            )
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            organization=self.organization,
        )

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1_000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        maybe_response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        response = await maybe_response if inspect.isawaitable(maybe_response) else maybe_response
        content = response.choices[0].message.content
        return content.strip() if content else ""

    async def stream_generate(
        self,
        prompt: str,
        max_tokens: int = 1_000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        maybe_stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        stream = await maybe_stream if inspect.isawaitable(maybe_stream) else maybe_stream
        async for chunk in stream:
            choices = getattr(chunk, "choices", None)
            if not choices:
                continue
            delta = choices[0].delta
            content = getattr(delta, "content", None)
            if content:
                yield content

    @staticmethod
    def _missing_client():  # pragma: no cover - fallback for optional dependency
        async def _raise(*_: Any, **__: Any):
            raise BackendNotAvailableError(
                "openai package is not installed but OpenAI backend was requested."
            )

        class _Completions:
            create = _raise

        class _Chat:
            completions = _Completions()

        class _Client:
            chat = _Chat()

        return _Client()


@dataclass
class AnthropicLLMBackend:
    """Backend targeting Anthropic Claude models."""

    model: str
    api_key: str
    base_url: Optional[str] = None

    def __post_init__(self) -> None:
        if AsyncAnthropic is None:  # pragma: no cover - import guard
            raise BackendNotAvailableError(
                "anthropic package is not installed but Anthropic backend was requested."
            )
        self.client = AsyncAnthropic(api_key=self.api_key, base_url=self.base_url)

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1_000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
        text_chunks = [
            block.text for block in response.content if getattr(block, "type", None) == "text"
        ]
        return "\n".join(text_chunks).strip()

    async def stream_generate(
        self,
        prompt: str,
        max_tokens: int = 1_000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ):
        maybe_stream = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        stream = await maybe_stream if inspect.isawaitable(maybe_stream) else maybe_stream
        async for event in stream:
            if getattr(event, "type", None) == "content_block_delta":
                delta = getattr(event, "delta", None)
                if delta and getattr(delta, "text", None):
                    yield delta.text
            elif getattr(event, "type", None) == "content_block_start":
                block = getattr(event, "content_block", None)
                if block and getattr(block, "text", None):
                    yield block.text



@dataclass
class OllamaLLMBackend:
    """Backend for local Ollama servers using the HTTP API."""

    model: str
    base_url: str = "http://localhost:11434"
    timeout: float = 60.0

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1_000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": False,
        }
        url = f"{self.base_url.rstrip('/')}/api/generate"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        text = data.get("response") or data.get("data") or ""
        return str(text).strip()

    async def stream_generate(
        self,
        prompt: str,
        max_tokens: int = 1_000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": True,
        }
        url = f"{self.base_url.rstrip('/')}/api/generate"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            stream_ctx = client.stream("POST", url, json=payload)
            stream_ctx = await stream_ctx if inspect.isawaitable(stream_ctx) else stream_ctx
            async with stream_ctx as response:
                response.raise_for_status()
                lines_iter = response.aiter_lines()
                lines_iter = await lines_iter if inspect.isawaitable(lines_iter) else lines_iter
                async for line in lines_iter:
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except Exception:
                        continue
                    chunk = data.get("response") or data.get("data")
                    if chunk:
                        yield str(chunk)


@dataclass
class CustomHTTPLLMBackend:
    """Lightweight backend for generic JSON HTTP APIs."""

    model: str
    api_base_url: str
    api_key: Optional[str] = None
    timeout: float = 60.0

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1_000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_prompt:
            payload["system_prompt"] = system_prompt

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        url = self.api_base_url
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()

        for key in ("text", "completion", "result", "output"):
            value = data.get(key)
            if isinstance(value, str):
                return value.strip()

        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                for key in ("text", "content"):
                    value = first.get(key)
                    if isinstance(value, str):
                        return value.strip()
                message = first.get("message")
                if isinstance(message, dict):
                    content = message.get("content")
                    if isinstance(content, str):
                        return content.strip()

        # Fallback: return the entire JSON payload as a string for inspection
        return str(data)


class DummyLLMBackend:
    """Deterministic backend for tests and demos."""

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1_000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        del max_tokens, temperature, system_prompt  # unused
        lower_prompt = prompt.lower()
        # Order matters: 'synthesis' and 'antithesis' contain 'thesis'
        if "synthesis phase" in lower_prompt:
            return (
                "Paris' symbolic capital status coexists with distributed governance realities. "
                "Treat the capital as a network of institutions rather than a single geography.\n"
                "RESEARCH_PROPOSAL: Compare civic outcomes between centralized and distributed capitals.\n"
                "TESTABLE_PREDICTION: Nations with distributed campuses show higher bureaucratic resilience."
            )
        if "antithesis phase" in lower_prompt:
            return (
                "CONTRADICTION: Thesis ignores shifting historical capitals.\n"
                "EVIDENCE: During the Vichy regime, the functional capital moved away from Paris.\n"
                "CONTRADICTION: Thesis presumes a monocentric governance model.\n"
                "EVIDENCE: The European Union dilutes exclusive national control of capital cities."
            )
        if "thesis phase" in lower_prompt:
            return (
                "Paris is the capital of France. It has been the capital since 508 CE; "
                "the city functions as France's cultural and political hub."
            )
        # fallback
        return "This is a deterministic dummy response for testing."

    # Legacy compatibility: some older tests expect a `query` coroutine.
    async def query(self, *args, **kwargs):  # pragma: no cover - compatibility shim
        return await self.generate(*args, **kwargs)


@dataclass
class GoogleLLMBackend:
    """Backend targeting Google Gemini models via google-generativeai."""

    model: str
    api_key: str
    base_url: Optional[str] = None

    def __post_init__(self) -> None:
        if genai is None:  # pragma: no cover - import guard
            raise BackendNotAvailableError(
                "google-generativeai package is not installed but Google backend was requested."
            )

        client_options = {"api_endpoint": self.base_url} if self.base_url else None
        configure_kwargs = {"api_key": self.api_key}
        if client_options:
            configure_kwargs["client_options"] = client_options

        genai.configure(**configure_kwargs)

        if not hasattr(genai, "AsyncGenerativeModel"):
            raise BackendNotAvailableError(
                "google-generativeai.AsyncGenerativeModel is unavailable; update the dependency."
            )

        self.client = genai.AsyncGenerativeModel(self.model)

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1_000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        kwargs: Dict[str, Any] = {
            "generation_config": {
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }
        }
        if system_prompt:
            kwargs["system_instruction"] = system_prompt

        response = await self.client.generate_content(prompt, **kwargs)

        text = getattr(response, "text", None)
        if isinstance(text, str):
            return text.strip()

        candidates = getattr(response, "candidates", None)
        if isinstance(candidates, list) and candidates:
            candidate = candidates[0]
            if hasattr(candidate, "content"):
                content = getattr(candidate, "content")
                parts = getattr(content, "parts", None)
                if isinstance(parts, list):
                    texts = [getattr(part, "text") for part in parts if hasattr(part, "text")]
                    joined = "\n".join(filter(None, (t for t in texts if isinstance(t, str))))
                    if joined:
                        return joined.strip()

        return ""


__all__ = [
    "LLMBackend",
    "OpenAILLMBackend",
    "AnthropicLLMBackend",
    "OllamaLLMBackend",
    "CustomHTTPLLMBackend",
    "DummyLLMBackend",
    "GoogleLLMBackend",
    "BackendNotAvailableError",
    "MockBackend",
]


# Backwards compatibility alias
MockBackend = DummyLLMBackend

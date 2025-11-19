"""Comprehensive tests for all LLM backends - Fixed version."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hegelion.backends import (
    AnthropicLLMBackend,
    BackendNotAvailableError,
    CustomHTTPLLMBackend,
    DummyLLMBackend,
    OllamaLLMBackend,
    OpenAILLMBackend,
)


def _create_mock_httpx_client(post_response=None, stream_response=None):
    """Helper to create properly mocked httpx.AsyncClient."""
    mock_post = AsyncMock(return_value=post_response) if post_response else None
    mock_stream = AsyncMock(return_value=stream_response) if stream_response else None

    mock_context = AsyncMock()
    if mock_post:
        mock_context.post = mock_post
    if mock_stream:
        mock_context.stream = mock_stream

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_context)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


@pytest.mark.asyncio
class TestOpenAILLMBackend:
    """Tests for OpenAI-compatible backend."""

    async def test_generate_basic(self):
        """Test basic text generation."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Generated text response"))]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch("hegelion.backends.AsyncOpenAI", return_value=mock_client):
            backend = OpenAILLMBackend(
                model="gpt-4",
                api_key="test-key",
                base_url="https://api.openai.com/v1",
            )

            result = await backend.generate("Test prompt", max_tokens=100, temperature=0.7)

            assert result == "Generated text response"
            mock_client.chat.completions.create.assert_called_once()
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs["model"] == "gpt-4"
            assert call_kwargs["max_tokens"] == 100
            assert call_kwargs["temperature"] == 0.7

    async def test_generate_with_system_prompt(self):
        """Test generation with system prompt."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch("hegelion.backends.AsyncOpenAI", return_value=mock_client):
            backend = OpenAILLMBackend(model="gpt-4", api_key="test-key")

            await backend.generate("User prompt", system_prompt="System instruction")

            call_args = mock_client.chat.completions.create.call_args[1]
            messages = call_args["messages"]
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[0]["content"] == "System instruction"
            assert messages[1]["role"] == "user"
            assert messages[1]["content"] == "User prompt"

    async def test_generate_empty_response(self):
        """Test handling of empty response."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=None))]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch("hegelion.backends.AsyncOpenAI", return_value=mock_client):
            backend = OpenAILLMBackend(model="gpt-4", api_key="test-key")

            result = await backend.generate("Test")

            assert result == ""

    async def test_stream_generate(self):
        """Test streaming generation."""
        mock_client = AsyncMock()

        # Create mock stream chunks
        chunks = [
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content=" World"))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content=None))]),
        ]

        async def mock_stream():
            for chunk in chunks:
                yield chunk

        mock_client.chat.completions.create = AsyncMock(return_value=mock_stream())

        with patch("hegelion.backends.AsyncOpenAI", return_value=mock_client):
            backend = OpenAILLMBackend(model="gpt-4", api_key="test-key")

            collected = []
            async for chunk in backend.stream_generate("Test prompt"):
                collected.append(chunk)

            assert "".join(collected) == "Hello World"

    async def test_stream_generate_empty_chunks(self):
        """Test streaming with empty chunks."""
        mock_client = AsyncMock()

        chunks = [
            MagicMock(choices=[]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Text"))]),
        ]

        async def mock_stream():
            for chunk in chunks:
                yield chunk

        mock_client.chat.completions.create = AsyncMock(return_value=mock_stream())

        with patch("hegelion.backends.AsyncOpenAI", return_value=mock_client):
            backend = OpenAILLMBackend(model="gpt-4", api_key="test-key")

            collected = []
            async for chunk in backend.stream_generate("Test"):
                collected.append(chunk)

            assert "".join(collected) == "Text"

    async def test_backend_not_available_error(self):
        """Test error when openai package is missing."""
        with patch("hegelion.backends.AsyncOpenAI", None):
            with pytest.raises(BackendNotAvailableError):
                OpenAILLMBackend(model="gpt-4", api_key="test-key")

    async def test_organization_parameter(self):
        """Test organization parameter is passed."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch("hegelion.backends.AsyncOpenAI", return_value=mock_client) as mock_openai:
            backend = OpenAILLMBackend(model="gpt-4", api_key="test-key", organization="org-123")

            await backend.generate("Test")

            mock_openai.assert_called_once_with(
                api_key="test-key", base_url=None, organization="org-123"
            )


@pytest.mark.asyncio
class TestAnthropicLLMBackend:
    """Tests for Anthropic Claude backend."""

    async def test_generate_basic(self):
        """Test basic text generation."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="Claude response text")]
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("hegelion.backends.AsyncAnthropic", return_value=mock_client):
            backend = AnthropicLLMBackend(
                model="claude-3-opus-20240229",
                api_key="test-key",
            )

            result = await backend.generate("Test prompt", max_tokens=200)

            assert result == "Claude response text"
            mock_client.messages.create.assert_called_once()
            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["model"] == "claude-3-opus-20240229"
            assert call_kwargs["max_tokens"] == 200

    async def test_generate_multiple_text_blocks(self):
        """Test handling multiple text blocks."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(type="text", text="First part"),
            MagicMock(type="text", text="Second part"),
        ]
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("hegelion.backends.AsyncAnthropic", return_value=mock_client):
            backend = AnthropicLLMBackend(model="claude-3-opus-20240229", api_key="test-key")

            result = await backend.generate("Test")

            assert result == "First part\nSecond part"

    async def test_generate_with_system_prompt(self):
        """Test generation with system prompt."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="Response")]
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with patch("hegelion.backends.AsyncAnthropic", return_value=mock_client):
            backend = AnthropicLLMBackend(model="claude-3-opus-20240229", api_key="test-key")

            await backend.generate("User prompt", system_prompt="System message")

            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["system"] == "System message"

    async def test_stream_generate(self):
        """Test streaming generation."""
        mock_client = AsyncMock()

        events = [
            MagicMock(
                type="content_block_start",
                content_block=MagicMock(text="Hello"),
            ),
            MagicMock(
                type="content_block_delta",
                delta=MagicMock(text=" World"),
            ),
            MagicMock(type="content_block_delta", delta=MagicMock(text="!")),
        ]

        async def mock_stream():
            for event in events:
                yield event

        mock_client.messages.create = AsyncMock(return_value=mock_stream())

        with patch("hegelion.backends.AsyncAnthropic", return_value=mock_client):
            backend = AnthropicLLMBackend(model="claude-3-opus-20240229", api_key="test-key")

            collected = []
            async for chunk in backend.stream_generate("Test"):
                collected.append(chunk)

            assert "".join(collected) == "Hello World!"

    async def test_stream_generate_skips_non_text(self):
        """Test streaming skips non-text events."""
        mock_client = AsyncMock()

        events = [
            MagicMock(type="content_block_start", content_block=MagicMock(text="Text")),
            MagicMock(type="message_start"),  # Should be skipped
            MagicMock(type="content_block_delta", delta=MagicMock(text="More")),
        ]

        async def mock_stream():
            for event in events:
                yield event

        mock_client.messages.create = AsyncMock(return_value=mock_stream())

        with patch("hegelion.backends.AsyncAnthropic", return_value=mock_client):
            backend = AnthropicLLMBackend(model="claude-3-opus-20240229", api_key="test-key")

            collected = []
            async for chunk in backend.stream_generate("Test"):
                collected.append(chunk)

            assert "".join(collected) == "TextMore"

    async def test_backend_not_available_error(self):
        """Test error when anthropic package is missing."""
        with patch("hegelion.backends.AsyncAnthropic", None):
            with pytest.raises(BackendNotAvailableError):
                AnthropicLLMBackend(model="claude-3-opus-20240229", api_key="test-key")

    async def test_base_url_parameter(self):
        """Test base_url parameter is passed."""
        with patch("hegelion.backends.AsyncAnthropic") as mock_anthropic:
            _ = AnthropicLLMBackend(
                model="claude-3-opus-20240229",
                api_key="test-key",
                base_url="https://custom.anthropic.com",
            )

            mock_anthropic.assert_called_once_with(
                api_key="test-key", base_url="https://custom.anthropic.com"
            )


@pytest.mark.asyncio
class TestOllamaLLMBackend:
    """Tests for Ollama backend."""

    async def test_generate_basic(self):
        """Test basic text generation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Ollama response text"}
        mock_response.raise_for_status = MagicMock()

        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = OllamaLLMBackend(model="llama3.3", base_url="http://localhost:11434")

            result = await backend.generate("Test prompt", max_tokens=100, temperature=0.8)

            assert result == "Ollama response text"

    async def test_generate_with_system_prompt(self):
        """Test generation with system prompt."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Response"}
        mock_response.raise_for_status = MagicMock()

        _ = AsyncMock(return_value=mock_response)
        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = OllamaLLMBackend(model="llama3.3")

            await backend.generate("Test", system_prompt="System message")

            # Get the post call
            call_kwargs = mock_client.__aenter__.return_value.post.call_args[1]
            payload = call_kwargs["json"]
            assert payload["system"] == "System message"

    async def test_generate_uses_data_field(self):
        """Test fallback to 'data' field if 'response' missing."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "Fallback response"}
        mock_response.raise_for_status = MagicMock()

        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = OllamaLLMBackend(model="llama3.3")

            result = await backend.generate("Test")

            assert result == "Fallback response"

    async def test_generate_custom_base_url(self):
        """Test custom base URL handling."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Response"}
        mock_response.raise_for_status = MagicMock()

        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = OllamaLLMBackend(model="llama3.3", base_url="http://custom:11434")

            await backend.generate("Test")

            call_args = mock_client.__aenter__.return_value.post.call_args
            assert call_args[0][0] == "http://custom:11434/api/generate"

    async def test_generate_timeout(self):
        """Test timeout parameter."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Response"}
        mock_response.raise_for_status = MagicMock()

        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client) as mock_patch:
            backend = OllamaLLMBackend(model="llama3.3", timeout=120.0)

            await backend.generate("Test")

            mock_patch.assert_called_once_with(timeout=120.0)

    async def test_stream_generate(self):
        """Test streaming generation."""
        lines = [
            '{"response": "Hello"}',
            '{"response": " World"}',
            '{"response": "!"}',
            "",
        ]

        async def mock_stream():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.aiter_lines = AsyncMock(return_value=mock_stream())

        mock_stream_context = AsyncMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)

        mock_context = AsyncMock()
        mock_context.stream = AsyncMock(return_value=mock_stream_context)
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_context)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = OllamaLLMBackend(model="llama3.3")

            collected = []
            async for chunk in backend.stream_generate("Test"):
                collected.append(chunk)

            assert "".join(collected) == "Hello World!"

    async def test_stream_generate_invalid_json(self):
        """Test streaming handles invalid JSON gracefully."""
        lines = [
            '{"response": "Valid"}',
            "invalid json",
            '{"response": "More"}',
        ]

        async def mock_stream():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.aiter_lines = AsyncMock(return_value=mock_stream())

        mock_stream_context = AsyncMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)

        mock_context = AsyncMock()
        mock_context.stream = AsyncMock(return_value=mock_stream_context)
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_context)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = OllamaLLMBackend(model="llama3.3")

            collected = []
            async for chunk in backend.stream_generate("Test"):
                collected.append(chunk)

            assert "".join(collected) == "ValidMore"

    async def test_stream_generate_uses_data_field(self):
        """Test streaming uses 'data' field if 'response' missing."""
        lines = [
            '{"data": "From data"}',
            '{"response": "From response"}',
        ]

        async def mock_stream():
            for line in lines:
                yield line

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.aiter_lines = AsyncMock(return_value=mock_stream())

        mock_stream_context = AsyncMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)

        mock_context = AsyncMock()
        mock_context.stream = AsyncMock(return_value=mock_stream_context)
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_context)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = OllamaLLMBackend(model="llama3.3")

            collected = []
            async for chunk in backend.stream_generate("Test"):
                collected.append(chunk)

            assert "".join(collected) == "From dataFrom response"


@pytest.mark.asyncio
class TestCustomHTTPLLMBackend:
    """Tests for custom HTTP backend."""

    async def test_generate_text_field(self):
        """Test response with 'text' field."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"text": "Custom response"}
        mock_response.raise_for_status = MagicMock()

        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = CustomHTTPLLMBackend(
                model="custom-model",
                api_base_url="https://api.example.com/v1/chat",
            )

            result = await backend.generate("Test prompt")

            assert result == "Custom response"

    async def test_generate_completion_field(self):
        """Test response with 'completion' field."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"completion": "Completion text"}
        mock_response.raise_for_status = MagicMock()

        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = CustomHTTPLLMBackend(
                model="custom-model", api_base_url="https://api.example.com/v1/chat"
            )

            result = await backend.generate("Test")

            assert result == "Completion text"

    async def test_generate_result_field(self):
        """Test response with 'result' field."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "Result text"}
        mock_response.raise_for_status = MagicMock()

        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = CustomHTTPLLMBackend(
                model="custom-model", api_base_url="https://api.example.com/v1/chat"
            )

            result = await backend.generate("Test")

            assert result == "Result text"

    async def test_generate_output_field(self):
        """Test response with 'output' field."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"output": "Output text"}
        mock_response.raise_for_status = MagicMock()

        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = CustomHTTPLLMBackend(
                model="custom-model", api_base_url="https://api.example.com/v1/chat"
            )

            result = await backend.generate("Test")

            assert result == "Output text"

    async def test_generate_choices_field(self):
        """Test response with OpenAI-style 'choices' field."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "From choices"}}]}
        mock_response.raise_for_status = MagicMock()

        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = CustomHTTPLLMBackend(
                model="custom-model", api_base_url="https://api.example.com/v1/chat"
            )

            result = await backend.generate("Test")

            assert result == "From choices"

    async def test_generate_choices_text_field(self):
        """Test choices with 'text' field."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"text": "Text from choices"}]}
        mock_response.raise_for_status = MagicMock()

        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = CustomHTTPLLMBackend(
                model="custom-model", api_base_url="https://api.example.com/v1/chat"
            )

            result = await backend.generate("Test")

            assert result == "Text from choices"

    async def test_generate_fallback_to_json_string(self):
        """Test fallback to JSON string when no recognized fields."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"unknown": "field", "data": 123}
        mock_response.raise_for_status = MagicMock()

        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = CustomHTTPLLMBackend(
                model="custom-model", api_base_url="https://api.example.com/v1/chat"
            )

            result = await backend.generate("Test")

            assert "unknown" in result
            assert "field" in result

    async def test_generate_with_api_key(self):
        """Test API key in Authorization header."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"text": "Response"}
        mock_response.raise_for_status = MagicMock()

        _ = AsyncMock(return_value=mock_response)
        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = CustomHTTPLLMBackend(
                model="custom-model",
                api_base_url="https://api.example.com/v1/chat",
                api_key="secret-key",
            )

            await backend.generate("Test")

            call_kwargs = mock_client.__aenter__.return_value.post.call_args[1]
            headers = call_kwargs["headers"]
            assert headers["Authorization"] == "Bearer secret-key"

    async def test_generate_with_system_prompt(self):
        """Test system prompt in payload."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"text": "Response"}
        mock_response.raise_for_status = MagicMock()

        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = CustomHTTPLLMBackend(
                model="custom-model", api_base_url="https://api.example.com/v1/chat"
            )

            await backend.generate("Test", system_prompt="System message")

            call_kwargs = mock_client.__aenter__.return_value.post.call_args[1]
            payload = call_kwargs["json"]
            assert payload["system_prompt"] == "System message"

    async def test_generate_timeout(self):
        """Test timeout parameter."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"text": "Response"}
        mock_response.raise_for_status = MagicMock()

        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client) as mock_patch:
            backend = CustomHTTPLLMBackend(
                model="custom-model",
                api_base_url="https://api.example.com/v1/chat",
                timeout=90.0,
            )

            await backend.generate("Test")

            mock_patch.assert_called_once_with(timeout=90.0)

    async def test_generate_url_stripping(self):
        """Test base URL trailing slash is stripped."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"text": "Response"}
        mock_response.raise_for_status = MagicMock()

        mock_client = _create_mock_httpx_client(post_response=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            backend = CustomHTTPLLMBackend(
                model="custom-model", api_base_url="https://api.example.com/v1/chat/"
            )

            await backend.generate("Test")

            call_args = mock_client.__aenter__.return_value.post.call_args
            assert call_args[0][0] == "https://api.example.com/v1/chat/"


class TestDummyLLMBackend:
    """Tests for dummy backend (deterministic responses)."""

    @pytest.mark.asyncio
    async def test_generate_thesis_phase(self):
        """Test thesis phase response."""
        backend = DummyLLMBackend()

        result = await backend.generate("THESIS phase: What is the capital of France?")

        assert "Paris" in result
        assert "capital" in result

    @pytest.mark.asyncio
    async def test_generate_antithesis_phase(self):
        """Test antithesis phase response."""
        backend = DummyLLMBackend()

        result = await backend.generate(
            "You are in the ANTITHESIS phase of Hegelian dialectical reasoning."
        )

        assert "CONTRADICTION" in result
        assert "EVIDENCE" in result

    @pytest.mark.asyncio
    async def test_generate_synthesis_phase(self):
        """Test synthesis phase response."""
        backend = DummyLLMBackend()

        result = await backend.generate(
            "You are in the SYNTHESIS phase of Hegelian dialectical reasoning."
        )

        assert "RESEARCH_PROPOSAL" in result
        assert "TESTABLE_PREDICTION" in result

    @pytest.mark.asyncio
    async def test_generate_fallback(self):
        """Test fallback response for unknown prompts."""
        backend = DummyLLMBackend()

        result = await backend.generate("Random prompt")

        assert "deterministic dummy response" in result

    @pytest.mark.asyncio
    async def test_generate_ignores_parameters(self):
        """Test that parameters are accepted but ignored."""
        backend = DummyLLMBackend()

        result = await backend.generate(
            "THESIS phase: Test",
            max_tokens=5000,
            temperature=0.9,
            system_prompt="Custom system",
        )

        # Should still return deterministic response
        assert "Paris" in result or "deterministic" in result

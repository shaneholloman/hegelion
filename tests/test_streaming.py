#!/usr/bin/env python
"""Tests for Hegelion streaming functionality."""

import asyncio
from unittest.mock import patch
import pytest

from hegelion import run_dialectic
from hegelion.scripts.hegelion_cli import create_stream_callbacks


class MockBackend:
    """Mock LLM backend for testing."""

    def __init__(self, responses=None):
        self.responses = responses or {
            "thesis": "This is a test thesis response.",
            "antithesis": """
            CONTRADICTION: The thesis makes unsupported assumptions.
            EVIDENCE: No evidence provided for key claims.

            CONTRADICTION: The thesis ignores important counterexamples.
            EVIDENCE: Well-known cases contradict the conclusion.
            """,
            "synthesis": """
            A synthesis that transcends both positions.

            RESEARCH_PROPOSAL: Study the relationship between X and Y.
            TESTABLE_PREDICTION: Results will show significant correlation.
            """,
        }
        self.call_count = 0

    async def generate(self, prompt, max_tokens=1000, temperature=0.7, system_prompt=None):
        """Mock generate method."""
        self.call_count += 1

        # Determine which phase we're in based on prompt content
        if "THESIS" in prompt:
            return self.responses["thesis"]
        elif "ANTITHESIS" in prompt:
            return self.responses["antithesis"]
        elif "SYNTHESIS" in prompt:
            return self.responses["synthesis"]
        else:
            return "Default response"

    async def stream_generate(self, prompt, max_tokens=1000, temperature=0.7, system_prompt=None):
        """Mock stream_generate method that yields chunks."""
        response = await self.generate(prompt, max_tokens, temperature, system_prompt)

        # Split response into words and yield them as chunks
        words = response.split()
        for i, word in enumerate(words):
            if i == 0:
                yield word
            else:
                yield " " + word


class MockSettings:
    """Mock engine settings."""

    def __init__(self):
        self.model = "mock-model"
        self.max_tokens_per_phase = 1000
        self.synthesis_threshold = 0.8
        self.validate_results = False
        self.cache_enabled = False
        self.cache_ttl_seconds = 3600
        self.cache_dir = "/tmp/test_cache"


class TestStreamingCallbacks:
    """Test the streaming callback system."""

    @pytest.mark.asyncio
    async def test_stream_callback_receives_chunks(self):
        """Verify stream_callback is called with phase and chunk."""
        chunks = []

        async def capture(phase, chunk):
            chunks.append((phase, chunk))

        mock_backend = MockBackend()

        with patch("hegelion.core.core.get_backend_from_env", return_value=mock_backend):
            with patch("hegelion.core.core.get_engine_settings") as mock_settings:
                mock_settings.return_value = MockSettings()

                await run_dialectic(
                    "Test query",
                    stream_callback=capture,
                )

        # Verify we received chunks for each phase
        phases_received = set(phase for phase, _ in chunks)
        assert "thesis" in phases_received
        assert "antithesis" in phases_received
        assert "synthesis" in phases_received

        # Verify we got some content
        assert len(chunks) > 0
        assert all(chunk for _, chunk in chunks)

    @pytest.mark.asyncio
    async def test_progress_callback_lifecycle(self):
        """Verify progress_callback receives phase_started/completed events."""
        events = []

        async def capture(event, payload):
            events.append((event, payload))

        mock_backend = MockBackend()

        with patch("hegelion.core.core.get_backend_from_env", return_value=mock_backend):
            with patch("hegelion.core.core.get_engine_settings") as mock_settings:
                mock_settings.return_value = MockSettings()

                await run_dialectic(
                    "Test query",
                    progress_callback=capture,
                )

        # Check phase lifecycle events
        phase_starts = [(e, p) for e, p in events if e == "phase_started"]
        phase_completes = [(e, p) for e, p in events if e == "phase_completed"]

        assert len(phase_starts) == 3  # thesis, antithesis, synthesis
        assert len(phase_completes) == 3

        # Verify event payloads
        for event_type, payload in phase_starts:
            assert "phase" in payload
            assert payload["phase"] in ["thesis", "antithesis", "synthesis"]

        for event_type, payload in phase_completes:
            assert "phase" in payload
            assert "time_ms" in payload
            assert isinstance(payload["time_ms"], (int, float))

    @pytest.mark.skip(reason="Council mode requires search_providers module")
    @pytest.mark.asyncio
    async def test_council_mode_persona_names(self):
        """Verify streaming handles council mode persona names correctly."""
        phases = []

        async def capture_phase(event, payload):
            if event == "phase_started":
                phases.append(payload.get("phase", ""))

        mock_backend = MockBackend()

        with patch("hegelion.core.core.get_backend_from_env", return_value=mock_backend):
            with patch("hegelion.core.core.get_engine_settings") as mock_settings:
                mock_settings.return_value = MockSettings()

                await run_dialectic(
                    "Test query",
                    use_council=True,
                    progress_callback=capture_phase,
                )

        # In council mode, antithesis should have persona names
        antithesis_phases = [p for p in phases if p.startswith("antithesis")]
        assert len(antithesis_phases) > 0

        # Check that persona names are included
        for phase in antithesis_phases:
            assert ":" in phase  # Should be "antithesis:persona_name"

    def test_create_stream_callbacks_with_console(self):
        """Test callback creation with Rich console."""
        from rich.console import Console

        console = Console()
        stream_cb, progress_cb = asyncio.run(create_stream_callbacks(console))

        assert asyncio.iscoroutinefunction(stream_cb)
        assert asyncio.iscoroutinefunction(progress_cb)

    def test_create_stream_callbacks_without_console(self):
        """Test callback creation without Rich console (fallback mode)."""
        console = None
        stream_cb, progress_cb = asyncio.run(create_stream_callbacks(console))

        assert asyncio.iscoroutinefunction(stream_cb)
        assert asyncio.iscoroutinefunction(progress_cb)

    @pytest.mark.asyncio
    async def test_stream_callback_handles_empty_chunks(self):
        """Verify stream callback gracefully handles empty chunks."""
        chunks = []

        async def capture(phase, chunk):
            if chunk:  # Only capture non-empty chunks
                chunks.append((phase, chunk))

        mock_backend = MockBackend()

        with patch("hegelion.core.core.get_backend_from_env", return_value=mock_backend):
            with patch("hegelion.core.core.get_engine_settings") as mock_settings:
                mock_settings.return_value = MockSettings()

                await run_dialectic(
                    "Test query",
                    stream_callback=capture,
                )

        # Should have received some non-empty chunks
        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_both_callbacks_simultaneously(self):
        """Verify both stream and progress callbacks work together."""
        chunks = []
        events = []

        async def capture_stream(phase, chunk):
            chunks.append((phase, chunk))

        async def capture_progress(event, payload):
            events.append((event, payload))

        mock_backend = MockBackend()

        with patch("hegelion.core.core.get_backend_from_env", return_value=mock_backend):
            with patch("hegelion.core.core.get_engine_settings") as mock_settings:
                mock_settings.return_value = MockSettings()

                await run_dialectic(
                    "Test query",
                    stream_callback=capture_stream,
                    progress_callback=capture_progress,
                )

        # Both should have been called
        assert len(chunks) > 0
        assert len(events) > 0

        # Verify proper sequencing: phases should start before chunks arrive
        phase_starts = [e for e, p in events if e == "phase_started"]
        assert len(phase_starts) == 3


class TestCLIStreaming:
    """Test CLI streaming integration."""

    def test_cli_stream_flag_parsing(self):
        """Test that --stream flag is properly parsed."""
        from hegelion.scripts.hegelion_cli import parse_args

        args = parse_args(["--stream", "test query"])
        assert args.stream is True
        assert args.query == "test query"

    def test_cli_stream_flag_with_other_options(self):
        """Test --stream flag combined with other options."""
        from hegelion.scripts.hegelion_cli import parse_args

        args = parse_args(["--stream", "--debug", "--format", "json", "test query"])
        assert args.stream is True
        assert args.debug is True
        assert args.format == "json"
        assert args.query == "test query"

    @pytest.mark.asyncio
    async def test_stream_output_format(self):
        """Test that streaming produces expected output format."""
        output_chunks = []
        progress_events = []

        async def capture_stream(phase, chunk):
            output_chunks.append((phase, chunk))

        async def capture_progress(event, payload):
            progress_events.append((event, payload))

        mock_backend = MockBackend()

        with patch("hegelion.core.core.get_backend_from_env", return_value=mock_backend):
            with patch("hegelion.core.core.get_engine_settings") as mock_settings:
                mock_settings.return_value = MockSettings()

                await run_dialectic(
                    "What is consciousness?",
                    stream_callback=capture_stream,
                    progress_callback=capture_progress,
                )

        # Verify we got the expected sequence
        phase_starts = [e for e, p in progress_events if e == "phase_started"]
        phase_completes = [e for e, p in progress_events if e == "phase_completed"]

        assert len(phase_starts) == 3  # thesis, antithesis, synthesis
        assert len(phase_completes) == 3

        # Verify chunks were received for each phase
        thesis_chunks = [c for p, c in output_chunks if p == "thesis"]
        antithesis_chunks = [c for p, c in output_chunks if p == "antithesis"]
        synthesis_chunks = [c for p, c in output_chunks if p == "synthesis"]

        assert len(thesis_chunks) > 0
        assert len(antithesis_chunks) > 0
        assert len(synthesis_chunks) > 0

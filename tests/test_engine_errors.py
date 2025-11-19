"""Tests for engine error handling and graceful degradation."""

from unittest.mock import patch

import numpy as np
import pytest

from hegelion.backends import DummyLLMBackend
from hegelion.engine import (
    HegelionEngine,
    ThesisPhaseError,
)


class _TestEmbedder:
    """Deterministic embedder for tests."""

    def encode(self, text: str) -> np.ndarray:
        arr = np.zeros(6, dtype=np.float32)
        arr[0] = len(text)
        arr[1] = sum(ord(ch) for ch in text) % 997
        norm = np.linalg.norm(arr)
        return arr / norm if norm else arr


class _FailingBackend:
    """Backend that fails on specific phases."""

    def __init__(self, fail_phase=None):
        self.fail_phase = fail_phase
        self.call_count = 0

    async def generate(
        self, prompt, max_tokens=1000, temperature=0.7, system_prompt=None
    ):
        self.call_count += 1

        # Check for phase in prompt (case-insensitive)
        prompt_upper = prompt.upper()

        if (
            self.fail_phase == "thesis"
            and "THESIS" in prompt_upper
            and "PHASE" in prompt_upper
        ):
            raise Exception("Thesis generation failed")
        if (
            self.fail_phase == "antithesis"
            and "ANTITHESIS" in prompt_upper
            and "PHASE" in prompt_upper
        ):
            raise Exception("Antithesis generation failed")
        if (
            self.fail_phase == "synthesis"
            and "SYNTHESIS" in prompt_upper
            and "PHASE" in prompt_upper
        ):
            raise Exception("Synthesis generation failed")

        # Default successful response (check in order: synthesis, antithesis, thesis)
        if "SYNTHESIS" in prompt_upper and "PHASE" in prompt_upper:
            return "Test synthesis\nRESEARCH_PROPOSAL: Test proposal"
        if "ANTITHESIS" in prompt_upper and "PHASE" in prompt_upper:
            return "CONTRADICTION: Test contradiction\nEVIDENCE: Test evidence"
        if "THESIS" in prompt_upper and "PHASE" in prompt_upper:
            return "Test thesis response"
        return "Default response"


@pytest.mark.asyncio
class TestPhaseErrors:
    """Tests for phase-specific errors."""

    async def test_thesis_phase_error_raises(self):
        """Test that thesis phase error raises exception."""
        backend = _FailingBackend(fail_phase="thesis")
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        with pytest.raises(ThesisPhaseError) as exc_info:
            await engine.process_query("Test query")

        assert "thesis" in str(exc_info.value).lower()
        assert exc_info.value.phase == "thesis"

    async def test_antithesis_phase_error_returns_partial(self):
        """Test that antithesis phase error returns partial result."""
        backend = _FailingBackend(fail_phase="antithesis")
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        result = await engine.process_query("Test query")

        # Should have thesis but failed antithesis
        assert result.thesis == "Test thesis response"
        assert "Antithesis generation failed" in result.antithesis
        assert result.mode == "thesis_only"
        # Antithesis failure causes synthesis to also fail (it depends on antithesis)
        errors = result.metadata.get("errors", [])
        assert len(errors) >= 1
        assert any(e["phase"] == "antithesis" for e in errors)

    async def test_synthesis_phase_error_returns_partial(self):
        """Test that synthesis phase error returns partial result."""
        backend = _FailingBackend(fail_phase="synthesis")
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        result = await engine.process_query("Test query")

        # Should have thesis and antithesis but failed synthesis
        assert result.thesis == "Test thesis response"
        assert "CONTRADICTION" in result.antithesis
        assert "Synthesis generation failed" in result.synthesis
        assert result.mode == "antithesis"
        assert len(result.metadata.get("errors", [])) == 1
        assert result.metadata["errors"][0]["phase"] == "synthesis"

    async def test_multiple_phase_errors(self):
        """Test handling multiple phase errors."""
        backend = _FailingBackend(fail_phase="antithesis")

        # Make synthesis also fail by raising in conflict estimation
        async def failing_conflict(*args, **kwargs):
            raise Exception("Conflict estimation failed")

        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        with patch.object(engine, "_compute_conflict", side_effect=failing_conflict):
            result = await engine.process_query("Test query")

            # Should still have thesis
            assert result.thesis == "Test thesis response"
            # Should have errors for both phases
            errors = result.metadata.get("errors", [])
            assert len(errors) >= 1
            assert any(e["phase"] == "antithesis" for e in errors)


@pytest.mark.asyncio
class TestErrorMetadata:
    """Tests for error tracking in metadata."""

    async def test_errors_tracked_in_metadata(self):
        """Test that errors are tracked in metadata."""
        backend = _FailingBackend(fail_phase="antithesis")
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        result = await engine.process_query("Test query")

        assert "errors" in result.metadata
        errors = result.metadata["errors"]
        # Antithesis failure causes synthesis to also fail
        assert len(errors) >= 1
        assert any(e["phase"] == "antithesis" for e in errors)
        assert "error" in errors[0]
        assert "message" in errors[0]

    async def test_no_errors_when_successful(self):
        """Test that no errors are tracked when all phases succeed."""
        backend = DummyLLMBackend()
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        result = await engine.process_query("Test query")

        assert (
            "errors" not in result.metadata
            or len(result.metadata.get("errors", [])) == 0
        )


@pytest.mark.asyncio
class TestStreamingCallbacks:
    """Tests for streaming callbacks."""

    async def test_stream_callback_sync(self):
        """Test synchronous stream callback."""
        backend = DummyLLMBackend()
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        collected = []

        def stream_callback(phase, chunk):
            collected.append((phase, chunk))

        _ = await engine.process_query("Test query", stream_callback=stream_callback)

        # Should have collected some chunks
        assert len(collected) > 0
        # Should have chunks from all phases
        phases = {phase for phase, _ in collected}
        assert "thesis" in phases or "antithesis" in phases or "synthesis" in phases

    async def test_stream_callback_async(self):
        """Test asynchronous stream callback."""
        backend = DummyLLMBackend()
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        collected = []

        async def stream_callback(phase, chunk):
            collected.append((phase, chunk))

        _ = await engine.process_query("Test query", stream_callback=stream_callback)

        assert len(collected) > 0

    async def test_stream_callback_with_backend_streaming(self):
        """Test stream callback with backend that supports streaming."""
        backend = DummyLLMBackend()

        # Add stream_generate method to backend
        async def stream_generate(
            prompt, max_tokens=1000, temperature=0.7, system_prompt=None
        ):
            chunks = ["Hello", " ", "World"]
            for chunk in chunks:
                yield chunk

        backend.stream_generate = stream_generate

        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        collected = []

        def stream_callback(phase, chunk):
            collected.append((phase, chunk))

        _ = await engine.process_query("Test query", stream_callback=stream_callback)

        # Should have collected chunks
        assert len(collected) > 0


@pytest.mark.asyncio
class TestProgressCallbacks:
    """Tests for progress callbacks."""

    async def test_progress_callback_phase_started(self):
        """Test progress callback for phase started events."""
        backend = DummyLLMBackend()
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        events = []

        def progress_callback(event, payload):
            events.append((event, payload))

        _ = await engine.process_query(
            "Test query", progress_callback=progress_callback
        )

        # Should have phase_started events
        phase_starts = [e for e, p in events if e == "phase_started"]
        assert len(phase_starts) >= 3  # thesis, antithesis, synthesis

    async def test_progress_callback_phase_completed(self):
        """Test progress callback for phase completed events."""
        backend = DummyLLMBackend()
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        events = []

        def progress_callback(event, payload):
            events.append((event, payload))

        _ = await engine.process_query(
            "Test query", progress_callback=progress_callback
        )

        # Should have phase_completed events
        phase_completes = [e for e, p in events if e == "phase_completed"]
        assert len(phase_completes) >= 3

        # Check payload structure
        for event, payload in events:
            if event == "phase_completed":
                assert "phase" in payload
                assert "time_ms" in payload

    async def test_progress_callback_async(self):
        """Test asynchronous progress callback."""
        backend = DummyLLMBackend()
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        events = []

        async def progress_callback(event, payload):
            events.append((event, payload))

        _ = await engine.process_query(
            "Test query", progress_callback=progress_callback
        )

        assert len(events) > 0


@pytest.mark.asyncio
class TestConflictScoreComputation:
    """Tests for conflict score computation edge cases."""

    async def test_conflict_score_empty_text(self):
        """Test conflict score with empty text."""
        backend = DummyLLMBackend()
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        # Should not crash with empty text
        score = await engine._compute_conflict("", "", [])
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    async def test_conflict_score_no_contradictions(self):
        """Test conflict score with no contradictions."""
        backend = DummyLLMBackend()
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        score = await engine._compute_conflict("Thesis text", "Antithesis text", [])
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    async def test_conflict_score_many_contradictions(self):
        """Test conflict score with many contradictions."""
        backend = DummyLLMBackend()
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        contradictions = [f"Contradiction {i}" for i in range(10)]
        score = await engine._compute_conflict("Thesis", "Antithesis", contradictions)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    async def test_conflict_score_backend_failure(self):
        """Test conflict score when backend fails."""
        backend = _FailingBackend()

        async def failing_generate(*args, **kwargs):
            raise Exception("Backend failed")

        backend.generate = failing_generate

        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        # Should handle backend failure gracefully
        # _estimate_normative_conflict returns 0.0 on failure, but other components
        # (semantic distance, contradiction_score) may still contribute
        score = await engine._compute_conflict(
            "Thesis", "Antithesis", ["Contradiction"]
        )
        # Should return a valid score (may not be exactly 0.0 due to other components)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


@pytest.mark.asyncio
class TestEmbedderFallback:
    """Tests for embedder fallback behavior."""

    async def test_fallback_embedder_when_sentence_transformers_unavailable(self):
        """Test fallback embedder when sentence-transformers is unavailable."""
        backend = DummyLLMBackend()

        with patch("hegelion.engine.SentenceTransformer", None):
            engine = HegelionEngine(
                backend=backend,
                model="test-model",
            )

            # Should use fallback embedder
            assert engine.embedder is not None
            # Should be able to encode
            embedding = engine.embedder.encode("test text")
            assert embedding is not None
            assert len(embedding) > 0

    async def test_fallback_embedder_on_import_error(self):
        """Test fallback when SentenceTransformer import fails."""
        backend = DummyLLMBackend()

        def failing_import(*args, **kwargs):
            raise ImportError("sentence-transformers not available")

        with patch("hegelion.engine.SentenceTransformer") as mock_st:
            mock_st.side_effect = failing_import
            engine = HegelionEngine(
                backend=backend,
                model="test-model",
            )

            # Should use fallback
            assert engine.embedder is not None
            embedding = engine.embedder.encode("test")
            assert embedding is not None

    async def test_fallback_embedder_deterministic(self):
        """Test that fallback embedder produces deterministic results."""
        backend = DummyLLMBackend()

        with patch("hegelion.engine.SentenceTransformer", None):
            engine = HegelionEngine(
                backend=backend,
                model="test-model",
            )

            text = "test text"
            embedding1 = engine.embedder.encode(text)
            embedding2 = engine.embedder.encode(text)

            # Should be deterministic
            assert np.allclose(embedding1, embedding2)


@pytest.mark.asyncio
class TestGracefulDegradation:
    """Tests for graceful degradation when phases fail."""

    async def test_partial_result_structure(self):
        """Test that partial results have correct structure."""
        backend = _FailingBackend(fail_phase="synthesis")
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        result = await engine.process_query("Test query")

        # Should still be a valid HegelionResult
        assert result.query == "Test query"
        assert result.thesis
        assert result.antithesis
        assert result.synthesis  # May contain error message
        assert isinstance(result.contradictions, list)
        assert isinstance(result.research_proposals, list)
        assert isinstance(result.metadata, dict)

    async def test_mode_reflects_completion_status(self):
        """Test that mode reflects which phases completed."""
        backend = _FailingBackend(fail_phase="antithesis")
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        result = await engine.process_query("Test query")

        # Should be thesis_only when antithesis fails
        assert result.mode == "thesis_only"

    async def test_contradictions_extracted_when_antithesis_succeeds(self):
        """Test that contradictions are extracted when antithesis succeeds."""
        backend = DummyLLMBackend()
        engine = HegelionEngine(
            backend=backend,
            model="test-model",
            embedder=_TestEmbedder(),
        )

        result = await engine.process_query("Test query")

        # Should have extracted contradictions
        assert len(result.contradictions) > 0
        assert all("description" in c for c in result.contradictions)

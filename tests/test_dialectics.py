import numpy as np
import pytest

from hegelion_server.dialectics import HegelionEngine
from hegelion_server.llm_backends import DummyLLMBackend


class _TestEmbedder:
    """Lightweight deterministic embedder for tests."""

    def encode(self, text: str) -> np.ndarray:
        arr = np.zeros(6, dtype=np.float32)
        arr[0] = len(text)
        arr[1] = sum(ord(ch) for ch in text) % 997
        arr[2] = text.count("a")
        arr[3] = text.count("e")
        arr[4] = text.count("i")
        arr[5] = text.count("o")
        norm = np.linalg.norm(arr)
        return arr / norm if norm else arr


@pytest.fixture
def engine() -> HegelionEngine:
    return HegelionEngine(
        backend=DummyLLMBackend(),
        model="dummy",
        embedder=_TestEmbedder(),
        synthesis_threshold=0.5,
    )


@pytest.mark.asyncio
async def test_simple_factual(engine: HegelionEngine) -> None:
    result = await engine.process_query("What is the capital of France?")
    assert result.mode in {"thesis_only", "synthesis"}
    assert "Paris" in result.trace.thesis
    assert result.conflict_score >= 0.0
    assert result.trace.contradictions_found >= 0


@pytest.mark.asyncio
async def test_conflict_score_is_bounded(engine: HegelionEngine) -> None:
    result = await engine.process_query("Is free will real?")
    assert 0.0 <= result.conflict_score <= 1.0
    assert isinstance(result.metadata.total_time_ms, float)


@pytest.mark.asyncio
async def test_research_generation(engine: HegelionEngine) -> None:
    result = await engine.process_query(
        "How do proteins fold quickly despite vast configuration space?"
    )
    assert isinstance(result.trace.research_proposals, list)
    assert all(isinstance(item, str) for item in result.trace.research_proposals)

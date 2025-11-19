import numpy as np
import pytest

from hegelion.backends import DummyLLMBackend
from hegelion.engine import HegelionEngine


class _TestEmbedder:
    """Deterministic embedder used for tests."""

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
    )


@pytest.mark.asyncio
async def test_process_query_always_synthesizes(engine: HegelionEngine) -> None:
    result = await engine.process_query("What is the capital of France?")

    assert result.mode == "synthesis"
    assert "Paris" in result.thesis
    assert result.synthesis
    assert result.metadata["backend_model"] == "dummy"
    assert "debug" not in result.metadata


@pytest.mark.asyncio
async def test_process_query_with_debug(engine: HegelionEngine) -> None:
    result = await engine.process_query("Is free will real?", debug=True)

    assert "debug" in result.metadata
    debug_info = result.metadata["debug"]
    assert "internal_conflict_score" in debug_info
    assert result.trace is not None
    assert (
        result.trace.get("internal_conflict_score")
        == debug_info["internal_conflict_score"]
    )


@pytest.mark.asyncio
async def test_process_query_structures_contradictions(engine: HegelionEngine) -> None:
    result = await engine.process_query(
        "How do proteins fold quickly despite vast configuration space?"
    )

    assert isinstance(result.contradictions, list)
    assert all("description" in item for item in result.contradictions)
    assert isinstance(result.research_proposals, list)
    assert "metadata" in result.to_dict()

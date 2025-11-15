import numpy as np
import pytest

from hegelion.backends import DummyLLMBackend
from hegelion.engine import HegelionEngine
from hegelion.parsing import extract_contradictions

PRIVACY_SECURITY_THESIS = """
Security must be prioritized over privacy when public safety is at stake. Governments owe citizens
maximal protection from unpredictable threats, which requires deep data access, network visibility,
and proactive policing. Without comprehensive surveillance, society becomes brittle and exposed.
Therefore, sacrificing some privacy is the only rational path to a stable future.
""".strip()

PRIVACY_SECURITY_ANTITHESIS = """
I will now dismantle the core assertions of the security-first thesis. Its framing commits multiple
category errors and ignores the actual structure of democratic resilience.

**CONTRADICTION 1: The Security Paradox**
EVIDENCE: Treating safety as absolute erodes trust, which is the substrate of any security regime.

**CONTRADICTION 2: The Misdefinition of "Security"**
EVIDENCE: Reducing protection to physical threats ignores informational, civic, and economic security.

**CONTRADICTION 3: The Flawed "Public Square" Analogy**
EVIDENCE: The thesis assumes centralized control over speech, but modern networks are decentralized ecosystems.

**CONTRADICTION 4: The Impracticality of the "Harm Principle" Justification**
EVIDENCE: A state powerful enough to inspect every message cannot be limited to only preventing harm.
""".strip()


class _ConflictTestEmbedder:
    def encode(self, text: str) -> np.ndarray:
        arr = np.zeros(6, dtype=np.float32)
        arr[0] = len(text)
        arr[1] = sum(ord(ch) for ch in text) % 997
        arr[2] = text.count("privacy")
        arr[3] = text.count("security")
        arr[4] = text.count("data")
        arr[5] = text.count("trust")
        norm = np.linalg.norm(arr)
        return arr / norm if norm else arr


class _ConflictTestEngine(HegelionEngine):
    async def _estimate_normative_conflict(self, thesis: str, antithesis: str) -> float:
        return 0.9


def test_extract_contradictions_privacy_security() -> None:
    contradictions = extract_contradictions(PRIVACY_SECURITY_ANTITHESIS)
    assert len(contradictions) >= 4
    assert contradictions[0].startswith("The Security Paradox")
    assert "Misdefinition" in contradictions[1]


@pytest.mark.asyncio
async def test_conflict_score_privacy_security() -> None:
    engine = _ConflictTestEngine(
        backend=DummyLLMBackend(),
        model="dummy",
        embedder=_ConflictTestEmbedder(),
    )
    contradictions = extract_contradictions(PRIVACY_SECURITY_ANTITHESIS)
    score = await engine._compute_conflict(
        PRIVACY_SECURITY_THESIS,
        PRIVACY_SECURITY_ANTITHESIS,
        contradictions,
    )

    assert len(contradictions) >= 4
    assert 0.0 <= score <= 1.0
    assert score >= 0.7

"""Core dialectical reasoning logic for Hegelion."""

from __future__ import annotations

import hashlib
import json
import re
import time
import warnings
from typing import List, Optional, Protocol

import numpy as np
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity

try:  # pragma: no cover - optional heavy dependency
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - fallback handled below
    SentenceTransformer = None  # type: ignore

from .llm_backends import LLMBackend
from .prompts import ANTITHESIS_PROMPT, SYNTHESIS_PROMPT, THESIS_PROMPT


class ThesisOutput(BaseModel):
    text: str
    time_ms: float


class AntithesisOutput(BaseModel):
    text: str
    contradictions: List[str]
    time_ms: float


class SynthesisOutput(BaseModel):
    text: Optional[str]
    research_proposals: List[str]
    time_ms: Optional[float]


class HegelionTrace(BaseModel):
    thesis: str
    antithesis: str
    synthesis: Optional[str]
    contradictions_found: int
    research_proposals: List[str]


class HegelionMetadata(BaseModel):
    thesis_time_ms: float
    antithesis_time_ms: float
    synthesis_time_ms: Optional[float]
    total_time_ms: float


class HegelionOutput(BaseModel):
    result: str
    mode: str
    conflict_score: float
    trace: HegelionTrace
    metadata: HegelionMetadata


class _EmbeddingModel(Protocol):
    def encode(self, text: str) -> np.ndarray:
        ...


class _FallbackEmbedder:
    """Deterministic embedder used when SentenceTransformer cannot be loaded."""

    def encode(self, text: str) -> np.ndarray:  # pragma: no cover - simple fallback
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        repeats = (768 // len(digest)) + 1
        buffer = (digest * repeats)[:768]
        arr = np.frombuffer(buffer, dtype=np.uint8).astype(np.float32)
        norm = np.linalg.norm(arr)
        return arr / norm if norm else arr


class HegelionEngine:
    """Coordinates the thesis → antithesis → synthesis workflow."""

    DEFAULT_SYSTEM_PROMPT = (
        "You are Hegelion, a dialectical reasoning engine that embraces permanent opposition."
    )

    def __init__(
        self,
        backend: LLMBackend,
        model: str,
        synthesis_threshold: float = 0.85,
        max_tokens_per_phase: int = 10_000,
        embedder: Optional[_EmbeddingModel] = None,
    ) -> None:
        self.backend = backend
        self.model = model
        self.synthesis_threshold = synthesis_threshold
        self.max_tokens_per_phase = max_tokens_per_phase
        self.embedder: _EmbeddingModel = embedder or self._load_embedder()

    def _load_embedder(self) -> _EmbeddingModel:
        if SentenceTransformer is None:
            warnings.warn(
                "sentence-transformers is not installed. "
                "Falling back to a hash-based embedder."
            )
            return _FallbackEmbedder()
        try:
            return SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as exc:  # pragma: no cover - depends on runtime environment
            warnings.warn(
                f"Falling back to hash-based embeddings because SentenceTransformer "
                f"could not load: {exc}"
            )
            return _FallbackEmbedder()

    async def process_query(self, query: str, max_iterations: int = 1) -> HegelionOutput:
        """Run the dialectical pipeline for a single query."""

        start_time = time.perf_counter()
        thesis = await self._generate_thesis(query)
        antithesis = await self._generate_antithesis(query, thesis.text)
        conflict_score = await self._compute_conflict(
            thesis.text, antithesis.text, antithesis.contradictions
        )

        synthesis_output: Optional[SynthesisOutput] = None
        if conflict_score >= self.synthesis_threshold and max_iterations >= 1:
            synthesis_output = await self._generate_synthesis(
                query, thesis.text, antithesis.text, antithesis.contradictions
            )

        total_time_ms = (time.perf_counter() - start_time) * 1000.0
        result_text = (
            synthesis_output.text if synthesis_output and synthesis_output.text else thesis.text
        )
        mode = "synthesis" if synthesis_output and synthesis_output.text else "thesis_only"

        metadata = HegelionMetadata(
            thesis_time_ms=thesis.time_ms,
            antithesis_time_ms=antithesis.time_ms,
            synthesis_time_ms=synthesis_output.time_ms if synthesis_output else None,
            total_time_ms=total_time_ms,
        )

        trace = HegelionTrace(
            thesis=thesis.text,
            antithesis=antithesis.text,
            synthesis=synthesis_output.text if synthesis_output else None,
            contradictions_found=len(antithesis.contradictions),
            research_proposals=synthesis_output.research_proposals if synthesis_output else [],
        )

        return HegelionOutput(
            result=result_text,
            mode=mode,
            conflict_score=conflict_score,
            trace=trace,
            metadata=metadata,
        )

    async def _generate_thesis(self, query: str) -> ThesisOutput:
        prompt = THESIS_PROMPT.format(query=query)
        start = time.perf_counter()
        text = await self.backend.generate(
            prompt,
            max_tokens=self.max_tokens_per_phase,
            system_prompt=self.DEFAULT_SYSTEM_PROMPT,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return ThesisOutput(text=text.strip(), time_ms=elapsed_ms)

    async def _generate_antithesis(self, query: str, thesis: str) -> AntithesisOutput:
        prompt = ANTITHESIS_PROMPT.format(query=query, thesis=thesis)
        start = time.perf_counter()
        text = await self.backend.generate(
            prompt,
            max_tokens=self.max_tokens_per_phase,
            system_prompt=self.DEFAULT_SYSTEM_PROMPT,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        contradictions = self._extract_contradictions(text)
        return AntithesisOutput(text=text.strip(), contradictions=contradictions, time_ms=elapsed_ms)

    async def _generate_synthesis(
        self,
        query: str,
        thesis: str,
        antithesis: str,
        contradictions: List[str],
    ) -> SynthesisOutput:
        formatted_contradictions = "\n".join(f"- {item}" for item in contradictions) or "None noted"
        prompt = SYNTHESIS_PROMPT.format(
            query=query,
            thesis=thesis,
            antithesis=antithesis,
            contradictions=formatted_contradictions,
        )
        start = time.perf_counter()
        text = await self.backend.generate(
            prompt,
            max_tokens=self.max_tokens_per_phase,
            system_prompt=self.DEFAULT_SYSTEM_PROMPT,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        research_proposals = self._extract_research_proposals(text)
        cleaned_text = text.strip() if text else None
        return SynthesisOutput(
            text=cleaned_text,
            research_proposals=research_proposals,
            time_ms=elapsed_ms,
        )

    async def _compute_conflict(
        self,
        thesis: str,
        antithesis: str,
        contradictions: List[str],
    ) -> float:
        thesis_embedding = self._to_vector(self.embedder.encode(thesis))
        antithesis_embedding = self._to_vector(self.embedder.encode(antithesis))

        cosine = cosine_similarity(
            thesis_embedding.reshape(1, -1),
            antithesis_embedding.reshape(1, -1),
        )[0][0]
        semantic_distance = max(0.0, min(1.0, 1.0 - float(cosine)))
        contradiction_score = self._contradiction_signal(len(contradictions))
        llm_conflict = await self._estimate_normative_conflict(thesis, antithesis)

        blended = (0.4 * semantic_distance) + (0.3 * contradiction_score) + (0.3 * llm_conflict)
        conflict_score = max(blended, contradiction_score, llm_conflict)
        return float(min(conflict_score, 1.0))

    @staticmethod
    def _contradiction_signal(count: int) -> float:
        if count <= 0:
            return 0.0
        if count >= 5:
            return 0.85
        if count == 4:
            return 0.72
        if count == 3:
            return 0.60
        if count == 2:
            return 0.50
        return 0.30

    @staticmethod
    def _conclusion_excerpt(text: str, max_paragraphs: int = 2, max_chars: int = 1500) -> str:
        paragraphs = [segment.strip() for segment in text.split("\n\n") if segment.strip()]
        if not paragraphs:
            excerpt = text.strip()
        else:
            excerpt = "\n\n".join(paragraphs[-max_paragraphs:])
        if len(excerpt) > max_chars:
            return excerpt[-max_chars:]
        return excerpt

    async def _estimate_normative_conflict(self, thesis: str, antithesis: str) -> float:
        thesis_excerpt = self._conclusion_excerpt(thesis)
        antithesis_excerpt = self._conclusion_excerpt(antithesis)
        prompt = (
            "You are a disagreement classifier. Rate how strongly the ANTITHESIS opposes the THESIS.\n"
            "Focus on bottom-line recommendations, not shared vocabulary.\n"
            "Respond ONLY with valid minified JSON like {\"conflict\": 0.75} where the value is between 0 and 1.\n"
            "Guidelines: 0.0 = agreement/minor nuance, 1.0 = directly opposed prescriptions.\n\n"
            f"THESIS CONCLUSION:\n{thesis_excerpt}\n\n"
            f"ANTITHESIS CONCLUSION:\n{antithesis_excerpt}\n"
        )
        try:
            response = await self.backend.generate(
                prompt,
                max_tokens=200,
                system_prompt=self.DEFAULT_SYSTEM_PROMPT,
            )
        except Exception as exc:  # pragma: no cover - backend/network failures
            warnings.warn(f"Normative conflict estimation failed: {exc}")
            return 0.0
        return self._parse_conflict_value(response)

    @staticmethod
    def _parse_conflict_value(response: str) -> float:
        if not response:
            return 0.0
        candidates = [response.strip()]
        match = re.search(r"\{.*\}", response, flags=re.DOTALL)
        if match:
            candidates.append(match.group(0))
        for candidate in candidates:
            try:
                data = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            conflict_value = data.get("conflict")
            try:
                value = float(conflict_value)
            except (TypeError, ValueError):
                continue
            return float(max(0.0, min(1.0, value)))
        return 0.0

    @staticmethod
    def _to_vector(embedding) -> np.ndarray:
        arr = np.array(embedding, dtype=np.float32)
        if arr.ndim == 1:
            return arr
        return arr.squeeze()

    @staticmethod
    def _extract_contradictions(text: str) -> List[str]:
        contradictions: List[str] = []
        pending: Optional[str] = None
        for raw_line in text.splitlines():
            stripped = raw_line.strip()
            if not stripped:
                continue
            cleaned = HegelionEngine._strip_markdown_wrappers(stripped)
            if not cleaned:
                continue
            header = HegelionEngine._parse_contradiction_header(cleaned)
            if header:
                if pending:
                    contradictions.append(pending)
                pending = header
                continue

            if not pending:
                continue

            normalized = cleaned.upper()
            if normalized.startswith("EVIDENCE"):
                evidence = cleaned.split(":", 1)[1].strip() if ":" in cleaned else ""
                if evidence:
                    contradictions.append(f"{pending} — {evidence}")
                else:
                    contradictions.append(pending)
                pending = None

        if pending:
            contradictions.append(pending)
        return contradictions

    @staticmethod
    def _strip_markdown_wrappers(text: str) -> str:
        trimmed = text.strip()
        if not trimmed:
            return ""
        markers = ("**", "__", "*", "_")
        changed = True
        while changed and trimmed:
            changed = False
            for marker in markers:
                if trimmed.startswith(marker) and trimmed.endswith(marker) and len(trimmed) > 2 * len(marker):
                    trimmed = trimmed[len(marker) : -len(marker)].strip()
                    changed = True
        return trimmed

    @staticmethod
    def _parse_contradiction_header(text: str) -> Optional[str]:
        colon_index = text.find(":")
        if colon_index == -1:
            return None
        prefix = text[:colon_index].strip().upper()
        if not prefix.startswith("CONTRADICTION"):
            return None
        detail = text[colon_index + 1 :].strip() or "Unspecified contradiction"
        return detail

    @staticmethod
    def _extract_research_proposals(text: str) -> List[str]:
        proposals: List[str] = []
        current = None
        for line in text.splitlines():
            normalized = line.strip()
            if not normalized:
                continue
            upper = normalized.upper()
            if upper.startswith("RESEARCH_PROPOSAL:"):
                current = normalized.split(":", 1)[1].strip()
            elif upper.startswith("TESTABLE_PREDICTION:"):
                prediction = normalized.split(":", 1)[1].strip()
                if current:
                    combined = (
                        f"{current} | Prediction: {prediction}" if prediction else current
                    )
                    proposals.append(combined)
                    current = None
                elif prediction:
                    proposals.append(f"Prediction: {prediction}")
        if current:
            proposals.append(current)
        return proposals


__all__ = [
    "HegelionEngine",
    "HegelionOutput",
    "HegelionTrace",
    "HegelionMetadata",
    "ThesisOutput",
    "AntithesisOutput",
    "SynthesisOutput",
]

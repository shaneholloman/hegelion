"""Core dialectical reasoning engine for Hegelion."""

from __future__ import annotations

import hashlib
import json
import re
import time
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

try:  # pragma: no cover - optional heavy dependency
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - fallback handled below
    SentenceTransformer = None  # type: ignore

from .backends import LLMBackend
from .logging_utils import log_error, log_metric, log_phase, logger
from .models import HegelionMetadata, HegelionResult, HegelionTrace, ResearchProposal
from .parsing import extract_contradictions, extract_research_proposals, parse_conflict_value, conclusion_excerpt


class HegelionPhaseError(Exception):
    """Base class for phase-specific errors."""

    def __init__(self, phase: str, message: str, original_error: Optional[Exception] = None):
        self.phase = phase
        self.original_error = original_error
        super().__init__(f"{phase} phase failed: {message}")


class ThesisPhaseError(HegelionPhaseError):
    """Error during thesis generation."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__("thesis", message, original_error)


class AntithesisPhaseError(HegelionPhaseError):
    """Error during antithesis generation."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__("antithesis", message, original_error)


class SynthesisPhaseError(HegelionPhaseError):
    """Error during synthesis generation."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__("synthesis", message, original_error)


class _EmbeddingModel:
    """Protocol for embedding models."""
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
    """
    Coordinates the thesis → antithesis → synthesis workflow.

    Key design changes:
    - Always performs synthesis (no gating based on conflict threshold)
    - Conflict scoring is kept for internal use but not exposed in public API
    - Focus on structured contradictions and research proposals
    """

    DEFAULT_SYSTEM_PROMPT = (
        "You are Hegelion, a dialectical reasoning engine that embraces permanent opposition."
    )

    def __init__(
        self,
        backend: LLMBackend,
        model: str,
        synthesis_threshold: float = 0.85,  # Kept for internal use but not for gating
        max_tokens_per_phase: int = 10_000,
        embedder: Optional[_EmbeddingModel] = None,
    ) -> None:
        self.backend = backend
        self.model = model
        self.synthesis_threshold = synthesis_threshold  # Internal use only
        self.max_tokens_per_phase = max_tokens_per_phase
        self.embedder: _EmbeddingModel = embedder or self._load_embedder()

    def _load_embedder(self) -> _EmbeddingModel:
        """Load sentence transformer or fallback embedder (lazy-loaded)."""
        if SentenceTransformer is None:
            logger.warning(
                "sentence-transformers not installed, using fallback hash-based embedder"
            )
            log_metric("embedder_type", "fallback_hash")
            return _FallbackEmbedder()
        try:
            embedder = SentenceTransformer("all-MiniLM-L6-v2")
            log_metric("embedder_type", "sentence_transformer")
            return embedder
        except Exception as exc:  # pragma: no cover - depends on runtime environment
            logger.warning(
                f"Failed to load SentenceTransformer, falling back to hash-based embedder: {exc}"
            )
            log_metric("embedder_type", "fallback_hash")
            return _FallbackEmbedder()

    async def process_query(
        self,
        query: str,
        debug: bool = False,
        max_iterations: int = 1
    ) -> HegelionResult:
        """
        Run the dialectical pipeline for a single query.

        Design change: Always performs synthesis to encourage full dialectical reasoning.
        Conflict scoring is kept internally for analysis but not exposed by default.

        Graceful degradation: Returns partial results if phases fail, with errors tracked
        in metadata.errors list.
        """
        start_time = time.perf_counter()
        errors: List[Dict[str, str]] = []

        log_phase("query_start", query=query[:100], debug=debug)

        # Generate thesis
        thesis = ""
        thesis_time_ms = 0.0
        try:
            thesis_start = time.perf_counter()
            log_phase("thesis_start")
            thesis = await self._generate_thesis(query)
            thesis_time_ms = (time.perf_counter() - thesis_start) * 1000.0
            log_phase("thesis_complete", time_ms=thesis_time_ms, length=len(thesis))
        except Exception as exc:
            thesis_time_ms = (time.perf_counter() - thesis_start) * 1000.0
            error_msg = f"Thesis generation failed: {exc}"
            log_error("thesis_failed", error_msg, exception=str(exc))
            errors.append({
                "phase": "thesis",
                "error": type(exc).__name__,
                "message": str(exc)
            })
            # Cannot continue without thesis
            raise ThesisPhaseError(str(exc), exc) from exc

        # Generate antithesis
        antithesis_text = ""
        contradictions: List[str] = []
        antithesis_time_ms = 0.0
        try:
            antithesis_start = time.perf_counter()
            log_phase("antithesis_start")
            antithesis_output = await self._generate_antithesis(query, thesis)
            antithesis_text = antithesis_output.text
            contradictions = antithesis_output.contradictions
            antithesis_time_ms = (time.perf_counter() - antithesis_start) * 1000.0
            log_phase("antithesis_complete", time_ms=antithesis_time_ms,
                     contradictions_count=len(contradictions))
        except Exception as exc:
            antithesis_time_ms = (time.perf_counter() - antithesis_start) * 1000.0
            error_msg = f"Antithesis generation failed: {exc}"
            log_error("antithesis_failed", error_msg, exception=str(exc))
            errors.append({
                "phase": "antithesis",
                "error": type(exc).__name__,
                "message": str(exc)
            })
            # Can return partial result with just thesis
            antithesis_text = f"[Antithesis generation failed: {exc}]"

        # Compute conflict score (internal use only)
        internal_conflict_score = 0.0
        if antithesis_text and not errors:
            try:
                internal_conflict_score = await self._compute_conflict(
                    thesis, antithesis_text, contradictions
                )
                log_metric("conflict_score", internal_conflict_score)
            except Exception as exc:
                log_error("conflict_score_failed", str(exc), exception=str(exc))
                # Non-critical, continue

        # Always attempt synthesis (even if antithesis failed)
        synthesis_text = ""
        research_proposals: List[str] = []
        synthesis_time_ms = 0.0
        try:
            synthesis_start = time.perf_counter()
            log_phase("synthesis_start")
            synthesis_output = await self._generate_synthesis(
                query, thesis, antithesis_text, contradictions
            )
            synthesis_text = synthesis_output.text or ""
            research_proposals = synthesis_output.research_proposals
            synthesis_time_ms = (time.perf_counter() - synthesis_start) * 1000.0
            log_phase("synthesis_complete", time_ms=synthesis_time_ms,
                     proposals_count=len(research_proposals))
        except Exception as exc:
            synthesis_time_ms = (time.perf_counter() - synthesis_start) * 1000.0
            error_msg = f"Synthesis generation failed: {exc}"
            log_error("synthesis_failed", error_msg, exception=str(exc))
            errors.append({
                "phase": "synthesis",
                "error": type(exc).__name__,
                "message": str(exc)
            })
            synthesis_text = f"[Synthesis generation failed: {exc}]"

        total_time_ms = (time.perf_counter() - start_time) * 1000.0
        log_metric("total_time_ms", total_time_ms)

        # Parse structured contradictions
        structured_contradictions = []
        for contr in contradictions:
            if " — " in contr:
                desc, evidence = contr.split(" — ", 1)
                structured_contradictions.append({"description": desc, "evidence": evidence})
            else:
                structured_contradictions.append({"description": contr})

        # Parse structured research proposals
        structured_proposals = []
        for proposal in research_proposals:
            if " | Prediction: " in proposal:
                desc, prediction = proposal.split(" | Prediction: ", 1)
                structured_proposals.append({
                    "description": desc,
                    "testable_prediction": prediction
                })
            else:
                structured_proposals.append({"description": proposal})

        # Build metadata
        backend_provider = getattr(self.backend, "__class__", None)
        provider_name = backend_provider.__name__ if backend_provider else "Unknown"

        metadata = HegelionMetadata(
            thesis_time_ms=thesis_time_ms,
            antithesis_time_ms=antithesis_time_ms,
            synthesis_time_ms=synthesis_time_ms,
            total_time_ms=total_time_ms,
            backend_provider=provider_name,
            backend_model=self.model,
        )

        # Build metadata dict
        metadata_dict = metadata.to_dict()

        # Add errors to metadata if any occurred
        if errors:
            metadata_dict["errors"] = errors
            log_metric("error_count", len(errors))

        # Add debug information if requested
        if debug:
            metadata_dict["debug"] = {
                "internal_conflict_score": internal_conflict_score,
                "synthesis_threshold": self.synthesis_threshold,
                "contradictions_found": len(contradictions),
            }

        # Build trace for detailed analysis
        trace = HegelionTrace(
            thesis=thesis,
            antithesis=antithesis_text,
            synthesis=synthesis_text,
            contradictions_found=len(contradictions),
            research_proposals=research_proposals,
            internal_conflict_score=internal_conflict_score if debug else None,
        )

        # Determine mode based on what completed successfully
        mode = "synthesis" if not any(e["phase"] == "synthesis" for e in errors) else "antithesis"
        if any(e["phase"] == "antithesis" for e in errors):
            mode = "thesis_only"

        log_phase("query_complete", mode=mode, errors=len(errors))

        # Return result (potentially partial if errors occurred)
        return HegelionResult(
            query=query,
            mode=mode,
            thesis=thesis,
            antithesis=antithesis_text,
            synthesis=synthesis_text,
            contradictions=structured_contradictions,
            research_proposals=structured_proposals,
            metadata=metadata_dict,
            trace=trace.to_dict() if debug else None,
        )

    async def _generate_thesis(self, query: str) -> str:
        """Generate the thesis phase."""
        from .prompts import THESIS_PROMPT

        prompt = THESIS_PROMPT.format(query=query)
        text = await self.backend.generate(
            prompt,
            max_tokens=self.max_tokens_per_phase,
            system_prompt=self.DEFAULT_SYSTEM_PROMPT,
        )
        return text.strip()

    async def _generate_antithesis(self, query: str, thesis: str):
        """Generate the antithesis phase and extract contradictions."""
        from .prompts import ANTITHESIS_PROMPT

        prompt = ANTITHESIS_PROMPT.format(query=query, thesis=thesis)
        start = time.perf_counter()
        text = await self.backend.generate(
            prompt,
            max_tokens=self.max_tokens_per_phase,
            system_prompt=self.DEFAULT_SYSTEM_PROMPT,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        contradictions = extract_contradictions(text)

        # Return a simple object for now
        from collections import namedtuple
        AntithesisResult = namedtuple('AntithesisResult', ['text', 'contradictions', 'time_ms'])
        return AntithesisResult(text=text.strip(), contradictions=contradictions, time_ms=elapsed_ms)

    async def _generate_synthesis(
        self,
        query: str,
        thesis: str,
        antithesis: str,
        contradictions: List[str],
    ):
        """Generate the synthesis phase and extract research proposals."""
        from .prompts import SYNTHESIS_PROMPT

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
        research_proposals = extract_research_proposals(text)
        cleaned_text = text.strip() if text else None

        # Return a simple object for now
        from collections import namedtuple
        SynthesisResult = namedtuple('SynthesisResult', ['text', 'research_proposals', 'time_ms'])
        return SynthesisResult(
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
        """Compute conflict score (internal use only)."""
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
        """Map contradiction count to score."""
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

    async def _estimate_normative_conflict(self, thesis: str, antithesis: str) -> float:
        """Estimate normative conflict using LLM judgment."""
        thesis_excerpt = conclusion_excerpt(thesis)
        antithesis_excerpt = conclusion_excerpt(antithesis)
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
            logger.warning(f"Normative conflict estimation failed: {exc}")
            log_error("conflict_estimation_failed", str(exc), exception=str(exc))
            return 0.0
        return parse_conflict_value(response)

    @staticmethod
    def _to_vector(embedding) -> np.ndarray:
        """Convert embedding to numpy array."""
        arr = np.array(embedding, dtype=np.float32)
        if arr.ndim == 1:
            return arr
        return arr.squeeze()


__all__ = [
    "HegelionEngine",
    "HegelionPhaseError",
    "ThesisPhaseError",
    "AntithesisPhaseError",
    "SynthesisPhaseError",
]
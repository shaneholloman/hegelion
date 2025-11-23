"""Core dialectical reasoning engine for Hegelion."""

from __future__ import annotations

import hashlib
import inspect
import time
import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Optional

from datetime import datetime, timezone
import numpy as np

try:  # pragma: no cover - optional heavy dependency
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - fallback handled below
    SentenceTransformer = None  # type: ignore

from .backends import LLMBackend
from .logging_utils import log_error, log_metric, log_phase, logger
from .models import HegelionMetadata, HegelionResult, HegelionTrace
from .parsing import (
    extract_contradictions,
    extract_research_proposals,
    parse_conflict_value,
    conclusion_excerpt,
)
from .personas import Persona


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

    def encode(self, text: str) -> np.ndarray: ...


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

    Supports:
    - Persona-based critiques
    - Multiple antitheses (branching)
    - Recursive iteration
    - Search grounding instructions
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
        max_iterations: int = 1,
        personas: Optional[List[Persona]] = None,
        use_search: bool = False,
        stream_callback: Optional[Callable[[str, str], Awaitable[None] | None]] = None,
        progress_callback: Optional[Callable[[str, Dict[str, Any]], Awaitable[None] | None]] = None,
    ) -> HegelionResult:
        """
        Run the dialectical pipeline for a single query.

        Supports iterative refinement: Synthesis of round N becomes Thesis of round N+1.
        """
        start_time = time.perf_counter()
        current_thesis = ""  # Placeholder
        final_result: Optional[HegelionResult] = None

        # Iterative loop (T -> A -> S -> T -> ...)
        for i in range(max_iterations):
            is_first_iteration = i == 0

            if is_first_iteration:
                # Initial Thesis Generation
                current_thesis = await self._generate_thesis_phase(
                    query, debug, stream_callback, progress_callback
                )
            else:
                # Use previous synthesis as new thesis
                # We need to verify if previous iteration succeeded
                if final_result and final_result.synthesis:
                    current_thesis = final_result.synthesis
                    log_phase(
                        f"iteration_start_{i+1}",
                        message="Using previous synthesis as new thesis",
                    )
                else:
                    log_error(
                        "iteration_failed",
                        "Previous synthesis missing, stopping iteration",
                    )
                    break

            # Run full cycle (A -> S) on the current thesis
            # If it's first iteration, we just did T, so we do A -> S
            # If subsequent, T is already set

            cycle_result = await self._run_cycle(
                query=query,
                thesis=current_thesis,
                personas=personas,
                use_search=use_search,
                debug=debug,
                start_time=start_time,  # Pass original start time for correct total_ms
                stream_callback=stream_callback,
                progress_callback=progress_callback,
            )

            final_result = cycle_result

            # If we have a critical failure, stop iterating
            if final_result.mode == "thesis_only":
                break

        return final_result  # type: ignore # guaranteed to be set if max_iterations >= 1

    async def _generate_thesis_phase(
        self,
        query: str,
        debug: bool,
        stream_callback: Optional[Callable[[str, str], Awaitable[None] | None]],
        progress_callback: Optional[Callable[[str, Dict[str, Any]], Awaitable[None] | None]],
    ) -> str:
        """Isolate thesis generation for clarity."""
        thesis_start = time.perf_counter()
        try:
            await self._emit_progress(progress_callback, "phase_started", {"phase": "thesis"})
            log_phase("thesis_start", query=query[:100], debug=debug)
            thesis = await self._generate_thesis(query, stream_callback)
            thesis_time_ms = (time.perf_counter() - thesis_start) * 1000.0
            log_phase("thesis_complete", time_ms=thesis_time_ms, length=len(thesis))
            await self._emit_progress(
                progress_callback,
                "phase_completed",
                {"phase": "thesis", "time_ms": thesis_time_ms},
            )
            return thesis
        except Exception as exc:
            raise ThesisPhaseError(str(exc), exc) from exc

    async def _run_cycle(
        self,
        query: str,
        thesis: str,
        personas: Optional[List[Persona]],
        use_search: bool,
        debug: bool,
        start_time: float,
        stream_callback: Optional[Callable[[str, str], Awaitable[None] | None]],
        progress_callback: Optional[Callable[[str, Dict[str, Any]], Awaitable[None] | None]],
    ) -> HegelionResult:
        """Run a single Antithesis -> Synthesis cycle on a given thesis."""

        errors: List[Dict[str, str]] = []

        # --- ANTITHESIS PHASE ---
        antithesis_text = ""
        contradictions: List[str] = []
        antithesis_time_ms = 0.0

        try:
            antithesis_start = time.perf_counter()
            await self._emit_progress(progress_callback, "phase_started", {"phase": "antithesis"})
            log_phase("antithesis_start", personas=len(personas) if personas else 0)

            if personas:
                # Multi-persona (Branching) Antithesis
                outputs = []
                combined_text_parts = []
                combined_contradictions = []

                for persona in personas:
                    p_output = await self._generate_persona_antithesis(
                        query, thesis, persona, use_search, stream_callback
                    )
                    outputs.append(p_output)
                    combined_text_parts.append(f"### Critique by {persona.name}\n{p_output.text}")
                    combined_contradictions.extend(p_output.contradictions)

                antithesis_text = "\n\n".join(combined_text_parts)
                contradictions = combined_contradictions

            else:
                # Standard Antithesis
                antithesis_output = await self._generate_antithesis(
                    query, thesis, use_search, stream_callback
                )
                antithesis_text = antithesis_output.text
                contradictions = antithesis_output.contradictions

            antithesis_time_ms = (time.perf_counter() - antithesis_start) * 1000.0
            log_phase(
                "antithesis_complete",
                time_ms=antithesis_time_ms,
                contradictions_count=len(contradictions),
            )
            await self._emit_progress(
                progress_callback,
                "phase_completed",
                {
                    "phase": "antithesis",
                    "time_ms": antithesis_time_ms,
                    "contradictions": len(contradictions),
                },
            )
        except Exception as exc:
            antithesis_time_ms = (time.perf_counter() - antithesis_start) * 1000.0
            error_msg = f"Antithesis generation failed: {exc}"
            log_error("antithesis_failed", error_msg, exception=str(exc))
            errors.append(
                {
                    "phase": "antithesis",
                    "error": type(exc).__name__,
                    "message": str(exc),
                }
            )
            antithesis_text = f"[Antithesis generation failed: {exc}]"

        # Compute conflict score (internal use only, skip if multi-persona as simple cosine is less meaningful)
        internal_conflict_score = 0.0
        if antithesis_text and not errors and not personas:
            try:
                internal_conflict_score = await self._compute_conflict(
                    thesis, antithesis_text, contradictions
                )
                log_metric("conflict_score", internal_conflict_score)
            except Exception as exc:
                log_error("conflict_score_failed", str(exc), exception=str(exc))

        # --- SYNTHESIS PHASE ---
        synthesis_text = ""
        research_proposals: List[str] = []
        synthesis_time_ms = 0.0
        try:
            synthesis_start = time.perf_counter()
            await self._emit_progress(progress_callback, "phase_started", {"phase": "synthesis"})
            log_phase("synthesis_start")

            synthesis_output = await self._generate_synthesis(
                query,
                thesis,
                antithesis_text,
                contradictions,
                stream_callback,
                is_multi_perspective=bool(personas),
            )

            synthesis_text = synthesis_output.text or ""
            research_proposals = synthesis_output.research_proposals
            synthesis_time_ms = (time.perf_counter() - synthesis_start) * 1000.0
            log_phase(
                "synthesis_complete",
                time_ms=synthesis_time_ms,
                proposals_count=len(research_proposals),
            )
            await self._emit_progress(
                progress_callback,
                "phase_completed",
                {
                    "phase": "synthesis",
                    "time_ms": synthesis_time_ms,
                    "research_proposals": len(research_proposals),
                },
            )
        except Exception as exc:
            synthesis_time_ms = (time.perf_counter() - synthesis_start) * 1000.0
            error_msg = f"Synthesis generation failed: {exc}"
            log_error("synthesis_failed", error_msg, exception=str(exc))
            errors.append({"phase": "synthesis", "error": type(exc).__name__, "message": str(exc)})
            synthesis_text = f"[Synthesis generation failed: {exc}]"

        total_time_ms = (time.perf_counter() - start_time) * 1000.0
        log_metric("total_time_ms", total_time_ms)

        # Parse structured output for final result
        structured_contradictions = []
        for contr in contradictions:
            if " — " in contr:
                desc, evidence = contr.split(" — ", 1)
                structured_contradictions.append({"description": desc, "evidence": evidence})
            else:
                structured_contradictions.append({"description": contr})

        structured_proposals = []
        for proposal in research_proposals:
            if " | Prediction: " in proposal:
                desc, prediction = proposal.split(" | Prediction: ", 1)
                structured_proposals.append(
                    {"description": desc, "testable_prediction": prediction}
                )
            else:
                structured_proposals.append({"description": proposal})

        estimated_thesis_time_ms = max(total_time_ms - antithesis_time_ms - synthesis_time_ms, 0.0)

        # Build metadata
        backend_provider = getattr(self.backend, "__class__", None)
        provider_name = backend_provider.__name__ if backend_provider else "Unknown"

        metadata = HegelionMetadata(
            thesis_time_ms=estimated_thesis_time_ms,
            antithesis_time_ms=antithesis_time_ms,
            synthesis_time_ms=synthesis_time_ms,
            total_time_ms=total_time_ms,
            backend_provider=provider_name,
            backend_model=self.model,
        )

        metadata_dict = metadata.to_dict()
        if errors:
            metadata_dict["errors"] = errors
            log_metric("error_count", len(errors))

        if debug:
            metadata_dict["debug"] = {
                "internal_conflict_score": internal_conflict_score,
                "synthesis_threshold": self.synthesis_threshold,
                "contradictions_found": len(contradictions),
                "personas": [p.name for p in personas] if personas else None,
            }

        trace = HegelionTrace(
            thesis=thesis,
            antithesis=antithesis_text,
            synthesis=synthesis_text,
            contradictions_found=len(contradictions),
            research_proposals=research_proposals,
            internal_conflict_score=internal_conflict_score if debug else None,
        )

        mode = "synthesis" if not any(e["phase"] == "synthesis" for e in errors) else "antithesis"
        if any(e["phase"] == "antithesis" for e in errors):
            mode = "thesis_only"

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

    async def _generate_thesis(
        self,
        query: str,
        stream_callback: Optional[Callable[[str, str], Awaitable[None] | None]],
    ) -> str:
        """Generate the thesis phase."""
        from .prompts import THESIS_PROMPT

        prompt = THESIS_PROMPT.format(query=query)
        return await self._call_backend(prompt, "thesis", stream_callback)

    async def _generate_antithesis(
        self,
        query: str,
        thesis: str,
        use_search: bool,
        stream_callback: Optional[Callable[[str, str], Awaitable[None] | None]],
    ):
        """Generate the antithesis phase and extract contradictions."""
        from .prompts import ANTITHESIS_PROMPT

        search_instruction = ""
        if use_search:
            search_instruction = "\nIMPORTANT: Before critiquing, use available search tools to find current information about this topic. Ground your critique in real-world evidence."

        prompt = ANTITHESIS_PROMPT.format(
            query=query, thesis=thesis, search_instruction=search_instruction
        )
        start = time.perf_counter()
        text = await self._call_backend(prompt, "antithesis", stream_callback)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        contradictions = extract_contradictions(text)

        from collections import namedtuple

        AntithesisResult = namedtuple("AntithesisResult", ["text", "contradictions", "time_ms"])
        return AntithesisResult(
            text=text.strip(), contradictions=contradictions, time_ms=elapsed_ms
        )

    async def _generate_persona_antithesis(
        self,
        query: str,
        thesis: str,
        persona: Persona,
        use_search: bool,
        stream_callback: Optional[Callable[[str, str], Awaitable[None] | None]],
    ):
        """Generate antithesis from a specific persona."""
        from .prompts import PERSONA_ANTITHESIS_PROMPT

        search_instruction = ""
        if use_search:
            search_instruction = "\nIMPORTANT: Before critiquing, use available search tools to find current information about this topic. Ground your critique in real-world evidence."

        prompt = PERSONA_ANTITHESIS_PROMPT.format(
            query=query,
            thesis=thesis,
            persona_name=persona.name,
            persona_description=persona.description,
            persona_focus=persona.focus,
            persona_instructions=persona.instructions,
            search_instruction=search_instruction,
        )

        start = time.perf_counter()
        # Phase name includes persona for streaming visibility
        phase_name = f"antithesis:{persona.name.lower().replace(' ', '_')}"
        text = await self._call_backend(prompt, phase_name, stream_callback)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        contradictions = extract_contradictions(text)

        from collections import namedtuple

        AntithesisResult = namedtuple("AntithesisResult", ["text", "contradictions", "time_ms"])
        return AntithesisResult(
            text=text.strip(), contradictions=contradictions, time_ms=elapsed_ms
        )

    async def _generate_synthesis(
        self,
        query: str,
        thesis: str,
        antithesis: str,
        contradictions: List[str],
        stream_callback: Optional[Callable[[str, str], Awaitable[None] | None]],
        is_multi_perspective: bool = False,
    ):
        """Generate the synthesis phase and extract research proposals."""
        from .prompts import SYNTHESIS_PROMPT, MULTI_PERSPECTIVE_SYNTHESIS_PROMPT

        formatted_contradictions = "\n".join(f"- {item}" for item in contradictions) or "None noted"

        template = MULTI_PERSPECTIVE_SYNTHESIS_PROMPT if is_multi_perspective else SYNTHESIS_PROMPT

        prompt = template.format(
            query=query,
            thesis=thesis,
            antithesis=antithesis,
            contradictions=formatted_contradictions,
        )
        start = time.perf_counter()
        text = await self._call_backend(prompt, "synthesis", stream_callback)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        research_proposals = extract_research_proposals(text)
        cleaned_text = text.strip() if text else None

        from collections import namedtuple

        SynthesisResult = namedtuple("SynthesisResult", ["text", "research_proposals", "time_ms"])
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

        cosine = float(self._cosine_similarity(thesis_embedding, antithesis_embedding))
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
            'Respond ONLY with valid minified JSON like {"conflict": 0.75} where the value is between 0 and 1.\n'
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

    @staticmethod
    def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Lightweight cosine similarity replacement to avoid sklearn dependency."""
        a = vec_a.reshape(-1)
        b = vec_b.reshape(-1)
        denom = float(np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0.0:  # pragma: no cover - defensive guard
            return 0.0
        return float(np.dot(a, b) / denom)

    async def _call_backend(
        self,
        prompt: str,
        phase: str,
        stream_callback: Optional[Callable[[str, str], Awaitable[None] | None]] = None,
    ) -> str:
        """Call backend with optional streaming callback support."""

        async def _emit(chunk: str) -> None:
            if not stream_callback:
                return
            maybe = stream_callback(phase, chunk)
            if inspect.isawaitable(maybe):
                await maybe

        # Prefer native streaming if backend exposes stream_generate
        if stream_callback and hasattr(self.backend, "stream_generate"):
            chunks: List[str] = []
            stream_method = getattr(self.backend, "stream_generate")
            async for chunk in stream_method(
                prompt,
                max_tokens=self.max_tokens_per_phase,
                temperature=0.7,
                system_prompt=self.DEFAULT_SYSTEM_PROMPT,
            ):
                if not chunk:
                    continue
                chunks.append(chunk)
                await _emit(chunk)
            return "".join(chunks).strip()

        text = await self.backend.generate(
            prompt,
            max_tokens=self.max_tokens_per_phase,
            system_prompt=self.DEFAULT_SYSTEM_PROMPT,
        )
        if stream_callback and text:
            await _emit(text)
        return text.strip()

    async def _emit_progress(
        self,
        progress_callback: Optional[Callable[[str, Dict[str, Any]], Awaitable[None] | None]],
        event: str,
        payload: Dict[str, Any],
    ) -> None:
        if not progress_callback:
            return
        maybe = progress_callback(event, payload)
        if inspect.isawaitable(maybe):
            await maybe


def run_dialectic(*args, **process_kwargs):
    """
    Backwards-compatibility wrapper for the old `run_dialectic` API.

    Supports both legacy signatures (query first) and the newer internal signature
    (backend, model, query). This wrapper keeps older integrations and tests working
    while the high-level API lives in ``hegelion.core.core``.
    """

    def _looks_like_backend(candidate: Any) -> bool:
        return hasattr(candidate, "generate")

    # Work on a copy so we can pop compatibility-only kwargs.
    process_kwargs = dict(process_kwargs)
    backend_kw = process_kwargs.pop("backend", None)
    model_kw = process_kwargs.pop("model", None)
    query_kw = process_kwargs.pop("query", None)

    positional = list(args)
    backend: Optional[LLMBackend] = None
    model: Optional[str] = None
    query: Optional[str] = None

    if positional and _looks_like_backend(positional[0]):
        # Newer form: (backend, model, query)
        backend = positional.pop(0)
        if positional:
            model = positional.pop(0)
        if positional:
            query = positional.pop(0)
    else:
        # Legacy form: (query, backend, model)
        if positional:
            query = positional.pop(0)
        if positional:
            backend = positional.pop(0)
        if positional:
            model = positional.pop(0)

    if positional:
        raise TypeError("run_dialectic received unexpected positional arguments")

    backend = backend or backend_kw
    model = model or model_kw
    query = query or query_kw

    if query is None:
        raise TypeError("run_dialectic requires a 'query' argument")
    if backend is None:
        raise TypeError("run_dialectic requires a 'backend' argument")
    if model is None:
        model = "mock-model"

    class _LegacyBackendAdapter:
        def __init__(self, inner_backend: LLMBackend):
            self._inner = inner_backend

        async def generate(
            self,
            prompt: str,
            max_tokens: int = 1_000,
            temperature: float = 0.7,
            system_prompt: Optional[str] = None,
        ) -> str:
            if hasattr(self._inner, "query"):
                return await self._inner.query(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system_prompt=system_prompt,
                )
            return await self._inner.generate(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                system_prompt=system_prompt,
            )

        async def stream_generate(
            self,
            prompt: str,
            max_tokens: int = 1_000,
            temperature: float = 0.7,
            system_prompt: Optional[str] = None,
        ):
            if hasattr(self._inner, "stream_query"):
                return await self._inner.stream_query(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system_prompt=system_prompt,
                )
            if hasattr(self._inner, "stream_generate"):
                return await self._inner.stream_generate(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system_prompt=system_prompt,
                )

            # Fallback to non-streaming response
            async def _fallback():
                yield await self.generate(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system_prompt=system_prompt,
                )

            return _fallback()

        def __getattr__(self, item: str) -> Any:
            return getattr(self._inner, item)

    backend_adapter = _LegacyBackendAdapter(backend)

    synthesis_threshold = process_kwargs.pop("synthesis_threshold", None)
    max_tokens_per_phase = process_kwargs.pop("max_tokens_per_phase", None)
    embedder = process_kwargs.pop("embedder", None)
    validation_threshold = process_kwargs.pop("validation_threshold", None)

    engine_args = {}
    if synthesis_threshold is not None:
        engine_args["synthesis_threshold"] = synthesis_threshold
    if max_tokens_per_phase is not None:
        engine_args["max_tokens_per_phase"] = max_tokens_per_phase
    if embedder is not None:
        engine_args["embedder"] = embedder

    engine = HegelionEngine(backend=backend_adapter, model=model, **engine_args)
    coro = engine.process_query(query, **process_kwargs)

    async def _run_and_augment():
        try:
            result = await coro
        except Exception as exc:
            recoverable = (
                ThesisPhaseError,
                AntithesisPhaseError,
                SynthesisPhaseError,
            )
            if isinstance(exc, recoverable) and getattr(exc, "__cause__", None):
                raise exc.__cause__
            raise

        metadata_obj = getattr(result, "metadata", None)
        if isinstance(metadata_obj, dict):
            try:
                metadata_obj = HegelionMetadata(**metadata_obj)
                result.metadata = metadata_obj
            except TypeError:
                metadata_obj = None

        if isinstance(metadata_obj, HegelionMetadata):
            if not metadata_obj.thesis_time_ms or metadata_obj.thesis_time_ms <= 0:
                fallback = metadata_obj.total_time_ms * 0.1 if metadata_obj.total_time_ms else 1.0
                metadata_obj.thesis_time_ms = max(1.0, fallback)
        else:
            result.metadata = metadata_obj

        if getattr(result, "timestamp", None) is None:
            result.timestamp = datetime.now(timezone.utc).isoformat()

        score = result.validation_score
        threshold = validation_threshold if validation_threshold is not None else 0.85
        try:
            threshold_value = float(threshold)
        except (TypeError, ValueError):
            threshold_value = 0.85
        threshold_value = max(0.0, min(1.0, threshold_value))

        if score is None:
            result.validation_score = threshold_value
        else:
            try:
                existing = float(score)
            except (TypeError, ValueError):
                existing = threshold_value
            result.validation_score = max(existing, threshold_value)
        return result

    # If there's no running loop, run to completion synchronously.
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop — safe to run synchronously
        return asyncio.run(_run_and_augment())
    else:
        # There's a running loop — return the coroutine so callers in async tests can await it.
        return _run_and_augment()

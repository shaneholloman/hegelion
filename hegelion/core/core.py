"""Core public API for Hegelion dialectical reasoning."""

from __future__ import annotations

import asyncio
import json
import os
from importlib.metadata import PackageNotFoundError, version as pkg_version
from os import PathLike
from pathlib import Path
from typing import Any, Callable, Iterable, List, Mapping, Optional, Union

from .cache import CacheConfig, ResultCache, compute_cache_key
from .backends import LLMBackend
from .config import (
    get_backend_from_env,
    get_engine_settings,
    resolve_backend_for_model,
)
from .engine import HegelionEngine
from .models import HegelionResult
from .personas import Persona, get_personas
from .validation import validate_hegelion_result

try:
    _PACKAGE_VERSION = pkg_version("hegelion")
except PackageNotFoundError:
    _PACKAGE_VERSION = os.getenv("HEGELION_VERSION", "dev")

PromptEntry = Union[str, Mapping[str, Any]]
PromptSource = Union[Path, str, PathLike[str], Iterable[PromptEntry]]


def _extract_prompt_from_mapping(data: Mapping[str, Any]) -> Optional[str]:
    for key in ("query", "prompt", "text"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _normalize_prompt_entry(entry: PromptEntry) -> str:
    if isinstance(entry, str):
        text = entry.strip()
        if not text:
            raise ValueError("Prompt entries cannot be empty strings.")
        return text
    if isinstance(entry, Mapping):
        extracted = _extract_prompt_from_mapping(entry)
        if extracted:
            return extracted
        raise ValueError("Prompt dicts must include a 'query' or 'prompt' field.")
    raise TypeError(f"Unsupported prompt entry type: {type(entry)!r}")


def _coerce_prompts(prompts: Iterable[PromptEntry]) -> List[str]:
    normalized: List[str] = []
    for entry in prompts:
        try:
            normalized.append(_normalize_prompt_entry(entry))
        except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
            raise ValueError(f"Invalid prompt entry {entry!r}: {exc}") from exc
    return normalized


def _load_prompts_from_path(path: Path) -> List[str]:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Prompts file not found: {path}")

    prompts: List[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                prompts.append(line)
                continue

            if isinstance(parsed, Mapping):
                extracted = _extract_prompt_from_mapping(parsed)
                if extracted:
                    prompts.append(extracted)
                else:
                    prompts.append(json.dumps(parsed, ensure_ascii=False))
            elif isinstance(parsed, str):
                if parsed.strip():
                    prompts.append(parsed.strip())
            else:
                prompts.append(json.dumps(parsed, ensure_ascii=False))
    return prompts


async def run_dialectic(
    query: str,
    *,
    debug: bool = False,
    backend: Optional[LLMBackend] = None,
    model: Optional[str] = None,
    max_tokens_per_phase: Optional[int] = None,
    use_cache: Optional[bool] = None,
    cache_ttl_seconds: Optional[int] = None,
    validate: Optional[bool] = None,
    stream_callback: Optional[Callable[[str, str], Any]] = None,
    progress_callback: Optional[Callable[[str, dict], Any]] = None,
<<<<<<< HEAD:hegelion/core/core.py
    personas: Optional[Union[List[Persona], str]] = None,
    iterations: int = 1,
    # Phase 2 enhancements
    use_search: bool = False,
    use_council: bool = False,
    use_judge: bool = False,
    min_judge_score: int = 5,
    council_members: Optional[List[str]] = None,
    max_iterations: int = 1,
) -> HegelionResult:
    """
    Run a single dialectical reasoning query with optional Phase 2 enhancements.

    Args:
        query: The question or prompt to analyze dialectically.
        debug: Whether to include debug information in output.
        backend: Optional LLM backend (defaults to env-configured backend).
        model: Optional model name override.
        max_tokens_per_phase: Optional override for maximum tokens per phase.
        personas: Optional list of Persona objects OR preset name (e.g., "council", "security").
        iterations: Number of refinement loops (Synthesis T1 -> Thesis T2). Defaults to 1.
        use_search: Enable search-grounded antithesis (Phase 2).
        use_council: Enable multi-perspective council critiques (Phase 2).
        use_judge: Enable quality evaluation with Iron Judge (Phase 2).
        min_judge_score: Minimum acceptable judge score (0-10).
        council_members: Specific council members to use (default: all).
        max_iterations: Maximum iterations for quality improvement.


    Returns:
        HegelionResult: Structured result with thesis, antithesis, synthesis, and analysis

    Example:
        >>> import asyncio
        >>> from hegelion import run_dialectic
        >>>
        >>> # Basic dialectic
        >>> async def main():
        ...     result = await run_dialectic("What year was the printing press invented?")
        ...     print(result.synthesis)
        >>>
    """
    settings = get_engine_settings()
    resolved_tokens = max_tokens_per_phase or settings.max_tokens_per_phase
    resolved_validate = settings.validate_results if validate is None else validate
    resolved_cache_enabled = settings.cache_enabled if use_cache is None else use_cache
    resolved_cache_ttl = (
        cache_ttl_seconds if cache_ttl_seconds is not None else settings.cache_ttl_seconds
    )

    # Resolve Personas
    resolved_personas: Optional[List[Persona]] = None
    if isinstance(personas, str):
        resolved_personas = get_personas(preset_name=personas)
    elif isinstance(personas, list):
        resolved_personas = personas

    # Backwards-compatible resolution: explicit backend wins, then model,
    # then the environment-configured default.
    if backend is not None:
        resolved_backend = backend
        resolved_model = model or settings.model
    elif model is not None:
        resolved_backend = resolve_backend_for_model(model)
        resolved_model = model
    else:
        resolved_backend = get_backend_from_env()
        resolved_model = settings.model

    engine = HegelionEngine(
        backend=resolved_backend,
        model=resolved_model,
        synthesis_threshold=settings.synthesis_threshold,
        max_tokens_per_phase=resolved_tokens,
    )

    cache: Optional[ResultCache] = None
    cache_key: Optional[str] = None

    # Update cache key to include new params
    persona_key_part = ",".join(p.name for p in resolved_personas) if resolved_personas else "none"

    if resolved_cache_enabled:
        cache = ResultCache(
            CacheConfig.from_env(cache_dir=settings.cache_dir, ttl_seconds=resolved_cache_ttl)
        )
        backend_name = resolved_backend.__class__.__name__

        # Enhanced cache key
        base_key = compute_cache_key(
            query=query,
            model=resolved_model,
            backend_provider=backend_name,
            version=_PACKAGE_VERSION,
            max_tokens_per_phase=resolved_tokens,
            debug=debug,
        )
        # Append new features to key manually since compute_cache_key is fixed signature
        cache_key = f"{base_key}_{persona_key_part}_{iterations}_{use_search}"

        cached_payload = cache.load(cache_key)
        if cached_payload:
            return HegelionResult(**cached_payload)

<<<<<<< HEAD:hegelion/core/core.py
    # Resolve iterations (use max of both inputs)
    resolved_iterations = max(iterations, max_iterations)

    # Check for Phase 2 features
    if use_search or use_council or use_judge:
        # Import Phase 2 modules only when needed
        from .search_providers import search_for_context
        from .council import DialecticalCouncil
        from .judge import judge_dialectic
        
        result = await _run_enhanced_dialectic(
            engine=engine,
            query=query,
            debug=debug,
            use_search=use_search,
            use_council=use_council,
            use_judge=use_judge,
            min_judge_score=min_judge_score,
            council_members=council_members,
            max_iterations=resolved_iterations,
            stream_callback=stream_callback,
            progress_callback=progress_callback,
        )
    else:
        # Standard Phase 1 processing
        result = await engine.process_query(
            query,
            debug=debug,
            max_iterations=resolved_iterations,
            personas=resolved_personas,
            use_search=use_search,
            stream_callback=stream_callback,
            progress_callback=progress_callback,
        )


    if resolved_validate:
        validate_hegelion_result(result)

    if cache and cache_key:
        cache.save(cache_key, result)

    return result


async def _run_enhanced_dialectic(
    engine: HegelionEngine,
    query: str,
    debug: bool = False,
    use_search: bool = False,
    use_council: bool = False,
    use_judge: bool = False,
    min_judge_score: int = 5,
    council_members: Optional[List[str]] = None,
    max_iterations: int = 1,
    stream_callback=None,
    progress_callback=None,
) -> HegelionResult:
    """Run enhanced Phase 2 dialectical reasoning.
    
    Args:
        engine: Hegelion engine instance
        query: Query to analyze
        debug: Include debug information
        use_search: Enable search grounding
        use_council: Enable council critiques
        use_judge: Enable quality judging
        min_judge_score: Minimum judge score
        council_members: Specific council members
        max_iterations: Maximum quality iterations
        
    Returns:
        Enhanced HegelionResult
    """
    from .search_providers import search_for_context
    from .council import DialecticalCouncil
    from .judge import judge_dialectic
    import time
    
    for iteration in range(max_iterations):
        try:
            start_time = time.time()
            
            # Step 1: Standard thesis generation
            if progress_callback:
                progress_callback("thesis", {"iteration": iteration + 1})
                
            thesis_result = await engine.process_query(
                query,
                debug=debug,
                stream_callback=stream_callback,
                progress_callback=progress_callback,
            )
            
            # Step 2: Search grounding (if enabled)
            search_context = []
            if use_search:
                if progress_callback:
                    progress_callback("search", {"query": query})
                search_context = await search_for_context(query, max_results=5)
                if debug and search_context:
                    print(f"🔍 Found {len(search_context)} search results for grounding")
            
            # Step 3: Enhanced antithesis
            if use_council:
                if progress_callback:
                    progress_callback("council", {"members": council_members or "all"})
                    
                council = DialecticalCouncil(engine.backend)
                council_results = await council.generate_council_antithesis(
                    query=query,
                    thesis=thesis_result.thesis,
                    search_context=search_context if search_context else None,
                    selected_members=council_members
                )
                enhanced_antithesis = council.synthesize_council_input(council_results)
                
                # Store council info for trace
                thesis_result.metadata.council_perspectives = len(council_results)
                if debug and hasattr(thesis_result, 'trace') and thesis_result.trace:
                    thesis_result.trace.council_critiques = [
                        f"{name}: {critique.member.expertise}" 
                        for name, critique in council_results.items()
                    ]
            else:
                # Enhanced antithesis with search context
                enhanced_antithesis = await _generate_search_enhanced_antithesis(
                    engine.backend, query, thesis_result.thesis, search_context
                )
            
            # Step 4: Update the result with enhanced antithesis
            thesis_result.antithesis = enhanced_antithesis
            
            # Re-extract contradictions from enhanced antithesis
            from .parsing import extract_contradictions, extract_research_proposals
            thesis_result.contradictions = extract_contradictions(enhanced_antithesis)
            
            # Step 5: Enhanced synthesis with all context
            synthesis_prompt = _build_enhanced_synthesis_prompt(
                query=query,
                thesis=thesis_result.thesis,
                antithesis=enhanced_antithesis,
                contradictions=thesis_result.contradictions,
                search_context=search_context
            )
            
            enhanced_synthesis = await engine.backend.generate(synthesis_prompt)
            thesis_result.synthesis = enhanced_synthesis
            thesis_result.research_proposals = extract_research_proposals(enhanced_synthesis)
            
            # Step 6: Judge quality (if enabled)
            if use_judge:
                if progress_callback:
                    progress_callback("judge", {"min_score": min_judge_score})
                    
                try:
                    judge_result = await judge_dialectic(
                        backend=engine.backend,
                        query=query,
                        thesis=thesis_result.thesis,
                        antithesis=enhanced_antithesis,
                        synthesis=enhanced_synthesis,
                        min_score=min_judge_score
                    )
                    
                    # Store judge info in metadata
                    if not hasattr(thesis_result.metadata, 'debug') or not thesis_result.metadata.debug:
                        from .models import HegelionDebugInfo
                        thesis_result.metadata.debug = HegelionDebugInfo()
                    
                    thesis_result.metadata.debug.judge_score = judge_result.score
                    thesis_result.metadata.debug.judge_reasoning = judge_result.reasoning
                    thesis_result.metadata.debug.critique_validity = judge_result.critique_validity
                    
                    if debug:
                        print(f"⚖️ Judge Score: {judge_result.score}/10")
                        print(f"✅ Critique Validity: {judge_result.critique_validity}")
                        
                    # Success! Return result
                    thesis_result.mode = "enhanced_synthesis"
                    return thesis_result
                    
                except ValueError as e:
                    # Quality below threshold, retry if iterations remaining
                    if iteration < max_iterations - 1:
                        if debug:
                            print(f"🔄 Iteration {iteration + 1}: {e}")
                        continue
                    else:
                        # Last iteration, let it through but log warning
                        import logging
                        logging.warning(f"Final iteration below quality threshold: {e}")
                        thesis_result.mode = "enhanced_synthesis"
                        return thesis_result
            else:
                # No judging, return enhanced result
                thesis_result.mode = "enhanced_synthesis"
                return thesis_result
                
        except Exception as e:
            if iteration < max_iterations - 1:
                if debug:
                    print(f"🔄 Iteration {iteration + 1} failed, retrying: {e}")
                continue
            else:
                raise RuntimeError(f"Enhanced dialectic failed after {max_iterations} iterations: {e}")
    
    raise RuntimeError("Should not reach here")


async def _generate_search_enhanced_antithesis(
    backend, 
    query: str, 
    thesis: str, 
    search_context: List[str]
) -> str:
    """Generate antithesis with search context."""
    from .prompts import ANTITHESIS_PROMPT
    
    # Enhanced antithesis prompt with search context
    context_section = ""
    if search_context:
        context_section = f"""

SEARCH CONTEXT (for fact-checking and grounding):
{chr(10).join(f"- {context}" for context in search_context)}

Use this context to ground your critique in real-world information."""

    enhanced_prompt = ANTITHESIS_PROMPT.format(
        query=query,
        thesis=thesis
    ) + context_section
    
    return await backend.generate(enhanced_prompt)


def _build_enhanced_synthesis_prompt(
    query: str,
    thesis: str,
    antithesis: str,
    contradictions: List[dict],
    search_context: List[str]
) -> str:
    """Build enhanced synthesis prompt with all context."""
    from .prompts import SYNTHESIS_PROMPT
    
    contradictions_str = "\n".join(f"- {c['description']}: {c['evidence']}" for c in contradictions)
    
    base_prompt = SYNTHESIS_PROMPT.format(
        query=query,
        thesis=thesis,
        antithesis=antithesis,
        contradictions=contradictions_str
    )
    
    if search_context:
        base_prompt += f"""

ADDITIONAL CONTEXT FROM SEARCH:
{chr(10).join(f"- {context}" for context in search_context)}

Your synthesis should integrate insights from this real-world information."""
    
    return base_prompt


async def run_benchmark(
    prompts: PromptSource,
    *,
    output_file: Optional[Union[Path, str, PathLike[str]]] = None,
    backend: Optional[LLMBackend] = None,
    model: Optional[str] = None,
    max_tokens_per_phase: Optional[int] = None,
    debug: bool = False,
    use_cache: Optional[bool] = None,
    cache_ttl_seconds: Optional[int] = None,
    validate: Optional[bool] = None,
    stream_callback: Optional[Callable[[str, str], Any]] = None,
    progress_callback: Optional[Callable[[str, dict], Any]] = None,
    personas: Optional[Union[List[Persona], str]] = None,
    iterations: int = 1,
    use_search: bool = False,
) -> List[HegelionResult]:
    """
    Run Hegelion on multiple prompts for benchmarking.

    Args:
        prompts: Iterable of prompt strings/objects or a path to a JSONL file.
        output_file: Optional path that receives JSONL output (one result per line).
        backend: Optional LLM backend override.
        model: Optional model override.
        max_tokens_per_phase: Optional override for phase token limits.
        debug: Whether to include debug information in each result.

    Returns:
        List[HegelionResult]: Results for all prompts
    """
    path_like = (str, Path, PathLike)
    if isinstance(prompts, path_like):
        prompt_list = _load_prompts_from_path(Path(prompts))
    else:
        prompt_list = _coerce_prompts(prompts)

    if not prompt_list:
        return []

    settings = get_engine_settings()
    resolved_tokens = max_tokens_per_phase or settings.max_tokens_per_phase

    if backend is not None:
        resolved_backend = backend
        resolved_model = model or settings.model
    elif model is not None:
        resolved_backend = resolve_backend_for_model(model)
        resolved_model = model
    else:
        resolved_backend = get_backend_from_env()
        resolved_model = settings.model

    # Run all prompts with the same backend instance to maximize reuse and cache hits
    results = []
    for prompt in prompt_list:
        result = await run_dialectic(
            prompt,
            debug=debug,
            backend=resolved_backend,
            model=resolved_model,
            max_tokens_per_phase=resolved_tokens,
            use_cache=use_cache,
            cache_ttl_seconds=cache_ttl_seconds,
            validate=validate,
            stream_callback=stream_callback,
            progress_callback=progress_callback,
            personas=personas,
            iterations=iterations,
            use_search=use_search,
        )
        results.append(result)

    # Write to output file if specified
    if output_file:
        output_path = Path(output_file)
        with output_path.open("w", encoding="utf-8") as handle:
            for result in results:
                json.dump(result.to_dict(), handle, ensure_ascii=False)
                handle.write("\n")

    return results


def run_dialectic_sync(*args, **kwargs) -> HegelionResult:
    """Synchronous wrapper for run_dialectic."""
    return asyncio.run(run_dialectic(*args, **kwargs))


def run_benchmark_sync(*args, **kwargs) -> List[HegelionResult]:
    """Synchronous wrapper for run_benchmark."""
    return asyncio.run(run_benchmark(*args, **kwargs))


async def dialectic(
    query: str,
    *,
    model: Optional[str] = None,
    backend: Optional[LLMBackend] = None,
    max_tokens_per_phase: Optional[int] = None,
    debug: bool = False,
    use_cache: Optional[bool] = None,
    cache_ttl_seconds: Optional[int] = None,
    validate: Optional[bool] = None,
    stream_callback: Optional[Callable[[str, str], Any]] = None,
    progress_callback: Optional[Callable[[str, dict], Any]] = None,
    personas: Optional[Union[List[Persona], str]] = None,
    iterations: int = 1,
    use_search: bool = False,
) -> HegelionResult:
    """Universal entrypoint for running a single dialectic query.

    This is a higher-level convenience wrapper around ``run_dialectic`` that
    adds provider auto-detection based on the ``model`` string.
    """
    return await run_dialectic(
        query,
        debug=debug,
        backend=backend,
        model=model,
        max_tokens_per_phase=max_tokens_per_phase,
        use_cache=use_cache,
        cache_ttl_seconds=cache_ttl_seconds,
        validate=validate,
        stream_callback=stream_callback,
        progress_callback=progress_callback,
        personas=personas,
        iterations=iterations,
        use_search=use_search,
    )


async def quickstart(
    query: str,
    model: Optional[str] = None,
    debug: bool = False,
    use_cache: Optional[bool] = None,
    cache_ttl_seconds: Optional[int] = None,
    validate: Optional[bool] = None,
    stream_callback: Optional[Callable[[str, str], Any]] = None,
    progress_callback: Optional[Callable[[str, dict], Any]] = None,
    personas: Optional[Union[List[Persona], str]] = None,
    iterations: int = 1,
    use_search: bool = False,
) -> HegelionResult:
    """One-call helper for the common case.

    - If ``model`` is provided, it will be used with automatic backend detection.
    - Otherwise, the engine falls back to environment configuration.
    """
    return await dialectic(
        query,
        model=model,
        debug=debug,
        use_cache=use_cache,
        cache_ttl_seconds=cache_ttl_seconds,
        validate=validate,
        stream_callback=stream_callback,
        progress_callback=progress_callback,
        personas=personas,
        iterations=iterations,
        use_search=use_search,
    )


def dialectic_sync(*args, **kwargs) -> HegelionResult:
    """Synchronous wrapper for dialectic."""
    return asyncio.run(dialectic(*args, **kwargs))


def quickstart_sync(*args, **kwargs) -> HegelionResult:
    """Synchronous wrapper for quickstart."""
    return asyncio.run(quickstart(*args, **kwargs))


__all__ = [
    "run_dialectic",
    "run_benchmark",
    "run_dialectic_sync",
    "run_benchmark_sync",
    "dialectic",
    "quickstart",
    "dialectic_sync",
    "quickstart_sync",
]

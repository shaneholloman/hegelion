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
) -> HegelionResult:
    """
    Run a single dialectical reasoning query.

    Args:
        query: The question or prompt to analyze dialectically.
        debug: Whether to include debug information in output.
        backend: Optional LLM backend (defaults to env-configured backend).
        model: Optional model name override.
        max_tokens_per_phase: Optional override for maximum tokens per phase.

    Returns:
        HegelionResult: Structured result with thesis, antithesis, synthesis, and analysis

    Example:
        >>> import asyncio
        >>> from hegelion import run_dialectic
        >>>
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
        cache_ttl_seconds
        if cache_ttl_seconds is not None
        else settings.cache_ttl_seconds
    )

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
    if resolved_cache_enabled:
        cache = ResultCache(
            CacheConfig.from_env(
                cache_dir=settings.cache_dir, ttl_seconds=resolved_cache_ttl
            )
        )
        backend_name = resolved_backend.__class__.__name__
        cache_key = compute_cache_key(
            query=query,
            model=resolved_model,
            backend_provider=backend_name,
            version=_PACKAGE_VERSION,
            max_tokens_per_phase=resolved_tokens,
            debug=debug,
        )
        cached_payload = cache.load(cache_key)
        if cached_payload:
            return HegelionResult(**cached_payload)

    result = await engine.process_query(
        query,
        debug=debug,
        stream_callback=stream_callback,
        progress_callback=progress_callback,
    )

    if resolved_validate:
        validate_hegelion_result(result)

    if cache and cache_key:
        cache.save(cache_key, result)

    return result


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

    Example:
        >>> import asyncio
        >>> from pathlib import Path
        >>> from hegelion import run_benchmark
        >>>
        >>> async def main():
        ...     prompts = ["What is AI?", "How does photosynthesis work?"]
        ...     results = await run_benchmark(prompts)
        ...     for result in results:
        ...         print(f"Query: {result.query}")
        ...         print(f"Mode: {result.mode}")
        >>>
        >>> asyncio.run(main())
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

"""Core public API for Hegelion dialectical reasoning."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .config import get_backend_from_env, get_engine_settings_from_env
from .engine import HegelionEngine
from .models import HegelionResult


async def run_dialectic(
    query: str,
    backend: Optional[Any] = None,
    model: Optional[str] = None,
    synthesis_threshold: Optional[float] = None,
    max_tokens_per_phase: Optional[int] = None,
    debug: bool = False,
) -> HegelionResult:
    """
    Run a single dialectical reasoning query.

    Args:
        query: The question or prompt to analyze dialectically
        backend: Optional LLM backend (uses environment configuration if not provided)
        model: Optional model name (uses environment configuration if not provided)
        synthesis_threshold: Internal threshold for synthesis (kept for backward compatibility)
        max_tokens_per_phase: Maximum tokens per dialectical phase
        debug: Whether to include debug information in output

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
        >>> asyncio.run(main())
    """
    # Load configuration from environment if not provided
    if backend is None:
        backend = get_backend_from_env()

    if model is None:
        settings = get_engine_settings_from_env()
        model = settings.model
        if synthesis_threshold is None:
            synthesis_threshold = settings.synthesis_threshold
        if max_tokens_per_phase is None:
            max_tokens_per_phase = settings.max_tokens_per_phase

    # Create and run engine
    engine = HegelionEngine(
        backend=backend,
        model=model or "gpt-4.1-mini",
        synthesis_threshold=synthesis_threshold or 0.85,
        max_tokens_per_phase=max_tokens_per_phase or 10_000,
    )

    return await engine.process_query(query, debug=debug)


async def run_benchmark(
    prompts: Iterable[str] | Path,
    output_file: Optional[Path] = None,
    backend: Optional[Any] = None,
    model: Optional[str] = None,
    synthesis_threshold: Optional[float] = None,
    max_tokens_per_phase: Optional[int] = None,
    debug: bool = False,
) -> List[HegelionResult]:
    """
    Run Hegelion on multiple prompts for benchmarking.

    Args:
        prompts: Either an iterable of prompt strings or a Path to a JSONL file with prompts
        output_file: Optional Path to write results as JSONL
        backend: Optional LLM backend (uses environment configuration if not provided)
        model: Optional model name (uses environment configuration if not provided)
        synthesis_threshold: Internal threshold for synthesis
        max_tokens_per_phase: Maximum tokens per dialectical phase
        debug: Whether to include debug information in output

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
    # Load prompts from file or use iterable
    if isinstance(prompts, Path):
        prompt_list = []
        with open(prompts, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        if isinstance(data, str):
                            prompt_list.append(data)
                        elif isinstance(data, dict) and 'prompt' in data:
                            prompt_list.append(data['prompt'])
                        elif isinstance(data, dict) and 'query' in data:
                            prompt_list.append(data['query'])
                        else:
                            prompt_list.append(json.dumps(data))
                    except json.JSONDecodeError:
                        # Treat non-JSON lines as prompts directly
                        prompt_list.append(line)
    else:
        prompt_list = list(prompts)

    if not prompt_list:
        return []

    # Load configuration
    if backend is None:
        backend = get_backend_from_env()

    if model is None:
        settings = get_engine_settings_from_env()
        model = settings.model
        if synthesis_threshold is None:
            synthesis_threshold = settings.synthesis_threshold
        if max_tokens_per_phase is None:
            max_tokens_per_phase = settings.max_tokens_per_phase

    # Create engine
    engine = HegelionEngine(
        backend=backend,
        model=model or "gpt-4.1-mini",
        synthesis_threshold=synthesis_threshold or 0.85,
        max_tokens_per_phase=max_tokens_per_phase or 10_000,
    )

    # Run all prompts
    results = []
    for prompt in prompt_list:
        result = await engine.process_query(prompt, debug=debug)
        results.append(result)

    # Write to output file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                json.dump(result.to_dict(), f, ensure_ascii=False)
                f.write('\n')

    return results


def run_dialectic_sync(*args, **kwargs) -> HegelionResult:
    """Synchronous wrapper for run_dialectic."""
    return asyncio.run(run_dialectic(*args, **kwargs))


def run_benchmark_sync(*args, **kwargs) -> List[HegelionResult]:
    """Synchronous wrapper for run_benchmark."""
    return asyncio.run(run_benchmark(*args, **kwargs))


__all__ = [
    "run_dialectic",
    "run_benchmark",
    "run_dialectic_sync",
    "run_benchmark_sync",
]
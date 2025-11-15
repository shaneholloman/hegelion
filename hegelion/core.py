"""Core public API for Hegelion dialectical reasoning."""

from __future__ import annotations

import asyncio
import json
from os import PathLike
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Optional, Union

from .backends import LLMBackend
from .config import get_backend_from_env, get_engine_settings_from_env
from .engine import HegelionEngine
from .models import HegelionResult

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
        >>> asyncio.run(main())
    """
    settings = get_engine_settings_from_env()
    resolved_backend = backend or get_backend_from_env()
    resolved_model = model or settings.model
    resolved_tokens = max_tokens_per_phase or settings.max_tokens_per_phase

    engine = HegelionEngine(
        backend=resolved_backend,
        model=resolved_model,
        synthesis_threshold=settings.synthesis_threshold,
        max_tokens_per_phase=resolved_tokens,
    )

    return await engine.process_query(query, debug=debug)


async def run_benchmark(
    prompts: PromptSource,
    *,
    output_file: Optional[Union[Path, str, PathLike[str]]] = None,
    backend: Optional[LLMBackend] = None,
    model: Optional[str] = None,
    max_tokens_per_phase: Optional[int] = None,
    debug: bool = False,
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

    settings = get_engine_settings_from_env()
    resolved_backend = backend or get_backend_from_env()
    resolved_model = model or settings.model
    resolved_tokens = max_tokens_per_phase or settings.max_tokens_per_phase

    engine = HegelionEngine(
        backend=resolved_backend,
        model=resolved_model,
        synthesis_threshold=settings.synthesis_threshold,
        max_tokens_per_phase=resolved_tokens,
    )

    # Run all prompts
    results = []
    for prompt in prompt_list:
        result = await engine.process_query(prompt, debug=debug)
        results.append(result)

    # Write to output file if specified
    if output_file:
        output_path = Path(output_file)
        with output_path.open('w', encoding='utf-8') as handle:
            for result in results:
                json.dump(result.to_dict(), handle, ensure_ascii=False)
                handle.write('\n')

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

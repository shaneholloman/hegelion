#!/usr/bin/env python
"""Batch runner for Hegelion queries with logging for evaluation."""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List

from hegelion_server.config import get_backend_from_env, get_engine_settings_from_env
from hegelion_server.dialectics import HegelionEngine


DEFAULT_QUERIES: Dict[str, List[str]] = {
    "factual": [
        "What is the capital of France?",
        "Explain what photosynthesis does for a plant.",
        "When was the first moon landing?",
    ],
    "philosophical": [
        "Can AI be genuinely creative?",
        "Is free will compatible with determinism?",
        "Is morality objective or subjective?",
    ],
    "scientific": [
        "How do proteins fold so quickly despite the large configuration space?",
        "Why is there dark matter?",
        "What are the biggest failure modes in AI alignment?",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run multiple hegelion queries and log JSON traces for analysis."
    )
    parser.add_argument(
        "--queries",
        type=Path,
        default=None,
        help="Optional path to a JSON file of the form {category: [queries]}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("logs/hegelion_runs.jsonl"),
        help="Where to store JSON lines with the run results",
    )
    parser.add_argument(
        "--synthesis-threshold",
        type=float,
        default=None,
        help="Override the synthesis threshold for all runs",
    )
    return parser.parse_args()


def _load_queries(path: Path | None) -> Dict[str, List[str]]:
    if path is None:
        return DEFAULT_QUERIES
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Query file must contain a JSON object mapping categories to lists.")
    result: Dict[str, List[str]] = {}
    for category, queries in data.items():
        if not isinstance(queries, list):
            raise ValueError(f"Category {category} must map to a list of strings.")
        result[category] = [str(item) for item in queries]
    return result


async def run_queries(
    queries: Dict[str, List[str]],
    output_path: Path,
    synthesis_threshold: float | None,
) -> None:
    backend = get_backend_from_env()
    settings = get_engine_settings_from_env()
    engine = HegelionEngine(
        backend=backend,
        model=settings.model,
        synthesis_threshold=synthesis_threshold or settings.synthesis_threshold,
        max_tokens_per_phase=settings.max_tokens_per_phase,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as fh:
        for category, prompts in queries.items():
            for prompt in prompts:
                started = time.time()
                result = await engine.process_query(prompt)
                entry = {
                    "timestamp": started,
                    "category": category,
                    "query": prompt,
                    "result": result.model_dump(),
                }
                fh.write(json.dumps(entry) + "\n")
                fh.flush()
                print(f"[{category}] logged query: {prompt}")


async def main() -> None:
    args = parse_args()
    queries = _load_queries(args.queries)
    await run_queries(queries, args.output, args.synthesis_threshold)
    print(f"Saved runs to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())

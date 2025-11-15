#!/usr/bin/env python
"""CLI helper to run a single Hegelion query using the configured backend."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from hegelion_server.config import get_backend_from_env, get_engine_settings_from_env
from hegelion_server.dialectics import HegelionEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a single hegelion_query call using the configured backend."
    )
    parser.add_argument(
        "query",
        help="Question or topic to analyze dialectically",
    )
    parser.add_argument(
        "--synthesis-threshold",
        type=float,
        default=None,
        help="Override synthesis threshold (default: env or 0.85)",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=1,
        help="Maximum dialectical cycles (currently 1 is implemented)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the JSON result",
    )
    return parser.parse_args()


async def _run(query: str, synthesis_threshold: float | None, max_iterations: int) -> dict:
    backend = get_backend_from_env()
    settings = get_engine_settings_from_env()
    engine = HegelionEngine(
        backend=backend,
        model=settings.model,
        synthesis_threshold=synthesis_threshold or settings.synthesis_threshold,
        max_tokens_per_phase=settings.max_tokens_per_phase,
    )
    result = await engine.process_query(query=query, max_iterations=max_iterations)
    return result.model_dump()


async def main() -> None:
    args = parse_args()
    payload = await _run(args.query, args.synthesis_threshold, args.max_iterations)
    text = json.dumps(payload, indent=2)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"Saved result to {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    asyncio.run(main())

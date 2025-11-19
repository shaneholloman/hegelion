#!/usr/bin/env python
"""Benchmark CLI for Hegelion dialectical reasoning."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

if (
    __package__ is None or __package__ == ""
):  # pragma: no cover - direct execution fallback
    sys.path.insert(0, str(Path(__file__).parent.parent))

from hegelion.core import run_benchmark


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Hegelion dialectical reasoning on multiple prompts."
    )
    parser.add_argument(
        "prompts_file",
        type=Path,
        help="Path to JSONL file containing prompts (one JSON object per line)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write results as JSONL",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Include debug information and internal diagnostics",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print aggregate statistics to stdout after the run",
    )
    return parser


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def _safe_time(result, key: str) -> float:
    metadata = result.metadata if isinstance(result.metadata, dict) else {}
    value = metadata.get(key)
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def print_summary(results: list) -> None:
    """Print a summary of benchmark results."""
    if not results:
        print("No results to summarize")
        return

    total = len(results)
    total_contradictions = sum(len(r.contradictions) for r in results)
    total_proposals = sum(len(r.research_proposals) for r in results)
    total_time = sum(_safe_time(r, "total_time_ms") for r in results)
    thesis_time = sum(_safe_time(r, "thesis_time_ms") for r in results)
    antithesis_time = sum(_safe_time(r, "antithesis_time_ms") for r in results)
    synthesis_time = sum(_safe_time(r, "synthesis_time_ms") for r in results)

    def _avg(total_value: float) -> float:
        return total_value / total if total else 0.0

    print("HEGELION BENCHMARK SUMMARY")
    print(f"Total queries processed: {total}")
    print(
        f"Contradictions: {total_contradictions} (avg: {_avg(total_contradictions):.1f})"
    )
    print(f"Research proposals: {total_proposals} (avg: {_avg(total_proposals):.1f})")
    print(f"Total time: {total_time:.0f}ms (avg: {_avg(total_time):.0f}ms per query)")
    print(f"Thesis time total/avg: {thesis_time:.0f}ms / {_avg(thesis_time):.0f}ms")
    print(
        f"Antithesis time total/avg: {antithesis_time:.0f}ms / {_avg(antithesis_time):.0f}ms"
    )
    print(
        f"Synthesis time total/avg: {synthesis_time:.0f}ms / {_avg(synthesis_time):.0f}ms"
    )
    print("")


async def _run(args: argparse.Namespace) -> None:
    if not args.prompts_file.exists():
        raise FileNotFoundError(f"Prompts file not found: {args.prompts_file}")

    results = await run_benchmark(
        prompts=args.prompts_file,
        output_file=args.output,
        debug=args.debug,
    )

    if args.summary:
        print_summary(results)

    if not args.output:
        for result in results:
            print(json.dumps(result.to_dict(), ensure_ascii=False))

    print(f"Processed {len(results)} queries", file=sys.stderr)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    try:
        asyncio.run(_run(args))
    except Exception as exc:  # pragma: no cover - CLI error surface
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()

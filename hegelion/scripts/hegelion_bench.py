#!/usr/bin/env python
"""Benchmark CLI for Hegelion dialectical reasoning."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add the hegelion package to Python path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))

from hegelion.core import run_benchmark


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run Hegelion dialectical reasoning on multiple prompts."
    )
    parser.add_argument(
        "prompts_file",
        type=Path,
        help="Path to JSONL file containing prompts (one per line)",
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
        help="Include debug information and internal conflict scores",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary of results to stdout",
    )
    return parser.parse_args()


def print_summary(results: list) -> None:
    """Print a summary of benchmark results."""
    if not results:
        print("No results to summarize")
        return

    total = len(results)
    synthesis_count = sum(1 for r in results if r.mode == "synthesis")
    total_contradictions = sum(len(r.contradictions) for r in results)
    total_proposals = sum(len(r.research_proposals) for r in results)
    total_time = sum(r.metadata["total_time_ms"] for r in results)

    print(f"=== HEGELION BENCHMARK SUMMARY ===")
    print(f"Total queries processed: {total}")
    print(f"Synthesis mode: {synthesis_count}/{total} ({100*synthesis_count/total:.1f}%)")
    print(f"Total contradictions found: {total_contradictions} (avg: {total_contradictions/total:.1f})")
    print(f"Total research proposals: {total_proposals} (avg: {total_proposals/total:.1f})")
    print(f"Total time: {total_time:.0f}ms (avg: {total_time/total:.0f}ms per query)")
    print("")


async def main() -> None:
    """Main CLI entry point."""
    args = parse_args()

    if not args.prompts_file.exists():
        print(f"Error: Prompts file not found: {args.prompts_file}", file=sys.stderr)
        sys.exit(1)

    try:
        results = await run_benchmark(
            prompts=args.prompts_file,
            output_file=args.output,
            debug=args.debug,
        )

        if args.summary:
            print_summary(results)

        if not args.output:
            # Print results to stdout as JSONL
            for result in results:
                print(json.dumps(result.to_dict(), ensure_ascii=False))

        print(f"Processed {len(results)} queries", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
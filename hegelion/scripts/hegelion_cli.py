#!/usr/bin/env python
"""CLI for Hegelion dialectical reasoning."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add the hegelion package to Python path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))

from hegelion.core import run_dialectic


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run Hegelion dialectical reasoning on a single query."
    )
    parser.add_argument(
        "query",
        help="Question or topic to analyze dialectically",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Include debug information and internal conflict scores",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the JSON result",
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json)",
    )
    return parser.parse_args()


def format_summary(result) -> str:
    """Format result as a human-readable summary."""
    lines = [
        f"Query: {result.query}",
        f"Mode: {result.mode}",
        f"Contradictions Found: {len(result.contradictions)}",
        f"Research Proposals: {len(result.research_proposals)}",
        "",
        "=== THESIS ===",
        result.thesis,
        "",
        "=== ANTITHESIS ===",
        result.antithesis,
        "",
        "=== SYNTHESIS ===",
        result.synthesis,
        "",
    ]

    if result.contradictions:
        lines.append("=== CONTRADICTIONS ===")
        for i, contradiction in enumerate(result.contradictions, 1):
            lines.append(f"{i}. {contradiction['description']}")
            if contradiction.get('evidence'):
                lines.append(f"   Evidence: {contradiction['evidence']}")
        lines.append("")

    if result.research_proposals:
        lines.append("=== RESEARCH PROPOSALS ===")
        for i, proposal in enumerate(result.research_proposals, 1):
            lines.append(f"{i}. {proposal['description']}")
            if proposal.get('testable_prediction'):
                lines.append(f"   Prediction: {proposal['testable_prediction']}")
        lines.append("")

    # Add timing info
    metadata = result.metadata
    lines.append("=== TIMING ===")
    lines.append(f"Thesis: {metadata['thesis_time_ms']:.0f}ms")
    lines.append(f"Antithesis: {metadata['antithesis_time_ms']:.0f}ms")
    if metadata.get('synthesis_time_ms'):
        lines.append(f"Synthesis: {metadata['synthesis_time_ms']:.0f}ms")
    lines.append(f"Total: {metadata['total_time_ms']:.0f}ms")

    return "\n".join(lines)


async def main() -> None:
    """Main CLI entry point."""
    args = parse_args()

    try:
        result = await run_dialectic(
            query=args.query,
            debug=args.debug,
        )

        if args.format == "summary":
            output = format_summary(result)
        else:
            output = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)

        if args.output:
            args.output.write_text(output, encoding="utf-8")
            print(f"Result saved to {args.output}", file=sys.stderr)
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
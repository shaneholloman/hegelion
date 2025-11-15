#!/usr/bin/env python
"""CLI for Hegelion dialectical reasoning."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

if __package__ is None or __package__ == "":  # pragma: no cover - direct execution fallback
    sys.path.insert(0, str(Path(__file__).parent.parent))

from hegelion.core import run_dialectic


def build_parser() -> argparse.ArgumentParser:
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
        help="Include debug information and internal diagnostics",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the structured result",
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json)",
    )
    return parser


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def format_summary(result) -> str:
    """Format result as a human-readable summary."""
    metadata = result.metadata or {}

    def _fmt_time(key: str) -> str:
        value = metadata.get(key)
        if isinstance(value, (int, float)):
            return f"{value:.0f}ms"
        return "n/a"

    lines = [
        f"Query: {result.query}",
        f"Mode: {result.mode}",
        f"Contradictions Found: {len(result.contradictions)}",
        f"Research Proposals: {len(result.research_proposals)}",
    ]

    backend_provider = metadata.get("backend_provider")
    backend_model = metadata.get("backend_model")
    if backend_provider or backend_model:
        backend_parts = [
            str(part).strip()
            for part in (backend_provider, backend_model)
            if part is not None and str(part).strip()
        ]
        if backend_parts:
            lines.append("Backend: " + ", ".join(backend_parts))

    lines.extend(
        [
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
    )

    if result.contradictions:
        lines.append("=== CONTRADICTIONS ===")
        for i, contradiction in enumerate(result.contradictions, 1):
            lines.append(f"{i}. {contradiction['description']}")
            evidence = contradiction.get("evidence")
            if evidence:
                lines.append(f"   Evidence: {evidence}")
        lines.append("")

    if result.research_proposals:
        lines.append("=== RESEARCH PROPOSALS ===")
        for i, proposal in enumerate(result.research_proposals, 1):
            lines.append(f"{i}. {proposal['description']}")
            prediction = proposal.get("testable_prediction")
            if prediction:
                lines.append(f"   Prediction: {prediction}")
        lines.append("")

    lines.append("=== TIMING ===")
    lines.append(f"Thesis: {_fmt_time('thesis_time_ms')}")
    lines.append(f"Antithesis: {_fmt_time('antithesis_time_ms')}")
    lines.append(f"Synthesis: {_fmt_time('synthesis_time_ms')}")
    lines.append(f"Total: {_fmt_time('total_time_ms')}")

    debug_info = metadata.get("debug")
    if isinstance(debug_info, dict) and debug_info:
        lines.append("")
        lines.append("=== DEBUG METRICS ===")
        for key, value in debug_info.items():
            lines.append(f"{key}: {value}")

    return "\n".join(lines)


async def _run(args: argparse.Namespace) -> None:
    result = await run_dialectic(query=args.query, debug=args.debug)

    if args.format == "summary":
        output = format_summary(result)
    else:
        output = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"Result saved to {args.output}", file=sys.stderr)
    else:
        print(output)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    try:
        asyncio.run(_run(args))
    except Exception as exc:  # pragma: no cover - CLI error surface
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()

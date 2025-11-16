#!/usr/bin/env python
"""CLI for Hegelion dialectical reasoning."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from importlib import resources

if __package__ is None or __package__ == "":  # pragma: no cover - direct execution fallback
    sys.path.insert(0, str(Path(__file__).parent.parent))

from hegelion.config import ConfigurationError
from hegelion.core import run_dialectic


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Hegelion dialectical reasoning on a single query."
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Question or topic to analyze dialectically (optional when using --demo)",
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
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Show a cached example trace without calling any live backend",
    )
    return parser


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def _load_demo_examples() -> list[dict]:
    """Load bundled demo examples from the installed package.

    Falls back gracefully if resources are unavailable.
    """
    try:
        with resources.open_text("hegelion.examples_data", "glm4_6_examples.jsonl", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    except Exception:
        return []


def print_cached_example() -> None:
    """Print a cached example result for demo mode."""
    examples = _load_demo_examples()
    if not examples:
        print("Demo data is not available in this installation.", file=sys.stderr)
        return

    example = examples[0]
    print(json.dumps(example, indent=2, ensure_ascii=False))


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
    if args.demo:
        # In demo mode we ignore live backends and just show a cached trace.
        print_cached_example()
        return

    if not args.query:
        raise SystemExit("Error: QUERY is required unless --demo is specified.")

    try:
        result = await run_dialectic(query=args.query, debug=args.debug)
    except ConfigurationError as exc:
        # Friendly guidance when no backend/API key is configured.
        message = str(exc)
        guidance = (
            "No LLM backend is configured.\n"
            "Run `hegelion --demo` to see a cached example without API keys,\n"
            "or set ANTHROPIC_API_KEY / OPENAI_API_KEY / GOOGLE_API_KEY and HEGELION_PROVIDER."
        )
        print(f"Error: {message}", file=sys.stderr)
        print(guidance, file=sys.stderr)
        raise SystemExit(1)

    if args.format == "summary":
        output = format_summary(result)
    else:
        output = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)

    if args.output:
        # If a JSONL path is provided, write a single-line JSON object suitable
        # for appending into a larger trace corpus.
        if args.output.suffix == ".jsonl":
            with args.output.open("w", encoding="utf-8") as handle:
                json.dump(result.to_dict(), handle, ensure_ascii=False)
                handle.write("\n")
        else:
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

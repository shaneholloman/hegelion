#!/usr/bin/env python
"""CLI for the adversarial Hegelion agent (thesis → antithesis → synthesis before acting)."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

if __package__ is None or __package__ == "":  # pragma: no cover - direct execution fallback
    sys.path.insert(0, str(Path(__file__).parent.parent))

from hegelion.core.agent import HegelionAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Adversarial reflexion agent: critiques plans before acting."
    )
    parser.add_argument("observation", help="Current observation/state to act on")
    parser.add_argument("--goal", help="Optional high-level goal", default=None)
    parser.add_argument("--personas", help="Critic persona preset (e.g., council)")
    parser.add_argument("--iterations", type=int, default=1, help="Refinement loops")
    parser.add_argument("--use-search", action="store_true", help="Allow search in critique")
    parser.add_argument("--coding", action="store_true", help="Use coding-focused guidance")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    parser.add_argument("--debug", action="store_true", help="Include debug output")
    parser.add_argument("--log-file", help="Path to append raw agent traces (JSONL)", default=None)
    return parser


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


async def run(args: argparse.Namespace) -> int:
    agent = (
        HegelionAgent.for_coding(
            goal=args.goal,
            personas=args.personas,
            iterations=args.iterations,
            use_search=args.use_search,
            debug=args.debug,
        )
        if args.coding
        else HegelionAgent(
            goal=args.goal,
            personas=args.personas,
            iterations=args.iterations,
            use_search=args.use_search,
            debug=args.debug,
        )
    )

    step = await agent.act(args.observation)

    if args.log_file:
        try:
            log_path = Path(args.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(step.result.to_dict(), ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Warning: Failed to write to log file {args.log_file}: {e}", file=sys.stderr)

    if args.format == "json":
        payload = {"action": step.action, "result": step.result.to_dict()}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Action: {step.action}\n")
        print("=== THESIS ===")
        print(step.result.thesis)
        print("\n=== ANTITHESIS ===")
        print(step.result.antithesis)
        print("\n=== SYNTHESIS ===")
        print(step.result.synthesis)

    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:  # pragma: no cover - CLI entrypoint
    args = parse_args(argv)
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())

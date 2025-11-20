"""CLI tool for converting Hegelion logs into training datasets (DPO/Instruction)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from hegelion.models import HegelionResult
from hegelion.datasets import export_training_data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert Hegelion agent logs to training datasets."
    )
    parser.add_argument(
        "input_file", type=Path, help="Path to input JSONL log file (from --log-file)"
    )
    parser.add_argument(
        "output_file", type=Path, help="Path to save the converted dataset (.jsonl or .json)"
    )
    parser.add_argument(
        "--format",
        choices=["dpo", "instruction"],
        default="dpo",
        help="Output format: 'dpo' (preference pairs) or 'instruction' (Alpaca-style)",
    )
    parser.add_argument(
        "--rejected",
        choices=["thesis", "antithesis", "both"],
        default="thesis",
        help="Which part of the dialectic to treat as the rejected response (DPO only)",
    )
    return parser


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def load_results(input_file: Path) -> List[HegelionResult]:
    """Load HegelionResults from a JSONL log file."""
    results = []
    if not input_file.exists():
        print(f"Error: Input file {input_file} not found.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    # Handle both direct result dumps and wrapped format
                    if "result" in data:
                        data = data["result"]
                    results.append(HegelionResult.from_dict(data))
                except Exception as e:
                    print(f"Warning: Skipping invalid JSON on line {i}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    return results


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    print(f"Loading results from {args.input_file}...")
    results = load_results(args.input_file)

    if not results:
        print("No valid results found in input file.", file=sys.stderr)
        return 1

    print(f"Found {len(results)} results. Converting to {args.format} format...")

    try:
        export_training_data(
            results,
            args.output_file,
            format=args.format,
            rejected_source=args.rejected,
        )
        print(f"Successfully created dataset at {args.output_file}")
        return 0
    except Exception as e:
        print(f"Error exporting dataset: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

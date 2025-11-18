#!/usr/bin/env python
"""Evaluation CLI for comparing Hegelion benchmark runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

if __package__ is None or __package__ == "":  # pragma: no cover - direct execution fallback
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

from hegelion.models import HegelionResult


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare multiple Hegelion benchmark runs and generate a report."
    )
    parser.add_argument(
        "results_files",
        type=Path,
        nargs="+",
        help="Paths to one or more Hegelion JSONL results files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the comparison report in Markdown format.",
    )
    return parser


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def load_results(path: Path) -> List[HegelionResult]:
    """Load Hegelion results from a JSONL file."""
    results = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            results.append(HegelionResult(**data))
    return results


def analyze_results(results: List[HegelionResult]) -> Dict[str, Any]:
    """Calculate aggregate metrics for a list of results."""
    if not results:
        return {}

    total_queries = len(results)
    total_contradictions = sum(len(r.contradictions) for r in results)
    total_proposals = sum(len(r.research_proposals) for r in results)
    total_time = sum(r.metadata.get("total_time_ms", 0) for r in results)
    
    conflict_scores = []
    for r in results:
        debug = r.metadata.get("debug", {})
        if debug and "internal_conflict_score" in debug:
            conflict_scores.append(debug["internal_conflict_score"])
    
    avg_conflict_score = sum(conflict_scores) / len(conflict_scores) if conflict_scores else None

    return {
        "model": results[0].metadata.get("backend_model", "Unknown"),
        "total_queries": total_queries,
        "avg_contradictions": total_contradictions / total_queries,
        "avg_proposals": total_proposals / total_queries,
        "avg_time_ms": total_time / total_queries,
        "avg_conflict_score": avg_conflict_score,
    }


def generate_report(analysis: List[Dict[str, Any]]) -> str:
    """Generate a Markdown report from the analysis."""
    report = ["# Hegelion Evaluation Report", ""]
    
    # Summary Table
    report.append("## Summary")
    report.append("| Model | Queries | Avg. Contradictions | Avg. Proposals | Avg. Time (ms) | Avg. Conflict Score |")
    report.append("|-------|---------|---------------------|----------------|----------------|---------------------|")
    for stats in analysis:
        conflict_score_str = f"{stats['avg_conflict_score']:.3f}" if stats['avg_conflict_score'] is not None else "N/A"
        report.append(
            f"| {stats['model']} | {stats['total_queries']} | {stats['avg_contradictions']:.2f} | "
            f"{stats['avg_proposals']:.2f} | {stats['avg_time_ms']:.0f} | {conflict_score_str} |"
        )
    report.append("")

    return "\n".join(report)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)

    all_analysis = []
    for results_file in args.results_files:
        if not results_file.exists():
            print(f"Error: File not found: {results_file}", file=sys.stderr)
            continue
        
        results = load_results(results_file)
        if not results:
            print(f"Warning: No results found in: {results_file}", file=sys.stderr)
            continue

        analysis = analyze_results(results)
        all_analysis.append(analysis)

    report = generate_report(all_analysis)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()

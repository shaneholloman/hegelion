#!/usr/bin/env python3
"""Format a manual Hegelian response into the official JSONL contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict

SECTION_HEADERS = ["**THESIS**", "## THESIS", "THESIS:", "THESIS"]


def _extract_sections(text: str) -> tuple[str, str, str]:
    """Split a response into thesis / antithesis / synthesis blocks."""
    lower = text
    thesis = antithesis = synthesis = ""

    # Normalize markdown markers
    markers = ["**THESIS**", "## THESIS", "THESIS:"]
    for marker in markers:
        lower = lower.replace(marker, "**THESIS**")
    lower = lower.replace("**ANTITHESIS**", "**ANTITHESIS**")
    lower = lower.replace("**SYNTHESIS**", "**SYNTHESIS**")

    if "**THESIS**" in lower:
        parts = lower.split("**THESIS**", 1)[1]
    else:
        parts = lower

    ant_split = parts.split("**ANTITHESIS**", 1)
    if len(ant_split) == 2:
        thesis = ant_split[0].strip()
        syn_split = ant_split[1].split("**SYNTHESIS**", 1)
        if len(syn_split) == 2:
            antithesis = syn_split[0].strip()
            synthesis = syn_split[1].strip()
        else:
            antithesis = ant_split[1].strip()
    else:
        thesis = parts.strip()

    return thesis, antithesis, synthesis


def _extract_contradictions(text: str) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    current: Dict[str, str] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        upper = line.upper()
        if upper.startswith("CONTRADICTION:"):
            current = {
                "description": line.split(":", 1)[1].strip(),
                "evidence": "",
            }
            results.append(current)
        elif upper.startswith("EVIDENCE:") and current:
            current["evidence"] = line.split(":", 1)[1].strip()
    return [c for c in results if c.get("description")]


def _extract_research(text: str) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    current: Dict[str, str] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        upper = line.upper()
        if upper.startswith("RESEARCH_PROPOSAL"):
            if current and not current.get("testable_prediction"):
                current["testable_prediction"] = ""
            current = {
                "description": line.split(":", 1)[1].strip(),
                "testable_prediction": "",
            }
            results.append(current)
        elif (
            upper.startswith("TESTABLE_PREDICTION") or upper.startswith("PREDICTION")
        ) and current:
            current["testable_prediction"] = line.split(":", 1)[1].strip()
    return [r for r in results if r.get("description")]


def parse_response(query: str, response_text: str) -> dict:
    thesis, antithesis, synthesis = _extract_sections(response_text)
    contradictions = _extract_contradictions(response_text)
    research = _extract_research(response_text)

    trace_research = [
        f"{item['description']} | Prediction: {item.get('testable_prediction', '')}".strip()
        for item in research
    ]

    return {
        "query": query,
        "mode": "synthesis",
        "thesis": thesis,
        "antithesis": antithesis,
        "synthesis": synthesis,
        "contradictions": contradictions,
        "research_proposals": research,
        "metadata": {
            "source": "manual",
            "backend_provider": "manual",
            "backend_model": "manual",
        },
        "trace": {
            "thesis": thesis,
            "antithesis": antithesis,
            "synthesis": synthesis,
            "contradictions_found": len(contradictions),
            "research_proposals": trace_research,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Format manual dialectical responses into JSONL")
    parser.add_argument("query", help="Original prompt/question")
    parser.add_argument(
        "input",
        help="Path to the Claude output (text/markdown). Use '-' to read from stdin.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="-",
        help="File to append JSONL to (default: stdout)",
    )
    args = parser.parse_args()

    if args.input == "-":
        response_text = sys.stdin.read()
    else:
        response_text = Path(args.input).read_text(encoding="utf-8")

    entry = parse_response(args.query, response_text)
    json_line = json.dumps(entry, ensure_ascii=False)

    if args.output == "-":
        print(json_line)
    else:
        with open(args.output, "a", encoding="utf-8") as handle:
            handle.write(json_line + "\n")
        print(f"✓ Appended sample to {args.output}")


if __name__ == "__main__":
    main()

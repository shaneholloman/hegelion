"""Parsing utilities for Hegelion dialectical reasoning."""

from __future__ import annotations

import json
import re
from typing import List, Optional


def parse_contradiction_header(text: str) -> Optional[str]:
    """Parse a contradiction header line and extract the description."""
    colon_index = text.find(":")
    if colon_index == -1:
        return None
    prefix = strip_markdown_wrappers(text[:colon_index].strip()).upper()
    if not prefix.startswith("CONTRADICTION"):
        return None
    detail = text[colon_index + 1 :].strip() or "Unspecified contradiction"
    return detail


def strip_markdown_wrappers(text: str) -> str:
    """Remove markdown formatting wrappers like **, __, *, _ from text."""
    trimmed = text.strip()
    if not trimmed:
        return ""
    markers = ("**", "__", "*", "_")
    changed = True
    while changed and trimmed:
        changed = False
        for marker in markers:
            if trimmed.startswith(marker) and trimmed.endswith(marker) and len(trimmed) > 2 * len(marker):
                trimmed = trimmed[len(marker) : -len(marker)].strip()
                changed = True
    return trimmed


def extract_contradictions(text: str) -> List[str]:
    """Extract structured contradictions from antithesis text.

    Expected format:
    CONTRADICTION: [description]
    EVIDENCE: [supporting evidence]
    """
    contradictions: List[str] = []
    pending: Optional[str] = None

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        cleaned = strip_markdown_wrappers(stripped)
        if not cleaned:
            continue
        header = parse_contradiction_header(cleaned)
        if header:
            if pending:
                contradictions.append(pending)
            pending = header
            continue

        if not pending:
            continue

        normalized = cleaned.upper()
        if normalized.startswith("EVIDENCE"):
            evidence = cleaned.split(":", 1)[1].strip() if ":" in cleaned else ""
            if evidence:
                contradictions.append(f"{pending} — {evidence}")
            else:
                contradictions.append(pending)
            pending = None

    if pending:
        contradictions.append(pending)
    return contradictions


def extract_research_proposals(text: str) -> List[str]:
    """Extract research proposals from synthesis text.

    Expected format:
    RESEARCH_PROPOSAL: [description]
    TESTABLE_PREDICTION: [falsifiable claim]
    """
    proposals: List[str] = []
    current = None

    for line in text.splitlines():
        normalized = line.strip()
        if not normalized:
            continue
        upper = normalized.upper()
        if upper.startswith("RESEARCH_PROPOSAL:"):
            if current:
                proposals.append(current)
            current = normalized.split(":", 1)[1].strip()
        elif upper.startswith("TESTABLE_PREDICTION:"):
            prediction = normalized.split(":", 1)[1].strip()
            if current:
                combined = (
                    f"{current} | Prediction: {prediction}" if prediction else current
                )
                proposals.append(combined)
                current = None
            elif prediction:
                proposals.append(f"Prediction: {prediction}")
    if current:
        proposals.append(current)
    return proposals


def parse_conflict_value(response: str) -> float:
    """Parse a conflict value from LLM response JSON."""
    if not response:
        return 0.0
    candidates = [response.strip()]
    candidates.extend(re.findall(r"\{.*?\}", response, flags=re.DOTALL))
    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        conflict_value = data.get("conflict")
        try:
            value = float(conflict_value)
        except (TypeError, ValueError):
            continue
        return float(max(0.0, min(1.0, value)))
    return 0.0


def conclusion_excerpt(text: str, max_paragraphs: int = 2, max_chars: int = 1500) -> str:
    """Extract a conclusion excerpt from text for conflict analysis."""
    paragraphs = [segment.strip() for segment in text.split("\n\n") if segment.strip()]
    if not paragraphs:
        excerpt = text.strip()
    else:
        excerpt = "\n\n".join(paragraphs[-max_paragraphs:])
    if len(excerpt) > max_chars:
        return excerpt[-max_chars:]
    return excerpt


__all__ = [
    "extract_contradictions",
    "extract_research_proposals",
    "parse_conflict_value",
    "conclusion_excerpt",
    "parse_contradiction_header",
    "strip_markdown_wrappers",
]

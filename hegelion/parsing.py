"""Parsing utilities for Hegelion dialectical reasoning."""

from __future__ import annotations

import json
import re
from typing import List, Optional


def parse_contradiction_header(text: str) -> Optional[str]:
    """Parse a contradiction header line and extract the description.

    Supports variations:
    - CONTRADICTION: description
    - **CONTRADICTION**: description
    - **CONTRADICTION:** description
    - Contradiction 1: description
    - contradiction: description (case insensitive)
    """
    colon_index = text.find(":")
    if colon_index == -1:
        return None

    # Strip markdown from the prefix only
    prefix = text[:colon_index].strip()

    # Remove leading and trailing markdown markers from the prefix
    for marker in ["**", "__", "*", "_"]:
        if prefix.startswith(marker):
            prefix = prefix[len(marker):].strip()
        if prefix.endswith(marker):
            prefix = prefix[:-len(marker)].strip()

    prefix = prefix.upper()

    # Remove numbering (e.g., "CONTRADICTION 1" -> "CONTRADICTION")
    prefix_parts = prefix.split()
    if prefix_parts and prefix_parts[0] == "CONTRADICTION":
        # Valid contradiction header
        detail = text[colon_index + 1 :].strip() or "Unspecified contradiction"

        # Strip markdown from the description as well
        for marker in ["**", "__", "*", "_"]:
            if detail.startswith(marker):
                detail = detail[len(marker):].strip()
                break

        return detail

    return None


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
            if (
                trimmed.startswith(marker)
                and trimmed.endswith(marker)
                and len(trimmed) > 2 * len(marker)
            ):
                trimmed = trimmed[len(marker) : -len(marker)].strip()
                changed = True
    return trimmed


def extract_contradictions(text: str) -> List[str]:
    """Extract structured contradictions from antithesis text.

    Supports formats:
    CONTRADICTION: [description]
    EVIDENCE: [supporting evidence]
    **CONTRADICTION**: [description]  (markdown)
    Contradiction 1: [description]    (numbered)

    Handles multiline evidence by accumulating lines until next CONTRADICTION.
    """
    contradictions: List[str] = []
    pending: Optional[str] = None
    evidence_buffer: List[str] = []

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue

        cleaned = strip_markdown_wrappers(stripped)
        if not cleaned:
            continue

        # Check if this is a new contradiction header
        header = parse_contradiction_header(cleaned)
        if header:
            # Save previous contradiction with accumulated evidence
            if pending:
                if evidence_buffer:
                    combined_evidence = " ".join(evidence_buffer).strip()
                    contradictions.append(f"{pending} — {combined_evidence}")
                else:
                    contradictions.append(pending)
                evidence_buffer = []
            pending = header
            continue

        if not pending:
            continue

        # Check if this is evidence
        normalized = cleaned.upper()
        if normalized.startswith("EVIDENCE"):
            # Extract evidence text after colon
            evidence_line = cleaned.split(":", 1)[1].strip() if ":" in cleaned else cleaned
            if evidence_line:
                evidence_buffer.append(evidence_line)
        elif evidence_buffer:
            # Continuation of evidence (multiline)
            evidence_buffer.append(cleaned)

    # Save final pending contradiction
    if pending:
        if evidence_buffer:
            combined_evidence = " ".join(evidence_buffer).strip()
            contradictions.append(f"{pending} — {combined_evidence}")
        else:
            contradictions.append(pending)

    return contradictions


def extract_research_proposals(text: str) -> List[str]:
    """Extract research proposals from synthesis text.

    Supports formats:
    - RESEARCH_PROPOSAL: [description]
    - TESTABLE_PREDICTION: [falsifiable claim]
    - PREDICTION 1: [claim]  (numbered)
    - TEST_PREDICTION: [claim]  (variations)

    Handles multiline predictions by accumulating until next header.
    """
    proposals: List[str] = []
    current: Optional[str] = None
    prediction_buffer: List[str] = []

    def _is_research_header(upper_line: str) -> bool:
        """Check if line is a research proposal header."""
        return upper_line.startswith("RESEARCH_PROPOSAL:") or upper_line.startswith(
            "RESEARCH PROPOSAL:"
        )

    def _is_prediction_header(upper_line: str) -> bool:
        """Check if line is a prediction header (with variations)."""
        # Match: TESTABLE_PREDICTION, TESTABLE PREDICTION, TEST_PREDICTION,
        # PREDICTION 1, PREDICTION:, etc.
        if upper_line.startswith("TESTABLE") and "PREDICTION" in upper_line:
            return True
        if upper_line.startswith("TEST") and "PREDICTION" in upper_line:
            return True
        # Handle numbered predictions: "PREDICTION 1:", "PREDICTION 2:", etc.
        if re.match(r"PREDICTION\s*\d*\s*:", upper_line):
            return True
        return False

    for line in text.splitlines():
        normalized = line.strip()
        if not normalized:
            continue

        cleaned = strip_markdown_wrappers(normalized)
        upper = cleaned.upper()

        # New research proposal header: flush previous
        if _is_research_header(upper):
            # Flush any existing current proposal
            if current:
                if prediction_buffer:
                    combined_pred = " ".join(prediction_buffer).strip()
                    proposals.append(f"{current} | Prediction: {combined_pred}")
                else:
                    proposals.append(current)
            elif prediction_buffer:
                # Standalone prediction before a new proposal
                combined_pred = " ".join(prediction_buffer).strip()
                proposals.append(f"Prediction: {combined_pred}")

            # Start new proposal
            current = cleaned.split(":", 1)[1].strip() if ":" in cleaned else cleaned
            prediction_buffer = []
            continue

        # Prediction header: start/replace prediction buffer
        if _is_prediction_header(upper):
            # If we have a current proposal, attach the prediction to it (don't flush yet)
            # If we have a standalone prediction buffer, flush it first
            if current is None and prediction_buffer:
                # Flush standalone prediction before starting new one
                combined_prev = " ".join(prediction_buffer).strip()
                if combined_prev:
                    proposals.append(f"Prediction: {combined_prev}")
                prediction_buffer = []

            # Start new prediction (will be attached to current proposal if exists)
            prediction_text = cleaned.split(":", 1)[1].strip() if ":" in cleaned else ""
            if prediction_text:
                prediction_buffer = [prediction_text]
            continue

        # Continuation for multiline prediction
        if prediction_buffer and cleaned:
            prediction_buffer.append(cleaned)

    # Flush tail
    if current:
        if prediction_buffer:
            combined_pred = " ".join(prediction_buffer).strip()
            proposals.append(f"{current} | Prediction: {combined_pred}")
        else:
            proposals.append(current)
    elif prediction_buffer:
        combined_pred = " ".join(prediction_buffer).strip()
        proposals.append(f"Prediction: {combined_pred}")

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

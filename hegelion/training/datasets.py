"""
Hegelion Datasets: Tools for converting dialectical results into training data.

This module enables Hegelion to be used as a generator for RLAIF (Reinforcement Learning
from AI Feedback) and DPO (Direct Preference Optimization) datasets.
"""

from typing import List, Literal
import json
from pathlib import Path
from hegelion.core.models import HegelionResult


def to_dpo_dataset(
    results: List[HegelionResult],
    output_file: str | Path,
    rejected_source: Literal["thesis", "antithesis", "both"] = "thesis",
) -> None:
    """
    Convert a list of Hegelion results into a DPO (Direct Preference Optimization) dataset.

    Format:
    {
        "prompt": "Query...",
        "chosen": "Synthesis...",
        "rejected": "Thesis/Antithesis..."
    }

    Args:
        results: List of HegelionResult objects
        output_file: Path to save the .jsonl file
        rejected_source: Which part of the dialectic to treat as the "rejected" (inferior) response.
                        - 'thesis': The initial position (good, but not transcendent)
                        - 'antithesis': The critique (critical, but one-sided)
                        - 'both': Creates two examples per result (one vs thesis, one vs antithesis)
    """

    dataset = []

    for res in results:
        # Basic prompt format
        prompt = f"Query: {res.query}\n\nProvide a comprehensive analysis."

        # The "Chosen" response is always the Synthesis (the transcendent view)
        chosen = res.synthesis

        rejected_items = []
        if rejected_source == "thesis" or rejected_source == "both":
            rejected_items.append(res.thesis)

        if rejected_source == "antithesis" or rejected_source == "both":
            rejected_items.append(res.antithesis)

        for rejected in rejected_items:
            entry = {
                "prompt": prompt,
                "chosen": chosen,
                "rejected": rejected,
                "metadata": {
                    "source": "hegelion-synthetic",
                    "mode": res.mode,
                    "contradictions_found": len(res.contradictions),
                },
            }
            dataset.append(entry)

    # Write to JSONL
    with open(output_file, "w", encoding="utf-8") as f:
        for entry in dataset:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Exported {len(dataset)} DPO pairs to {output_file}")


def to_instruction_tuning_dataset(results: List[HegelionResult], output_file: str | Path) -> None:
    """
    Convert results into standard instruction tuning format (Alpaca/ShareGPT style).

    Format:
    {
        "instruction": "Query...",
        "output": "Synthesis..."
    }
    """
    dataset = []
    for res in results:
        entry = {
            "instruction": res.query,
            "input": "",
            "output": res.synthesis,
            "system": "You are a dialectical reasoner capable of synthesizing opposing viewpoints.",
        }
        dataset.append(entry)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(dataset)} instruction tuning examples to {output_file}")


def export_training_data(
    results: List[HegelionResult],
    output_file: str | Path,
    *,
    format: Literal["dpo", "instruction"] = "dpo",
    rejected_source: Literal["thesis", "antithesis", "both"] = "thesis",
) -> None:
    """
    Convenience wrapper for exporting Hegelion results to common training formats.

    Args:
        results: List of HegelionResult objects.
        output_file: Destination path (``.jsonl`` for DPO, ``.json`` for instruction tuning).
        format: ``"dpo"`` (preference pairs) or ``"instruction"`` (Alpaca-style).
        rejected_source: Which side to treat as the rejected answer for DPO exports.
    """

    if format == "dpo":
        to_dpo_dataset(results, output_file, rejected_source=rejected_source)
    elif format == "instruction":
        to_instruction_tuning_dataset(results, output_file)
    else:
        raise ValueError("format must be 'dpo' or 'instruction'")

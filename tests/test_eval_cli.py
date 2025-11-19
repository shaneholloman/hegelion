"""Tests for the evaluation CLI."""

import json
from pathlib import Path
from unittest.mock import patch

from hegelion.scripts import hegelion_eval


def test_eval_cli_generates_report(tmp_path: Path, capsys):
    """Test that hegelion-eval generates a report from JSONL files."""
    # Create mock results
    result1 = {
        "query": "Test Query 1",
        "mode": "synthesis",
        "thesis": "Thesis 1",
        "antithesis": "Antithesis 1",
        "synthesis": "Synthesis 1",
        "contradictions": [{"description": "C1"}],
        "research_proposals": [{"description": "RP1"}],
        "metadata": {
            "total_time_ms": 1000,
            "thesis_time_ms": 100,
            "antithesis_time_ms": 100,
            "synthesis_time_ms": 100,
            "backend_model": "model-a",
            "debug": {"internal_conflict_score": 0.5},
        },
    }
    result2 = {
        "query": "Test Query 2",
        "mode": "synthesis",
        "thesis": "Thesis 2",
        "antithesis": "Antithesis 2",
        "synthesis": "Synthesis 2",
        "contradictions": [{"description": "C2"}, {"description": "C3"}],
        "research_proposals": [],
        "metadata": {
            "total_time_ms": 2000,
            "thesis_time_ms": 200,
            "antithesis_time_ms": 200,
            "synthesis_time_ms": 200,
            "backend_model": "model-a",
            "debug": {"internal_conflict_score": 0.8},
        },
    }

    file1 = tmp_path / "run1.jsonl"
    with file1.open("w") as f:
        f.write(json.dumps(result1) + "\n")
        f.write(json.dumps(result2) + "\n")

    # Run evaluation
    with patch("sys.argv", ["hegelion-eval", str(file1)]):
        hegelion_eval.main()

    # Verify output
    captured = capsys.readouterr()
    output = captured.out

    assert "# Hegelion Evaluation Report" in output
    assert "model-a" in output
    assert "2" in output  # Queries
    assert "1.50" in output  # Avg contradictions (1+2)/2 = 1.5
    assert "0.50" in output  # Avg proposals (1+0)/2 = 0.5
    assert "1500" in output  # Avg time (1000+2000)/2 = 1500
    assert "0.650" in output  # Avg conflict (0.5+0.8)/2 = 0.65


def test_eval_cli_multiple_files(tmp_path: Path, capsys):
    """Test that hegelion-eval handles multiple input files."""
    result = {
        "query": "Q",
        "mode": "synthesis",
        "thesis": "T",
        "antithesis": "A",
        "synthesis": "S",
        "contradictions": [],
        "research_proposals": [],
        "metadata": {
            "total_time_ms": 1000,
            "thesis_time_ms": 100,
            "antithesis_time_ms": 100,
            "synthesis_time_ms": 100,
            "backend_model": "model-b",
        },
    }

    file1 = tmp_path / "file1.jsonl"
    file2 = tmp_path / "file2.jsonl"

    file1.write_text(json.dumps(result) + "\n", encoding="utf-8")
    file2.write_text(json.dumps(result) + "\n", encoding="utf-8")

    with patch("sys.argv", ["hegelion-eval", str(file1), str(file2)]):
        hegelion_eval.main()

    captured = capsys.readouterr()
    output = captured.out

    # Should appear twice in the table (once per file analysis)
    assert output.count("model-b") == 2

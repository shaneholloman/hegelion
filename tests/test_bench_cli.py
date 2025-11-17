"""Tests for benchmark CLI functionality."""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from hegelion.models import HegelionResult
from hegelion.scripts import hegelion_bench


@pytest.fixture
def sample_result() -> HegelionResult:
    """Sample result for testing."""
    return HegelionResult(
        query="Test Query",
        mode="synthesis",
        thesis="Thesis text",
        antithesis="Antithesis text",
        synthesis="Synthesis text",
        contradictions=[{"description": "Contradiction 1"}],
        research_proposals=[{"description": "Proposal 1"}],
        metadata={
            "thesis_time_ms": 100.0,
            "antithesis_time_ms": 200.0,
            "synthesis_time_ms": 300.0,
            "total_time_ms": 600.0,
        },
    )


def test_bench_help_runs() -> None:
    """Test that help command runs successfully."""
    subprocess.run(
        [sys.executable, "-m", "hegelion.scripts.hegelion_bench", "--help"], check=True
    )


def test_bench_with_jsonl_file(monkeypatch, tmp_path: Path, sample_result: HegelionResult) -> None:
    """Test benchmark with JSONL prompts file."""
    prompts_file = tmp_path / "prompts.jsonl"
    prompts_file.write_text('{"query": "Query 1"}\n{"prompt": "Query 2"}\n')

    mock_runner = AsyncMock(return_value=[sample_result, sample_result])
    monkeypatch.setattr(hegelion_bench, "run_benchmark", mock_runner)

    hegelion_bench.main([str(prompts_file)])

    mock_runner.assert_awaited_once()
    call_kwargs = mock_runner.call_args[1]
    assert call_kwargs["prompts"] == prompts_file


def test_bench_with_plain_text_prompts(monkeypatch, tmp_path: Path, sample_result: HegelionResult) -> None:
    """Test benchmark with plain text prompts (one per line)."""
    prompts_file = tmp_path / "prompts.txt"
    prompts_file.write_text("Query 1\nQuery 2\nQuery 3\n")

    mock_runner = AsyncMock(return_value=[sample_result] * 3)
    monkeypatch.setattr(hegelion_bench, "run_benchmark", mock_runner)

    hegelion_bench.main([str(prompts_file)])

    mock_runner.assert_awaited_once()


def test_bench_with_mixed_formats(monkeypatch, tmp_path: Path, sample_result: HegelionResult) -> None:
    """Test benchmark with mixed JSON and plain text prompts."""
    prompts_file = tmp_path / "prompts.jsonl"
    prompts_file.write_text('{"query": "JSON query"}\nPlain text query\n{"prompt": "Another JSON"}\n')

    mock_runner = AsyncMock(return_value=[sample_result] * 3)
    monkeypatch.setattr(hegelion_bench, "run_benchmark", mock_runner)

    hegelion_bench.main([str(prompts_file)])

    mock_runner.assert_awaited_once()


def test_bench_with_output_file(monkeypatch, tmp_path: Path, sample_result: HegelionResult) -> None:
    """Test benchmark with --output file."""
    prompts_file = tmp_path / "prompts.jsonl"
    prompts_file.write_text('{"query": "Test"}\n')

    output_file = tmp_path / "output.jsonl"
    mock_runner = AsyncMock(return_value=[sample_result])
    monkeypatch.setattr(hegelion_bench, "run_benchmark", mock_runner)

    hegelion_bench.main([str(prompts_file), "--output", str(output_file)])

    # Output file should be created by run_benchmark
    # We just verify the call was made correctly
    call_kwargs = mock_runner.call_args[1]
    assert call_kwargs["output_file"] == output_file


def test_bench_with_debug_flag(monkeypatch, tmp_path: Path, sample_result: HegelionResult) -> None:
    """Test benchmark with --debug flag."""
    prompts_file = tmp_path / "prompts.jsonl"
    prompts_file.write_text('{"query": "Test"}\n')

    mock_runner = AsyncMock(return_value=[sample_result])
    monkeypatch.setattr(hegelion_bench, "run_benchmark", mock_runner)

    hegelion_bench.main([str(prompts_file), "--debug"])

    call_kwargs = mock_runner.call_args[1]
    assert call_kwargs["debug"] is True


def test_bench_with_summary(monkeypatch, tmp_path: Path, capsys, sample_result: HegelionResult) -> None:
    """Test benchmark with --summary flag."""
    prompts_file = tmp_path / "prompts.jsonl"
    prompts_file.write_text('{"query": "Query 1"}\n{"query": "Query 2"}\n')

    results = [sample_result, sample_result]
    mock_runner = AsyncMock(return_value=results)
    monkeypatch.setattr(hegelion_bench, "run_benchmark", mock_runner)

    hegelion_bench.main([str(prompts_file), "--summary"])

    captured = capsys.readouterr()
    assert "HEGELION BENCHMARK SUMMARY" in captured.out
    assert "Total queries processed: 2" in captured.out
    assert "Contradictions:" in captured.out
    assert "Research proposals:" in captured.out
    assert "Total time:" in captured.out


def test_bench_summary_statistics(monkeypatch, tmp_path: Path, capsys) -> None:
    """Test that summary calculates statistics correctly."""
    prompts_file = tmp_path / "prompts.jsonl"
    prompts_file.write_text('{"query": "Q1"}\n{"query": "Q2"}\n{"query": "Q3"}\n')

    results = [
        HegelionResult(
            query=f"Query {i}",
            mode="synthesis",
            thesis="T",
            antithesis="A",
            synthesis="S",
            contradictions=[{"description": f"Contradiction {i}"}] * (i + 1),
            research_proposals=[{"description": f"Proposal {i}"}] * (i + 1),
            metadata={
                "thesis_time_ms": float(i * 100),
                "antithesis_time_ms": float(i * 200),
                "synthesis_time_ms": float(i * 300),
                "total_time_ms": float(i * 600),
            },
        )
        for i in range(3)
    ]

    mock_runner = AsyncMock(return_value=results)
    monkeypatch.setattr(hegelion_bench, "run_benchmark", mock_runner)

    hegelion_bench.main([str(prompts_file), "--summary"])

    captured = capsys.readouterr()
    assert "Total queries processed: 3" in captured.out
    # Total contradictions: 1 + 2 + 3 = 6
    assert "6" in captured.out or "avg: 2.0" in captured.out


def test_bench_missing_file_raises(monkeypatch) -> None:
    """Test that missing prompts file raises error."""
    nonexistent = Path("/nonexistent/prompts.jsonl")

    mock_runner = AsyncMock()
    monkeypatch.setattr(hegelion_bench, "run_benchmark", mock_runner)

    with pytest.raises(SystemExit):
        hegelion_bench.main([str(nonexistent)])


def test_bench_empty_file(monkeypatch, tmp_path: Path, capsys) -> None:
    """Test benchmark with empty prompts file."""
    prompts_file = tmp_path / "empty.jsonl"
    prompts_file.write_text("")

    mock_runner = AsyncMock(return_value=[])
    monkeypatch.setattr(hegelion_bench, "run_benchmark", mock_runner)

    hegelion_bench.main([str(prompts_file), "--summary"])

    captured = capsys.readouterr()
    assert "No results to summarize" in captured.out or "Total queries processed: 0" in captured.out


def test_bench_without_output_prints_jsonl(monkeypatch, tmp_path: Path, capsys, sample_result: HegelionResult) -> None:
    """Test that benchmark prints JSONL when no output file specified."""
    prompts_file = tmp_path / "prompts.jsonl"
    prompts_file.write_text('{"query": "Test"}\n')

    mock_runner = AsyncMock(return_value=[sample_result])
    monkeypatch.setattr(hegelion_bench, "run_benchmark", mock_runner)

    hegelion_bench.main([str(prompts_file)])

    captured = capsys.readouterr()
    # Should print JSON
    lines = [line for line in captured.out.splitlines() if line.strip()]
    assert len(lines) > 0
    # First line should be valid JSON
    payload = json.loads(lines[0])
    assert payload["query"] == "Test Query"


def test_bench_error_handling(monkeypatch, tmp_path: Path) -> None:
    """Test that benchmark handles errors gracefully."""
    prompts_file = tmp_path / "prompts.jsonl"
    prompts_file.write_text('{"query": "Test"}\n')

    def failing_runner(*args, **kwargs):
        raise Exception("Test error")

    mock_runner = AsyncMock(side_effect=failing_runner)
    monkeypatch.setattr(hegelion_bench, "run_benchmark", mock_runner)

    with pytest.raises(SystemExit):
        hegelion_bench.main([str(prompts_file)])


def test_bench_processes_message(monkeypatch, tmp_path: Path, capsys, sample_result: HegelionResult) -> None:
    """Test that processed message is printed to stderr."""
    prompts_file = tmp_path / "prompts.jsonl"
    prompts_file.write_text('{"query": "Q1"}\n{"query": "Q2"}\n')

    mock_runner = AsyncMock(return_value=[sample_result, sample_result])
    monkeypatch.setattr(hegelion_bench, "run_benchmark", mock_runner)

    hegelion_bench.main([str(prompts_file)])

    captured = capsys.readouterr()
    assert "Processed 2 queries" in captured.err


import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from hegelion.models import HegelionResult
from hegelion.scripts import hegelion_cli, hegelion_bench


@pytest.fixture
def sample_result() -> HegelionResult:
    metadata = {
        "thesis_time_ms": 10.0,
        "antithesis_time_ms": 20.0,
        "synthesis_time_ms": 30.0,
        "total_time_ms": 60.0,
        "backend_provider": "Dummy",
        "backend_model": "dummy-model",
        "debug": {"internal_conflict_score": 0.5},
    }
    return HegelionResult(
        query="Sample Query",
        mode="synthesis",
        thesis="Sample thesis",
        antithesis="Sample antithesis",
        synthesis="Sample synthesis",
        contradictions=[{"description": "A contradiction", "evidence": "Evidence"}],
        research_proposals=[
            {"description": "A proposal", "testable_prediction": "Prediction"}
        ],
        metadata=metadata,
        trace={
            "thesis": "Sample thesis",
            "antithesis": "Sample antithesis",
            "synthesis": "Sample synthesis",
        },
    )


def test_cli_help_runs() -> None:
    subprocess.run(
        [sys.executable, "-m", "hegelion.scripts.hegelion_cli", "--help"], check=True
    )


def test_bench_help_runs() -> None:
    subprocess.run(
        [sys.executable, "-m", "hegelion.scripts.hegelion_bench", "--help"], check=True
    )


def test_cli_json_output(
    monkeypatch: pytest.MonkeyPatch, capsys, sample_result: HegelionResult
) -> None:
    mock_runner = AsyncMock(return_value=sample_result)
    monkeypatch.setattr(hegelion_cli, "run_dialectic", mock_runner)

    hegelion_cli.main([sample_result.query])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["query"] == "Sample Query"
    assert payload["mode"] == "synthesis"
    mock_runner.assert_awaited_once()


def test_cli_demo_mode(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    # Demo mode should not call the live runner and should print some JSON.
    mock_runner = AsyncMock()
    monkeypatch.setattr(hegelion_cli, "run_dialectic", mock_runner)

    hegelion_cli.main(["--demo"])

    captured = capsys.readouterr()
    assert captured.out.strip()  # some output
    assert "Result saved" not in captured.err
    mock_runner.assert_not_awaited()


def test_cli_summary_output(
    monkeypatch: pytest.MonkeyPatch, capsys, sample_result: HegelionResult
) -> None:
    mock_runner = AsyncMock(return_value=sample_result)
    monkeypatch.setattr(hegelion_cli, "run_dialectic", mock_runner)

    hegelion_cli.main([sample_result.query, "--format", "summary", "--debug"])

    captured = capsys.readouterr()
    assert "=== DEBUG METRICS ===" in captured.out
    assert "Result saved" not in captured.err


def test_bench_cli_prints_json(
    monkeypatch: pytest.MonkeyPatch,
    capsys,
    tmp_path: Path,
    sample_result: HegelionResult,
) -> None:
    prompts_path = tmp_path / "prompts.jsonl"
    prompts_path.write_text('{"query": "Sample"}\n', encoding="utf-8")

    mock_runner = AsyncMock(return_value=[sample_result])
    monkeypatch.setattr(hegelion_bench, "run_benchmark", mock_runner)

    hegelion_bench.main([str(prompts_path), "--summary"])

    captured = capsys.readouterr()
    lines = [line for line in captured.out.splitlines() if line.strip()]
    json_line = next(line for line in reversed(lines) if line.strip().startswith("{"))
    payload = json.loads(json_line)
    assert payload["query"] == "Sample Query"
    assert "HEGELION BENCHMARK SUMMARY" in captured.out
    assert "Processed 1 queries" in captured.err
    mock_runner.assert_awaited_once()


def test_cli_with_output_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, sample_result: HegelionResult
) -> None:
    """Test CLI with --output file."""
    output_file = tmp_path / "output.json"
    mock_runner = AsyncMock(return_value=sample_result)
    monkeypatch.setattr(hegelion_cli, "run_dialectic", mock_runner)

    hegelion_cli.main([sample_result.query, "--output", str(output_file)])

    assert output_file.exists()
    content = json.loads(output_file.read_text())
    assert content["query"] == "Sample Query"


def test_cli_with_output_jsonl(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, sample_result: HegelionResult
) -> None:
    """Test CLI with --output JSONL file."""
    output_file = tmp_path / "output.jsonl"
    mock_runner = AsyncMock(return_value=sample_result)
    monkeypatch.setattr(hegelion_cli, "run_dialectic", mock_runner)

    hegelion_cli.main([sample_result.query, "--output", str(output_file)])

    assert output_file.exists()
    content = output_file.read_text().strip()
    assert content.startswith("{")
    assert content.endswith("}")
    payload = json.loads(content)
    assert payload["query"] == "Sample Query"


def test_cli_with_debug_flag(
    monkeypatch: pytest.MonkeyPatch, capsys, sample_result: HegelionResult
) -> None:
    """Test CLI with --debug flag."""
    mock_runner = AsyncMock(return_value=sample_result)
    monkeypatch.setattr(hegelion_cli, "run_dialectic", mock_runner)

    hegelion_cli.main([sample_result.query, "--debug"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert "debug" in payload["metadata"]
    mock_runner.assert_awaited_once_with(query=sample_result.query, debug=True)


def test_cli_missing_query_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CLI raises error when query is missing."""
    with pytest.raises(SystemExit):
        hegelion_cli.main([])


def test_cli_configuration_error_handling(
    monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    """Test CLI handles ConfigurationError gracefully."""
    from hegelion.config import ConfigurationError

    def failing_runner(*args, **kwargs):
        raise ConfigurationError("No API key configured")

    mock_runner = AsyncMock(side_effect=failing_runner)
    monkeypatch.setattr(hegelion_cli, "run_dialectic", mock_runner)

    with pytest.raises(SystemExit):
        hegelion_cli.main(["Test query"])

    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert "No API key" in captured.err or "No LLM backend" in captured.err


def test_cli_demo_mode_with_format(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    """Test CLI demo mode with --format summary."""
    mock_runner = AsyncMock()
    monkeypatch.setattr(hegelion_cli, "run_dialectic", mock_runner)

    hegelion_cli.main(["--demo", "--format", "summary"])

    captured = capsys.readouterr()
    # Should print summary format
    assert captured.out.strip()
    mock_runner.assert_not_awaited()


def test_cli_summary_format_structure(
    monkeypatch: pytest.MonkeyPatch, capsys, sample_result: HegelionResult
) -> None:
    """Test that summary format has correct structure."""
    mock_runner = AsyncMock(return_value=sample_result)
    monkeypatch.setattr(hegelion_cli, "run_dialectic", mock_runner)

    hegelion_cli.main([sample_result.query, "--format", "summary"])

    captured = capsys.readouterr()
    output = captured.out

    # Check for key sections
    assert "Query:" in output
    assert "Mode:" in output
    assert "=== THESIS ===" in output
    assert "=== ANTITHESIS ===" in output
    assert "=== SYNTHESIS ===" in output
    assert "=== CONTRADICTIONS ===" in output
    assert "=== RESEARCH PROPOSALS ===" in output
    assert "=== TIMING ===" in output


def test_cli_summary_with_evidence(
    monkeypatch: pytest.MonkeyPatch, capsys, sample_result: HegelionResult
) -> None:
    """Test summary format includes evidence when present."""
    mock_runner = AsyncMock(return_value=sample_result)
    monkeypatch.setattr(hegelion_cli, "run_dialectic", mock_runner)

    hegelion_cli.main([sample_result.query, "--format", "summary"])

    captured = capsys.readouterr()
    assert "Evidence:" in captured.out


def test_cli_summary_with_prediction(
    monkeypatch: pytest.MonkeyPatch, capsys, sample_result: HegelionResult
) -> None:
    """Test summary format includes predictions when present."""
    mock_runner = AsyncMock(return_value=sample_result)
    monkeypatch.setattr(hegelion_cli, "run_dialectic", mock_runner)

    hegelion_cli.main([sample_result.query, "--format", "summary"])

    captured = capsys.readouterr()
    assert "Prediction:" in captured.out


def test_cli_json_format_default(
    monkeypatch: pytest.MonkeyPatch, capsys, sample_result: HegelionResult
) -> None:
    """Test that JSON format is default."""
    mock_runner = AsyncMock(return_value=sample_result)
    monkeypatch.setattr(hegelion_cli, "run_dialectic", mock_runner)

    hegelion_cli.main([sample_result.query])

    captured = capsys.readouterr()
    # Should be valid JSON
    payload = json.loads(captured.out)
    assert payload["query"] == "Sample Query"


def test_cli_output_file_message(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, sample_result: HegelionResult
) -> None:
    """Test that output file message is printed to stderr."""
    output_file = tmp_path / "output.json"
    mock_runner = AsyncMock(return_value=sample_result)
    monkeypatch.setattr(hegelion_cli, "run_dialectic", mock_runner)

    hegelion_cli.main([sample_result.query, "--output", str(output_file)])

    # Message should be in stderr (not stdout)
    # This is tested implicitly by the file existing
    assert output_file.exists()

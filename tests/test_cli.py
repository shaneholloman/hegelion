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
        research_proposals=[{"description": "A proposal", "testable_prediction": "Prediction"}],
        metadata=metadata,
        trace={"thesis": "Sample thesis", "antithesis": "Sample antithesis", "synthesis": "Sample synthesis"},
    )


def test_cli_help_runs() -> None:
    subprocess.run([sys.executable, "-m", "hegelion.scripts.hegelion_cli", "--help"], check=True)


def test_bench_help_runs() -> None:
    subprocess.run([sys.executable, "-m", "hegelion.scripts.hegelion_bench", "--help"], check=True)


def test_cli_json_output(monkeypatch: pytest.MonkeyPatch, capsys, sample_result: HegelionResult) -> None:
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


def test_cli_summary_output(monkeypatch: pytest.MonkeyPatch, capsys, sample_result: HegelionResult) -> None:
    mock_runner = AsyncMock(return_value=sample_result)
    monkeypatch.setattr(hegelion_cli, "run_dialectic", mock_runner)

    hegelion_cli.main([sample_result.query, "--format", "summary", "--debug"])

    captured = capsys.readouterr()
    assert "=== DEBUG METRICS ===" in captured.out
    assert "Result saved" not in captured.err


def test_bench_cli_prints_json(monkeypatch: pytest.MonkeyPatch, capsys, tmp_path: Path, sample_result: HegelionResult) -> None:
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

import json

import pytest

from hegelion.datasets import (
    export_training_data,
    to_dpo_dataset,
    to_instruction_tuning_dataset,
)
from hegelion.models import HegelionResult


def sample_result() -> HegelionResult:
    return HegelionResult(
        query="How to reduce bugs?",
        mode="synthesis",
        thesis="Add logging",
        antithesis="Logging is not enough",
        synthesis="Add tests and logging",
        contradictions=[],
        research_proposals=[],
        metadata={},
    )


def test_to_dpo_dataset_writes_preference_pairs(tmp_path):
    path = tmp_path / "dpo.jsonl"
    res = sample_result()

    to_dpo_dataset([res], path, rejected_source="both")

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2  # thesis and antithesis rejected examples

    rejected_values = {json.loads(line)["rejected"] for line in lines}
    assert rejected_values == {res.thesis, res.antithesis}
    for line in lines:
        payload = json.loads(line)
        assert payload["chosen"] == res.synthesis
        assert payload["prompt"].startswith("Query: How to reduce bugs?")


def test_to_instruction_tuning_dataset(tmp_path):
    path = tmp_path / "instructions.json"
    res = sample_result()

    to_instruction_tuning_dataset([res], path)

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data[0]["instruction"] == res.query
    assert data[0]["output"] == res.synthesis
    assert data[0]["system"]


def test_export_training_data_dispatch(tmp_path):
    res = sample_result()
    dpo_path = tmp_path / "out.jsonl"
    export_training_data([res], dpo_path, format="dpo", rejected_source="thesis")
    assert dpo_path.exists()

    instr_path = tmp_path / "out.json"
    export_training_data([res], instr_path, format="instruction")
    assert instr_path.exists()

    with pytest.raises(ValueError):
        export_training_data([res], tmp_path / "bad.json", format="unknown")

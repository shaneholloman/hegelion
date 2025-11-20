import json
from types import SimpleNamespace

import pytest

from hegelion.models import HegelionResult
from hegelion.scripts import hegelion_agent_cli


def make_result() -> HegelionResult:
    return HegelionResult(
        query="Investigate outage",
        mode="synthesis",
        thesis="Initial hypothesis",
        antithesis="Counter-argument",
        synthesis="Action: add tests",
        contradictions=[{"description": "Missing logging"}],
        research_proposals=[{"description": "Collect metrics"}],
        metadata={},
    )


class SpyAgent:
    init_calls = []
    for_coding_calls = []
    observations = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        SpyAgent.init_calls.append(kwargs)

    async def act(self, observation: str):
        SpyAgent.observations.append(observation)
        return SimpleNamespace(action="add tests", result=make_result())

    @classmethod
    def for_coding(cls, **kwargs):
        SpyAgent.for_coding_calls.append(kwargs)
        return cls(**kwargs)

    @classmethod
    def reset(cls):
        cls.init_calls = []
        cls.for_coding_calls = []
        cls.observations = []


@pytest.fixture(autouse=True)
def reset_spy_agent():
    SpyAgent.reset()


@pytest.mark.asyncio
async def test_run_text_output(monkeypatch: pytest.MonkeyPatch, capsys):
    monkeypatch.setattr(hegelion_agent_cli, "HegelionAgent", SpyAgent)

    args = hegelion_agent_cli.parse_args(["Cache is inconsistent"])
    exit_code = await hegelion_agent_cli.run(args)

    assert exit_code == 0
    assert SpyAgent.init_calls[0]["goal"] is None
    assert SpyAgent.observations == ["Cache is inconsistent"]

    captured = capsys.readouterr()
    assert "Action: add tests" in captured.out
    assert "=== THESIS ===" in captured.out
    assert "=== ANTITHESIS ===" in captured.out
    assert "=== SYNTHESIS ===" in captured.out


@pytest.mark.asyncio
async def test_run_json_output_uses_coding_agent(monkeypatch: pytest.MonkeyPatch, capsys):
    monkeypatch.setattr(hegelion_agent_cli, "HegelionAgent", SpyAgent)

    args = hegelion_agent_cli.parse_args(
        [
            "CI fails on Python 3.12",
            "--coding",
            "--goal",
            "Fix CI",
            "--personas",
            "council",
            "--iterations",
            "2",
            "--use-search",
            "--format",
            "json",
            "--debug",
        ]
    )

    await hegelion_agent_cli.run(args)

    assert SpyAgent.for_coding_calls == [
        {
            "goal": "Fix CI",
            "personas": "council",
            "iterations": 2,
            "use_search": True,
            "debug": True,
        }
    ]

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["action"] == "add tests"
    assert payload["result"]["query"] == "Investigate outage"

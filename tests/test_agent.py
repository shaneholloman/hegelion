import pytest

from hegelion.agent import HegelionAgent, default_action_extractor
from hegelion.models import HegelionResult


def make_result(synthesis: str = "Action: run tests") -> HegelionResult:
    return HegelionResult(
        query="q",
        mode="synthesis",
        thesis="thesis",
        antithesis="antithesis",
        synthesis=synthesis,
        contradictions=[],
        research_proposals=[],
        metadata={},
    )


def test_default_action_extractor_prefers_action_line():
    res = make_result("Next Action: deploy safely\nOther line")
    assert default_action_extractor(res) == "deploy safely"


def test_act_sync_builds_query_and_history(monkeypatch):
    captured = {}

    def fake_run_dialectic_sync(query, **kwargs):
        captured["query"] = query
        return make_result("Action: ship")

    monkeypatch.setattr("hegelion.agent.run_dialectic_sync", fake_run_dialectic_sync)

    agent = HegelionAgent.for_coding(goal="Fix CI")
    step = agent.act_sync("CI fails on Python 3.12")

    assert "Goal: Fix CI" in captured["query"]
    assert "Observation: CI fails on Python 3.12" in captured["query"]
    assert "Focus on code changes" in captured["query"]
    assert step.action == "ship"
    assert len(agent.history) == 1


@pytest.mark.asyncio
async def test_act_async_uses_adversarial_prompt(monkeypatch):
    captured = {}

    async def fake_run_dialectic(query, **kwargs):
        captured["query"] = query
        return make_result("Action -> add tests")

    monkeypatch.setattr("hegelion.agent.run_dialectic", fake_run_dialectic)

    agent = HegelionAgent(goal="Reduce regressions", action_guidance="Prefer tests")
    step = await agent.act("Validate new cache layer")

    assert "adversarially attack hallucinations" in captured["query"].lower()
    assert "Action" in step.action
    assert len(agent.history) == 1

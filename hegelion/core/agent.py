"""Agent helpers for using Hegelion inside reflexive/action loops."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Union

from .backends import LLMBackend
from .core import run_dialectic, run_dialectic_sync
from .models import HegelionResult
from .personas import Persona

# Extract the actionable move from a synthesized answer.
ActionExtractor = Callable[[HegelionResult], str]


def default_action_extractor(result: HegelionResult) -> str:
    """
    Pull a concrete action line from the synthesis when present.

    Falls back to returning the entire synthesis when no explicit action is
    detected. This keeps the agent usable with existing prompts while still
    preferring concise commands when the model provides them.
    """

    for line in result.synthesis.splitlines():
        lowered = line.strip().lower()
        if lowered.startswith(("action:", "next action:", "next_action:", "do:", "action ->")):
            # Preserve the original casing of the action line for readability.
            return line.split(":", 1)[1].strip() if ":" in line else line.strip()
    return result.synthesis.strip()


@dataclass
class AgentStep:
    """Container for a single agent turn."""

    observation: str
    result: HegelionResult
    action: str

    def to_dict(self) -> dict:
        """Serialize to a plain dict (handy for logging)."""

        return {
            "observation": self.observation,
            "action": self.action,
            "result": self.result.to_dict(),
        }


class HegelionAgent:
    """
    Lightweight wrapper that runs the dialectic before acting.

    Useful for Reflexion-style agents: the agent critiques its own plan
    (thesis → antithesis) and only acts on the synthesized recommendation.
    """

    def __init__(
        self,
        *,
        goal: Optional[str] = None,
        backend: Optional[LLMBackend] = None,
        model: Optional[str] = None,
        personas: Optional[Union[List[Persona], str]] = None,
        iterations: int = 1,
        use_search: bool = False,
        debug: bool = False,
        action_extractor: Optional[ActionExtractor] = None,
        action_guidance: Optional[str] = None,
    ) -> None:
        self.goal = goal
        self.backend = backend
        self.model = model
        self.personas = personas
        self.iterations = iterations
        self.use_search = use_search
        self.debug = debug
        self._action_extractor = action_extractor or default_action_extractor
        self.action_guidance = action_guidance
        self.history: List[AgentStep] = []

    @classmethod
    def for_coding(
        cls,
        goal: Optional[str] = None,
        **kwargs,
    ) -> "HegelionAgent":
        """
        Convenience constructor tuned for coding agents.

        Adds guidance that nudges the dialectic toward concrete edits, tests, and
        verification steps to reduce hallucinations in code suggestions.
        """

        guidance = (
            "Focus on code changes, tests, and reproducible commands. Prefer minimal"
            " diffs, name exact files, and include validation steps. Reject actions"
            " that rely on unverified APIs or assumptions."
        )
        return cls(goal=goal, action_guidance=guidance, **kwargs)

    def _build_query(self, observation: str) -> str:
        """Shape the agent observation into a dialectic-friendly query."""

        parts = []
        if self.goal:
            parts.append(f"Goal: {self.goal}")
        parts.append(f"Observation: {observation}")
        if self.action_guidance:
            parts.append(f"Context: {self.action_guidance}")
        parts.append(
            "Run a full thesis → antithesis → synthesis pass on the next step."
            " The antithesis must adversarially attack hallucinations, unverifiable"
            " claims, and risky assumptions. The synthesis should propose a single"
            " concrete, testable action that survives critique and lists any checks"
            " needed to de-risk it. Return the action first, then the reasoning."
        )
        return "\n\n".join(parts)

    async def deliberate(self, observation: str) -> HegelionResult:
        """Run the full dialectic for an observation and return the result."""

        query = self._build_query(observation)
        return await run_dialectic(
            query,
            debug=self.debug,
            backend=self.backend,
            model=self.model,
            personas=self.personas,
            iterations=self.iterations,
            use_search=self.use_search,
        )

    async def act(self, observation: str) -> AgentStep:
        """Deliberate, extract an action, record it, and return the step."""

        result = await self.deliberate(observation)
        action = self._action_extractor(result)
        step = AgentStep(observation=observation, result=result, action=action)
        self.history.append(step)
        return step

    def act_sync(self, observation: str) -> AgentStep:
        """Synchronous convenience wrapper around ``act``."""

        query = self._build_query(observation)
        result = run_dialectic_sync(
            query,
            debug=self.debug,
            backend=self.backend,
            model=self.model,
            personas=self.personas,
            iterations=self.iterations,
            use_search=self.use_search,
        )
        action = self._action_extractor(result)
        step = AgentStep(observation=observation, result=result, action=action)
        self.history.append(step)
        return step

    def reset_history(self) -> None:
        """Clear stored agent turns."""

        self.history.clear()

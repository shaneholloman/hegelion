# Hegelion Agents Protocol

Hegelion can run as a reflexive agent loop: every action must survive an adversarial dialectic (thesis → antithesis → synthesis) before it is executed. This pattern reduces hallucinations by forcing the model to critique its own plan and propose verification steps.

## Core Loop

1. **Observe:** Receive environment state/input.
2. **Thesis (Plan A):** Propose the best next action with reasoning.
3. **Antithesis (Adversarial Critique):** Attack the plan for hallucinations, missing evidence, unsafe assumptions, and unclear validation.
4. **Synthesis (Action Decision):** Produce a single action that survives critique, plus checks/tests to de-risk it.
5. **Act:** Execute the synthesized action, log traces for preference data (optional), and repeat with the new observation.

This is adversarial reflexion: the agent refuses to act until its own critique passes.

## Python API

```python
from hegelion.agent import HegelionAgent

# General-purpose agent
agent = HegelionAgent(goal="Ship the feature safely", personas="council", iterations=2)
step = agent.act_sync("Tests are flaky after enabling caching; what should we do next?")
print("Action:", step.action)

# Coding-focused convenience
coding_agent = HegelionAgent.for_coding(goal="Fix the failing CI job", iterations=2)
step = coding_agent.act_sync("CI fails on Python 3.12 with import errors")
print("Action:", step.action)
```

Key behaviors:
- Injects adversarial critique instructions to reduce hallucinations and overconfident plans.
- Supports async (`act`) and sync (`act_sync`) flows.
- Stores a `history` of `AgentStep` objects for logging or training data.

## CLI and MCP

- **CLI (coding-focused):**

```bash
python -m hegelion.scripts.hegelion_agent_cli "CI fails on Python 3.12" --goal "Fix CI" --coding --iterations 2
```

- **MCP tool:** `hegelion_agent_act`
  - Input: `{ observation: string, goal?: string, personas?: string, iterations?: number, use_search?: boolean, action_guidance?: string, debug?: boolean }`
  - Output: `{ action: string, result: HegelionResult }`

## Why It Reduces Hallucinations

- **Adversarial antithesis:** Forces the model to find missing evidence and risky assumptions before acting.
- **Synthesis with checks:** The action includes validations/tests to run, making unverified claims explicit.
- **Iterative refinement:** `iterations > 1` lets the synthesis become the next thesis, compounding scrutiny.

## Tips for Coding Agents

- Set `personas="council"` for multi-critic stress tests.
- Keep `iterations=2` for fast yet reflective runs.
- Log `history` and feed it to `export_training_data` to bootstrap preference datasets.

# Hegelion Agents Protocol

Hegelion can run as a reflexive agent loop: every action must survive an adversarial dialectic (thesis → antithesis → synthesis) before it is executed. This pattern reduces hallucinations by forcing the model to critique its own plan and propose verification steps.

## Core Loop

1. **Observe:** Receive environment state/input.
2. **Thesis (Plan A):** Propose the best next action with reasoning.
3. **Antithesis (Adversarial Critique):** Attack the plan for hallucinations, missing evidence, unsafe assumptions, and unclear validation.
4. **Synthesis (Action Decision):** Produce a single action that survives critique, plus checks/tests to de-risk it.
5. **Act:** Execute the synthesized action, log traces for preference data (optional), and repeat with the new observation.

This is adversarial reflexion: the agent refuses to act until its own critique passes.

## Prompt-Driven Implementation (No API Keys)

Hegelion ships a **prompt MCP server** (`hegelion.prompt_mcp_server`) that returns the exact prompts needed for each phase. Sequential-thinking hosts such as Cursor, Claude Desktop, or Gemini can call these tools and run the prompts with their own LLMs.

### Dialectical Workflow Tool

```python
from hegelion.prompt_dialectic import create_dialectical_workflow

workflow = create_dialectical_workflow(
    query="Should we subsidize fusion research?",
    use_search=True,
    use_council=True,
    use_judge=True,
)
```

This returns JSON like:

```jsonc
{
  "workflow_type": "prompt_driven_dialectic",
  "steps": [
    { "step": 1, "name": "Generate Thesis", "prompt": { "phase": "thesis", ... } },
    { "step": 2, "name": "Council Critique: council_the_logician", "prompt": { ... } },
    { "step": 5, "name": "Generate Synthesis", "prompt": { "phase": "synthesis", ... } }
  ],
  "instructions": {
    "execution_mode": "sequential",
    "variable_substitution": "Replace {{thesis_from_step_1}} with the actual output",
    "final_output": "Combine all steps into a HegelionResult"
  }
}
```

Each `prompt` entry contains:
- `phase`: thesis / antithesis / synthesis / council member
- `prompt`: the actual text to feed into the LLM
- `instructions`: how the LLM should respond
- `expected_format`: e.g., `CONTRADICTION:` / `EVIDENCE:` pairs

The FastAPI service under `extensions/gemini/server` exposes HTTP endpoints (`/dialectical_workflow`, `/dialectical_single_shot`, `/thesis_prompt`, etc.) that simply return this data—ideal for Gemini Extensions or other marketplaces where only HTTP tools are allowed.

### Sequential Thinking (single prompt)

`create_single_shot_dialectic_prompt` returns a monolithic prompt that instructs the LLM to run Thesis → Antithesis → Synthesis by itself and format the result into:

```
## THESIS
...
## ANTITHESIS
...
## SYNTHESIS
...
```

## Python Agent (Optional, requires provider keys)

For teams that want Hegelion to run the loop itself, use the Python agent:

```python
from hegelion.agent import HegelionAgent

agent = HegelionAgent(goal="Ship safely", personas="council", iterations=2)
step = agent.act_sync("Tests are flaky after enabling caching")
print(step.action)
```

CLI + MCP:

```bash
python -m hegelion.scripts.hegelion_agent_cli "CI fails on Python 3.12" --goal "Fix CI" --coding --iterations 2
```

`hegelion_agent_act` (MCP tool) accepts `{ observation, goal?, personas?, iterations?, use_search?, debug? }` and returns `{ action, result }`.

## Why the Protocol Works

- **Adversarial Antithesis:** explicit instructions to attack hallucinations.
- **Structured Output:** prompts require `CONTRADICTION` / `EVIDENCE` fields and synthesis predictions.
- **Optional Council & Judge:** multi-perspective critiques plus a scoring phase catch gaps before action.

Whether you use the prompt server or the Python agent, the structure is identical—only the executor changes.

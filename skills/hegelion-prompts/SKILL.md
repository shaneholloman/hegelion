---
name: hegelion-prompts
description: Generate and execute Hegelion dialectical reasoning and autocoding prompts without MCP. Use when users ask for thesis/antithesis/synthesis, contradictions, or player/coach autocoding loops, or when integrating Hegelion into Codex/agent workflows.
---

# Hegelion Prompt Workflows

## Instructions
- Prefer MCP tools when available (`dialectical_single_shot`, `dialectical_workflow`, `hegelion`, `autocoding_*`) and execute the returned prompts.
- If MCP tools are not available, use the Python prompt APIs in this repo.
- Prefer `create_single_shot_dialectic_prompt` for quick analyses; use `create_dialectical_workflow` for step-by-step prompts.
- Use `response_style="json"` when you need structured output.
- For autocoding loops, use `PromptDrivenAutocoding` and manage multi-turn state with `AutocodingState`.

## Examples

### Dialectical reasoning (no MCP)

```python
from hegelion.core.prompt_dialectic import create_single_shot_dialectic_prompt

prompt = create_single_shot_dialectic_prompt(
    "Is open source sustainable?",
    use_council=True,
    response_style="json",
)
```

Run the prompt with the host model and return the synthesis plus any structured fields.

### Autocoding (no MCP)

```python
from hegelion.core.autocoding_state import AutocodingState
from hegelion.core.prompt_autocoding import PromptDrivenAutocoding

state = AutocodingState.create(requirements="... checklist ...")
autocoder = PromptDrivenAutocoding()
player_prompt = autocoder.generate_player_prompt(
    state.requirements,
    turn_number=1,
    max_turns=state.max_turns,
)
```

After the coach phase, advance with `state.advance_turn(...)` and continue until approved or timeout.

## References
- For tool lists and MCP behavior, open `docs/guides/mcp_instructions.md`.
- For agent protocol details, open `docs/guides/agents.md`.

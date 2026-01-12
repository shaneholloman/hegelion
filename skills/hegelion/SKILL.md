---
name: hegelion
description: Apply dialectical reasoning or autocoding via Hegelion MCP tools; use for /hegelion, thesis/antithesis/synthesis, or player/coach workflows.
---

# Hegelion Skill

Use this skill when the user asks for Hegelion, dialectical reasoning, or autocoding with verification.

## Workflow

1) Classify the task: analysis/decision vs implementation.
2) If MCP tools are available:
   - Analysis: call `mcp__hegelion__dialectical_single_shot` with `response_style="synthesis_only"` (or `sections` if full output requested).
   - Step-by-step analysis: call `mcp__hegelion__dialectical_workflow` with `format="workflow"`.
   - Implementation: call `mcp__hegelion__hegelion` with `mode="workflow"` and follow `player_prompt` -> `coach_prompt` -> `autocoding_advance`.
3) If MCP tools are not available, run a manual loop:
   - THESIS -> ANTITHESIS -> SYNTHESIS for analysis.
   - PLAYER -> COACH (with a compliance checklist and verdict) for implementation.
4) Keep outputs concise and make verification explicit. The COACH decides when requirements are satisfied.

## Notes

- Never let PLAYER self-approve.
- Prefer tests or checks when implementing changes.
- Use `use_council=true` when the user wants multi-perspective critique.

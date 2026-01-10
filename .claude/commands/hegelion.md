# /hegelion

Apply dialectical reasoning to the task below.

## Task
$ARGUMENTS

---

## Quick Start

**Detect task type:**
- Questions/decisions → **Dialectical** (thesis → antithesis → synthesis)
- Code changes → **Autocoding** (player → coach verification loop)
- Both → Do dialectical analysis first, then autocoding for implementation

**MCP tools available?** Use them. Otherwise, follow manual workflows below.

---

## Dialectical Reasoning

*For: "should we...", "evaluate...", "compare...", "what's the best..."*

### With MCP:
```
mcp__hegelion__dialectical_single_shot(
  query="<question>",
  response_style="synthesis_only"
)
```
Execute the returned prompt.

### Without MCP:
1. **THESIS** — Strongest case for one position
2. **ANTITHESIS** — Steel-man the opposite, find contradictions
3. **SYNTHESIS** — Novel insight that transcends both

Output: 2-3 paragraphs of synthesis only (not the thesis/antithesis).

---

## Autocoding

*For: "add...", "fix...", "implement...", "refactor..."*

### With MCP:
```
mcp__hegelion__hegelion(
  requirements="- req 1\n- req 2",
  mode="workflow"
)
```
Follow workflow: `player_prompt` → execute → `coach_prompt` → execute → `autocoding_advance`

### Without MCP:

**PLAYER** (implement):
- Parse requirements as checklist
- Implement systematically
- Run tests
- Hand off: "Switching to COACH"

**COACH** (verify):
- Ignore PLAYER's claims
- Verify each requirement independently
- Output:
```
COMPLIANCE:
- [✓] Req 1 — how verified
- [✗] Req 2 — what's wrong

VERDICT: COACH APPROVED | NEEDS WORK
```

Loop until approved (max 5 turns, then ask user).

---

## Advanced Options

| Option | Effect | Example |
|--------|--------|---------|
| `use_council=true` | Multi-perspective critique (Logician, Empiricist, Ethicist) | Deeper analysis |
| `use_search=true` | Ground in real-world evidence | Current events, facts |
| `response_style="json"` | Structured output with schema | Programmatic use |

---

## Core Rules

1. **COACH decides** — PLAYER never self-approves
2. **Verify > assume** — Run code, check output
3. **Synthesis > lists** — Insight, not enumeration

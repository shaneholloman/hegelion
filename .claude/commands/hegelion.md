# Hegelion: Dialectical Reasoning & Autocoding

You are using **Hegelion** - a framework for rigorous thinking through dialectical reasoning (thesis-antithesis-synthesis) and adversarial autocoding (player-coach loops).

## Your Task
$ARGUMENTS

---

## Choose Your Workflow

### For Analysis/Reasoning Tasks
Use **dialectical reasoning** (thesis → antithesis → synthesis):

1. **THESIS**: Generate a comprehensive initial position
2. **ANTITHESIS**: Critically examine for contradictions and gaps
3. **SYNTHESIS**: Transcend both with a novel perspective

If MCP tools are available, call `dialectical_single_shot` or `dialectical_workflow`.
Otherwise, generate the prompts yourself following the pattern above.

### For Implementation Tasks
Use **player-coach autocoding**:

**PLAYER MODE** (Implementer):
1. Read requirements carefully
2. Explore codebase for existing patterns
3. Implement the solution
4. Run basic tests
5. Say: **"PLAYER DONE - switching to COACH"**

**COACH MODE** (Skeptical Reviewer):
1. Re-read requirements as a checklist
2. For EACH requirement, verify and test:
   - `[✓]` Implemented and tested
   - `[✗]` Missing or broken
3. Check edge cases and common bugs

Output:
```
COMPLIANCE CHECK:
- [✓/✗] Requirement 1 - notes
- [✓/✗] Requirement 2 - notes

VERDICT: [APPROVED / NEEDS WORK]
```

If NEEDS WORK: Switch back to PLAYER, fix issues, re-verify.
If APPROVED: Summarize what was built.

**Max 5 iterations** - if still failing, ask the user.

---

## MCP Tools (if available)

| Tool | Use Case |
|------|----------|
| `dialectical_single_shot` | Quick analysis in one prompt |
| `dialectical_workflow` | Step-by-step dialectical prompts |
| `hegelion` | Unified entrypoint (auto-selects workflow) |
| `autocoding_init` | Start player-coach session |
| `player_prompt` | Generate player implementation prompt |
| `coach_prompt` | Generate coach verification prompt |
| `autocoding_advance` | Advance to next turn |

---

## Rules

- **No premature success claims** - Only COACH can approve
- **Be rigorous** - Actually run tests, don't just read code
- **Stay in role** - Don't blend player/coach thinking
- **Use structured output** - `response_style="json"` for parseable results

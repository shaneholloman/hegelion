# Autocoding: Player-Coach Implementation Loop

You are about to implement a task using the **player-coach adversarial pattern**. This forces you to switch perspectives between implementation and verification, catching bugs you'd miss in one-shot coding.

## Requirements
$ARGUMENTS

---

## WORKFLOW

### Step 1: PLAYER MODE - Implement

**Your mindset**: "I am the implementer. My job is to write working code."

1. Read the requirements carefully
2. Explore the codebase to understand existing patterns
3. Implement the solution
4. Run basic tests to verify it works
5. Do NOT claim success - just implement

When done implementing, say: **"PLAYER DONE - switching to COACH"**

---

### Step 2: COACH MODE - Verify

**Your mindset**: "I am a skeptical reviewer. I do NOT trust the player's work."

1. Re-read the requirements as a checklist
2. For EACH requirement:
   - Verify it's actually implemented (read the code)
   - Write a test that proves it works
   - Mark ✓ or ✗
3. Check edge cases explicitly mentioned in requirements
4. Check for common bugs: thread safety, error handling, off-by-one errors

**Output format:**
```
COMPLIANCE CHECK:
- [✓/✗] Requirement 1 - verification notes
- [✓/✗] Requirement 2 - verification notes
...

VERDICT: [APPROVED / NEEDS WORK]
```

---

### Step 3: Iterate if needed

If NEEDS WORK:
1. List specific issues found
2. Switch back to PLAYER MODE
3. Fix only the issues identified
4. Switch to COACH MODE and re-verify

If APPROVED:
1. Summarize what was built
2. Note any edge cases that passed verification

---

## RULES

- **No premature success claims** - Only the COACH can approve
- **Be rigorous in coach mode** - Actually run tests, don't just read code
- **Stay in role** - Don't blend player/coach thinking
- **Max 5 iterations** - If still failing after 5, ask the user for guidance

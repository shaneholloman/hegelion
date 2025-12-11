# Hegelion

> "The True is the whole." — G.W.F. Hegel

Hegelion applies dialectical reasoning to LLMs: forcing models to argue with themselves before reaching conclusions. This produces better reasoning for questions and better code for implementations.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg) [![PyPI version](https://badge.fury.io/py/hegelion.svg)](https://badge.fury.io/py/hegelion)

---

## Two Modes

| Mode | Pattern | Use Case |
|------|---------|----------|
| **Dialectical Reasoning** | Thesis → Antithesis → Synthesis | Deep analysis of questions, philosophy, strategy |
| **Autocoding** | Player → Coach → Iterate | Verified code implementations with independent review |

Both modes use the same principle: **force the model to oppose itself** before concluding. This catches blind spots that single-pass approaches miss.

---

## Autocoding: Player-Coach Loop

**New in v0.4.0** — Based on [Block AI's g3 agent research](https://block.xyz/documents/adversarial-cooperation-in-code-synthesis.pdf).

### The Problem

Single-agent coding tools often:
- Declare success prematurely ("I have successfully implemented all requirements!")
- Accumulate context pollution over long sessions
- Miss edge cases because they verify their own work

### The Solution

Two roles iterate until requirements are verified:

```
REQUIREMENTS (Source of Truth)
        │
        ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│    PLAYER     │────▶│     COACH     │────▶│    ADVANCE    │
│  Implements   │     │   Verifies    │     │    State      │
│  code & tests │     │ independently │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
        ▲                                           │
        │              ┌───────────┐                │
        └──────────────│ APPROVED? │◀───────────────┘
                       └───────────┘
                         │       │
                        No      Yes
                         │       │
                         ▼       ▼
                     Continue   Done
```

**Player**: Implements requirements, writes tests, responds to feedback. Does NOT declare success.

**Coach**: Independently verifies each requirement, ignores player's self-assessment, outputs structured checklist.

### Key Insight

> "Discard the player's self-report of success. Have the coach perform independent evaluation."

The coach catches issues by re-reading requirements and actually running tests—not by trusting what the player says it did.

### Quick Start

In Claude Code, Cursor, or any MCP-enabled editor:

```
You: Use autocoding_init with these requirements:
     - Add user authentication to src/api.py
     - Add tests in tests/test_auth.py
     - All tests must pass

[Session initializes]

You: Generate player_prompt and implement

[Player writes code and tests]

You: Generate coach_prompt and verify

[Coach: ✓ auth endpoint exists, ✗ missing password validation test]

You: Call autocoding_advance and continue

[Loop until COACH APPROVED]
```

### MCP Tools

| Tool | Purpose |
|------|---------|
| `autocoding_init` | Start session with requirements checklist |
| `player_prompt` | Generate implementation prompt |
| `coach_prompt` | Generate verification prompt |
| `autocoding_advance` | Update state after coach review |
| `autocoding_single_shot` | Combined prompt for simpler tasks |
| `autocoding_save` / `autocoding_load` | Persist and resume sessions |

### Why It Works

| Problem | Single Agent | Coach-Player |
|---------|--------------|--------------|
| **Anchoring** | Drifts from requirements | Requirements anchor every turn |
| **Verification** | Self-assessment (unreliable) | Independent verification |
| **Context** | Accumulates pollution | Fresh context each turn |
| **Completion** | Open-ended | Explicit approval gates |

---

## Dialectical Reasoning: Thesis → Antithesis → Synthesis

For questions requiring deep analysis, Hegelion forces three separate LLM calls:

```
[Call 1] Thesis     → LLM commits to a position
[Call 2] Antithesis → LLM attacks that position (separate call, no hedging)
[Call 3] Synthesis  → LLM reconciles the opposition
```

### Why Separate Calls Matter

| Method | Calls | Result |
|--------|:-----:|--------|
| **Raw** | 1 | "It depends on definitions..." |
| **Enhanced** | 1 | "Hold both views in tension..." |
| **Hegelion** | 3 | Novel framework with testable predictions |

When the model must commit to a thesis, then genuinely attack it in a separate call, the synthesis surfaces insights that single-call approaches shortcut.

<details>
<summary><b>Example: "Is free will compatible with determinism?"</b></summary>

**Hegelion synthesis** (after thesis and antithesis):

> The deadlock dissolves when we recognize free will exists on a **spectrum of self-authorship**:
>
> 1. **Minimal freedom**: Acting on desires without external coercion
> 2. **Reflective freedom**: Second-order endorsement—I want to want this
> 3. **Narrative freedom**: Acting consistently with a coherent life narrative
> 4. **Constitutive freedom**: Recursive self-modification through deliberate habituation
>
> **Research proposal**: Use fMRI to scan participants under (1) snap judgments, (2) brief reflection, (3) extended deliberation. Hypothesis: Condition (3) shows strongest correlation with self-reported decision "ownership."

This 4-level framework emerged from actually arguing with itself—not from asking for "thesis/antithesis/synthesis" in one prompt.
</details>

### Quick Start

```bash
pip install hegelion

# MCP setup for Claude Desktop (macOS)
hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

Or use the Python API:

```python
import asyncio
from hegelion import run_dialectic

async def main():
    result = await run_dialectic("Is AI conscious?")
    print(result.synthesis)

asyncio.run(main())
```

Or CLI:

```bash
hegelion --stream "Is consciousness fundamental or emergent?"
```

### Feature Toggles

| Option | Description |
|--------|-------------|
| `use_council` | Three critics: Logician, Empiricist, Ethicist |
| `use_judge` | Final quality evaluation |
| `use_search` | Grounds arguments with web search |
| `response_style` | `sections`, `json`, or `synthesis_only` |

---

## Installation

```bash
pip install hegelion
```

For MCP integration (Claude Desktop, Cursor, VS Code):

```bash
# Claude Desktop (macOS)
hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Then restart Claude Desktop
```

See [MCP Integration Guide](docs/guides/mcp-integration.md) for other editors.

---

## Documentation

- **[MCP Integration](docs/guides/mcp-integration.md)** — Setup for Claude Desktop, Cursor, VS Code, Gemini CLI
- **[Python API](docs/guides/python-api.md)** — Full API reference
- **[CLI Reference](docs/guides/cli-reference.md)** — Command-line usage
- **[Configuration](docs/getting-started/configuration.md)** — Backends and feature toggles
- **[Technical Specification](docs/HEGELION_SPEC.md)** — Output schemas, phase specs

---

## Contributing

Issues and PRs welcome. For significant changes, open a discussion first.

---

## Recent Changes

### v0.4.0 (December 2025)

- **Autocoding system**: Player-coach dialectical loop based on Block AI's g3 agent
- MCP tools: `autocoding_init`, `player_prompt`, `coach_prompt`, `autocoding_advance`
- Session persistence with `autocoding_save` / `autocoding_load`
- Single-shot mode for simpler use cases

### v0.3.x

- CLI streaming with `--stream` flag
- MCP progress notifications
- 470+ tests passing

---

**License:** MIT

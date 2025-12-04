# Hegelion

> "The True is the whole." — G.W.F. Hegel

Hegelion is a reasoning wrapper that forces LLMs through three phases: **Thesis → Antithesis → Synthesis**. Each phase is a separate API call, preventing the model from hedging its way to a balanced answer.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg) [![PyPI version](https://badge.fury.io/py/hegelion.svg)](https://badge.fury.io/py/hegelion)

---

## The Difference

The question: **Does separating thesis → antithesis → synthesis into distinct API calls produce better reasoning than asking for all three in one prompt?**

We tested three approaches:

| Method | Calls | Approach |
|--------|:-----:|----------|
| **Raw** | 1 | Simple prompt, no structure |
| **Enhanced** | 1 | Single prompt requesting thesis/antithesis/synthesis |
| **Hegelion** | 3 | Separate calls with forced redirection between phases |

### Test: *"Is free will compatible with determinism?"*

<details>
<summary><b>Raw (1 call)</b></summary>

> The compatibility of free will and determinism depends heavily on how we define free will. Compatibilists argue yes, incompatibilists say no... Ultimately, **the debate often turns on whether we prioritize metaphysical concerns or practical concerns about autonomy.**

*Result: Survey of positions, ends with "it depends."*
</details>

<details>
<summary><b>Enhanced (1 call)</b></summary>

> A mature view likely requires what Wilfrid Sellars called **'stereoscopic vision'—holding both perspectives while recognizing their distinct purposes.** We are both determined and deciding, caused and choosing.

*Result: Comprehensive analysis, ends with "hold both views."*
</details>

<details>
<summary><b>Hegelion (3 calls)</b></summary>

> The deadlock dissolves when we recognize free will is not binary but exists on a **spectrum of self-authorship**:
>
> 1. **Minimal freedom**: Acting on desires without external coercion
> 2. **Reflective freedom**: Second-order endorsement—I want to want this
> 3. **Narrative freedom**: Acting consistently with a coherent life narrative
> 4. **Constitutive freedom**: Recursive self-modification through deliberate habituation
>
> **Resolving manipulation**: The manipulated agent lacks freedom not because their desires are caused externally, but because the causation *bypasses their enduring character*.
>
> **Research proposal**: Use fMRI to scan participants under (1) snap judgments, (2) brief reflection, (3) extended deliberation. Hypothesis: Condition (3) shows strongest correlation with self-reported decision "ownership."

*Result: Novel 4-level framework with testable predictions.*
</details>

### Why the Difference?

Both Enhanced and Hegelion ask for dialectical reasoning. But:

- **Enhanced (1 call)**: The model knows where it's going. It constructs a balanced synthesis without genuinely confronting contradictions.
- **Hegelion (3 calls)**: The model commits to a thesis, then attacks it in a separate call (no hedging), then synthesizes. The forced redirection surfaces insights the single-call approach shortcuts.

The "self-authorship spectrum" emerged from *actually arguing with itself* across separate calls—not from asking for thesis/antithesis/synthesis in one breath.

---

## Quick Start

### MCP (Claude Desktop, Cursor, VS Code)

No extra API keys needed. Hegelion generates prompts; your editor's model runs them.

```bash
pip install hegelion

# Claude Desktop (macOS)
hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Then restart Claude Desktop (Cmd+Q and reopen)
```

Verify by asking: *"What Hegelion tools are available?"*

**Agent Instructions:** If you are configuring an AI agent to use Hegelion, see [MCP_INSTRUCTIONS.md](docs/guides/mcp_instructions.md) for system prompt guidelines.

**Other editors:** See [MCP Integration Guide](docs/guides/mcp-integration.md)

### Python API

```bash
pip install hegelion
```

```python
import asyncio
from hegelion import run_dialectic

async def main():
    result = await run_dialectic("Is AI conscious?")
    print(result.synthesis)

asyncio.run(main())
```

Configure your backend in `.env`:
```bash
HEGELION_PROVIDER=anthropic
HEGELION_MODEL=claude-4.5-sonnet-latest
ANTHROPIC_API_KEY=your-key
```

### CLI & Visualization

Run dialectics directly from the command line with rich output:

```bash
hegelion "Is mathematics invented or discovered?"
```

**Streaming Mode** — Watch the dialectic unfold in real-time:
```bash
hegelion --stream "Is consciousness fundamental or emergent?"
```

Output streams phase-by-phase with visual headers:
```
━━━ THESIS ━━━
Consciousness appears to be a fundamental feature of reality...
(thesis completed in 8,234ms)

━━━ ANTITHESIS ━━━
The thesis commits several critical errors...
(antithesis completed in 12,891ms)

━━━ SYNTHESIS ━━━
The deadlock dissolves when we recognize...
(synthesis completed in 15,442ms)
```

**Interactive Mode:**
```bash
hegelion --interactive
```

---

## How It Works

Hegelion is multi-call orchestration. Each phase is a separate LLM call.

```
[Call 1] Thesis prompt    → LLM → thesis
[Call 2] Antithesis prompt → LLM → critique (attacks the thesis)
[Call 3] Synthesis prompt  → LLM → resolution
```

### Cost

| Mode | API Calls | Cost vs Raw |
|------|-----------|-------------|
| Basic | 3 | ~3-4x |
| + Council | 5 (3 concurrent critics) | ~5-6x |
| + Judge | 4-6+ (with retries) | ~6-10x |

More calls = more cost, but each phase builds on the previous, catching blind spots a single pass misses.

### Feature Toggles

| Option | Description |
|--------|-------------|
| `use_council` | Three critics: Logician, Empiricist, Ethicist |
| `use_judge` | Final quality evaluation |
| `use_search` | Grounds arguments with web search |
| `response_style` | `sections`, `json`, or `synthesis_only` |

---

## When to Use Hegelion

- **High-stakes reasoning** where a reflex answer isn't good enough
- **Agent orchestration** where you need auditable traces
- **Research questions** where you want novel frameworks, not literature summaries
- **Safety analysis** where explicit contradiction handling matters

---

## Documentation

- **[MCP Integration](docs/guides/mcp-integration.md)** — Setup for Claude Desktop, Cursor, VS Code, Gemini CLI
- **[Python API](docs/guides/python-api.md)** — Full API reference
- **[CLI Reference](docs/guides/cli-reference.md)** — Command-line usage
- **[Configuration](docs/getting-started/configuration.md)** — Backends and feature toggles
- **[Showcase](docs/examples/showcase.md)** — Full example traces
- **[Technical Specification](docs/HEGELION_SPEC.md)** — Output schemas, phase specs
- **[Training Guide](docs/guides/training_guide.md)** — Fine-tuning models on dialectical data
- **[Agents Protocol](docs/guides/agents.md)** — Using Hegelion as an agent loop

### Concepts

- **[Dialectical Method](docs/concepts/dialectical-method.md)** — The philosophy behind the architecture
- **[Architecture](docs/concepts/architecture.md)** — How the prompt server works

---

## Why This Architecture?

Single-shot prompts are reflexes—the model commits immediately. Hegelion gives it time to argue with itself first.

The architecture enforces a path: claim → critique → resolution. The antithesis phase doesn't just ask for "counterarguments"; it forces the model to seriously attack its own position in a separate call. When the synthesis runs, it must reconcile genuinely opposed positions.

This is a structural implementation of dialectical reasoning. The format forces the content.

---

## Contributing

Issues and PRs welcome. For significant changes, open a discussion first.

---

## Recent Changes

### v0.4.x (December 2024)

#### CLI Streaming Support

- New `--stream` flag for real-time output as each phase generates
- Visual phase headers with timing: `━━━ THESIS ━━━`, `━━━ ANTITHESIS ━━━`, `━━━ SYNTHESIS ━━━`
- Interactive mode now streams by default
- Graceful fallback when Rich library is not installed

#### MCP Progress Notifications

- MCP server now emits progress notifications during tool execution
- Compatible clients (Claude Desktop, etc.) can display phase status in real-time
- Progress messages: `━━━ THESIS prompt ready ━━━ (1.0/3.0)`

#### Infrastructure

- Comprehensive streaming test suite (`tests/test_streaming.py`)
- All 460+ tests passing

---

**License:** MIT

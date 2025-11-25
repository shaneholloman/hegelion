# Hegelion

LLMs often produce confident-sounding answers that fall apart under scrutiny—hallucinations, blind spots, weak assumptions. **Hegelion forces your AI to argue with itself before it responds.**

It wraps any model in a structured **claim → critique → refined answer** loop, surfacing contradictions the first draft missed. The result: answers you can actually trust.

**Zero dependencies on new APIs**—Hegelion is a prompt protocol. Run it as an **MCP server** (for Claude Desktop, Cursor, VS Code), a **Python agent** (for scripted workflows), or just copy the prompts into any LLM you already use.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg) [![PyPI version](https://badge.fury.io/py/hegelion.svg)](https://badge.fury.io/py/hegelion) [![Status](https://img.shields.io/badge/status-actively--maintained-brightgreen.svg)](https://github.com/Hmbown/Hegelion)

**Quick links:** [Showcase](#-showcase) · [Quickstart](#-quickstart-mcp--python) · [Docs](#-documentation) · [Examples](#-examples) · [Feature toggles](#-feature-toggles)

---

## ⚡️ Showcase

See dialectical reasoning in action:

### **[Is consciousness fundamental or emergent?](docs/showcase.md)**
> *Full trace showing how Hegelion drives thesis → antithesis → synthesis to reach a sharper answer.*

[**View the full trace →**](docs/showcase.md)

---

## 💎 Why Hegelion?

- **Antifragile reasoning**: Built-in antithesis step hunts hallucinations, weak assumptions, and bias before a final answer ships.
- **Agent-grade outputs**: Returns structured workflows (JSON) for autonomous agents, plus friendly sectioned prose for humans.
- **Pluggable everywhere**: MCP (Model Context Protocol) server for Claude/Cursor/VS Code, Python agent for code, prompt server for any LLM.
- **Research-ready (Coming Soon)**: Future roadmap includes a training pipeline to fine-tune open models for dialectical thinking.
- **Auditability**: Every run emits a trace of thesis, critiques, and synthesis so you can verify how the answer formed.

### When to use it
- Hard reasoning tasks where linear chains miss contradictions.
- Safety- and evaluation-heavy workflows that demand explicit critique.
- Agent loops that need structured, machine-readable reasoning steps.

---

## 📊 Benchmark: Does Multi-Call Matter?

The key question: **Does separating thesis → antithesis → synthesis into distinct API calls produce better reasoning than asking for all three in a single prompt?**

We compared three approaches on the same question:

| Method | API Calls | Approach |
| :--- | :---: | :--- |
| **Raw** | 1 | Simple prompt, no structure |
| **Enhanced** | 1 | Single prompt requesting thesis/antithesis/synthesis |
| **Hegelion** | 3 | Separate calls with forced redirection between phases |

### Test Case: *"Is free will compatible with determinism?"*

<details>
<summary><b>Raw (1 call)</b> — Click to expand</summary>

> The compatibility of free will and determinism depends heavily on how we define free will. Compatibilists argue that yes, they can coexist, while incompatibilists say no... Ultimately, **the debate often turns on whether we prioritize metaphysical concerns about causal chains or practical concerns about autonomy and moral responsibility.**

*Conclusion: Survey of positions, ends with "it depends on priorities."*
</details>

<details>
<summary><b>Enhanced (1 call)</b> — Click to expand</summary>

> A mature view likely requires what Wilfrid Sellars called **'stereoscopic vision'—holding both perspectives while recognizing their distinct purposes.** We are both determined and deciding, caused and choosing, and the apparent contradiction may reflect complementary levels of description rather than metaphysical inconsistency.

*Conclusion: Comprehensive analysis, ends with "hold both views" (Sellars).*
</details>

<details>
<summary><b>Hegelion (3 calls)</b> — Click to expand</summary>

> The deadlock dissolves when we recognize free will is not binary (present/absent) but exists on a **spectrum of self-authorship**:
>
> 1. **Minimal freedom**: Acting on desires without external coercion
> 2. **Reflective freedom**: Second-order endorsement—I want to want this
> 3. **Narrative freedom**: Acting consistently with a coherent life narrative
> 4. **Constitutive freedom**: Recursive self-modification through deliberate habituation
>
> **RESOLVING MANIPULATION**: The manipulated agent lacks freedom not because their desires are caused externally, but because the causation *bypasses their enduring character*. When I choose coffee because I've cultivated a taste through years of reflection, my choice is deeply mine—even though that cultivation was itself caused.
>
> **RESEARCH PROPOSAL**: Use fMRI to scan participants making decisions under (1) snap judgments, (2) brief reflection, (3) extended deliberation. Hypothesis: Condition (3) shows strongest correlation between brain patterns and self-reported decision "ownership."

*Conclusion: Novel 4-level framework that resolves the manipulation argument, with testable predictions.*
</details>

### Why the difference?

Both **Enhanced** and **Hegelion** ask for dialectical reasoning. But:

- **Enhanced** (1 call): The model knows where it's going. It can construct a balanced synthesis without genuinely confronting contradictions.
- **Hegelion** (3 calls): The model must commit to a thesis, then attack it in a separate call (no hedging), then synthesize. The forced redirection surfaces insights the single-call approach shortcuts.

The "self-authorship spectrum" didn't emerge from asking for thesis/antithesis/synthesis in one breath. It emerged from *actually arguing with itself* across separate calls.

**You decide**: Is the 3× cost worth the difference? [Full responses available in `benchmarks/data/responses/`]

---

## ⚙️ How it Works

Hegelion is **multi-call orchestration**—similar to sequential thinking or multi-turn reasoning patterns. Each phase is a separate LLM call, not a single prompt asking the model to roleplay all three roles.

### The Dialectical Loop

1. **Thesis** (Call 1): Generate the best initial argument.
2. **Antithesis** (Call 2+): Attack the thesis to expose gaps. With Council mode, this spawns 3 concurrent critic calls (Logician, Empiricist, Ethicist).
3. **Synthesis** (Final call): Reconcile the tension into a higher-order, evidence-backed answer.

### API Calls & Cost

| Mode | API Calls | Cost vs Raw |
| :--- | :--- | :--- |
| Basic | 3 sequential | ~3-4× |
| + Council | 5 (3 concurrent) | ~5-6× |
| + Judge | 4-6+ (with retries) | ~6-10× |

**This is the tradeoff:** More calls = more cost, but each phase builds on the previous one's output, catching blind spots a single pass misses.

### Architecture

```
User / Agent
   │
   ▼
Hegelion (MCP server or Python agent)
   │
   ├─► [Call 1] Thesis prompt → LLM → thesis output
   │
   ├─► [Call 2] Antithesis prompt (includes thesis) → LLM → critique
   │   (Council mode: 3 concurrent critic calls)
   │
   └─► [Call 3] Synthesis prompt (includes both) → LLM → final answer
   │
   ▼
Structured trace + final answer
```

**MCP mode note:** When using Hegelion as an MCP server with Claude Desktop or Cursor, Hegelion returns the prompts and the *host LLM* executes them. You're using your existing model's tokens—Hegelion doesn't call external APIs in this mode.

### Feature toggles

| Option | Default | Description |
| :--- | :--- | :--- |
| `use_search` | `false` | Grounds arguments with real-time web search. |
| `use_council` | `false` | Activates the **Council of Philosophers** (Logician, Empiricist, Ethicist) for deeper critique. |
| `use_judge` | `false` | Adds a final quality evaluation step. |
| `response_style` | `sections` | Choose `json` for agents, `sections` for reading, or `synthesis_only` for brevity. |

---

## 🚀 Quickstart (MCP + Python)

Hegelion ships as an **MCP server** and a **Python agent**. You can try it locally with no provider keys.

### For Claude Desktop Users (GUI App)

```bash
# Install
pip install hegelion

# If running from source (cloned repo):
pip install -e .
# Or if you get "externally-managed-environment" error:
pip install --break-system-packages -e .

# Auto-config (recommended)
hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Or manual setup - add to mcpServers section:
{
  "mcpServers": {
    "hegelion": {
      "command": "/full/path/to/python",
      "args": ["-m", "hegelion.mcp.server"]
    }
  }
}
```

> ⚠️ **Restart Required:** Quit and reopen Claude Desktop (Cmd+Q) after modifying the config.

**Find your Python path:**
```bash
which python
# Example output: /usr/local/bin/python
# Use this exact path in the config above
```

**Verify installation:** In Claude Desktop, ask: *"What Hegelion tools are available?"* — you should see `dialectical_workflow`, `thesis_prompt`, etc.

### For Claude Code Users (Terminal/CLI)

```bash
# Install
pip install hegelion

# Add the MCP server
claude mcp add hegelion python -- -m hegelion.mcp.server

# Verify it's added
claude mcp list

# Restart Claude Code
exit  # Then reopen terminal
```

**Verify installation:** In Claude Code, ask: *"Use Hegelion to analyze: [your question]"*

### Common Setup Issues

| Error | Cause | Fix |
|-------|-------|-----|
| `spawn hegelion-server ENOENT` | `hegelion-server` not in PATH | Use `python -m hegelion.mcp.server` instead |
| `ModuleNotFoundError: hegelion` | **Running from source without installation** | **Install with `pip install -e .` from repo root** |
| Server disconnects on startup | Python path issues or missing deps | Check log file at `~/Library/Logs/Claude/mcp-server-hegelion.log` |

**IMPORTANT: Running from Source?**
If you cloned Hegelion and are running from source (not from PyPI), you MUST install it first:

```bash
# From the repo root
pip install -e .

# If you get "externally-managed-environment" error:
pip install --break-system-packages -e .
```

This installs Hegelion in "editable" mode so:
- ✅ No PYTHONPATH tricks needed
- ✅ Changes to source code are reflected immediately
- ✅ Works reliably with MCP servers

**Pro tip:** Always use the full Python path if you use pyenv/conda/venv:
```bash
# Find your Python path
which python
# Example output: /Users/username/.pyenv/shims/python
# Use this exact path in your config
```

```bash
# Or use the Python agent directly
python - <<'PY'
from hegelion.core.agent import HegelionAgent

agent = HegelionAgent(goal="Ship safely", personas="council", iterations=2)
step = agent.act_sync("Tests are flaky after enabling caching")
print(step.action)
PY
```

**Prompt-only mode:** Use the prompt server (`hegelion.mcp.server`) to fetch ready-made thesis/antithesis/synthesis prompts for any LLM.

---

## 🧠 See the reasoning

```text
## THESIS
Consciousness is emergent from complex neural computation...

## ANTITHESIS
- Lacks account for phenomenology (hard problem)
- Underestimates quantum/field perspectives
- Offers no falsifiable mechanism for emergence

## SYNTHESIS
Consciousness likely emerges, but only when neural dynamics achieve integrated information thresholds; empirical tests should combine IIT-style metrics with perturbational complexity on neuromorphic systems.
```

---

## 📚 Documentation

- **[Human Quickstart](docs/QUICKSTART.md)**: Detailed guide for getting started.
- **[MCP Setup for Claude Desktop](docs/CLAUDE_DESKTOP_SETUP.md)**: GUI app integration guide.
- **[MCP Setup for Claude Code](docs/development/CLAUDE_CODE_SETUP.md)**: CLI integration guide.
- **[MCP Reference](docs/MCP.md)**: Advanced configuration for the Model Context Protocol.
- **[Training Data](hegelion-data/README.md)**: *Planned: Guidelines for building dialectical datasets.*
- **[Showcase](docs/showcase.md)**: Full consciousness example trace.

---

## 🧩 Examples

- **In-process smoke test**: `python examples/mcp/inprocess_check.py`
- **MCP config samples**: `examples/mcp/*.json`
- **More examples**: `examples/mcp/README.md`

---

## 🤝 Contributing & Status

- We welcome issues and PRs; please open a discussion for significant changes.
- Status: Actively maintained.
- License: MIT.

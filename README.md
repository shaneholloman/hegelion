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

```bash
# Install
pip install hegelion

# Claude Desktop auto-config (macOS)
hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

> ⚠️ **Restart Required:** Quit and reopen Claude Desktop after modifying the config.

**Verify installation:** In Claude Desktop, ask: *"What Hegelion tools are available?"* — you should see `dialectical_workflow`, `thesis_prompt`, etc.

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
- **[MCP Setup for Claude Code](docs/development/CLAUDE_CODE_SETUP.md)**: How to integrate Hegelion into agentic workflows.
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

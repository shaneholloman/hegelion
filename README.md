# Hegelion

> *“The truth is the whole. The whole, however, is merely the essential nature reaching its completeness through the process of its own development.”* — **G.W.F. Hegel**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg) [![PyPI version](https://badge.fury.io/py/hegelion.svg)](https://badge.fury.io/py/hegelion) [![Status](https://img.shields.io/badge/status-actively--maintained-brightgreen.svg)](https://github.com/Hmbown/Hegelion)

**Hegelion is the dialectical engine for AI.** It wraps any LLM in a rigorous **Thesis → Antithesis → Synthesis** loop so models critique themselves, surface contradictions, and produce sturdier reasoning.

**Quick links:** [Showcase](#-showcase) · [Quickstart](#-quickstart-mcp--python) · [Docs](#-documentation) · [Examples](#-examples) · [Feature toggles](#-feature-toggles)

**TL;DR:** Drop-in dialectical reasoning layer for your assistant, MCP server for tool hosts, Python agent for code, and prompt packs for any LLM. No API keys required to try.

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
- **Pluggable everywhere**: MCP server for Claude/Cursor/VS Code, Python agent for code, prompt server for any LLM.
- **Research-ready**: Training pipeline + `hegelion-data` to fine-tune open models (Llama, Qwen) for dialectical thinking.
- **Auditability**: Every run emits a trace of thesis, critiques, and synthesis so you can verify how the answer formed.

### When to use it
- Hard reasoning tasks where linear chains miss contradictions.
- Safety- and evaluation-heavy workflows that demand explicit critique.
- Agent loops that need structured, machine-readable reasoning steps.

---

## ⚙️ How it Works

1. **Thesis**: Generate the best initial argument.
2. **Antithesis**: Attack the thesis (optionally with a council of Logician / Empiricist / Ethicist) to expose gaps.
3. **Synthesis**: Reconcile the tension into a higher-order, evidence-backed answer.

### Architecture at a glance

```
User / Agent
   │
   ▼
Hegelion (MCP server or Python agent)
   │  prompts / JSON workflow
   ▼
LLM provider (your choice)
   │  thesis → antithesis → synthesis
   ▼
Structured trace + final answer
```

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

# Claude Desktop auto-config
hegelion-setup-mcp --write ~/.claude_desktop_config.json

# Run MCP server
python -m hegelion.mcp.server

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
- **[AI/Agent Quickstart](AI_README.md)**: How to integrate Hegelion into agentic workflows.
- **[MCP Reference](docs/MCP.md)**: Advanced configuration for the Model Context Protocol.
- **[Training Data](hegelion-data/README.md)**: How we built the dataset and how to train your own models.
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

# Hegelion

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/hegelion.svg)](https://badge.fury.io/py/hegelion)
[![Status](https://img.shields.io/badge/status-actively--maintained-brightgreen.svg)](https://github.com/Hmbown/Hegelion)

**Agent Protocol for Smarter AI (Thesis → Antithesis → Synthesis)**

Hegelion is an **agent-first protocol**: every action is stress-tested by an adversarial dialectic to reduce hallucinations. MCP/CLI are delivery layers—the brain lives here.

> Start here: `pip install hegelion` · `hegelion-setup-mcp` · run your first agent step.

---

## Table of Contents

- [The Agent Protocol: How It Works](#the-agent-protocol-how-it-works)
- [Quick Start: Agent First](#quick-start-agent-first)
- [Python SDK & Agent Integration](#python-sdk--agent-integration)
- [Key Features](#key-features)
- [Value Proposition](#value-proposition)
- [Documentation](#documentation)
- [Contributing & License](#contributing--license)

---

## The Agent Protocol: How It Works

Hegelion transforms the way LLMs process information by imposing a structured "Brain" over the raw model. Instead of generating a single, linear response, the Agent Protocol enforces a recursive reasoning loop:

### 1. The Dialectical Loop
The core engine drives every query through a three-step evolutionary process:
-   **Thesis:** The model generates an initial solution or argument.
-   **Antithesis:** The system challenges the thesis, actively searching for flaws, edge cases, and contradictions.
-   **Synthesis:** The model resolves the conflict, producing a refined insight that is more robust than the original thought.

### 2. Council of Critics
To ensure rigor, the protocol employs a "Council of Critics"—specialized personas (e.g., Logic, Facts, Ethics) that audit the reasoning at each step. This adversarial review process uncovers hidden assumptions and reduces hallucinations before the user ever sees the result.

---

## Quick Start: Agent First

### 1) Install (choose one)
- **pip:** `pip install hegelion`
- **uvx (no env overlap):** `uvx hegelion hegelion-setup-mcp`
- **pipx:** `pipx install hegelion`

### 2) Configure Cursor / Claude Desktop
```bash
hegelion-setup-mcp --write ~/.mcp_config.json
```
This writes both prompt and backend servers. Run without `--write` to print a snippet to paste into Cursor “Global MCP Settings” or `claude_desktop_config.json`.

### 3) First agent step (no code required)
```bash
hegelion-agent "CI fails on Python 3.12" --goal "Fix CI" --coding --iterations 2
```
See thesis/antithesis/synthesis plus a single vetted action.

---

## Python SDK & Agent Integration

Hegelion is a library first. You can integrate the dialectical agent directly into your Python applications to build self-correcting autonomous systems.

### Agent Wrapper (Reflexion-style loop)

```python
from hegelion.agent import HegelionAgent

# Initialize the agent with a goal and a Council of Critics
agent = HegelionAgent(goal="Ship the feature safely", personas="council", iterations=2)

# The agent thinks before it acts
step = agent.act_sync("Tests are flaky after enabling caching; what should we do next?")
print("Action:", step.action)
```

The agent calls the full **Thesis → Antithesis → Synthesis** loop before acting. This means every action is vetted by contradiction-hunting critics, significantly reducing the risk of hallucinations and unsafe plans.

### CLI for Coding Tasks
For quick, code-focused reasoning tasks:

```bash
python -m hegelion.scripts.hegelion_agent_cli "CI fails on Python 3.12" --goal "Fix CI" --coding --iterations 2
```

---

## Key Features

-   **Adversarial Critics (Logic):** Multi-perspective analysis (Logic, Facts, Ethics) stress-tests every assertion.
-   **Zero-Config MCP (Interface):** Connects instantly to Cursor and Claude Desktop without complex setup.
-   **Dialectical Loop (Logic):** Automated Thesis → Antithesis → Synthesis workflow for self-improving answers.
-   **Structured Output (Interface):** Returns JSON results with identified contradictions and research proposals.
-   **Search Grounding (Logic):** Prompts include instructions to use available search tools for evidence.
-   **Iterative Refinement (Logic):** Run multiple rounds where Synthesis becomes the new Thesis.

---

## Value Proposition

-   **Deeper Insights:** Move beyond simple Q&A to complex, multi-layered analysis.
-   **Uncover Assumptions:** The dialectical process surfaces hidden biases and logical gaps.
-   **Model Agnostic:** Works with your existing tools (Cursor, Claude Desktop) or as a standalone library.

---

## Documentation

-   [Quick Start (docs/QUICKSTART.md)](docs/QUICKSTART.md) — detailed setup guide
-   [User Guide (docs/USER_GUIDE.md)](docs/USER_GUIDE.md) — advanced usage and options
-   [Model-Agnostic Prompt Server (docs/MODEL_AGNOSTIC.md)](docs/MODEL_AGNOSTIC.md)
-   [MCP Reference (docs/MCP.md)](docs/MCP.md)
-   [Examples (examples/README.md)](examples/README.md)
-   [Agent Protocol (agents.md)](agents.md)
-   [Gemini Extension & Marketplaces (extensions/gemini/README.md)](extensions/gemini/README.md)
-   [Marketplace Checklist (docs/marketplaces.md)](docs/marketplaces.md)

---

## Contributing & License

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Hegelion is licensed under the [MIT License](LICENSE).

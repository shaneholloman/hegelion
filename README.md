# Hegelion

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/hegelion.svg)](https://badge.fury.io/py/hegelion)
[![Status](https://img.shields.io/badge/status-actively--maintained-brightgreen.svg)](https://github.com/Hmbown/Hegelion)

**Dialectical Reasoning Framework for Large Language Models**

Hegelion is a framework that upgrades AI reasoning by forcing language models through a structured, dialectical process. It stress-tests assertions, uncovers hidden assumptions, and produces significantly more robust and well-reasoned insights.

> Get started: [Quick Start](docs/QUICKSTART.md) · [User Guide](docs/USER_GUIDE.md) · [MCP Setup](docs/MODEL_AGNOSTIC.md) · [Examples](examples/README.md)

---

## Table of Contents

- [Value Proposition](#value-proposition)
- [Key Features](#key-features)
- [Two Ways to Use Hegelion](#two-ways-to-use-hegelion)
- [Documentation](#documentation)
- [Quick Start](#quick-start)
- [Supported Backends](#supported-backends)
- [Who is this for?](#who-is-this-for)
- [Common Use Cases](#common-use-cases)
- [FAQ](#faq)
- [New in Version 0.3.0](#new-in-version-030)
- [Contributing & License](#contributing--license)

---

At its core is a simple, powerful loop:

```
      ┌──────────────────┐
      │      Thesis      │
      │ (Initial Stance) │
      └─────────┬────────┘
                │
      ┌─────────▼────────┐
      │    Antithesis    │
      │(Critique/Counter)│
      └─────────┬────────┘
                │
      ┌─────────▼────────┐
      │     Synthesis    │
      │ (Refined Result) │
      └──────────────────┘
```

This framework moves beyond simple Q&A to facilitate complex, multi-layered analysis.

---

## See It In Action: Transforming AI Reasoning

We asked the same model (GLM-4.6) a complex philosophical question:
*"If AI achieves zero-marginal-cost production for all goods, does the concept of 'Economic Value' collapse or transform?"*

### Without Hegelion
The model provided a competent, standard analysis:
> "It collapses for a world of things but transforms into a world of meaning... moving from an economics of production to an economics of curation."
*(A logical, textbook response constrained by existing economic frameworks.)*

### With Hegelion
Forced through a dialectical loop, the system uncovered **6 contradictions** in its own initial thinking. The synthesis transcended the binary of "collapse vs. transformation" to identify a fundamental **re-ontologization** of value:

> **The Economy of Intention**
> Value shifts from **possession** to **influence**.
>
> "The ultimate scarcity is the **priority of action** of the omnipotent production system itself. The economy ceases to be about the allocation of goods and becomes the allocation of the AI's **Intention**."
>
> *— Hegelion Synthesis*

**Key Differentiators:**
*   **Paradigm Shift:** Instead of predicting a service economy, it identified a "Governance of Intention" where political and economic power fuse.
*   **Rigorous Critique:** It challenged the "Zero Cost" premise, identifying the **opportunity cost of AI attention** as the new scarce resource.
*   **Actionable Science:** Beyond theory, the system proposed a **multi-agent simulation** to empirically observe the emergence of "influence tokens" as a post-scarcity currency.

[**View the full dialectical transcript →**](examples/zero_marginal_cost_example.md)

---

## Value Proposition

- **Deeper Insights:** Move beyond simple Q&A to complex, multi-layered analysis.
- **Uncover Assumptions:** The dialectical process surfaces hidden biases and logical gaps.
- **Model Agnostic:** Works with your existing tools (Cursor, Claude Desktop) or as a standalone library.

---

## Key Features

- **Dialectical Loop:** Automated Thesis → Antithesis → Synthesis workflow.
- **Council of Critics:** Multi-perspective analysis (Logic, Facts, Ethics) or custom personas (Security, Editorial, etc.).
- **Structured Output:** JSON results with identified contradictions and research proposals.
- **Search Grounding:** Prompts include instructions to use available search tools for evidence.
- **Iterative Refinement:** Run multiple rounds where Synthesis becomes the new Thesis for deeper analysis.
- **Evaluation Harness:** Tools to benchmark and compare model reasoning capabilities.

---

## Two Ways to Use Hegelion

Hegelion supports two distinct usage patterns depending on your needs:

### 1. Model-Agnostic (Prompt-Based)
**Best for:** Users of Cursor, Claude Desktop, VS Code, or Antigravity.

- **Why:** Use your *existing* configured model (Gemini 3, Claude 4.5, GPT-5.1, etc.). Zero configuration required.
- **Tool:** `hegelion-prompt-server` (MCP)
- **Key Features:**
  - **Council of Critics:** Activates "The Logician," "The Empiricist," and "The Ethicist" for multi-perspective critiques.
  - **Zero Cost:** Uses your existing subscription/API setup.
  - **Flexible:** Works with any model that can follow instructions.

### 2. Automated (API-Based)
**Best for:** Python scripts, CI/CD pipelines, and Batch Benchmarking.

- **Why:** Automate testing across multiple models programmatically.
- **Tool:** `hegelion` Python API (or basic CLI demo)
- **Key Features:**
  - **Batch Processing:** Run benchmarks on hundreds of prompts.
  - **Structured Evaluation:** Compare model performance systematically.
  - **Backend Agnostic:** Supports Anthropic, OpenAI, Google Gemini, Ollama, etc.
  - **Advanced Features:** Full access to persona-based critiques, iterations, and search grounding via Python API.

---

## Documentation

- [Quick Start (docs/QUICKSTART.md)](docs/QUICKSTART.md) — 5-minute setup for MCP and Python API
- [User Guide (docs/USER_GUIDE.md)](docs/USER_GUIDE.md) — detailed usage and options
- [Model-Agnostic Prompt Server (docs/MODEL_AGNOSTIC.md)](docs/MODEL_AGNOSTIC.md)
- [MCP Reference (docs/MCP.md)](docs/MCP.md)
- [Examples (examples/README.md)](examples/README.md)
- [Publishing Guide (docs/PUBLISHING.md)](docs/PUBLISHING.md)

---

## Quick Start

See [docs/QUICKSTART.md](docs/QUICKSTART.md) for a 5-minute guide. The basics are below.

### Installation

```bash
pip install hegelion
```

### Option 1: Cursor / Claude Desktop Setup (MCP)

Add this to your MCP configuration file (e.g., `claude_desktop_config.json` or Cursor settings):

```json
{
  "mcpServers": {
    "hegelion-prompt": {
      "command": "uv",
      "args": ["run", "hegelion-prompt-server"]
    }
  }
}
```
*Now, just ask your AI: "Run a dialectical analysis on 'Is AI conscious?' using the prompt server with council critiques."*

### Option 2: Python API

1. Copy `env.example` to `.env` and configure your API keys (or set environment variables).

2. Run a script:

```python
import asyncio
from hegelion import run_dialectic

async def main():
    # Basic query
    result = await run_dialectic("Is AI conscious?")
    print(result.synthesis)
    
    # With Council of Critics
    result = await run_dialectic(
        "Should we regulate AI?",
        personas="council",  # Activates Logician, Empiricist, Ethicist
        use_search=True,     # Instructs model to verify facts
        iterations=2         # Runs 2 refinement loops
    )
    
    print(f"Contradictions Found: {len(result.contradictions)}")
    print(f"Research Proposals: {len(result.research_proposals)}")

asyncio.run(main())
```

### CLI Demo

A basic CLI is included for quick checks and demos:

```bash
# Run a single query with default settings
hegelion "Can AI be genuinely creative?" --format summary

# Run in demo mode (no API key needed)
hegelion --demo
```

---

## New in Version 0.3.0

- 🎭 **Persona-Based Critiques**: Configure specific critic personas for targeted analysis.
- 🔄 **Iterative Refinement**: Run multiple rounds of dialectics for deeper reasoning.
- 🔍 **Search Grounding**: Instruct models to verify facts with search tools.
- 🌳 **Branching Analysis**: Generate multiple critiques from different perspectives simultaneously.

See [CHANGELOG.md](CHANGELOG.md) for full details.

---

## Contributing & License

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Hegelion is licensed under the [MIT License](LICENSE).

---

## Supported Backends

| Provider | Env Vars (minimum) | Example Model |
| --- | --- | --- |
| Anthropic (Claude) | `HEGELION_PROVIDER=anthropic`, `ANTHROPIC_API_KEY` | `claude-4.5-sonnet-latest` |
| OpenAI / GLM-compatible | `HEGELION_PROVIDER=openai`, `OPENAI_API_KEY`, optional `OPENAI_BASE_URL` | `gpt-4o`, `GLM-4.6` |
| Google (Gemini) | `HEGELION_PROVIDER=google`, `GOOGLE_API_KEY` | `gemini-2.5-pro` |
| Ollama (local) | `HEGELION_PROVIDER=ollama`, optional `OLLAMA_BASE_URL` | `llama3.3` |
| Custom HTTP | `HEGELION_PROVIDER=custom_http`, `CUSTOM_API_BASE_URL`, optional `CUSTOM_API_KEY` | Your internal model ID |

See `env.example` for a ready-to-edit template.

---

## Who is this for?

- Researchers comparing reasoning patterns across models
- Engineers building evaluation harnesses and CI checks
- Power users of Cursor / Claude Desktop who want model-agnostic dialectics
- Educators teaching argumentation and critical thinking

---

## Common Use Cases

- Stress-test a design or policy with structured critique (antithesis)
- Generate research proposals with testable predictions (synthesis)
- Batch-benchmark prompts across providers (JSONL in/out)
- Prompt-driven dialectics in MCP without any API keys

---

## FAQ

- **Why not put everything in the CLI?**  The CLI is great for demos, but advanced workflows (personas, iterations, search grounding) belong in the Python API or MCP where composition is easier.
- **Why do results vary between runs?**  Different providers/models have different strengths; enable `debug=True` to include internal diagnostics in `metadata.debug`.
- **How do I capture runs for analysis?**  Use `--output file.jsonl` on the CLI or write `result.to_dict()` in code; process with `jq` or `pandas.read_json(..., lines=True)`.
- **Which models work best?**  Strong generalists like Claude Sonnet, GPT-4 class, or Gemini Pro produce the most useful contradictions and syntheses.

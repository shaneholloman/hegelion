# Hegelion

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/hegelion.svg)](https://badge.fury.io/py/hegelion)
[![Status](https://img.shields.io/badge/status-actively--maintained-brightgreen.svg)](https://github.com/Hmbown/Hegelion)

**Dialectical Reasoning Framework for LLMs**

Hegelion is a framework that upgrades AI reasoning by forcing language models through a **Thesis → Antithesis → Synthesis** loop. It stress-tests models, uncovers hidden assumptions, and produces structured, actionable insights.

---

## Value Proposition

- **Deeper Insights:** Move beyond simple Q&A to complex, multi-layered analysis.
- **Uncover Assumptions:** The dialectical process surfaces hidden biases and logical gaps.
- **Model Agnostic:** Works with your existing tools (Cursor, Claude Desktop) or as a standalone library.

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
- **Tool:** `hegelion` CLI / Python API
- **Key Features:**
  - **Batch Processing:** Run benchmarks on hundreds of prompts.
  - **Structured Evaluation:** Compare model performance systematically.
  - **Backend Agnostic:** Supports Anthropic, OpenAI, Google Gemini, Ollama, etc.
  - **Persona-Based Critiques:** Configure custom critic personas (Security Engineer, Ruthless Editor, etc.).
  - **Iterative Refinement:** Run multiple rounds of dialectics (Synthesis Round 1 → Thesis Round 2).
  - **Search Grounding:** Instruct models to verify claims with search tools during critique.

---

## Quick Start

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

### Option 2: Python API / CLI

```bash
# Configure your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Run a single query with default critique
hegelion "Can AI be genuinely creative?" --format summary

# Run with Council of Critics (multi-perspective)
hegelion "Should we implement UBI?" --personas council --format summary

# Run with iterative refinement (2 rounds)
hegelion "What is consciousness?" --personas council --iterations 2

# Run with search grounding (instructs model to verify facts)
hegelion "What are the latest developments in fusion energy?" --use-search --format summary
```

**Python API Example:**

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

---

## Key Features

- **Dialectical Loop:** Automated Thesis → Antithesis → Synthesis workflow.
- **Council of Critics:** Multi-perspective analysis (Logic, Facts, Ethics) or custom personas (Security, Editorial, etc.).
- **Structured Output:** JSON results with identified contradictions and research proposals.
- **Search Grounding:** Prompts include instructions to use available search tools for evidence.
- **Iterative Refinement:** Run multiple rounds where Synthesis becomes the new Thesis for deeper analysis.
- **Evaluation Harness:** Tools to benchmark and compare model reasoning capabilities.

### Available Persona Presets

- **`council`**: The Logician, The Empiricist, The Ethicist (default multi-perspective)
- **`security`**: Security Engineer (focuses on vulnerabilities and exploits)
- **`editorial`**: Ruthless Editor (cuts fluff, demands clarity)
- **`debate`**: Devil's Advocate (takes opposite view, steel-mans opposition)
- **`comprehensive`**: All of the above

---

## Documentation

- **[Full Specification (HEGELION_SPEC.md)](HEGELION_SPEC.md)**: Detailed architecture and schema.
- **[Prompt Server Guide (docs/MODEL_AGNOSTIC.md)](docs/MODEL_AGNOSTIC.md)**: How to use the model-agnostic MCP server.
- **[MCP Reference (docs/MCP.md)](docs/MCP.md)**: Technical details for MCP integration.

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

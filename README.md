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

- **Why:** Use your *existing* configured model (Gemini 3, Claude 3.5, GPT-5, etc.). Zero configuration required.
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
*Now, just ask your AI: "Run a dialectical analysis on 'Is AI conscious?' using the prompt server."*

### Option 2: Python API / CLI

```bash
# Configure your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Run a single query
hegelion "Can AI be genuinely creative?" --format summary
```

---

## Key Features

- **Dialectical Loop:** Automated Thesis → Antithesis → Synthesis workflow.
- **Council of Critics:** Multi-perspective analysis (Logic, Facts, Ethics).
- **Structured Output:** JSON results with identified contradictions and research proposals.
- **Search Grounding:** Prompts include instructions to use available search tools for evidence.
- **Evaluation Harness:** Tools to benchmark and compare model reasoning capabilities.

---

## Documentation

- **[Full Specification (HEGELION_SPEC.md)](HEGELION_SPEC.md)**: Detailed architecture and schema.
- **[Prompt Server Guide (docs/MODEL_AGNOSTIC.md)](docs/MODEL_AGNOSTIC.md)**: How to use the model-agnostic MCP server.
- **[MCP Reference (docs/MCP.md)](docs/MCP.md)**: Technical details for MCP integration.

---

## Contributing & License

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Hegelion is licensed under the [MIT License](LICENSE).

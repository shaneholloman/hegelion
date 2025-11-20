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

## Quick Start (Recommended for Cursor / Claude)

Hegelion works best as a **Model Context Protocol (MCP)** server. This lets you use it directly inside Cursor or Claude Desktop with your existing AI model (Claude 3.5, GPT-4o, etc.).

### 1. Install & Setup
From your project root:

```bash
# 1. Install the package
pip install hegelion

# 2. Run the setup script
python scripts/setup_mcp.py
```

### 2. Configure Your Editor
The script will generate a `mcp_config.json` file.
*   **If tools don't appear immediately:** The script will also print a JSON snippet. **Copy and paste** that snippet into your **Global MCP Settings** (Cursor) or `claude_desktop_config.json`.

### 3. Use It
Ask your AI:
> *"Run a dialectical analysis on 'Will AI replace programmers?' using the prompt server."*

---

## Two Ways to Use Hegelion

Hegelion supports two distinct usage patterns depending on your needs:

### 1. Prompt-Driven (Model Agnostic) - **Default**
**Best for:** Interactive use in Cursor, Claude Desktop, VS Code.

- **Why:** Zero configuration. No API keys needed.
- **How it works:** The server generates structured reasoning **prompts** that your current AI session executes.
- **Tool Name:** `hegelion` (via `hegelion-prompt-server`)

### 2. Backend-Driven (Automated)
**Best for:** Python scripts, CI/CD pipelines, and Batch Benchmarking.

- **Why:** Automate testing across multiple models in the background.
- **How it works:** The server makes API calls to OpenAI/Anthropic/Google using keys in your `.env` file.
- **Tool Name:** `hegelion-backend` (via `hegelion-server`)

---

## Value Proposition

- **Deeper Insights:** Move beyond simple Q&A to complex, multi-layered analysis.
- **Uncover Assumptions:** The dialectical process surfaces hidden biases and logical gaps.
- **Model Agnostic:** Works with your existing tools (Cursor, Claude Desktop) or as a standalone library.

---

## Key Features

- **Dialectical Loop:** Automated Thesis → Antithesis → Synthesis workflow.
- **Council of Critics:** Multi-perspective analysis (Logic, Facts, Ethics) or custom personas.
- **Structured Output:** JSON results with identified contradictions and research proposals.
- **Search Grounding:** Prompts include instructions to use available search tools for evidence.
- **Iterative Refinement:** Run multiple rounds where Synthesis becomes the new Thesis.

---

## Documentation

- [Quick Start (docs/QUICKSTART.md)](docs/QUICKSTART.md) — detailed setup guide
- [User Guide (docs/USER_GUIDE.md)](docs/USER_GUIDE.md) — advanced usage and options
- [Model-Agnostic Prompt Server (docs/MODEL_AGNOSTIC.md)](docs/MODEL_AGNOSTIC.md)
- [MCP Reference (docs/MCP.md)](docs/MCP.md)
- [Examples (examples/README.md)](examples/README.md)

---

## Contributing & License

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Hegelion is licensed under the [MIT License](LICENSE).

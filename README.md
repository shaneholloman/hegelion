```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          H   H  EEEEE  GGG   EEEEE  L      III   OOO   N   N ║
║          H   H  E      G     E      L       I   O   O  NN  N ║
║          HHHHH  EEE    G  GG EEE    L       I   O   O  N N N ║
║          H   H  E      G   G E      L       I   O   O  N  NN ║
║          H   H  EEEEE  GGG   EEEEE  LLLLL  III   OOO   N   N ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

# Hegelion

> **Structured reasoning that surfaces contradictions and generates novel insights through thesis-antithesis-synthesis.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-actively--maintained-brightgreen.svg)](https://github.com/Hmbown/Hegelion)

---

## Table of Contents

- [Overview](#overview)
- [Why Hegelion?](#why-hegelion)
- [Use Cases](#use-cases)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Python API](#python-api)
  - [Claude Desktop Integration](#claude-desktop-integration)
- [Examples](#examples)
- [Hero Example](#hero-example)
- [For Model Builders & Evaluation Teams](#for-model-builders--evaluation-teams)
- [Limitations](#limitations)
- [Development](#development)
- [License & Status](#license--status)

### Quick Links

- 🚀 [Quick Start](#quick-start) - Get running quickly
- 📦 [Installation](#installation) - PyPI or from source
- ⚙️ [Configuration](#configuration) - Set up your backend
- 💻 [Python API](#python-api) - Use in your code
- 🔌 [MCP Integration](#claude-desktop-integration) - Connect to Claude Desktop
- 📚 [Examples](#examples) - See it in action
- 🧪 [Development](#development) - Contribute to the project

---

## Overview

Hegelion runs any LLM through **Thesis → Antithesis → Synthesis** and ships the full result as structured JSON (`HegelionResult`). You always get the three passages plus contradictions, research proposals, and metadata (timings, backend info, optional debug trace). The default backend is Anthropic Claude Sonnet, but the same loop works with OpenAI, Ollama, or a custom HTTP endpoint.

### Key Features

- **Always synthesizes** – every query completes the full loop
- **Structured output** – contradictions and proposals arrive as lists, ready for scoring
- **Honest provenance** – backend/model/timings live in `metadata`, internal scores only appear under `metadata.debug` when requested
- **Tooling included** – CLI (`hegelion`, `hegelion-bench`) and MCP server (`hegelion-server`) come with the package

---

## Why Hegelion?

Most LLM tools give you a single answer. Hegelion forces models to:
- **Argue with themselves** - The antithesis phase finds contradictions in the initial thesis.
- **Transcend the conflict** - Synthesis generates insights neither position alone would produce.
- **Propose research** - Each synthesis includes testable predictions.

This isn't just prompt chaining—it's structured reasoning that surfaces what single-pass responses miss.

```
   Query → Thesis → Antithesis → Synthesis
            ↓         ↓            ↓
         Position  Contradictions  Novel Insight
```

---

## Use Cases

Hegelion is a versatile tool for structured reasoning. Use it for:

- **Research & Analysis:** Uncover hidden assumptions, analyze arguments, and identify gaps in reasoning.
- **Decision-Making:** Systematically explore trade-offs and build a stronger case for a chosen path.
- **Education:** Teach critical thinking by making the structure of argumentation explicit.
- **Content Creation:** Generate balanced, multi-faceted content that explores a topic from multiple angles.
- **Creative Ideation:** Break through creative blocks by forcing a confrontation between an idea and its opposite.

---

## Quick Start

```bash
# Install from PyPI
pip install hegelion

# Set your API key
export ANTHROPIC_API_KEY=your-key-here

# Run your first dialectic
hegelion "Can AI be genuinely creative?" --format summary
```

> See contradictions, research proposals, and synthesis in one structured response.
>
> **Next Steps:** See [Installation](#installation) for source builds, [Configuration](#configuration) for backend setup, or [Usage](#usage) for Python API examples.

---

## Installation

### Requirements

- Python 3.10+ (regularly tested on 3.10 and 3.11)
- `uv` recommended for dependency management (fallback: standard `pip`)

### Installation Options

**From PyPI (recommended):**

```bash
pip install hegelion
```

**From source:**

1. Clone the repository
   ```bash
   git clone https://github.com/Hmbown/Hegelion.git
   cd Hegelion
   ```

2. Install dependencies (prefer `uv`)
   ```bash
   uv sync              # creates .venv and installs runtime deps
   ```

   Alternative with pip:
   ```bash
   pip install -e .
   ```

---

## Configuration

1. **Copy the environment template**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your preferred backend**

   **Anthropic Claude (default):**
   ```bash
   HEGELION_PROVIDER=anthropic
   HEGELION_MODEL=claude-4.5-sonnet-latest
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   ```

   **OpenAI:**
   ```bash
   HEGELION_PROVIDER=openai
   HEGELION_MODEL=gpt-4o
   OPENAI_API_KEY=your-openai-api-key-here
   ```

   **Google Gemini:**
   ```bash
   HEGELION_PROVIDER=google
   HEGELION_MODEL=gemini-2.5-pro
   GOOGLE_API_KEY=your-google-api-key-here
   # GOOGLE_API_BASE_URL=https://generativelanguage.googleapis.com
   ```

   **Ollama (local):**
   ```bash
   HEGELION_PROVIDER=ollama
   HEGELION_MODEL=llama3.1
   OLLAMA_BASE_URL=http://localhost:11434
   ```

   **Custom HTTP backend:**
   ```bash
   HEGELION_PROVIDER=custom_http
   HEGELION_MODEL=your-model-id
   CUSTOM_API_BASE_URL=https://your-endpoint.example.com/v1/run
   CUSTOM_API_KEY=your-custom-api-key
   ```

### Verified Backends & Log Sharing

We regularly exercise Hegelion with two backends:

- **Anthropic Claude (default)** – daily dev target; no extra setup beyond `ANTHROPIC_API_KEY`
- **GLM 4.6 (OpenAI-compatible)** – configure `HEGELION_PROVIDER=openai`, `HEGELION_MODEL=GLM-4.6`, `OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4`, and an API key from the [Z.AI devpack](https://docs.z.ai/devpack/tool/others). Canonical traces ship in `examples/glm4_6_examples.jsonl`

To capture your own verification run, keep the output on disk (ignored by git) and reference it when filing an issue or PR:

```bash
mkdir -p logs
HEGELION_PROVIDER=openai \
HEGELION_MODEL=GLM-4.6 \
OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4 \
OPENAI_API_KEY=sk-... \
uv run hegelion "Can AI be genuinely creative?" --format json > logs/glm_run.json
```

Before sharing logs publicly, redact sensitive fields while preserving metadata so we can confirm backend/model/timings:

```bash
jq 'del(.query, .thesis, .antithesis, .synthesis, .contradictions, .research_proposals)' \
  logs/glm_run.json > logs/glm_run.metadata.json
```

We would love reports for other Anthropic or OpenAI-compatible endpoints (e.g., Azure OpenAI, custom base URLs). Open a GitHub issue with sanitized metadata plus which model/base URL you exercised.

---

## Usage

### Command Line Interface

```bash
# Single query with readable summary
hegelion "Can AI be genuinely creative?" --format summary

# Raw JSON result (handy for scripting)
hegelion "Explain what photosynthesis does for a plant." --debug --format json

# JSONL benchmark (one prompt per line)
hegelion-bench benchmarks/examples_basic.jsonl --output runs.jsonl --summary
```

### Python API

```python
import asyncio
from hegelion import run_dialectic, run_benchmark

async def main():
    result = await run_dialectic("Is privacy more important than security?", debug=True)
    print(result.synthesis)
    print(f"Contradictions: {len(result.contradictions)}")
    print(f"Research proposals: {len(result.research_proposals)}")

asyncio.run(main())
```

### Claude Desktop Integration

Add Hegelion as an MCP server in Claude Desktop by configuring your `claude_desktop_config.json` file. A ready-to-copy example lives in `examples/mcp/claude_desktop_config.json`, and the full MCP reference (alternate clients, troubleshooting, and tool schemas) is documented in `docs/MCP.md`.

```json
{
  "mcpServers": {
    "hegelion": {
      "command": "hegelion-server",
      "args": [],
      "cwd": "/path/to/Hegelion",
      "env": {
        "HEGELION_PROVIDER": "anthropic",
        "HEGELION_MODEL": "claude-4.5-sonnet-latest",
        "ANTHROPIC_API_KEY": "your-anthropic-api-key-here"
      }
    }
  }
}
```

> **Note:** If `hegelion-server` isn't on PATH, use `python -m hegelion.mcp_server` as the command instead.

> **Coming soon:** a visual walkthrough of the Claude Desktop integration. Until then, the `docs/MCP.md` guide contains step-by-step screenshots callouts.

#### MCP Tools

Hegelion MCP server exposes the following tools:

##### `run_dialectic`

Process a query using Hegelian dialectical reasoning (thesis → antithesis → synthesis). Always performs synthesis to generate comprehensive reasoning. Returns structured contradictions and research proposals.

**Input Schema:**

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "The question or topic to analyze dialectically"
    },
    "debug": {
      "type": "boolean",
      "description": "Include debug information and internal conflict scores",
      "default": false
    }
  },
  "required": ["query"]
}
```

##### `run_benchmark`

Run Hegelion on multiple prompts from a JSONL file. Each line should contain a JSON object with a 'prompt' or 'query' field. Returns newline-delimited JSON, one HegelionResult per line.

**Input Schema:**

```json
{
  "type": "object",
  "properties": {
    "prompts_file": {
      "type": "string",
      "description": "Path to JSONL file containing prompts (one per line)"
    },
    "debug": {
      "type": "boolean",
      "description": "Include debug information and internal conflict scores",
      "default": false
    }
  },
  "required": ["prompts_file"]
}
```

---

## Examples

**Example Files:**

- `examples/glm4_6_examples.jsonl` — canonical glm-4.6 traces for:
  - Philosophical: "Can AI be genuinely creative?"
  - Factual: "What is the capital of France?"
  - Scientific: "Explain what photosynthesis does for a plant."
  - Historical: "When was the first moon landing?"
- `examples/README.md` — index + CLI instructions for replaying each example
- `examples/*.md` — narrative walk-throughs for creative reasoning prompts
- `examples/demo_glm_api.py` — Python API demo script (see [examples/README_DEMO.md](examples/README_DEMO.md))
- `benchmarks/examples_basic.jsonl` — starter JSONL for benchmarking harness behavior

**Generate Your Own Dataset:**

Add `--output my_runs.jsonl` to the CLI or call `run_benchmark(..., output_file="file.jsonl")` from Python. See [For Model Builders & Evaluation Teams](#for-model-builders--evaluation-teams) for benchmarking workflows.

**Quick Start with Another AI:**

If you'd like to have another AI assistant set up Hegelion for you, use this prompt:

```text
Please clone https://github.com/Hmbown/Hegelion, run `uv sync`, copy `.env.example`, set Anthropic keys, and start `hegelion-server`. Confirm `hegelion --help` works.
```

---

## Hero Example

Example output for "Can AI be genuinely creative?" using glm-4.6 backend.
*Full example available in `examples/glm4_6_examples.jsonl`*

```json
{
  "query": "Can AI be genuinely creative?",
  "mode": "synthesis",
  "thesis": "THESIS: The Creative Machine ...",
  "antithesis": "ANTITHESIS: The Sophisticated Mirror ...",
  "synthesis": "SYNTHESIS: The Co-Creative Process and the Emergence of Synthetic Subjectivity ...",
  "contradictions": [
    {
      "description": "The Redefinition Fallacy",
      "evidence": "The thesis narrows 'creativity' to a computable procedure, ignoring intent and subjective urgency."
    },
    {
      "description": "The Stochastic Parrot Illusion",
      "evidence": "Interpolation cannot generate the domain-breaking novelty the thesis cites as proof."
    },
    {
      "description": "Dismissing Intent as a Category Error",
      "evidence": "Removing the creator's context impoverishes art; model objective functions are not creative will."
    }
  ],
  "research_proposals": [
    {
      "description": "The Co-Creative Trace Analysis",
      "testable_prediction": "Iterative human–AI dialogues produce artifacts judged more creative than single-pass outputs."
    }
  ],
  "metadata": {
    "backend_provider": "AnthropicLLMBackend",
    "backend_model": "glm-4.6",
    "total_time_ms": 37564.40,
    "debug": {
      "internal_conflict_score": 0.95
    }
  }
}
```

---

## For Model Builders & Evaluation Teams

1. Switch providers by editing `.env` (`HEGELION_PROVIDER` + `HEGELION_MODEL`)
2. Run benchmarks via `hegelion-bench prompts.jsonl --output results.jsonl`, then rerun with other providers for apples-to-apples comparison
3. Parse the JSONL output—each line already includes thesis/antithesis/synthesis, contradictions, proposals, metadata, and (optionally) debug metrics

---

## Limitations

- **Cost & Latency:** Each query involves three separate LLM calls (Thesis, Antithesis, Synthesis), which can be slower and more expensive than a single-pass query.
- **Model Dependency:** The quality of the output (especially the synthesis) is highly dependent on the capabilities of the backend LLM.
- **Complexity Variance:** The effectiveness of the dialectical process can vary based on the complexity and nature of the query.

---

## Development

```bash
# Install dev extras
uv sync --dev

# Lint / tests
uv run pytest -v

# Optional: run CLI smoke tests
uv run hegelion --help
uv run hegelion-bench --help

# (Optional) install pre-commit hooks
uv run pre-commit install
```

---

## License & Status

- **License:** MIT (see `LICENSE`)
- **Status:** Actively maintained research infrastructure. The dialectical protocol and JSON schema are stable; internal engine/backends may evolve.

---

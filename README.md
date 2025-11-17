# Hegelion: Dialectical AI Reasoning for Deeper Insights

Hegelion runs large language models through a three-phase loop — **Thesis → Antithesis → Synthesis** — and returns the full reasoning trace in structured JSON.

- **Self-critique:** Go beyond single-answer responses by making models explore opposing viewpoints.
- **Structured output:** Get `HegelionResult` (JSON) with clear contradictions and testable research proposals.
- **Multiple entrypoints:** Use a **CLI**, **Python API**, or **MCP server** for Claude Desktop.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-actively--maintained-brightgreen.svg)](https://github.com/Hmbown/Hegelion)

---

## Table of Contents

- [Overview](#overview)
- [Why Hegelion?](#why-hegelion)
- [Use Cases](#use-cases)
- [Quick Start](#quick-start)
- [What You Get](#what-you-get)
- [Your Traces, Your Data](#your-traces-your-data)
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

- 🚀 [Quick Start](#quick-start) - Installation and basic usage
- 📦 [Installation](#installation) - PyPI or from source
- ⚙️ [Configuration](#configuration) - Set up your backend
- 💻 [Python API](#python-api) - Use in your code
- 🔌 [MCP Integration](#claude-desktop-integration) - Connect to Claude Desktop
- 📚 [Examples](#examples) - Example outputs and usage
- 🧪 [Development](#development) - Contribute to the project

---

## Overview

Hegelion runs any LLM through **Thesis → Antithesis → Synthesis** and returns structured JSON (`HegelionResult`). Each result includes the three passages plus contradictions, research proposals, and metadata (timings, backend info, optional debug trace). The default backend is Anthropic Claude Sonnet, but the same loop works with OpenAI, Ollama, or a custom HTTP endpoint.

### Key Features

- **Synthesizes** – each query completes the full loop
- **Structured output** – contradictions and proposals are returned as lists
- **Metadata tracking** – backend/model/timings live in `metadata`, internal scores only appear under `metadata.debug` when requested
- **Tooling included** – CLI (`hegelion`, `hegelion-bench`) and MCP server (`hegelion-server`) come with the package
- **Production-ready** – Robust parsing handles real LLM output variations; graceful degradation returns partial results on backend failures; structured JSON logging for observability (`HEGELION_LOG_LEVEL`)

---

## Why Hegelion?

Many LLM tools provide a single pass answer. Hegelion instead runs a structured, three-phase dialectical process:

1. **Thesis:** The LLM establishes an initial position or argument on the given query.
2. **Antithesis:** The LLM then critically examines its own thesis, identifying contradictions, weaknesses, and alternative perspectives.
3. **Synthesis:** Finally, the LLM reconciles the tension between the thesis and antithesis, generating a more nuanced understanding and testable research proposals.

This process surfaces assumptions, tensions, and research directions that single-pass responses often miss.

```text
Query    → Thesis      → Antithesis      → Synthesis
       ↓              ↓                 ↓
     Position     Contradictions      Synthesis
```

---

## Use Cases

- **Research & Analysis:** Identify assumptions, analyze arguments, and identify gaps in reasoning.
- **Decision-Making:** Explore trade-offs and evaluate different positions.
- **Education:** Demonstrate argumentation structure and critical thinking.
- **Content Creation:** Generate content that explores topics from multiple perspectives.
- **Creative Ideation:** Explore ideas by examining their contradictions and opposites.

---

## Quick Start: Get Started in Minutes!

Ready to dive into dialectical reasoning? Follow these simple steps to get Hegelion up and running:

```bash
# Install
pip install hegelion

# Demo mode (no API key needed)
hegelion --demo

# With your API key
export ANTHROPIC_API_KEY="sk-ant-..."
hegelion "Your question" --format summary

# Batch processing
hegelion-bench benchmarks/examples_basic.jsonl --output results.jsonl
```

> See contradictions, research proposals, and synthesis in one structured response.
>
> **Next Steps:** Keep reading for structure and traces, or jump to [Installation](#installation) for backend configuration.


## What You Get: Actionable, Structured Insights

Every Hegelion run delivers a rich, structured `HegelionResult` object, providing far more than just a text response. This JSON output is designed for immediate utility in various applications, from automated analysis to advanced research.

You can think about the output in two layers:

1. **Friendly mental model (short form)** – the pieces you’ll usually read as a human.
2. **Canonical schema (spec-grade)** – the exact fields and types that tools and evaluators should rely on.

### Friendly: What it feels like

At a glance, each run gives you:

```json
{
  "thesis": "Initial position...",
  "antithesis": "Critique with contradictions...",
  "synthesis": "Higher-level synthesis...",
  "contradictions": [
    {"description": "...", "evidence": "..."}
  ],
  "research_proposals": [
    {"description": "...", "testable_prediction": "..."}
  ]
}
```

This is the core **three-phase reasoning loop** plus structured contradictions and research proposals.

### Canonical schema: What tools should depend on

Under the hood, every result follows the `HegelionResult` schema (see `HEGELION_SPEC.md` for the full spec). The canonical shape looks like this:

```json
{
  "query": "Can AI be genuinely creative?",
  "mode": "synthesis",
  "thesis": "THESIS: The Creative Machine ...",
  "antithesis": "ANTITHESIS: The Sophisticated Mirror ...",
  "synthesis": "SYNTHESIS: The Co-Creative Process ...",
  "contradictions": [
    {
      "description": "The Redefinition Fallacy",
      "evidence": "The thesis narrows 'creativity' to a computable procedure, ignoring intent and subjective urgency."
    }
  ],
  "research_proposals": [
    {
      "description": "The Co-Creative Trace Analysis",
      "testable_prediction": "Iterative human–AI dialogues produce artifacts judged more creative than single-pass outputs."
    }
  ],
  "metadata": {
    "thesis_time_ms": 1234.5,
    "antithesis_time_ms": 2345.6,
    "synthesis_time_ms": 3456.7,
    "total_time_ms": 7036.8,
    "backend_provider": "AnthropicLLMBackend",
    "backend_model": "glm-4.6",
    "debug": {
      "internal_conflict_score": 0.95
    }
  },
  "trace": {
    "thesis": "... full phase output ...",
    "antithesis": "... full phase output ...",
    "synthesis": "... full phase output ...",
    "contradictions_found": 3,
    "research_proposals": ["..."],
    "internal_conflict_score": 0.95
  }
}
```

Notes:

- `metadata.backend_provider` and `metadata.backend_model` are the **canonical** backend fields.
- Timing fields are broken out (`*_time_ms`) instead of a single nested `timing` object.
- `trace` is included when `debug=true` (for CLI/API) or when requested via MCP; it exposes internal phase outputs and metrics.
- `research_proposals` is a list that may be empty when synthesis has nothing actionable to propose; consumers should not assume at least one entry.
- `metadata.debug.internal_conflict_score` is an experimental indicator surfaced only when `debug=true`; treat it as best-effort research telemetry, not ground truth.

This structured data is ideal for:
- **Eval Pipelines:** Directly feed into automated evaluation systems for LLM performance and reasoning quality.
- **Safety Analysis:** Identify potential biases or flawed reasoning patterns within LLM outputs.
- **Research Questions:** Generate novel hypotheses and testable predictions for scientific inquiry.
- **Advanced RAG:** Enhance Retrieval Augmented Generation by providing deeper contextual understanding.
```
---

## Your Traces, Your Data

```bash
# Output is plain JSONL
hegelion "question" --output trace.jsonl

# Analyze with standard tools
jq '.contradictions | length' trace.jsonl
python -c "import pandas as pd; print(pd.read_json('trace.jsonl', lines=True).head())"
```

No proprietary formats. No vendor lock-in.

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
   HEGELION_MODEL=claude-4.5-sonnet-latest  # Latest Claude model
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   ```

   **OpenAI:**
   ```bash
   HEGELION_PROVIDER=openai
   HEGELION_MODEL=gpt-5.1  # Latest GPT model
   OPENAI_API_KEY=your-openai-api-key-here
   ```

   **Google Gemini:**
   ```bash
   HEGELION_PROVIDER=google
   HEGELION_MODEL=gemini-2.5-pro  # Highest reasoning capability
   GOOGLE_API_KEY=your-google-api-key-here
   # GOOGLE_API_BASE_URL=https://generativelanguage.googleapis.com
   ```

   **Ollama (local):**
   ```bash
   HEGELION_PROVIDER=ollama
   HEGELION_MODEL=llama3.3  # Choose your model - 8B, 70B, or 405B
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

Reports for other Anthropic or OpenAI-compatible endpoints (e.g., Azure OpenAI, custom base URLs) are welcome. Open a GitHub issue with sanitized metadata plus which model/base URL you tested.

---

## Usage

### Command Line Interface

```bash
# Single query with readable summary
hegelion "Can AI be genuinely creative?" --format summary

# Raw JSON result (for scripting)
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

#### High-level Python API

Hegelion also exposes two convenience entrypoints on top of the lower-level `run_dialectic` / `run_benchmark` functions:

- `quickstart(query, model=None, debug=False)` – one-call helper for the common case.  
  - If `model` is provided, Hegelion auto-detects the right backend from the model string.  
  - Otherwise it uses your environment configuration (`HEGELION_PROVIDER`, `HEGELION_MODEL`, API keys).
- `dialectic(query, *, model=None, backend=None, max_tokens_per_phase=None, debug=False)` – universal, explicit entrypoint.  
  - If `backend` is passed, it is used as-is.  
  - Else if `model` is passed, Hegelion resolves the backend from the model name.  
  - Else it falls back to the env-configured backend.

Basic usage:

```python
import asyncio
from hegelion import quickstart, dialectic

async def main():
    # Use whatever backend/model your environment is configured for
    base = await quickstart("Is privacy more important than security?")
    print(base.synthesis)

    # Pin a specific model; backend is auto-detected from the model name
    anth = await dialectic("Can AI be genuinely creative?", model="claude-4.5-sonnet")
    gpt = await dialectic("Can AI be genuinely creative?", model="gpt-5.1")
    local = await dialectic("Can AI be genuinely creative?", model="local-llama3.3")

asyncio.run(main())
```

Synchronous wrappers are also available if you prefer not to use `asyncio`:

```python
from hegelion import quickstart_sync, dialectic_sync

result = quickstart_sync("Your question here")
alt = dialectic_sync("Your question here", model="gpt-5.1")
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

> **Note:** The `docs/MCP.md` guide contains step-by-step instructions and screenshots for the Claude Desktop integration.

#### Assistant Integration: How tools should call Hegelion

When you wire Hegelion into an AI assistant (Claude Desktop MCP or any MCP-capable client), the contract is:

- **Tool name:** `run_dialectic`
- **Inputs:**

  ```json
  {
    "query": "Can AI be genuinely creative?",
    "debug": true
  }
  ```

- **Output:** one JSON object exactly following the `HegelionResult` schema above. Assistants should:

  - Read `thesis`, `antithesis`, `synthesis` for the three textual components.
  - Treat `contradictions[]` and `research_proposals[]` as the main **actionable lists**.
  - Use `metadata.backend_provider`, `metadata.backend_model`, and `*_time_ms` for routing and evaluation.
  - Look under `metadata.debug` and `trace` **only when present** (typically when `debug=true`).

For batch workflows:

- **Tool name:** `run_benchmark`
- **Inputs:**

  ```json
  {
    "prompts_file": "benchmarks/examples_basic.jsonl",
    "debug": false
  }
  ```

- **Output:** a single text block containing **newline-delimited JSON**, one `HegelionResult` per line. Assistants should split on newlines and parse each line as independent JSON.

See `docs/MCP.md` for full tool schemas and an end-to-end Claude Desktop walkthrough.

#### MCP Tools

Hegelion MCP server exposes the following tools:

##### `run_dialectic`

Process a query using Hegelian dialectical reasoning (thesis → antithesis → synthesis). Performs synthesis to generate reasoning. Returns structured contradictions and research proposals.

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

**Setup with AI Assistant:**

To have an AI assistant set up Hegelion, use this prompt:

```text
Please clone https://github.com/Hmbown/Hegelion, run `uv sync`, copy `.env.example`, set Anthropic keys, and start `hegelion-server`. Confirm `hegelion --help` works.
```

---

## Hero Example: Witness Dialectical Reasoning in Action

Explore Hegelion's core capability with this compelling example, showcasing how it transforms a single query into a rich, multi-faceted analysis:

**Input:**
```bash
hegelion "Can AI be genuinely creative?" --format summary
```

**Output (excerpt):

**Thesis:** *The Creative Machine* - AI can be genuinely creative, mirroring human creativity as a computational process of synthesis and pattern recognition.

**Antithesis:** *The Sophisticated Mirror* - AI lacks genuine intent; it's stochastic interpolation that cannot break domains or embody creative will.

**Synthesis:** *The Co-Creative Process* - Creativity emerges from human-AI collaboration where each contributes complementary strengths.

**Contradictions:**
- *The Redefinition Fallacy*: Narrowing "creativity" to computation ignores subjective urgency
- *The Stochastic Parrot Illusion*: Interpolation cannot generate domain-breaking novelty

**Research Proposal:**
- *Co-Creative Trace Analysis*: Human-AI dialogues produce artifacts judged more creative than single-pass outputs

*Full example in `examples/glm4_6_examples.jsonl` - one command → three positions + contradictions + testable prediction.*
```
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

### Eval harness: JSONL → quick metrics

You can treat Hegelion output as plain JSONL and build a tiny eval harness around it.

**1. Generate traces with the CLI**

```bash
# From a prompts file (one JSON or plain line per prompt)
hegelion-bench prompts.jsonl --output results.jsonl --summary

# Or accumulate single-query runs into one file
hegelion "Can AI be genuinely creative?" --format json --output trace.jsonl
hegelion "What is the capital of France?" --format json --output trace.jsonl  # append mode via shell redirect
```

**2. Minimal Python eval script (e.g. `examples/eval_harness.py`)**

```python
import json
import sys
from collections import Counter
from pathlib import Path

def load_results(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)

def main(path_str: str):
    path = Path(path_str)
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    total = 0
    total_contradictions = 0
    conflict_scores = []
    by_model = Counter()

    for obj in load_results(path):
        total += 1
        total_contradictions += len(obj.get("contradictions", []))

        meta = obj.get("metadata", {}) or {}
        model = meta.get("backend_model") or "unknown"
        by_model[model] += 1

        debug = meta.get("debug") or {}
        if isinstance(debug, dict) and "internal_conflict_score" in debug:
            conflict_scores.append(float(debug["internal_conflict_score"]))

    print(f"Total queries: {total}")
    print(f"Total contradictions: {total_contradictions}")
    if total:
        print(f"Avg contradictions per query: {total_contradictions / total:.2f}")

    if conflict_scores:
        avg_conflict = sum(conflict_scores) / len(conflict_scores)
        print(f"Avg internal_conflict_score: {avg_conflict:.3f}")

    print("\nQueries per model:")
    for model, count in by_model.most_common():
        print(f"  {model}: {count}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python eval_harness.py results.jsonl", file=sys.stderr)
        raise SystemExit(1)
    main(sys.argv[1])
```

Run it like:

```bash
python examples/eval_harness.py results.jsonl
```

This gives you a simple, JSONL-native eval pipeline you can extend (e.g., stratify by prompt type, compute per-prompt contradiction rates, compare providers, etc.).

---

## Limitations

- **Cost & Latency:** Each query involves three separate LLM calls (Thesis, Antithesis, Synthesis), which can be slower and more expensive than a single-pass query.
- **Model Dependency:** The quality of the output (especially the synthesis) is highly dependent on the capabilities of the backend LLM.
- **Complexity Variance:** The effectiveness of the dialectical process can vary based on the complexity and nature of the query.

---

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and contribution guidelines.

---

## License & Status

- **License:** MIT (see `LICENSE`)
- **Status:** Actively maintained research infrastructure. The dialectical protocol and JSON schema are stable; internal engine/backends may evolve.

---

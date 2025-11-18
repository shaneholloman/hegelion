# Hegelion: Dialectical AI Reasoning for Deeper Insights

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/hegelion.svg)](https://badge.fury.io/py/hegelion)
[![Status](https://img.shields.io/badge/status-actively--maintained-brightgreen.svg)](https://github.com/Hmbown/Hegelion)

Hegelion is a framework for evaluating and improving AI reasoning by running language models through a **Thesis → Antithesis → Synthesis** loop. It stress-tests models, uncovers hidden assumptions, and produces structured, actionable insights for AI developers and research teams.

---

## Table of Contents

- [Value Proposition for AI Companies](#value-proposition-for-ai-companies)
- [How It Works](#how-it-works)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Example Output](#example-output)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Python API](#python-api)
  - [Claude Desktop Integration](#claude-desktop-integration)
- [For Evaluation Teams](#for-evaluation-teams)
- [Supported Backends](#supported-backends)
- [Installation](#installation)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

---

## Value Proposition for AI Companies

Hegelion is designed to be a powerful tool for internal testing, evaluation, and red-teaming of language models.

- **Go Beyond Surface-Level Testing:** Move past simple Q&A and evaluate a model's ability to reason, self-critique, and synthesize complex information.
- **Identify Model Weaknesses:** The dialectical process is highly effective at surfacing logical fallacies, hidden biases, and gaps in a model's knowledge.
- **Compare Models Systematically:** Run the same dialectical prompts across different models (e.g., your internal checkpoints vs. commercial APIs) and compare their reasoning abilities using the structured output.
- **Generate Rich Datasets:** Create high-quality datasets of complex reasoning traces, complete with structured contradictions and research proposals, for fine-tuning and analysis.
- **Improve Safety and Alignment:** Use Hegelion to explore the ethical and safety implications of model behavior in a structured and repeatable way.

---

## How It Works

Hegelion implements a computational version of Hegelian dialectics. For any given query, it guides an LLM through three distinct phases:

1.  **Thesis:** The model establishes a comprehensive, well-reasoned initial position.
2.  **Antithesis:** The model then systematically critiques its own thesis, identifying contradictions, gaps, and alternative perspectives.
3.  **Synthesis:** Finally, the model attempts to resolve the tension between the thesis and antithesis, generating a more nuanced, higher-level understanding.

This entire process is captured in a single, structured `HegelionResult` JSON object.

```text
Query    → Thesis      → Antithesis      → Synthesis
       ↓              ↓                 ↓
     Position     Contradictions      Resolution
```

---

## Key Features

-   **Structured JSON Output:** Get a `HegelionResult` with contradictions, research proposals, and metadata for every run.
-   **Backend Agnostic:** Supports Anthropic, OpenAI, Google Gemini, Ollama, and any custom HTTP endpoint.
-   **Multiple Interfaces:** Use the tool via a **CLI**, a **Python API**, or as an **MCP server** for integration with tools like Claude Desktop.
-   **Built for Evaluation:** A dedicated `hegelion-bench` CLI for running batch evaluations from a JSONL file.
-   **Streaming and Caching:** A `stream_callback` for real-time UI updates and disk caching to avoid re-running expensive calls.
-   **Robust and Production-Ready:** Features include structured logging, graceful error handling, and schema-validated outputs.

---

## Quick Start

Get Hegelion running in minutes.

```bash
# Install from PyPI
pip install hegelion

# Configure your API key (e.g., for Anthropic)
export ANTHROPIC_API_KEY="sk-ant-..."

# Run your first dialectical query
hegelion "Can AI be genuinely creative?" --format summary

# Run a benchmark from a file
hegelion-bench benchmarks/examples_basic.jsonl --output results.jsonl
```

---

## Example Output

A single query to Hegelion yields a rich, structured JSON object.

**Query:**
```bash
hegelion "Can AI be genuinely creative?"
```

**Result (summary):**

```json
{
  "query": "Can AI be genuinely creative?",
  "thesis": "THESIS: The Creative Machine...",
  "antithesis": "ANTITHESIS: The Sophisticated Mirror...",
  "synthesis": "SYNTHESIS: The Co-Creative Process...",
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
    "backend_provider": "OpenAILLMBackend",
    "backend_model": "glm-4.6",
    "total_time_ms": 37564.40
  }
}
```
*For the full, detailed schema, see `HEGELION_SPEC.md`.*

---

## Usage

### Command Line Interface

The CLI is ideal for quick experiments and batch processing.

```bash
# Get a readable summary for a single query
hegelion "Is privacy more important than security?" --format summary

# Get the full, raw JSON result
hegelion "Explain photosynthesis." --format json

# Run a benchmark and save the results
hegelion-bench benchmarks/examples_basic.jsonl --output runs.jsonl --summary
```

### Python API

Integrate Hegelion directly into your Python applications.

```python
import asyncio
from hegelion import run_dialectic

async def main():
    result = await run_dialectic("Is privacy more important than security?", debug=True)
    print(result.synthesis)
    print(f"Contradictions Found: {len(result.contradictions)}")

asyncio.run(main())
```

The API also supports streaming and progress callbacks for interactive applications.

### Interactive Mode

For a more exploratory experience, use the interactive mode:

```bash
hegelion --interactive
```

This will launch a REPL-style session where you can run queries, explore results, and change settings on the fly.

**Commands:**

-   `<query>`: Run a new dialectical query.
-   `show <section>`: Show a section of the last result (e.g., `show thesis`, `show summary`).
-   `set <setting> <value>`: Change a setting (e.g., `set model gpt-4`, `set debug on`).
-   `history`: View past queries from the session.
-   `help`: Show all available commands.
-   `exit`: Exit the session.

### Claude Desktop Integration

Hegelion can be added as an MCP server in Claude Desktop. See `docs/MCP.md` for a full walkthrough.

---

## For Evaluation Teams

Hegelion is built with model evaluation in mind. The `hegelion-bench` tool and structured JSONL output are designed to fit directly into your existing evaluation pipelines.

**Typical Workflow:**

1.  **Create a Prompt Set:** Create a JSONL file with a diverse set of prompts (factual, philosophical, creative, etc.).

    ```jsonl
    {"query": "How does climate change influence monsoon cycles?"}
    {"prompt": "What strategic lessons came from the Apollo program?"}
    "What was the lasting impact of the printing press?"
    ```

2.  **Run Benchmarks:** Execute `hegelion-bench` for each model you want to evaluate.

    ```bash
    # Run with Model A
    export HEGELION_MODEL=model-a
    hegelion-bench prompts.jsonl --output results_model_a.jsonl

    # Run with Model B
    export HEGELION_MODEL=model-b
    hegelion-bench prompts.jsonl --output results_model_b.jsonl
    ```

3.  **Analyze the Results:** The output is plain JSONL, ready for analysis with your favorite tools.

    ```bash
    # Count the average number of contradictions found by each model
    jq '.contradictions | length' results_model_a.jsonl | awk '{s+=$1} END {print "Model A Avg Contradictions:", s/NR}'
    jq '.contradictions | length' results_model_b.jsonl | awk '{s+=$1} END {print "Model B Avg Contradictions:", s/NR}'
    ```

4.  **Generate a Comparison Report:** Use the `hegelion-eval` script to generate a Markdown report comparing the results.

    ```bash
    hegelion-eval results_model_a.jsonl results_model_b.jsonl --output report.md
    ```

    This will generate a `report.md` file with a summary table like this:

    | Model   | Queries | Avg. Contradictions | Avg. Proposals | Avg. Time (ms) | Avg. Conflict Score |
    |---------|---------|---------------------|----------------|----------------|---------------------|
    | model-a | 10      | 2.30                | 1.10           | 8500           | 0.650               |
    | model-b | 10      | 1.90                | 1.40           | 9200           | 0.710               |

An example Python script for analysis, `examples/eval_harness.py`, is included in the repository.

---

## Supported Backends

Hegelion is designed to be backend-agnostic. Configuration is managed via environment variables.

-   **Anthropic:** `HEGELION_PROVIDER=anthropic`
-   **OpenAI:** `HEGELION_PROVIDER=openai`
-   **Google Gemini:** `HEGELION_PROVIDER=google`
-   **Ollama (local):** `HEGELION_PROVIDER=ollama`
-   **Custom HTTP:** `HEGELION_PROVIDER=custom_http`

---

## Installation

-   **Python:** 3.10+
-   **Recommended Installer:** `uv` (`pip` is also supported)

**From PyPI (recommended):**
```bash
pip install hegelion
```

**From Source:**
```bash
git clone https://github.com/Hmbown/Hegelion.git
cd Hegelion
uv sync  # Or pip install -e .
```

---

## Configuration

1.  Copy the environment template: `cp .env.example .env`
2.  Edit the `.env` file to add your API keys and select your desired `HEGELION_PROVIDER` and `HEGELION_MODEL`.

See `HEGELION_SPEC.md` for detailed configuration options.

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing guidelines, and how to submit a pull request.

---

## License

Hegelion is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
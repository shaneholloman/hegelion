# Hegelion

[![CI](https://github.com/Shannon-Labs/Hegelion/actions/workflows/ci.yml/badge.svg)](https://github.com/Shannon-Labs/Hegelion/actions/workflows/ci.yml)

> A dialectical reasoning harness for LLMs: Thesis → Antithesis → Synthesis with structured contradictions, research proposals, and metadata you can trust.

**TL;DR**

- Runs a deterministic three-phase loop: Thesis → Antithesis → Synthesis
- Emits contradictions and research proposals as structured JSON, not buried in text
- Backend-agnostic: Anthropic, OpenAI, Ollama, or custom HTTP bridges
- Ships with JSONL benchmarks + CLI (`hegelion`, `hegelion-bench`) and MCP server (`hegelion-server`)

## What Hegelion Is

Hegelion runs any LLM through Thesis → Antithesis → Synthesis and ships the full result as structured JSON (`HegelionResult`). You always get the three passages plus contradictions, research proposals, and metadata (timings, backend info, optional debug trace). The default backend is Anthropic Claude Sonnet, but the same loop works with OpenAI, Ollama, or a custom HTTP endpoint.

## Why Hegelion?

- **Always synthesizes** – every query completes the full loop.
- **Structured output** – contradictions and proposals arrive as lists, ready for scoring.
- **Honest provenance** – backend/model/timings live in `metadata`, internal scores only appear under `metadata.debug` when requested.
- **Tooling included** – CLI (`hegelion`, `hegelion-bench`) and MCP server (`hegelion-server`) come with the package.

## Quick Start

### Requirements

- Python 3.10+ (regularly tested on 3.10 and 3.11)
- `uv` recommended for dependency management (fallback: `pip install -e .`)

1. **Clone + enter the repo**
   ```bash
   git clone https://github.com/Shannon-Labs/Hegelion.git
   cd Hegelion
   ```
2. **Install dependencies** (prefer `uv`)
   ```bash
   uv sync              # creates .venv and installs runtime deps
   # Fallback:
   # pip install -e .
   ```
   Local editable install (if you prefer plain pip):
   ```bash
   pip install -e .
   ```
   Hegelion is currently a Git-first research release; PyPI packaging will come later.
3. **Configure your backend**
   ```bash
   cp .env.example .env
   # Edit .env with at least:
   # HEGELION_PROVIDER=anthropic
   # HEGELION_MODEL=claude-4.5-sonnet-latest
   # ANTHROPIC_API_KEY=sk-...
   ```
   Switch to `openai`, `ollama`, or `custom_http` by editing `.env`. Set `HEGELION_PROVIDER=auto` only if you want Hegelion to pick the first available key.
4. **Run your first dialectic**
   ```bash
   uv run hegelion "Can AI be genuinely creative?" --format summary
   ```

## Usage

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

### CLI

```bash
# Single query with readable summary
hegelion "What is the capital of France?" --format summary

# JSONL benchmark (one prompt per line)
hegelion-bench benchmarks/examples_basic.jsonl --output runs.jsonl --summary

# Raw JSON result (handy for scripting)
hegelion "Explain what photosynthesis does for a plant." --debug --format json
```

### MCP Server

- `hegelion-server` → stdio server for Claude Desktop, Cursor, or any MCP host.
- Tools: `run_dialectic(query: string, debug?: bool)` and `run_benchmark(prompts_file: string, debug?: bool)`.
- Responses are the same JSON you get from the Python API.

## Hero Example (AI Creativity)

Recorded glm-4.6 run for “Can AI be genuinely creative?” (full trace lives in `examples/glm4_6_examples.jsonl`).

> Generated with a Claude-compatible `glm-4.6` backend via an Anthropic-style API. Your provider/model will change the wording, not the schema.

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

Full text (including thesis, antithesis, synthesis, trace, and timings) lives in `examples/glm4_6_examples.jsonl` line 1.

## Examples & Benchmarks

- `examples/glm4_6_examples.jsonl` — canonical glm-4.6 traces for:
  - Philosophical: “Can AI be genuinely creative?”
  - Factual: “What is the capital of France?”
  - Scientific: “Explain what photosynthesis does for a plant.”
  - Historical: “When was the first moon landing?”
- `examples/README.md` — index + CLI instructions for replaying each example.
- `examples/*.md` — narrative walk-throughs for creative reasoning prompts.
- `benchmarks/examples_basic.jsonl` — starter JSONL for benchmarking harness behavior.

Generate your own dataset by adding `--output my_runs.jsonl` to either CLI or by calling `run_benchmark(..., output_file="file.jsonl")` from Python.

## For Model Builders & Evaluation Teams

1. Switch providers by editing `.env` (`HEGELION_PROVIDER` + `HEGELION_MODEL`).
2. Run benchmarks via `hegelion-bench prompts.jsonl --output results.jsonl`, then rerun with other providers for apples-to-apples comparison.
3. Parse the JSONL output—each line already includes thesis/antithesis/synthesis, contradictions, proposals, metadata, and (optionally) debug metrics.

## MCP Integration

Claude Desktop config example (`~/Library/Application Support/Claude/claude_desktop_config.json`):

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
        "ANTHROPIC_API_KEY": "sk-..."
      }
    }
  }
}
```

If `hegelion-server` isn’t on PATH, swap the command for `python -m hegelion.mcp_server`. Only `run_dialectic` and `run_benchmark` are exposed.

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

## License & Status

- **License:** MIT (see `LICENSE`).
- **Status:** Actively maintained research infrastructure. The dialectical protocol and JSON schema are stable; internal engine/backends may evolve.

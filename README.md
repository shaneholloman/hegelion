# Hegelion

> A dialectical reasoning harness for LLMs: Thesis → Antithesis → Synthesis with structured contradictions, research proposals, and metadata you can trust.

## What Hegelion Is

Hegelion wraps any large language model in a deterministic three-phase reasoning loop. Every run produces a thesis, a rigorous antithesis, and an unavoidable synthesis that transcends both sides while emitting machine-readable contradictions and research proposals. Results come back as a `HegelionResult` dataclass (and MCP payload) with provenance metadata, timing, backend identifiers, and optional debug traces.

The engine is backend-agnostic. It defaults to Anthropic Claude Sonnet (`HEGELION_PROVIDER=anthropic`, `HEGELION_MODEL=claude-4.5-sonnet-latest`) but also speaks OpenAI, custom HTTP bridges, and local Ollama.

## Why Hegelion?

- **Always synthesizes** – no conflict gating; every query yields a dialectical resolution.
- **Inspectable structure** – contradictions and research proposals are extracted into lists, not buried inside Markdown.
- **Backend transparency** – provenance (provider, model, timings) is part of the result; conflict metrics live only under `metadata.debug` when `debug=True`.
- **Research-grade outputs** – emit JSONL for benchmarking, evaluation, or data collection pipelines.
- **MCP ready** – ships with `hegelion-server` exposing only the sanctioned `run_dialectic` and `run_benchmark` tools.

## Quick Start

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

The star example is the recorded glm-4.6 run answering “Can AI be genuinely creative?”:

- **Thesis** argues a functional, computational definition of creativity and positions AI as a creative machine.
- **Antithesis** highlights intent, experience, and domain-breaking novelty as criteria AI cannot meet.
- **Synthesis** reframes creativity as an emergent property of a co-creative human–AI process and proposes the Co-Creative Trace Analysis.

> Example output below was generated with a Claude-compatible `glm-4.6` backend via an Anthropic-style API. Your outputs will differ depending on your configured provider/model (docs assume Claude 4.5 Sonnet as the default).

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

1. **Flip providers quickly** — change `HEGELION_PROVIDER` / `HEGELION_MODEL` in `.env` (e.g., `openai` + `gpt-4.1-mini`, `ollama` + `llama3.1`, or `custom_http`).
2. **Run JSONL benchmarks** — `hegelion-bench prompts.jsonl --output anthropic.jsonl`, then swap env vars and rerun for OpenAI/Ollama.
3. **Compare structured fields** — every line carries `thesis/antithesis/synthesis`, `contradictions`, `research_proposals`, `metadata.backend_*`, and optional `metadata.debug.internal_conflict_score` when `--debug` is passed.
4. **Integrate with evaluation pipelines** — parse JSONL, rank contradictions, grade syntheses, or compute deltas across backends.

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

If the console scripts are unavailable in your PATH, use `"command": "python", "args": ["-m", "hegelion.mcp_server"]` instead. Only the `run_dialectic` and `run_benchmark` tools are exposed, mirroring the public Python API.

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
- **Status:** Actively maintained research infrastructure. Treat the dialectical protocol as stable; internal engine/backends are intentionally private.

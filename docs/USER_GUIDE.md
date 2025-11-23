# Hegelion User Guide

This guide covers everyday usage of Hegelion once it is installed from PyPI or from source.

## Installation

### From PyPI (recommended)

```bash
pip install hegelion
```

### From source

```bash
git clone https://github.com/Hmbown/Hegelion.git
cd Hegelion
uv sync  # or: pip install -e .
```

## Basic Configuration

Create a `.env` file (or export environment variables) to choose your backend. We provide a template `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` to point at Anthropic, OpenAI, Ollama, or a custom HTTP backend as described in `HEGELION_SPEC.md` and the main README.

## Verified Backends

The project maintainers currently verify two providers end-to-end:

- **Anthropic Claude** (default in `env.example`).
- **GLM 4.6** — configure `HEGELION_PROVIDER=openai`, `HEGELION_MODEL=GLM-4.6`, `OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4`, and your Z.AI API key. Reference transcripts live in `examples/glm4_6_examples.jsonl`; replay with `hegelion-bench` to diff against new runs.

We welcome confirmation for other Anthropic/OpenAI-compatible deployments (Azure OpenAI, custom base URLs, etc.).

## Share Sanitized Logs

Keep raw run output locally (the `artifacts/logs/` directory is git-ignored) and attach only redacted metadata when opening an issue or PR:

```bash
mkdir -p artifacts/logs
HEGELION_PROVIDER=openai \
HEGELION_MODEL=GLM-4.6 \
OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4 \
OPENAI_API_KEY=sk-... \
uv run hegelion "Can AI be genuinely creative?" --format json > artifacts/logs/glm_run.json

jq 'del(.query, .thesis, .antithesis, .synthesis, .contradictions, .research_proposals)' \
    artifacts/logs/glm_run.json > artifacts/logs/glm_run.metadata.json
```

Attach the sanitized file (or paste its contents) when reporting provider success/failure.

## CLI Usage (Basic)

The CLI is primarily for demos and quick checks. For advanced features (personas, iterations), use the Python API or MCP.

Single query with a readable summary:

```bash
# Demo mode (no API key needed)
hegelion --demo

# Single query with a readable summary
hegelion "Can AI be genuinely creative?" --format summary
```

Raw JSON result:

```bash
hegelion "Explain what photosynthesis does for a plant." --debug --format json
```

Benchmark on a JSONL file:

```bash
hegelion-bench benchmarks/examples_basic.jsonl --output runs.jsonl --summary
```

Traces are written as **JSONL** – one `HegelionResult` per line – so you can post-process them with tools like `jq` or `pandas.read_json(..., lines=True)`.

## Python API

For full control, use the Python API.

```python
import asyncio
from hegelion import quickstart, dialectic, run_benchmark

async def main():
    # Easiest path – uses env-configured backend/model
    result = await quickstart("Is privacy more important than security?", debug=True)
    print(result.synthesis)

    # Explicit model with auto-detected backend (e.g., Anthropic/OpenAI/Gemini/local)
    alt = await dialectic("Can AI be genuinely creative?", model="claude-4.5-sonnet")
    print(f"Backend synthesis: {alt.synthesis[:120]}...")

asyncio.run(main())
```

## MCP Server

Start the MCP server:

```bash
python -m hegelion.mcp.server
```

Then wire it into your MCP client (for example, Claude Desktop) using the configuration snippet in the main README.

Additional resources:

- `docs/MCP.md` – in-depth reference covering MCP tool schemas, troubleshooting, and client-specific notes.
- `examples/mcp/claude_desktop_config.json` – ready-made Claude Desktop snippet you can drop into your config file.

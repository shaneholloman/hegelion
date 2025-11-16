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

Create a `.env` file (or export environment variables) to choose your backend:

```bash
cp .env.example .env
```

Edit `.env` to point at Anthropic, OpenAI, Ollama, or a custom HTTP backend as described in `HEGELION_SPEC.md` and the main README.

## Verified Backends

The project maintainers currently verify two providers end-to-end:

- **Anthropic Claude** (default `.env.example` entries).
- **GLM 4.6** — configure `HEGELION_PROVIDER=openai`, `HEGELION_MODEL=GLM-4.6`, `OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4`, and your Z.AI API key. Reference transcripts live in `examples/glm4_6_examples.jsonl`; replay with `hegelion-bench` to diff against new runs.

We welcome confirmation for other Anthropic/OpenAI-compatible deployments (Azure OpenAI, custom base URLs, etc.).

## Share Sanitized Logs

Keep raw run output locally (the `logs/` directory is git-ignored) and attach only redacted metadata when opening an issue or PR:

```bash
mkdir -p logs
HEGELION_PROVIDER=openai \
HEGELION_MODEL=GLM-4.6 \
OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4 \
OPENAI_API_KEY=sk-... \
uv run hegelion "Can AI be genuinely creative?" --format json > logs/glm_run.json

jq 'del(.query, .thesis, .antithesis, .synthesis, .contradictions, .research_proposals)' \
    logs/glm_run.json > logs/glm_run.metadata.json
```

Attach the sanitized file (or paste its contents) when reporting provider success/failure.

## CLI Usage

Single query with a readable summary:

```bash
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

## Python API

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

## MCP Server

Start the MCP server:

```bash
python -m hegelion.mcp_server
```

Then wire it into your MCP client (for example, Claude Desktop) using the configuration snippet in the main README.

Additional resources:

- `docs/MCP.md` – in-depth reference covering MCP tool schemas, troubleshooting, and client-specific notes.
- `examples/mcp/claude_desktop_config.json` – ready-made Claude Desktop snippet you can drop into your config file.


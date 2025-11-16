# Hegelion User Guide

This guide covers everyday usage of Hegelion once it is installed from PyPI or from source.

## Installation

### From PyPI (recommended)

```bash
pip install hegelion
```

### From source

```bash
git clone https://github.com/Shannon-Labs/Hegelion.git
cd Hegelion
uv sync  # or: pip install -e .
```

## Basic Configuration

Create a `.env` file (or export environment variables) to choose your backend:

```bash
cp .env.example .env
```

Edit `.env` to point at Anthropic, OpenAI, Ollama, or a custom HTTP backend as described in `HEGELION_SPEC.md` and the main README.

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


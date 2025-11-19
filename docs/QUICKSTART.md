# Quick Start

Get Hegelion running in 5 minutes. No docs site needed.

## Prerequisites

- Python 3.10+
- One of:
  - uv (recommended): `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - pip (works fine)

## Option A: Model-Agnostic (MCP) in Your Editor (Zero API Keys)

Works with any model already configured in your editor (Cursor, Claude Desktop, VS Code).

1) Install Hegelion

```bash
pip install hegelion
# or
uv pip install hegelion
```

2) Register the prompt server in your MCP config

Claude Desktop example (`claude_desktop_config.json`):

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

3) Ask your AI to run a dialectic

> “Run a dialectical analysis on ‘Is AI conscious?’ using the Hegelion prompt server with council critiques.”

That’s it—no API keys required. The model you already use will execute the steps using structured prompts.

## Option B: Python API (Full Control)

Use your preferred LLM provider via environment variables.

1) Install

```bash
pip install hegelion
```

2) Configure environment

```bash
cp env.example .env
# edit .env with your provider keys (Anthropic / OpenAI / Google / Ollama / custom)
```

3) First query

```python
import asyncio
from hegelion import run_dialectic

async def main():
    result = await run_dialectic("Is AI conscious?")
    print(result.synthesis)

asyncio.run(main())
```

4) Advanced options

```python
result = await run_dialectic(
    "Should we regulate AI?",
    personas="council",   # Logician, Empiricist, Ethicist
    iterations=2,          # Synthesis -> new Thesis
    use_search=True        # Encourage fact-checking during critique
)
```

## Troubleshooting

- "No backend configured" error:
  - Ensure `.env` contains your provider keys and `HEGELION_PROVIDER`/`HEGELION_MODEL`.
- Claude Desktop can’t see the server:
  - Ensure `hegelion-prompt-server` is on PATH or use the `uv run` command in the config.
- Results look empty:
  - Try a more complex query or a stronger model; enable `debug=True` to include internal metrics.

## What’s Next

- MCP reference: `docs/MCP.md`
- Prompt-driven usage: `docs/MODEL_AGNOSTIC.md`
- User guide (CLI, API details): `docs/USER_GUIDE.md`
- Examples and recorded traces: `examples/`

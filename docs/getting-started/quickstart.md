# Quickstart

Get Hegelion running in 5 minutes.

## Option A: MCP (No API Keys)

Works with any model in your editor (Claude Desktop, Cursor, VS Code).

### 1. Install

```bash
pip install hegelion
```

### 2. Configure

**Claude Desktop (macOS):**
```bash
hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

**Cursor:**
```bash
hegelion-setup-mcp
# Copy output to Settings → Features → MCP
```

### 3. Restart Your Editor

Claude Desktop: Cmd+Q and reopen (not just close the window).

### 4. Test

Ask: *"What Hegelion tools are available?"*

You should see: `dialectical_workflow`, `dialectical_single_shot`, `thesis_prompt`, `antithesis_prompt`, `synthesis_prompt`.

### 5. Run Your First Dialectic

> "Use Hegelion to analyze: Is AI conscious?"

That's it. Your editor's model runs the prompts—no extra API keys.

---

## Option B: Python API

Use your own LLM provider directly.

### 1. Install

```bash
pip install hegelion
```

### 2. Configure

Create a `.env` file:

```bash
HEGELION_PROVIDER=anthropic
HEGELION_MODEL=claude-4.5-sonnet-latest
ANTHROPIC_API_KEY=your-key
```

### 3. Run

```python
import asyncio
from hegelion import run_dialectic

async def main():
    result = await run_dialectic("Is AI conscious?")
    print(result.synthesis)

asyncio.run(main())
```

### 4. Advanced Options

```python
result = await run_dialectic(
    "Should we regulate AI?",
    personas="council",     # Logician, Empiricist, Ethicist
    iterations=2,           # Multiple dialectical passes
    use_search=True         # Ground arguments with search
)
```

---

## Next Steps

- **[MCP Integration](../guides/mcp-integration.md)** — Full setup guide for all editors
- **[Python API](../guides/python-api.md)** — Complete API reference
- **[Configuration](configuration.md)** — All backend options

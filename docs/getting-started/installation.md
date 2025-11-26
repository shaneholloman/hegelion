# Installation

## From PyPI (Recommended)

```bash
pip install hegelion
```

Or with uv:

```bash
uv pip install hegelion
```

## From Source

```bash
git clone https://github.com/Hmbown/Hegelion.git
cd Hegelion
pip install -e .
```

If you get an "externally-managed-environment" error:

```bash
pip install --break-system-packages -e .
```

## Requirements

- Python 3.10+
- For MCP mode: No additional requirements
- For Python API: Provider SDK (anthropic, openai, or google-generativeai)

## Verifying Installation

```bash
# Check CLI is available
hegelion --demo

# Check MCP server
python -m hegelion.mcp.server --help
```

## Next Steps

- **[MCP Integration](../guides/mcp-integration.md)** — Use with Claude Desktop, Cursor, VS Code
- **[Configuration](configuration.md)** — Set up your LLM backend
- **[Quickstart](quickstart.md)** — Run your first dialectic

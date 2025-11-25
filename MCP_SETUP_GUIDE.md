# Hegelion MCP Server Setup

## Quick Setup for Claude Desktop

The Hegelion MCP server provides dialectical reasoning tools that work with any LLM. Two setup methods are available:

### Method 1: Using the Setup Script (Recommended)

Run the automated setup script:
```bash
hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

This automatically detects your Python installation and creates the correct configuration.

### Method 2: Manual Configuration

Add the following to your Claude Desktop config file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "hegelion": {
      "command": "python",
      "args": ["-m", "hegelion.mcp.server"],
      "env": {
        "PYTHONPATH": "/path/to/hegelion/source/if/not/installed"
      }
    }
  }
}
```

**Important Notes:**
- Use the full path to Python if needed (e.g., `/usr/local/bin/python` or `/Users/yourname/.pyenv/shims/python`)
- If Hegelion is installed from PyPI, you don't need the PYTHONPATH environment variable
- If running from source, set PYTHONPATH to the Hegelion repository root

### Common Issues and Solutions

1. **"spawn hegelion-server ENOENT" error**
   - This means the `hegelion-server` command isn't found in PATH
   - Solution: Use the `python -m hegelion.mcp.server` approach instead

2. **"Module not found" error**
   - This happens when running from source without proper Python path
   - Solution: Add `PYTHONPATH` environment variable pointing to the repo root

3. **Which Python to use?**
   - Find your Python path with: `which python`
   - Common paths: `/usr/local/bin/python`, `/usr/bin/python3`, `/Users/yourname/.pyenv/shims/python`

## Available Tools

Once connected, these tools are available:

- `dialectical_workflow` - Step-by-step prompts for thesis → antithesis → synthesis
- `dialectical_single_shot` - Single comprehensive prompt for powerful models
- `thesis_prompt` - Generate thesis phase prompt only
- `antithesis_prompt` - Generate antithesis phase prompt only
- `synthesis_prompt` - Generate synthesis phase prompt only

## Restart Required

After updating the configuration, **quit and restart Claude Desktop** for changes to take effect.
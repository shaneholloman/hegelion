# MCP Integration

Hegelion works as an MCP (Model Context Protocol) server. It returns structured prompts that your existing LLM executes—no extra API keys required.

## How It Works

When you use Hegelion via MCP, the server generates prompts for each dialectical phase. Your editor's model (Claude, GPT, Gemini, etc.) runs them. Hegelion never makes API calls in this mode.

```
Your Editor (Cursor, Claude Desktop, VS Code)
    │
    ▼
Hegelion MCP Server (generates prompts)
    │
    ▼
Your LLM (executes the prompts)
```

## Installation

```bash
pip install hegelion

# If running from source:
pip install -e .
```

## Supported Environments

| Environment | Config Location | Setup |
|-------------|-----------------|-------|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) | [Auto](#claude-desktop) or [Manual](#claude-desktop-1) |
| Claude Code | `~/.claude.json` | [CLI](#claude-code) |
| Cursor | Settings → Features → MCP | [Manual](#cursor) |
| VS Code | MCP extension settings | [Manual](#vs-code) |
| Gemini CLI | Extension install | [CLI](#gemini-cli) |

## Setup by Environment

### Claude Desktop

**Auto-config (recommended):**

```bash
# macOS
hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Windows
hegelion-setup-mcp --write "%APPDATA%\Claude\claude_desktop_config.json"

# Linux
hegelion-setup-mcp --write "$HOME/.config/Claude/claude_desktop_config.json"
```

**Manual config:**

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hegelion": {
      "command": "/full/path/to/python",
      "args": ["-m", "hegelion.mcp.server"]
    }
  }
}
```

Find your Python path:
```bash
which python
# Example: /usr/local/bin/python
```

**Restart required:** Quit Claude Desktop completely (Cmd+Q on macOS) and reopen.

### Claude Code

```bash
# Add the MCP server
claude mcp add hegelion python -- -m hegelion.mcp.server

# Verify
claude mcp list

# Restart Claude Code
exit  # Then reopen terminal
```

### Cursor

1. Run `hegelion-setup-mcp` (without `--write`)
2. Copy the output JSON
3. Paste into **Settings → Features → MCP**
4. Restart Cursor

### VS Code

Configure your MCP extension to use:
- Command: `python`
- Args: `["-m", "hegelion.mcp.server"]`

### Gemini CLI

```bash
gemini extensions install https://github.com/Hmbown/Hegelion --branch main --path hegelion-mcp-node
```

## Available Tools

### `dialectical_single_shot`
Primary tool. Returns one prompt that guides the LLM through Thesis → Antithesis → Synthesis.

```
Use Hegelion's dialectical_single_shot to analyze: "Can AI be creative?"
```

### `dialectical_workflow`
Returns a structured workflow for step-by-step execution. Use for complex queries.

```
Generate a Hegelion workflow for: "Should we regulate AI?" with use_council=true
```

### Individual Phase Prompts
- `thesis_prompt` — Generate thesis only
- `antithesis_prompt` — Generate antithesis only (requires thesis)
- `synthesis_prompt` — Generate synthesis (requires both)

## Feature Toggles

| Option | Default | Description |
|--------|---------|-------------|
| `use_council` | `false` | Activates three critics: Logician, Empiricist, Ethicist |
| `use_judge` | `false` | Adds quality evaluation step |
| `use_search` | `false` | Prompts include search grounding instructions |
| `response_style` | `sections` | Output format: `json`, `sections`, or `synthesis_only` |

**Example with options:**
```
Run dialectical_single_shot on "Is consciousness fundamental?" with use_council=true
```

## Troubleshooting

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `spawn hegelion-server ENOENT` | `hegelion-server` not in PATH | Use `python -m hegelion.mcp.server` |
| `ModuleNotFoundError: hegelion` | Running from source without install | Run `pip install -e .` from repo root |
| Server disconnects on startup | Python path issues | Use full path (see below) |
| "Unknown tool" error | Config not loaded | Restart your editor completely |

### Finding Your Python Path

**Standard:**
```bash
which python
which python3
```

**Pyenv:**
```bash
pyenv which python
# Example: /Users/you/.pyenv/versions/3.11.9/bin/python
```

**Conda:**
```bash
conda list python | grep python
```

**Virtual environment:**
```bash
# With env activated:
which python
# Example: /path/to/venv/bin/python
```

### Checking Logs

**macOS:**
```bash
cat ~/Library/Logs/Claude/mcp-server-hegelion.log
```

**Windows:**
```cmd
type %APPDATA%\Claude\logs\mcp-server-hegelion.log
```

**Linux:**
```bash
cat ~/.local/share/Claude/logs/mcp-server-hegelion.log
```

### Sample Configurations

**Standard (Homebrew Python):**
```json
{
  "mcpServers": {
    "hegelion": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "hegelion.mcp.server"]
    }
  }
}
```

**Pyenv:**
```json
{
  "mcpServers": {
    "hegelion": {
      "command": "/Users/you/.pyenv/versions/3.11.9/bin/python",
      "args": ["-m", "hegelion.mcp.server"]
    }
  }
}
```

**Conda:**
```json
{
  "mcpServers": {
    "hegelion": {
      "command": "/Users/you/miniconda3/bin/python",
      "args": ["-m", "hegelion.mcp.server"]
    }
  }
}
```

## Verifying Installation

After setup, ask in your editor:

> "What Hegelion tools are available?"

You should see: `dialectical_workflow`, `dialectical_single_shot`, `thesis_prompt`, `antithesis_prompt`, `synthesis_prompt`.

## Getting Help

If you're stuck:
1. Check the log file (see above)
2. Ensure you used full Python path
3. Verify `pip install hegelion` completed
4. Open an issue at [github.com/Hmbown/Hegelion](https://github.com/Hmbown/Hegelion/issues)

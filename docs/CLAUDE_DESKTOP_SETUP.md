# Hegelion MCP Setup for Claude Desktop

This guide shows how to integrate Hegelion's dialectical reasoning capabilities with Claude Desktop via MCP (Model Context Protocol). **Hegelion operates as a prompt server, leveraging Claude Desktop's own internal LLM to execute the reasoning steps. No API keys are needed for Hegelion itself.**

## 🚀 Quick Setup

### 1. Install Hegelion

**Option A: Install from PyPI (Easiest)**
```bash
pip install hegelion
```

**Option B: Install from Source (If you cloned the repo)**
```bash
# From the repo root
pip install -e .

# If you get "externally-managed-environment" error:
pip install --break-system-packages -e .
```

### 2. Configure Claude Desktop

**Method 1: Auto-Config (Recommended)**
```bash
# macOS
hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Windows
hegelion-setup-mcp --write "%APPDATA%\Claude\claude_desktop_config.json"

# Linux
hegelion-setup-mcp --write "$HOME/.config/Claude/claude_desktop_config.json"
```

**Method 2: Manual Configuration**

1. Find your config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add to the `mcpServers` section:

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

3. Find your Python path:
   ```bash
   which python
   # Example output: /usr/local/bin/python
   # Use this exact path in the config above
   ```

### 3. Restart Claude Desktop

**Important**: You must completely quit and restart Claude Desktop:
- **macOS**: Cmd+Q (not just closing the window)
- **Windows**: Close from taskbar or File → Exit
- **Linux**: File → Quit

### 4. Verify Installation

In Claude Desktop, ask: *"What Hegelion tools are available?"*

You should see:
- `dialectical_workflow`
- `dialectical_single_shot`
- `thesis_prompt`
- `antithesis_prompt`
- `synthesis_prompt`

## 🛠️ Available Tools

### `dialectical_single_shot`
The primary tool for general use. Returns a single comprehensive prompt that guides Claude through the entire Thesis → Antithesis → Synthesis reasoning process.

**Example usage:**
```
Use Hegelion's dialectical_single_shot to analyze: "Can AI be genuinely creative?" with use_council=true
```

### `dialectical_workflow`
Returns a structured workflow for step-by-step execution. Perfect for complex queries that benefit from systematic reasoning.

**Example usage:**
```
Generate a Hegelion dialectical_workflow for: "Should we implement universal basic income?" with use_council=true and use_judge=true
```

### Individual Phase Prompts
- `thesis_prompt` - Generate thesis phase only
- `antithesis_prompt` - Generate antithesis phase only
- `synthesis_prompt` - Generate synthesis phase only

## 💡 Usage Examples

### Simple Analysis
```
Use Hegelion to analyze: "Is privacy more important than security?"
```

### With Council Critiques
```
Run a Hegelion single-shot analysis on "Is consciousness fundamental or emergent?" using council critiques
```

### Complex Multi-Step Analysis
```
Generate a Hegelion workflow for "How can we best address climate change?" with council and judge enabled
```

## ⚙️ Configuration Options

All Hegelion features are controlled via tool parameters:

- **`use_council`** (default: false) - Activates the Council of Philosophers (Logician, Empiricist, Ethicist)
- **`use_judge`** (default: false) - Adds a final quality evaluation step
- **`response_style`** (default: "sections") - Choose "json" for structured output, "sections" for reading
- **`use_search`** (default: false) - Includes instructions to use available search tools

## 🔧 Troubleshooting

### Common Issues

| Error | Cause | Fix |
|-------|-------|-----|
| `spawn hegelion-server ENOENT` | `hegelion-server` not in PATH | Use `python -m hegelion.mcp.server` instead |
| `ModuleNotFoundError: hegelion` | Running from source without installation | Install with `pip install -e .` from repo root |
| Server disconnects on startup | Python path issues or missing deps | Check log file |
| "Unknown tool" error | Tools not available | Verify config and restart |

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

### Finding Your Python Path

**Standard Python:**
```bash
which python
which python3
```

**Pyenv:**
```bash
pyenv which python
# Example: /Users/username/.pyenv/versions/3.11.9/bin/python
```

**Conda:**
```bash
conda list python | grep python
# Or: where python (Windows)
```

**Virtual Environments:**
```bash
# Activated environment
which python
# Example: /path/to/venv/bin/python
```

## 📝 Sample Configurations

### Standard Installation
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

### Pyenv Installation
```json
{
  "mcpServers": {
    "hegelion": {
      "command": "/Users/username/.pyenv/versions/3.11.9/bin/python",
      "args": ["-m", "hegelion.mcp.server"]
    }
  }
}
```

### Conda Installation
```json
{
  "mcpServers": {
    "hegelion": {
      "command": "/Users/username/miniconda3/bin/python",
      "args": ["-m", "hegelion.mcp.server"]
    }
  }
}
```

## 🎯 Best Practices

1. **Always use full Python paths** - Claude Desktop spawns processes with a clean PATH
2. **Install from source with `-e` flag** - Makes hegelion importable without PYTHONPATH
3. **Restart completely** - Cmd+Q, not just closing the window
4. **Check logs** - If something fails, the log file will show the error

## 🤝 Getting Help

If you're still having trouble:

1. Check the [Complete Setup Guide](../MCP_COMPLETE_SETUP_GUIDE.md)
2. Review [Common Issues](../README.md#common-setup-issues)
3. Create an issue on [GitHub](https://github.com/Hmbown/Hegelion/issues)
4. Include:
   - Your OS and Claude Desktop version
   - Your exact configuration (remove API keys)
   - The error message from logs

## 📚 Related Documentation

- [Quick Start](../README.md)
- [MCP Reference](../MCP.md)
- [Complete Setup Guide](../MCP_COMPLETE_SETUP_GUIDE.md)
- [User Guide](USER_GUIDE.md)
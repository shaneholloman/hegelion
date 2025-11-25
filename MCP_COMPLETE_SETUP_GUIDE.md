# Complete MCP Setup Guide for Hegelion

This guide covers setup for both Claude Desktop (GUI app) and Claude Code (terminal/CLI). Please follow the section for your specific environment.

---

## 📋 Before You Start

### Prerequisites
- Python 3.10+ installed
- Hegelion installed: `pip install hegelion`

### Verify Installation
```bash
# Check Hegelion is installed
python -c "import hegelion; print(f'Hegelion installed at: {hegelion.__file__}')"

# Check Python path (save this for later)
which python
```

---

## 🖥️ Claude Desktop Setup (GUI App)

### Option 1: Auto-Config (Recommended)

```bash
# macOS
hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Windows
hegelion-setup-mcp --write "%APPDATA%\Claude\claude_desktop_config.json"

# Linux
hegelion-setup-mcp --write "$HOME/.config/Claude/claude_desktop_config.json"
```

### Option 2: Manual Configuration

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

**Important**: Replace `/full/path/to/python` with your actual Python path from `which python`.

3. Save and **completely quit Claude Desktop** (Cmd+Q on Mac, not just closing window)

4. Restart Claude Desktop

### Verify Setup
In Claude Desktop, ask: *"What tools are available?"* You should see:
- `dialectical_workflow`
- `dialectical_single_shot`
- `thesis_prompt`
- `antithesis_prompt`
- `synthesis_prompt`

---

## 💻 Claude Code Setup (Terminal/CLI)

### Option 1: Using the CLI (Recommended)

```bash
# Add the server
claude mcp add hegelion python -- -m hegelion.mcp.server

# Verify it's added
claude mcp list

# Exit and restart Claude Code
exit
# Then reopen terminal and run claude again
```

### Option 2: Manual Configuration

1. Edit your Claude Code config:
   ```bash
   # User-level config
   vim ~/.claude.json

   # Or project-level config
   vim .claude.json
   ```

2. Add the MCP server configuration:
   ```json
   {
     "mcpServers": {
       "hegelion": {
         "command": "python",
         "args": ["-m", hegelion.mcp.server"]
       }
     }
   }
   ```

3. Save and restart Claude Code

### Verify Setup
In Claude Code, ask: *"Use Hegelion to analyze: Can AI be conscious?"*

---

## 🔧 Troubleshooting

### Common Errors and Solutions

| Error | Environment | Solution |
|-------|-------------|----------|
| `spawn hegelion-server ENOENT` | Claude Desktop | Use `python -m hegelion.mcp.server` instead |
| `ModuleNotFoundError: hegelion` | Both | Use full Python path with `which python` |
| `command not found: python` | Both | Use `python3` or full path to Python |
| Server disconnects immediately | Both | Check logs below |

### Finding Your Python Path

```bash
# For standard Python
which python
# Example: /usr/local/bin/python

# For pyenv
which python
# Example: /Users/username/.pyenv/shims/python

# For conda
which python
# Example: /Users/username/miniconda3/bin/python

# For virtual environments
which python
# Example: /Users/username/.venv/bin/python
```

### Checking Logs

**Claude Desktop:**
```bash
# macOS
cat ~/Library/Logs/Claude/mcp-server-hegelion.log

# Windows
type %APPDATA%\Claude\logs\mcp-server-hegelion.log

# Linux
cat ~/.local/share/Claude/logs/mcp-server-hegelion.log
```

**Claude Code:**
```bash
claude mcp list
# Look for ✓ (connected) or ✗ (failed) status
```

### Manual Server Test

```bash
# This should hang waiting for input (that's success!)
python -m hegelion.mcp.server

# Press Ctrl+C to exit
```

If this works, the server is fine - the issue is in the MCP configuration.

---

## 📝 Configuration Examples

### Standard Pyenv Setup (macOS/Linux)
```json
{
  "hegelion": {
    "command": "/Users/username/.pyenv/shims/python",
    "args": ["-m", "hegelion.mcp.server"]
  }
}
```

### Conda Environment Setup
```json
{
  "hegelion": {
    "command": "/Users/username/miniconda3/envs/hegelion/bin/python",
    "args": ["-m", "hegelion.mcp.server"]
  }
}
```

### Virtual Environment Setup
```json
{
  "hegelion": {
    "command": "/path/to/project/.venv/bin/python",
    "args": ["-m", "hegelion.mcp.server"],
    "env": {
      "PYTHONPATH": "/path/to/project"
    }
  }
}
```

---

## ✅ Success Checklist

- [ ] Hegelion installed with `pip install hegelion`
- [ ] Correct Python path identified with `which python`
- [ ] MCP server added to correct config file
- [ ] Application restarted (Desktop: Cmd+Q, Code: exit/reopen)
- [ ] Tools appear when asking "What tools are available?"
- [ ] Can run a test analysis

---

## 🎯 Next Steps

Once Hegelion is connected, try these examples:

### Simple Single-Shot Analysis
```
Use Hegelion's dialectical_single_shot to analyze: "Is remote work better than office work?"
```

### Full Workflow with Council
```
Run a Hegelion dialectical_workflow with use_council=true for: "Should social media platforms be regulated?"
```

### Quick Thesis/Antithesis
```
Generate a thesis prompt for: "Will AI replace human programmers?"
```

---

## 🆘 Getting Help

If you're still having trouble:

1. Check the [GitHub Issues](https://github.com/Hmbown/Hegelion/issues)
2. Create a new issue with:
   - Your OS and Claude version
   - Your exact configuration
   - The error message from logs
3. Join the community discussions

Remember: The most common issue is Python path problems. Always use the full path from `which python` in your configuration!
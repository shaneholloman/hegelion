# Hegelion MCP Integration for Claude Code (Zero API Keys)

This guide shows how to integrate Hegelion's dialectical reasoning capabilities with Claude Code via MCP (Model Context Protocol). **Hegelion operates as a prompt server, leveraging Claude Code's own internal LLM to execute the reasoning steps. No API keys are needed for Hegelion itself.**

## Quick Setup

### 1. Install Hegelion

**If installing from PyPI:**
```bash
pip install hegelion
```

**If running from source (cloned repo):**
```bash
pip install -e .
# If you get "externally-managed-environment" error:
pip install --break-system-packages -e .
```

### 2. Configure Claude Code (CLI)

**Method 1: Using the CLI (Recommended)**
```bash
# Add the MCP server
claude mcp add hegelion python -- -m hegelion.mcp.server

# Verify it's added
claude mcp list

# Restart Claude Code (exit and reopen terminal)
exit
```

**Method 2: Using the setup script**
```bash
# Generate config (you'll need to manually copy the output)
hegelion-setup-mcp
```

Then manually add the output to your Claude Code config file.

### 3. Configure Claude Desktop (GUI)

```bash
# Auto-config (recommended)
hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Or manually edit the config file
```

## MCP Tools Available

Once connected, Claude Code can access these tools:

### `dialectical_single_shot`
The primary tool for general use. It provides Claude with a single, comprehensive prompt designed to guide it through the entire Thesis → Antithesis (with optional Council critique) → Synthesis reasoning process in one go.

**Input Example for Claude Code:**
```json
{
  "query": "Can AI be genuinely creative?",
  "use_council": true,
  "response_style": "sections"
}
```

### `dialectical_workflow`
For more advanced users or when building agents that require step-by-step control over the dialectical process. This tool returns a structured JSON object containing a sequence of prompts for each phase (Thesis, Antithesis, Synthesis), allowing Claude to execute them sequentially.

**Input Example for Claude Code:**
```json
{
  "query": "Should we implement universal basic income?",
  "use_council": true,
  "use_judge": true,
  "format": "workflow"
}
```

## Example Usage

In Claude Code, you can now ask:
- "Use Hegelion to analyze 'Is privacy more important than security?'"
- "Run a Hegelion single-shot analysis on 'Is consciousness fundamental or emergent?' using council critiques."
- "Generate a Hegelion workflow for 'How can we best address climate change?'"

## Configuration Options

The `hegelion-server` operates without needing its own LLM provider keys because it provides prompts for Claude Code's integrated LLM. All other Hegelion feature toggles (`use_search`, `use_council`, `use_judge`) are handled via the tool arguments.

For a full list of prompt server options and their effects, refer to `docs/MCP.md` and the `hegelion-server --help` output.

## Installation from PyPI

Hegelion v0.3.0 is now available on PyPI:

```bash
pip install hegelion
```

This includes the MCP server (`hegelion-server`) and all CLI tools.

## Common Issues

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: hegelion` | Running from source without installation | Install with `pip install -e .` from repo root |
| `Failed to connect` | Server not starting | Check Python path in config |
| `Command not found: python` | Wrong python command | Use `python3` or full path to Python |

## Configuration Files

- **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
- **Claude Code**: `~/.claude.json` (user) or `.claude.json` (project-local)
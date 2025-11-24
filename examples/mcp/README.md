# MCP Configuration Examples

Example configuration files for integrating Hegelion with MCP-compatible editors.

## Files

| File | Description |
|------|-------------|
| `inprocess_check.py` | Quick smoke test that lists tools and exercises `response_style` options. |
| `claude_desktop_config.json` | Full Claude Desktop config with API key placeholders (for direct LLM calls). |
| `claude_desktop_prompt_config.json` | Minimal Claude Desktop config (recommended — no API keys needed). |
| `cursor_mcp_config.json` | Cursor MCP configuration using `uv run`. |

## Usage

**Claude Desktop (macOS):**
Copy `claude_desktop_prompt_config.json` contents to:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

Or use the automated setup:
```bash
hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

> ⚠️ **Restart Required:** Quit and reopen Claude Desktop after modifying the config.

**Cursor:**
Paste `cursor_mcp_config.json` contents into **Settings → Features → MCP**.

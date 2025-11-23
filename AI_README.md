# Hegelion MCP Quickstart for AI Assistants

Use these exact steps to validate and use the server.

## 1) Install
```bash
pip install hegelion
# or: uv sync
```

## 2) Configure MCP
```bash
hegelion-setup-mcp --write ~/.claude_desktop_config.json
```
This writes the MCP snippet. If running from source, it also sets `PYTHONPATH` automatically.

## 3) Run the server
```bash
python -m hegelion.mcp.server
# alias: hegelion-server
```

## 4) Call tools (include response_style)
- Tools: `dialectical_workflow`, `dialectical_single_shot`, `thesis_prompt`, `antithesis_prompt`, `synthesis_prompt`
- `response_style` values: `json` (structured), `sections` (full text), `synthesis_only` (just the resolution)

Example request payload:
```json
{
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "dialectical_workflow",
    "arguments": {"query": "Should AI be regulated?", "response_style": "json"}
  }
}
```

## One-command validation
```bash
python examples/mcp/inprocess_check.py
```
This prints registered tools and verifies all response styles.

## Common fixes
- "Module not found" when starting server: set `PYTHONPATH` to the repo root when running from source.
- "Unknown tool": use exact tool names above.
- Invalid response_style: allowed values are `json`, `sections`, `synthesis_only`.

## Verified
- MCP ≥1.21.1 installs and imports cleanly.
- `hegelion-setup-mcp` writes a valid config (adds `PYTHONPATH` for source installs).
- Server starts with stdio transport and exposes all tools.
- `response_style` works for `json`, `sections`, and `synthesis_only`.

# CLI Reference

Hegelion ships two CLI entry points focused on MCP integration.

## `hegelion-server`

Run the prompt-driven MCP server over stdio.

```bash
hegelion-server
```

Self-test (lists tools and generates a sample prompt):

```bash
hegelion-server --self-test
```

You can also run it as a module:

```bash
python -m hegelion.mcp.server
```

## `hegelion-setup-mcp`

Generate or write MCP configuration for your editor.

Print a JSON snippet:

```bash
hegelion-setup-mcp
```

Write directly to a config file:

```bash
hegelion-setup-mcp --write ./mcp_config.json
```

Example for Claude Desktop (macOS):

```bash
hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

Notes:

- If Hegelion is not installed in site-packages, the generated config includes `PYTHONPATH` so the MCP server can import local code.
- Restart your MCP host after editing its config.

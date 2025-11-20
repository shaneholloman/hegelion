# Hegelion MCP Reference

This reference walks through running the Hegelion Model Context Protocol (MCP) server, wiring it into Claude Desktop or Cursor, and choosing the right mode for your needs.

## Choose Your Mode

Hegelion offers two distinct MCP servers. You can run one or both.

| Mode | Server Name | Description | Best For |
| --- | --- | --- | --- |
| **Prompt-Driven** | `hegelion-prompt-server` | Generates reasoning *prompts* that your IDE's AI (Claude, GPT-4) executes. **No API keys required.** | **Cursor, Claude Desktop**, VS Code users who want to use their existing model. |
| **Backend-Driven** | `hegelion-server` | Executes the reasoning loop on a background server using API keys you provide. | **Pipelines, Automation**, or offloading heavy reasoning to a different model (e.g. using O1 for reasoning while coding with Sonnet). |

---

## Quick Setup (Automated)

The easiest way to configure Hegelion for Cursor or Claude Desktop is to run the setup command from your terminal:

```bash
# Detects your python environment and generates valid config files
hegelion-setup-mcp
```

This will output a configuration snippet that you can copy directly into your:
1. **Cursor:** `Global MCP Settings`
2. **Claude Desktop:** `claude_desktop_config.json`

---

## Manual Setup

### 1. Cursor Configuration (`mcp_config.json`)

Place this in your project root. **Note:** Use absolute paths for robustness.

```json
{
  "mcpServers": {
    "hegelion": {
      "command": "/absolute/path/to/python",
      "args": ["-m", "hegelion.prompt_mcp_server"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/project_root"
      }
    }
  }
}
```

### 2. Claude Desktop (`claude_desktop_config.json`)

Locate your config file (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`) and add:

```json
{
  "mcpServers": {
    "hegelion-prompt": {
      "command": "/absolute/path/to/python",
      "args": ["-m", "hegelion.prompt_mcp_server"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/project_root"
      }
    }
  }
}
```

---

## Available Tools

### Prompt-Driven Server (`hegelion.prompt_mcp_server`)

These tools return **text prompts** that you (or your agent) execute immediately.

*   `dialectical_single_shot`: Generates one massive prompt for Thesis → Antithesis → Synthesis.
*   `dialectical_workflow`: Generates a JSON plan for step-by-step execution.
*   `thesis_prompt`, `antithesis_prompt`, `synthesis_prompt`: Generates individual phase prompts.

### Backend-Driven Server (`hegelion.mcp_server`)

These tools perform the work **remotely** and return the final result.

*   `run_dialectic`: Runs the full loop. Requires `HEGELION_PROVIDER` and API keys in `.env`.
*   `run_benchmark`: Runs a batch of prompts from a file.

---

## Troubleshooting

### "Tool not found"
- Did you restart your IDE (Cursor/Claude) after changing the config?
- Are you looking for `run_dialectic` (backend) but only installed the prompt server? (Look for `dialectical_single_shot` instead).

### "Module not found: hegelion"
- Ensure `PYTHONPATH` is set correctly in the `env` section of your JSON config.
- Ensure you are using the python executable from your virtual environment (`.venv/bin/python`).

### "API Key missing"
- The **Prompt-Driven** server does *not* need API keys.
- The **Backend-Driven** server needs keys defined in `.env` or passed via the `env` block in the MCP config.

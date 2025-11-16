# Hegelion MCP Reference

This reference walks through running the Hegelion Model Context Protocol (MCP) server, wiring it into Claude Desktop, and troubleshooting common issues. Use it alongside `README.md` and `HEGELION_SPEC.md` when embedding Hegelion into other MCP-capable clients.

## Overview

- **Command:** `hegelion-server` (installed via the `project.scripts` entry point) or `python -m hegelion.mcp_server` if you need an explicit module call.
- **Tools exposed:**
  - `run_dialectic` – single-query thesis → antithesis → synthesis loop with optional debug metrics.
  - `run_benchmark` – batch runner for JSONL prompt files that returns one `HegelionResult` per line.
- **Runtime requirements:** Python 3.10+, configured backend credentials via `.env` (Anthropic by default, GLM and other OpenAI-compatible providers supported).

## Quick Start (Claude Desktop)

1. Ensure `hegelion` is installed (either from PyPI or via `uv sync`).
2. Copy `.env.example` to `.env` and fill in the provider keys you plan to use.
3. Drop the sample config from `examples/mcp/claude_desktop_config.json` into your `claude_desktop_config.json` (or merge it with existing servers).
4. Restart Claude Desktop. You should see "Hegelion" listed under available tools.
5. Run a prompt such as "Can AI be genuinely creative?". The Hegelion MCP server will return the structured JSON described in `HEGELION_SPEC.md`.

## Configuration Notes

| Setting | Description |
| --- | --- |
| `HEGELION_PROVIDER` | `anthropic`, `openai`, `google`, `ollama`, `custom_http`, or `auto`. Defaults to Anthropic. |
| `HEGELION_MODEL` | Model identifier for the provider (`claude-4.5-sonnet-latest`, `GLM-4.6`, etc.). |
| Provider-specific API keys | `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, etc. The same values can be passed into Claude Desktop's MCP config if you don't want to rely on `.env`. |
| Debug toggle | Pass `debug=true` in tool arguments to surface conflict scores in `metadata.debug`. |

## Tool Schemas

### `run_dialectic`

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Question or topic to analyze dialectically"
    },
    "debug": {
      "type": "boolean",
      "description": "Include debug information and conflict metrics",
      "default": false
    }
  },
  "required": ["query"]
}
```

### `run_benchmark`

```json
{
  "type": "object",
  "properties": {
    "prompts_file": {
      "type": "string",
      "description": "Path to JSONL file containing prompts"
    },
    "debug": {
      "type": "boolean",
      "description": "Include debug information and conflict metrics",
      "default": false
    }
  },
  "required": ["prompts_file"]
}
```

## Troubleshooting Checklist

- **Server not visible:** Verify `hegelion-server` is on `PATH` or provide the module invocation in the MCP config.
- **Authentication errors:** Confirm the relevant API key is available to both the server process and the MPC client (Claude Desktop does not inherit `.env` by default).
- **Timeouts:** Large benchmarks can take several minutes. Reduce prompt count or increase the MCP client timeout.
- **Backend metadata says "Unknown":** Ensure the backend factory in `hegelion/config.py` reads your environment after you set provider/model (restart the MCP server if switching providers mid-session).

## Contributing / Testing

- Use `uv run hegelion "<prompt>" --format json` to reproduce server outputs outside MCP.
- Capture sanitized logs (see `README.md` → Verified Backends) before opening issues.
- Planned enhancement: add an automated MCP smoke test that spins up `hegelion-server` under pytest and exercises `run_dialectic` via a mock MCP client.

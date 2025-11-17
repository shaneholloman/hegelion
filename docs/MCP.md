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

## Tool Schemas & Payloads

### `run_dialectic`

**Input schema (canonical):**

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
      "description": "Include debug information and conflict metrics (metadata.debug and trace)",
      "default": false
    }
  },
  "required": ["query"]
}
```

**Friendly example call:**

```json
{
  "query": "Can AI be genuinely creative?",
  "debug": true
}
```

**Representative response payload:**

The MCP server wraps the result in a `TextContent` object whose `text` field is a single JSON object following the canonical `HegelionResult` schema:

```json
{
  "query": "Can AI be genuinely creative?",
  "mode": "synthesis",
  "thesis": "THESIS: The Creative Machine ...",
  "antithesis": "ANTITHESIS: The Sophisticated Mirror ...",
  "synthesis": "SYNTHESIS: The Co-Creative Process ...",
  "contradictions": [
    {
      "description": "The Redefinition Fallacy",
      "evidence": "The thesis narrows 'creativity' to a computable procedure, ignoring intent and subjective urgency."
    }
  ],
  "research_proposals": [
    {
      "description": "The Co-Creative Trace Analysis",
      "testable_prediction": "Iterative human–AI dialogues produce artifacts judged more creative than single-pass outputs."
    }
  ],
  "metadata": {
    "thesis_time_ms": 1234.5,
    "antithesis_time_ms": 2345.6,
    "synthesis_time_ms": 3456.7,
    "total_time_ms": 7036.8,
    "backend_provider": "AnthropicLLMBackend",
    "backend_model": "glm-4.6",
    "debug": {
      "internal_conflict_score": 0.95
    }
  },
  "trace": {
    "thesis": "... full phase output ...",
    "antithesis": "... full phase output ...",
    "synthesis": "... full phase output ...",
    "contradictions_found": 3,
    "research_proposals": ["..."],
    "internal_conflict_score": 0.95
  }
}
```

### `run_benchmark`

**Input schema (canonical):**

```json
{
  "type": "object",
  "properties": {
    "prompts_file": {
      "type": "string",
      "description": "Path to JSONL file containing prompts (one per line; each line may be a string or a JSON object with 'query'/'prompt'/'text')"
    },
    "debug": {
      "type": "boolean",
      "description": "Include debug information and conflict metrics for each result",
      "default": false
    }
  },
  "required": ["prompts_file"]
}
```

**Friendly example call:**

```json
{
  "prompts_file": "benchmarks/examples_basic.jsonl",
  "debug": false
}
```

**Representative response payload:**

`run_benchmark` returns a single `TextContent` whose `text` field is **newline-delimited JSON** (JSONL). Each line is one `HegelionResult` object matching the schema above, for example:

```text
{"query": "Can AI be genuinely creative?", "mode": "synthesis", "thesis": "...", "antithesis": "...", "synthesis": "...", "contradictions": [...], "research_proposals": [...], "metadata": {...}}
{"query": "What is the capital of France?", "mode": "synthesis", "thesis": "...", "antithesis": "...", "synthesis": "...", "contradictions": [...], "research_proposals": [...], "metadata": {...}}
```

Assistants should split on newlines and parse each line as independent JSON.

## Assistant Integration Patterns

When integrating Hegelion as an MCP server in a general-purpose AI assistant, we recommend the following patterns:

- Treat `run_dialectic` as the **single-query reasoning tool**.
- Treat `run_benchmark` as a **batch evaluation tool** for pre-existing prompt sets.
- For each tool call:
  - Use the canonical input schemas above.
  - Parse the `text` content as JSON (or JSONL for `run_benchmark`).
  - Map fields as follows:
    - `thesis`, `antithesis`, `synthesis` → the three core reasoning components.
    - `contradictions[]` → structured critiques with `description` and optional `evidence`.
    - `research_proposals[]` → structured proposals with `description` and optional `testable_prediction`.
    - `metadata.backend_provider`, `metadata.backend_model` → backend identification.
    - `metadata.thesis_time_ms`, `metadata.antithesis_time_ms`, `metadata.synthesis_time_ms`, `metadata.total_time_ms` → timing information.
    - `metadata.debug` and `trace` → internal metrics and phase traces, present primarily when `debug=true`.

Downstream tools (e.g., custom evaluators, dashboards, or RAG pipelines) should treat `HegelionResult` as a stable contract; engine details may evolve, but this schema is intended to remain compatible.

## Troubleshooting Checklist

- **Server not visible:** Verify `hegelion-server` is on `PATH` or provide the module invocation in the MCP config.
- **Authentication errors:** Confirm the relevant API key is available to both the server process and the MPC client (Claude Desktop does not inherit `.env` by default).
- **Timeouts:** Large benchmarks can take several minutes. Reduce prompt count or increase the MCP client timeout.
- **Backend metadata says "Unknown":** Ensure the backend factory in `hegelion/config.py` reads your environment after you set provider/model (restart the MCP server if switching providers mid-session).

## Contributing / Testing

- Use `uv run hegelion "<prompt>" --format json` to reproduce server outputs outside MCP.
- Capture sanitized logs (see `README.md` → Verified Backends) before opening issues.
- Planned enhancement: add an automated MCP smoke test that spins up `hegelion-server` under pytest and exercises `run_dialectic` via a mock MCP client.

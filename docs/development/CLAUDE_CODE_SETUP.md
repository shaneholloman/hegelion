# Hegelion MCP Integration for Claude Code

This guide shows how to integrate Hegelion's dialectical reasoning capabilities with Claude Code via MCP (Model Context Protocol).

## Quick Setup

1. **Install Hegelion with MCP support:**
   ```bash
   pip install hegelion
   ```

2. **Configure your LLM backend** by setting environment variables:
   ```bash
   # For Z.AI GLM-4.6 (recommended)
   export HEGELION_PROVIDER="openai"
   export HEGELION_MODEL="GLM-4.6"
   export OPENAI_BASE_URL="https://api.z.ai/api/coding/paas/v4"
   export OPENAI_API_KEY="your-zai-api-key-here"

   # Or for Anthropic Claude (default)
   export HEGELION_PROVIDER="anthropic"
   export HEGELION_MODEL="claude-4.5-sonnet-latest"
   export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
   ```

3. **Start the MCP server:**
   ```bash
   hegelion-server
   ```

## MCP Tools Available

Once connected, Hegelion provides these tools:

### `run_dialectic`
Analyze a single query using dialectical reasoning (thesis → antithesis → synthesis)

**Input:**
```json
{
  "query": "Can AI be genuinely creative?",
  "debug": false
}
```

**Output:** Structured HegelionResult with thesis, antithesis, synthesis, contradictions, and research proposals

### `run_benchmark`
Run multiple queries from a JSONL file for batch analysis

**Input:**
```json
{
  "prompts_file": "benchmarks/examples_basic.jsonl",
  "debug": false
}
```

**Output:** Newline-delimited JSON with one HegelionResult per line

## Example Usage

In Claude Code, you can now ask:
- "Use Hegelion to analyze 'Is privacy more important than security?'"
- "Run a Hegelion benchmark on this prompts file"
- "What are the contradictions in the Hegelion analysis of climate change?"

## Configuration Options

The MCP server respects all Hegelion environment variables:

- `HEGELION_PROVIDER`: anthropic, openai, google, ollama, custom_http
- `HEGELION_MODEL`: Specific model name (e.g., GLM-4.6, claude-4.5-sonnet-latest)
- `HEGELION_LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

For a full list of backend configurations, see the main README.md.

## Installation from PyPI

Hegelion v0.2.3 is now available on PyPI:

```bash
pip install hegelion
```

This includes the MCP server (`hegelion-server`) and all CLI tools.
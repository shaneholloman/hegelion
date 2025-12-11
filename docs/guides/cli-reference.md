# CLI Reference

Command-line interface for quick checks and demos.

## Basic Commands

### Single Query

```bash
hegelion "Can AI be genuinely creative?"
```

### Demo Mode (No API Key)

```bash
hegelion --demo
```

### Output Formats

```bash
# Raw JSON (default)
hegelion "Your question" --format json

# Human-readable summary
hegelion "Your question" --format summary

# Rich terminal output with formatted panels
hegelion "Your question" --format rich
```

### Debug Output

```bash
hegelion "Your question" --debug --format json
```

## Additional Options

```bash
# Stream output in real-time as each phase is generated
hegelion "Your question" --stream

# Run in interactive mode for an exploratory session
hegelion "Your question" --interactive

# Save output to a file
hegelion "Your question" --output result.json
```

> **Note:** Phase 2 features like `use_council`, `use_judge`, and `use_search` are available via the Python API but not as CLI flags. Use the Python API for these advanced features.

## Benchmarking

Run analysis on multiple prompts from a JSONL file:

```bash
hegelion-bench prompts.jsonl --output results.jsonl --summary
```

### JSONL Format

Each line can be:

```jsonl
{"query": "Is consciousness fundamental?"}
{"prompt": "Can AI be creative?"}
"What was the impact of the printing press?"
```

### Options

```bash
hegelion-bench prompts.jsonl \
    --output results.jsonl \
    --summary \
    --debug
```

## MCP Server

Start the MCP server directly:

```bash
python -m hegelion.mcp.server
```

## Environment Variables

The CLI respects the same environment variables as the Python API:

```bash
export HEGELION_PROVIDER=anthropic
export HEGELION_MODEL=claude-4.5-sonnet-latest
export ANTHROPIC_API_KEY=your-key

hegelion "Your question"
```

Or use a `.env` file in the current directory.

## Output Processing

Results are JSONL format—one `HegelionResult` per line:

```bash
# Process with jq
hegelion "Your question" --format json | jq '.synthesis'

# Process with Python
hegelion-bench prompts.jsonl --output results.jsonl
python -c "import pandas as pd; df = pd.read_json('results.jsonl', lines=True)"
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error (missing API key, etc.) |

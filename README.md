# Hegelion

*“The truth is the whole. The whole, however, is merely the essential nature reaching its completeness through the process of its own development.”* — **G.W.F. Hegel**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg) [![PyPI version](https://badge.fury.io/py/hegelion.svg)](https://badge.fury.io/py/hegelion) [![Status](https://img.shields.io/badge/status-actively--maintained-brightgreen.svg)](https://github.com/Hmbown/Hegelion)

## TL;DR

- Wrap any LLM in a thesis → antithesis → synthesis loop
- Return structured JSON/workflows (agent-friendly), not just text
- Ship as an MCP server (`hegelion-server`) so Claude Desktop, Cursor, VS Code work with zero API keys

## Quickstart (MCP)

```bash
pip install hegelion
# latest-from-main (if PyPI lags): pip install git+https://github.com/Hmbown/Hegelion.git
# prefer venv/pipx if system Python is PEP 668 managed
# Optional helper: writes a ready-to-use MCP snippet for Cursor/Claude Desktop
hegelion-setup-mcp --write ~/.claude_desktop_config.json
python -m hegelion.mcp.server
```

In-process smoke test (no MCP client needed):
```bash
python examples/mcp/inprocess_check.py
```

Smoke-test with MCP Inspector:
```bash
npx -y @modelcontextprotocol/inspector python -m hegelion.mcp.server
```
- In the UI, call `initialize`, then `tools/list`, then `dialectical_workflow` with a query.

## Feature toggles

| Option | Default | What it does |
| --- | --- | --- |
| `use_search` | `false` | Adds search-grounding instructions. |
| `use_council` | `false` | Adds Logician/Empiricist/Ethicist critiques to Antithesis. |
| `use_judge` | `false` | Adds quality judge step. |
| `response_style` | `sections` | `sections` (full text), `synthesis_only` (just the resolution), `json` (structured). |

## Docs

- AI/agent quickstart: `AI_README.md`
- Human quickstart: `docs/QUICKSTART.md`
- MCP reference & common issues: `docs/MCP.md`
- Overview, examples, rationale: `docs/overview.md`
- Training/data details: `README_TRAINING.md`, `README_DATASET_GENERATION.md`

## Examples

- In-process smoke test: `python examples/mcp/inprocess_check.py`
- MCP config samples: `examples/mcp/*.json`
- More examples listed in `examples/mcp/README.md`

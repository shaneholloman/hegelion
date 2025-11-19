# CLI Removal Plan (Optional)

## Background

As of v0.3.0, the `hegelion` CLI is primarily a demo tool. Advanced features (personas, iterations, search grounding) are available via the Python API and MCP servers. This document outlines the optional steps to fully remove the CLI if desired.

## Rationale for Removal

- **Simplified Maintenance:** Reduces surface area for bugs and documentation updates.
- **Clearer Focus:** Emphasizes the two primary usage paths (MCP prompt server + Python API).
- **Test Reduction:** Removes CLI-specific test files that currently need maintenance.

## Steps to Remove CLI

### 1. Update `pyproject.toml`

Remove the CLI entry points:

```toml
[project.scripts]
# hegelion = "hegelion.scripts.hegelion_cli:main"  # REMOVE
# hegelion-bench = "hegelion.scripts.hegelion_bench:main"  # REMOVE
# hegelion-eval = "hegelion.scripts.hegelion_eval:main"  # REMOVE
hegelion-server = "hegelion.mcp_server:main"
hegelion-prompt-server = "hegelion.prompt_mcp_server:main"
```

### 2. Remove CLI Scripts

Delete the following files:

```bash
rm hegelion/scripts/hegelion_cli.py
rm hegelion/scripts/hegelion_bench.py
rm hegelion/scripts/hegelion_eval.py
```

### 3. Remove CLI Tests

Delete the following test files:

```bash
rm tests/test_cli.py
rm tests/test_bench_cli.py
rm tests/test_eval_cli.py
```

### 4. Update Documentation

- Remove CLI examples from `README.md` (Quick Start section)
- Update `docs/USER_GUIDE.md` to remove CLI usage section
- Update `CHANGELOG.md` to note CLI deprecation

### 5. Update Examples

Remove or update any example scripts that reference the CLI.

## If You Keep the CLI

If you decide to keep the CLI as-is:

- Document clearly that it's a demo/summary tool
- Do not implement advanced features in the CLI (keep them API-only)
- Consider adding a deprecation warning to the CLI help text

## Migration Guide for Users

For users currently using the CLI:

### Old (CLI):
```bash
hegelion "query" --format summary
```

### New (Python):
```python
import asyncio
from hegelion import run_dialectic

async def main():
    result = await run_dialectic("query")
    print(result.synthesis)

asyncio.run(main())
```

### Alternative (MCP):
Use the MCP prompt server in your editor/IDE for zero-configuration dialectical reasoning.


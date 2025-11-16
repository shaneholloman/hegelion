# Changelog

## 0.2.2 – MCP documentation and GLM backend verification

- Added comprehensive MCP reference guide (`docs/MCP.md`) with tool schemas, troubleshooting, and client integration notes
- Added Claude Desktop configuration example (`examples/mcp/claude_desktop_config.json`)
- Verified GLM 4.6 backend via OpenAI-compatible endpoint (Z.AI devpack)
- Enhanced documentation with verified backends section and log-sharing guidance
- Improved README with MCP quick start and backend verification details
- Fixed package discovery in `pyproject.toml` to exclude `logs/` directory from builds

## 0.2.1 – License format fix

- Fixed deprecated license format in `pyproject.toml` (changed from table to SPDX string format)
- Removed deprecated license classifier

## 0.2.0 – First public release

- Refactored into a clean `hegelion` Python package with clear module boundaries (core, engine, backends, parsing, models, prompts, config, MCP server).
- Introduced `HegelionResult` with structured contradictions, research proposals, and provenance metadata.
- Added CLI tools: `hegelion` for single queries and `hegelion-bench` for JSONL benchmarks.
- Implemented MCP server (`hegelion-server`) exposing `run_dialectic` and `run_benchmark` tools.
- Wrote comprehensive README and `HEGELION_SPEC.md` describing the protocol and JSON schema.
- Added test suite, pre-commit hooks, and GitHub Actions CI for automated testing.


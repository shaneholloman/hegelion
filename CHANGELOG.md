# Changelog

## 0.2.0 – First public release

- Refactored into a clean `hegelion` Python package with clear module boundaries (core, engine, backends, parsing, models, prompts, config, MCP server).
- Introduced `HegelionResult` with structured contradictions, research proposals, and provenance metadata.
- Added CLI tools: `hegelion` for single queries and `hegelion-bench` for JSONL benchmarks.
- Implemented MCP server (`hegelion-server`) exposing `run_dialectic` and `run_benchmark` tools.
- Wrote comprehensive README and `HEGELION_SPEC.md` describing the protocol and JSON schema.
- Added test suite, pre-commit hooks, and GitHub Actions CI for automated testing.


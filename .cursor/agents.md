## Hegelion Maintainer Agent

You are an AI assistant working inside the `Hegelion` repository. Your job is to help maintain and extend a **dialectical reasoning harness for LLMs** that runs queries through **Thesis → Antithesis → Synthesis**, extracts **multiple structured contradictions**, and uses an internal **conflict judge** in debug mode.

### Project Overview

- **Core idea**: For a given query, generate a rich `HegelionResult`:
  - `thesis`: comprehensive, multi-perspective position.
  - `antithesis`: adversarial critique that surfaces **multiple CONTRADICTION/EVIDENCE pairs**.
  - `synthesis`: higher-level resolution plus optional **RESEARCH_PROPOSAL/TESTABLE_PREDICTION** entries.
- **Internal judge**: The engine computes an **internal conflict score** by combining:
  - Embedding-based semantic distance between thesis and antithesis.
  - The number of extracted contradictions.
  - An LLM-based **“disagreement classifier”** that rates how strongly the antithesis opposes the thesis.
  - This score lives under `metadata.debug.internal_conflict_score` and is **debug/research-only**.

### How to Use the Tooling

- **CLI (single query & REPL)**:
  - `uv run hegelion --demo` – show a cached example without any API keys.
  - `uv run hegelion "Can AI be genuinely creative?" --format summary`
  - `uv run hegelion --interactive` – REPL with commands like `show thesis`, `show antithesis`, `set model claude-4.5-sonnet`, etc.
- **Benchmarks & evaluation**:
  - `uv run hegelion-bench benchmarks/examples_basic.jsonl --output runs.jsonl --summary`
  - `uv run hegelion-eval runs_model_a.jsonl runs_model_b.jsonl --output report.md`
- **Python API**:
  - Prefer `quickstart` / `dialectic` from `hegelion.core` for new code.
  - Always return or log the full `HegelionResult` so downstream tools can use contradictions and research proposals.
- **MCP server**:
  - `uv run hegelion-server` or `uv run python -m hegelion.mcp_server`
  - Tools: `run_dialectic` (single query) and `run_benchmark` (JSONL prompts).

### Environment & Safety

- Never hardcode API keys. Use `.env`:
  - `cp .env.example .env` and edit locally.
  - `.env` is git-ignored; do not leak secrets in code, tests, or docs.
- When sharing logs, follow `docs/USER_GUIDE.md`:
  - Keep raw traces under `logs/` (git-ignored).
  - Sanitize JSON with `jq` before attaching to issues.
- Prefer **Anthropic** or other configured backends, but treat provider wiring as pluggable:
  - Respect `HEGELION_PROVIDER`, `HEGELION_MODEL`, and related keys.

### Development Workflow Expectations

- Use `uv` when possible:
  - `uv sync` to install.
  - `uv run pytest` before and after significant changes.
- When modifying the dialectical flow (prompts, parsing, engine):
  - Keep the **three-phase structure** intact.
  - Preserve structured **contradictions** and **research proposals**.
  - Keep conflict scores **internal** (debug-only) and do not expose them as core API outputs.
- When changing CLI or MCP behavior:
  - Ensure `tests/` still pass and update docs (`README.md`, `docs/MCP.md`, `docs/USER_GUIDE.md`) to match the true behavior.

### How to Think While Editing

- Default to **dialectical reasoning** when making non-trivial changes:
  - Form a **thesis** (proposed design or change).
  - Sketch an **antithesis** (risks, edge cases, regressions, user confusion).
  - Aim for a **synthesis** (refined design that resolves the tension).
- Use Hegelion itself (CLI or Python API) to stress-test tricky design decisions or to generate example traces for docs and tests.



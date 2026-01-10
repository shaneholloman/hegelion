# Launch Checklist

- [x] Ruff lint clean (`uv run ruff check .`).
- [x] Ruff formatting applied (`uv run ruff format .`).
- [x] Full test suite passing (`uv run pytest -v`).
- [x] MCP server self-test passing (`uv run hegelion-server --self-test`).
- [x] CLI help output verified (`hegelion-server --help`, `hegelion-setup-mcp --help`).
- [x] MCP host shortcut verified with temp config (`hegelion-setup-mcp --host claude-desktop`).
- [x] Docs aligned with COACH APPROVED wording and updated metadata/UX notes.

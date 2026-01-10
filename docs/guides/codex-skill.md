# Codex Skill

This repo includes a Codex skill at `skills/hegelion-prompts/` for prompt-driven use without MCP.

## When to use it

Use the skill when you want Hegelion's dialectical reasoning or autocoding workflows inside Codex or other agent environments that do not support MCP tools.

## What it covers

- Dialectical prompts via `hegelion.core.prompt_dialectic`
- Autocoding player/coach prompts via `hegelion.core.prompt_autocoding`
- Guidance on when to use MCP tools versus local prompt generation

If your host supports MCP, prefer the MCP server for typed tools and structured outputs.

## Installing the skill

- Claude Code: copy or symlink `skills/hegelion-prompts/` into `~/.claude/skills/` or `.claude/skills/` in a repo.
- Codex-style skill bundles: a packaged file is available at `dist/hegelion-prompts.skill`.

Example (Claude Code, personal):

```bash
mkdir -p ~/.claude/skills
cp -R skills/hegelion-prompts ~/.claude/skills/
```

Example (Claude Code, project):

```bash
mkdir -p .claude/skills
cp -R skills/hegelion-prompts .claude/skills/
```

## Claude Code skill conventions

Claude Code uses the same `SKILL.md` format with YAML frontmatter. Key conventions from the official docs:

- Skill folders live at `~/.claude/skills/` (personal) or `.claude/skills/` (project).
- `SKILL.md` must include `name` and `description` in YAML frontmatter.
- `name` must be lowercase letters, numbers, and hyphens only (max 64 chars) and match the folder name.
- Optional fields include `allowed-tools`, `model`, `context`, `agent`, `hooks`, and `user-invocable`.
- Keep `SKILL.md` under ~500 lines and use progressive disclosure for large references.

For details, see `https://code.claude.com/docs/en/skills`.

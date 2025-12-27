"""Hegelion MCP Setup Logic and CLI helper."""

import sys
import json
import site
from pathlib import Path
import hegelion


USAGE_NOTE = """
Hegelion MCP setup
------------------
Use this helper to generate the MCP snippet for MCP hosts like Cursor, Claude Desktop,
VS Code + Copilot, Windsurf, or Gemini CLI.

Examples:
  hegelion-setup-mcp                # print JSON snippet
  hegelion-setup-mcp --write        # write to ./mcp_config.json
  hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"  # macOS Claude Desktop
  hegelion-setup-mcp --write "%APPDATA%\\Claude\\claude_desktop_config.json"  # Windows Claude Desktop

Note: After modifying the config, restart your MCP host for changes to take effect.
"""


def get_python_path():
    """Get the absolute path to the current python interpreter."""
    return sys.executable


def is_installed_in_site_packages():
    """Check if hegelion is installed in site-packages."""
    package_path = Path(hegelion.__file__).parent
    for site_package in site.getsitepackages():
        if str(package_path).startswith(site_package):
            return True
    # Also check user site packages
    if site.getusersitepackages() and str(package_path).startswith(site.getusersitepackages()):
        return True
    return False


def get_project_root():
    """Get the absolute path to the project root (if running from source)."""
    return Path(hegelion.__file__).parent.parent.absolute()


def generate_config(python_path, project_root, is_installed):
    """Generate the MCP config."""

    env = {}
    if not is_installed:
        # If not installed in site-packages, we likely need PYTHONPATH
        env["PYTHONPATH"] = str(project_root)

    config = {
        "mcpServers": {
            "hegelion": {
                "command": python_path,
                "args": ["-m", "hegelion.mcp.server"],
            },
        }
    }

    if env:
        config["mcpServers"]["hegelion"]["env"] = env

    return config


def print_setup_instructions(dry_run=False):
    python_path = get_python_path()
    is_installed = is_installed_in_site_packages()
    project_root = get_project_root()

    config = generate_config(python_path, project_root, is_installed)

    snippet = config["mcpServers"]
    json_output = json.dumps(snippet, indent=2)

    print("\n" + "=" * 60)
    print("MCP CONFIGURATION SNIPPET")
    print("=" * 60)
    print("Copy the snippet below into your MCP configuration file for your host:")
    print("-" * 60)
    print(json_output)
    print("-" * 60)

    print(
        "Tools available: dialectical_* (workflow/single_shot/thesis/antithesis/synthesis) "
        "and autocoding_* (init/workflow/player/coach/advance/single_shot/save/load)"
    )
    print("response_style options: json, sections, synthesis_only, conversational, bullet_points")
    print("\nCommon config paths:")
    print("  macOS Claude Desktop: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("  Windows Claude Desktop: %APPDATA%\\Claude\\claude_desktop_config.json")
    print("  Claude Code:          ~/.claude.json")
    print("  Cursor (macOS/Linux): ~/.cursor/mcp_config.json")
    print("  Cursor (Windows):     %APPDATA%\\Cursor\\User\\globalStorage\\mcp_config.json")
    print("  VS Code + Copilot:    .vscode/mcp.json")
    print("  Windsurf:             ~/.codeium/windsurf/mcp_config.json")
    print("\n⚠️  Restart Required: Restart your MCP host after modifying the config.")

    if not is_installed:
        print(f"\nNOTE: Detected source installation at {project_root}")
        print("Added PYTHONPATH to ensure the server runs correctly.")
    else:
        print("\nNOTE: Detected installed package.")


def _write_config(target: Path, snippet: dict) -> None:
    target = target.expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        existing = {}
        try:
            existing = json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
        merged = existing.get("mcpServers", {})
        merged.update(snippet)
        payload = {"mcpServers": merged, **{k: v for k, v in existing.items() if k != "mcpServers"}}
    else:
        payload = {"mcpServers": snippet}
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote MCP config to {target}")


def main(argv=None):  # pragma: no cover - lightweight CLI
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate MCP config for Hegelion", epilog=USAGE_NOTE
    )
    parser.add_argument(
        "--write",
        nargs="?",
        const="mcp_config.json",
        help="Write to path (default: mcp_config.json in CWD)",
    )
    args = parser.parse_args(argv)

    python_path = get_python_path()
    is_installed = is_installed_in_site_packages()
    project_root = get_project_root()
    config = generate_config(python_path, project_root, is_installed)
    snippet = config["mcpServers"]

    if args.write:
        _write_config(Path(args.write), snippet)
    else:
        print_setup_instructions()


if __name__ == "__main__":
    main()

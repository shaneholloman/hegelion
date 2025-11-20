#!/usr/bin/env python3
"""
Hegelion MCP Setup Script

This script automatically generates the correct configuration files for running
Hegelion as an MCP server in Cursor, Claude Desktop, and other environments.

It detects the current Python interpreter to ensure paths are absolute and correct.
"""

import sys
import json
from pathlib import Path
import argparse


def get_python_path():
    """Get the absolute path to the current python interpreter."""
    return sys.executable


def get_project_root():
    """Get the absolute path to the project root."""
    # Assuming this script is in scripts/setup_mcp.py
    return Path(__file__).parent.parent.absolute()


def check_installation():
    """Verify that hegelion can be imported."""
    try:
        import importlib.util

        return importlib.util.find_spec("hegelion") is not None
    except ImportError:
        return False


def generate_cursor_config(python_path, project_root):
    """Generate the mcp_config.json for Cursor."""
    config = {
        "mcpServers": {
            "hegelion": {
                "command": python_path,
                "args": ["-m", "hegelion.prompt_mcp_server"],
                "env": {"PYTHONPATH": str(project_root)},
            },
            "hegelion-backend": {
                "command": python_path,
                "args": ["-m", "hegelion.mcp_server"],
                "env": {
                    "PYTHONPATH": str(project_root),
                    # "HEGELION_PROVIDER": "anthropic",
                    # "ANTHROPIC_API_KEY": "..."
                },
            },
        }
    }
    return config


def generate_claude_config(python_path, project_root):
    """Generate a snippet for claude_desktop_config.json."""
    config = {
        "mcpServers": {
            "hegelion-prompt": {
                "command": python_path,
                "args": ["-m", "hegelion.prompt_mcp_server"],
                "env": {"PYTHONPATH": str(project_root)},
            }
        }
    }
    return config


def main():
    parser = argparse.ArgumentParser(description="Setup Hegelion MCP configuration")
    parser.add_argument(
        "--cursor", action="store_true", default=True, help="Generate mcp_config.json for Cursor"
    )
    parser.add_argument("--dry-run", action="store_true", help="Print config to stdout only")
    args = parser.parse_args()

    python_path = get_python_path()
    project_root = get_project_root()

    print(f"Detected Python: {python_path}")
    print(f"Detected Project Root: {project_root}")
    print("-" * 40)

    # Check installation
    if not check_installation():
        print("❌ WARNING: 'hegelion' package not found in this python environment.")
        print(f"   Please run: {python_path} -m pip install -e .")
        print("   (Or install it via uv/poetry if using those tools)")
        print("-" * 40)

    # Generate Cursor Config
    cursor_config = generate_cursor_config(python_path, project_root)
    cursor_config_path = project_root / "mcp_config.json"

    if args.dry_run:
        print("\n[DRY RUN] Content for mcp_config.json:")
        print(json.dumps(cursor_config, indent=2))
    else:
        with open(cursor_config_path, "w") as f:
            json.dump(cursor_config, f, indent=2)
        print(f"✅ Wrote local config to: {cursor_config_path}")

    # Print Copy-Paste Snippets
    print("\n" + "=" * 60)
    print("GLOBAL CONFIGURATION (RECOMMENDED)")
    print("=" * 60)
    print("If the tools do not appear, copy the snippet below into your")
    print("Cursor 'Global MCP Settings' or 'claude_desktop_config.json':\n")

    snippet = cursor_config["mcpServers"]
    print(json.dumps(snippet, indent=2))
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

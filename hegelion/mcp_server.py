"""MCP server wiring for Hegelion."""

from __future__ import annotations

import asyncio
import json

from mcp.server import Server
from mcp.types import TextContent, Tool

import mcp.server.stdio

from .core import run_dialectic, run_benchmark

app = Server("hegelion-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return the single dialectical reasoning tool exposed by the server."""

    return [
        Tool(
            name="run_dialectic",
            description=(
                "Process a query using Hegelian dialectical reasoning "
                "(thesis → antithesis → synthesis). "
                "Always performs synthesis to generate comprehensive reasoning. "
                "Returns structured contradictions and research proposals."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question or topic to analyze dialectically",
                    },
                    "debug": {
                        "type": "boolean",
                        "description": "Include debug information and internal conflict scores",
                        "default": False,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="run_benchmark",
            description=(
                "Run Hegelion on multiple prompts from a JSONL file. "
                "Each line should contain a JSON object with a 'prompt' or 'query' field. "
                "Returns newline-delimited JSON, one HegelionResult per line."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "prompts_file": {
                        "type": "string",
                        "description": "Path to JSONL file containing prompts (one per line)",
                    },
                    "debug": {
                        "type": "boolean",
                        "description": "Include debug information and internal conflict scores",
                        "default": False,
                    },
                },
                "required": ["prompts_file"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute Hegelion tools."""

    if name == "run_dialectic":
        query = arguments["query"]
        debug = arguments.get("debug", False)

        result = await run_dialectic(query=query, debug=debug)
        payload = json.dumps(result.to_dict(), indent=2)
        return [TextContent(type="text", text=payload)]

    elif name == "run_benchmark":
        from pathlib import Path

        prompts_file = Path(arguments["prompts_file"])
        debug = arguments.get("debug", False)

        if not prompts_file.exists():
            raise ValueError(f"Prompts file not found: {prompts_file}")

        results = await run_benchmark(prompts_file, debug=debug)

        # Format results as JSONL
        lines = [json.dumps(result.to_dict(), ensure_ascii=False) for result in results]
        payload = "\n".join(lines)

        return [TextContent(type="text", text=payload)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    """Run the MCP stdio server."""

    from mcp.server.stdio import stdio_server

    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options(),
        )


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    asyncio.run(main())

# Expose decorated handlers on the app instance for test convenience
# These wrappers allow awaiting app.list_tools() and app.call_tool(name=..., arguments=...)
# in a way that is independent of the underlying MCP server implementation details.
app.list_tools = list_tools  # type: ignore[attr-defined]
app.call_tool = call_tool  # type: ignore[attr-defined]

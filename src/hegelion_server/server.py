"""MCP server wiring for Hegelion."""

from __future__ import annotations

import asyncio
import json

from mcp.server import Server
from mcp.types import TextContent, Tool

import mcp.server.stdio

from .config import get_backend_from_env, get_engine_settings_from_env
from .dialectics import HegelionEngine

app = Server("hegelion-server")

backend = get_backend_from_env()
settings = get_engine_settings_from_env()
engine = HegelionEngine(
    backend=backend,
    model=settings.model,
    synthesis_threshold=settings.synthesis_threshold,
    max_tokens_per_phase=settings.max_tokens_per_phase,
)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return the single dialectical reasoning tool exposed by the server."""

    return [
        Tool(
            name="hegelion_query",
            description=(
                "Process a query using Hegelian dialectical reasoning "
                "(thesis → antithesis → synthesis). "
                "Use this to expose contradictions, gauge conflict, "
                "and surface novel synthesis proposals."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question or topic to analyze dialectically",
                    },
                    "synthesis_threshold": {
                        "type": "number",
                        "description": (
                            "Conflict score threshold for triggering synthesis "
                            "(0–1, default 0.85)"
                        ),
                        "default": 0.85,
                    },
                    "max_iterations": {
                        "type": "number",
                        "description": "Maximum dialectical cycles (default 1)",
                        "default": 1,
                    },
                },
                "required": ["query"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute the hegelion_query tool."""

    if name != "hegelion_query":
        raise ValueError(f"Unknown tool: {name}")

    query = arguments["query"]
    synthesis_threshold = float(arguments.get("synthesis_threshold", engine.synthesis_threshold))
    max_iterations = int(arguments.get("max_iterations", 1))

    engine.synthesis_threshold = synthesis_threshold

    result = await engine.process_query(query=query, max_iterations=max_iterations)
    payload = json.dumps(result.model_dump(), indent=2)

    return [TextContent(type="text", text=payload)]


async def main() -> None:
    """Run the MCP stdio server."""

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    asyncio.run(main())

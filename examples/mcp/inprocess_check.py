"""In-process smoke test for the Hegelion MCP server.

This runs entirely in Python (no MCP client needed) and exercises the tool
registration plus JSON-friendly `response_style` options.

Usage:
    python examples/mcp/inprocess_check.py
"""

import asyncio
import json

from hegelion.mcp import server


async def main() -> None:
    tools = await server.list_tools()
    print("Tools registered:", [t.name for t in tools])

    contents, structured = await server.call_tool(
        "dialectical_workflow",
        {"query": "test query", "response_style": "json"},
    )

    print("\nHuman-readable output:\n", contents[0].text[:200], "...")
    print("\nStructuredContent JSON:\n", json.dumps(structured, indent=2)[:500], "...")


if __name__ == "__main__":
    asyncio.run(main())

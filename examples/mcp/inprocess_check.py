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

    print("\nTesting response styles on dialectical_single_shot:")
    for style in ["conversational", "bullet_points", "json", "sections", "synthesis_only"]:
        contents, structured = await server.call_tool(
            "dialectical_single_shot",
            {"query": "test query", "response_style": style},
        )
        print(f"✅ response_style='{style}' -> content_len={len(contents)}")
        if style == "json":
            print("StructuredContent keys:", list(structured.keys()))

    contents, structured = await server.call_tool(
        "dialectical_workflow",
        {"query": "test query", "response_style": "json"},
    )

    print("\nWorkflow StructuredContent JSON:\n", json.dumps(structured, indent=2)[:500], "...")


if __name__ == "__main__":
    asyncio.run(main())

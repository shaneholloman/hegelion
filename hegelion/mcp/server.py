"""Model-agnostic MCP server for dialectical reasoning.

This version works with whatever LLM is calling the MCP server,
rather than making its own API calls. Perfect for Cursor, Claude Desktop,
VS Code, or any MCP-compatible environment.
"""

from __future__ import annotations

import asyncio
import argparse
import json
import sys

from mcp.server import Server
from mcp.types import TextContent, Tool
import anyio

from hegelion.core.prompt_dialectic import (
    create_dialectical_workflow,
    create_single_shot_dialectic_prompt,
)

app = Server("hegelion-server")

# Compatibility: older anyio versions expose create_memory_object_stream as a plain function
# which cannot be subscripted (newer typing style uses subscripting). Patch a lightweight
# wrapper so the MCP server session setup does not crash when subscripting is attempted.
if not hasattr(anyio.create_memory_object_stream, "__getitem__"):
    _create_stream = anyio.create_memory_object_stream

    class _CreateStreamWrapper:
        def __call__(self, *args, **kwargs):
            return _create_stream(*args, **kwargs)

        def __getitem__(self, _):
            return self

    anyio.create_memory_object_stream = _CreateStreamWrapper()  # type: ignore[assignment]


async def list_tools() -> list[Tool]:
    """Return dialectical reasoning tools that work with any LLM."""
    tools = [
        Tool(
            name="dialectical_workflow",
            description=(
                "Generate a structured dialectical reasoning workflow (thesis → antithesis → synthesis) "
                "that can be executed by any LLM. Returns step-by-step prompts instead of making API calls. "
                "Perfect for Cursor, Claude Desktop, VS Code, or any environment where you want the "
                "current LLM to perform the reasoning."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question or topic to analyze dialectically",
                    },
                    "use_search": {
                        "type": "boolean",
                        "description": "Include instructions to use search tools for real-world grounding",
                        "default": False,
                    },
                    "use_council": {
                        "type": "boolean",
                        "description": "Enable multi-perspective council critiques (Logician, Empiricist, Ethicist)",
                        "default": False,
                    },
                    "use_judge": {
                        "type": "boolean",
                        "description": "Include quality evaluation step",
                        "default": False,
                    },
                    "format": {
                        "type": "string",
                        "enum": ["workflow", "single_prompt"],
                        "description": "Return structured workflow or single comprehensive prompt",
                        "default": "workflow",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="dialectical_single_shot",
            description=(
                "Generate a single comprehensive prompt for dialectical reasoning that can be "
                "executed by any capable LLM in one go. The LLM performs thesis → antithesis → synthesis "
                "and returns structured results. Great for any powerful model with large context."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question or topic to analyze dialectically",
                    },
                    "use_search": {
                        "type": "boolean",
                        "description": "Include instructions to use search tools",
                        "default": False,
                    },
                    "use_council": {
                        "type": "boolean",
                        "description": "Enable multi-perspective council critiques",
                        "default": False,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="thesis_prompt",
            description=(
                "Generate just the thesis prompt for dialectical reasoning. "
                "Use this when you want to execute dialectical reasoning step-by-step."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question or topic to analyze dialectically",
                    }
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="antithesis_prompt",
            description=(
                "Generate the antithesis prompt for dialectical reasoning. "
                "Requires the thesis output from a previous step."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The original question or topic",
                    },
                    "thesis": {
                        "type": "string",
                        "description": "The thesis output to critique",
                    },
                    "use_search": {
                        "type": "boolean",
                        "description": "Include instructions to use search tools",
                        "default": False,
                    },
                    "use_council": {
                        "type": "boolean",
                        "description": "Use council-based multi-perspective critique",
                        "default": False,
                    },
                },
                "required": ["query", "thesis"],
            },
        ),
        Tool(
            name="synthesis_prompt",
            description=(
                "Generate the synthesis prompt for dialectical reasoning. "
                "Requires thesis and antithesis outputs from previous steps."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The original question or topic",
                    },
                    "thesis": {
                        "type": "string",
                        "description": "The thesis output",
                    },
                    "antithesis": {
                        "type": "string",
                        "description": "The antithesis critique output",
                    },
                },
                "required": ["query", "thesis", "antithesis"],
            },
        ),
    ]
    return tools


async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute dialectical reasoning tools."""

    if name == "dialectical_workflow":
        query = arguments["query"]
        use_search = arguments.get("use_search", False)
        use_council = arguments.get("use_council", False)
        use_judge = arguments.get("use_judge", False)
        format_type = arguments.get("format", "workflow")

        if format_type == "single_prompt":
            prompt = create_single_shot_dialectic_prompt(
                query=query, use_search=use_search, use_council=use_council
            )
            return [TextContent(type="text", text=prompt)]
        else:
            workflow = create_dialectical_workflow(
                query=query,
                use_search=use_search,
                use_council=use_council,
                use_judge=use_judge,
            )
            return [TextContent(type="text", text=json.dumps(workflow, indent=2))]

    elif name == "dialectical_single_shot":
        query = arguments["query"]
        use_search = arguments.get("use_search", False)
        use_council = arguments.get("use_council", False)

        prompt = create_single_shot_dialectic_prompt(
            query=query, use_search=use_search, use_council=use_council
        )
        return [TextContent(type="text", text=prompt)]

    elif name == "thesis_prompt":
        from hegelion.core.prompt_dialectic import PromptDrivenDialectic

        query = arguments["query"]
        dialectic = PromptDrivenDialectic()
        prompt_obj = dialectic.generate_thesis_prompt(query)

        response = f"""# THESIS PROMPT

{prompt_obj.prompt}

**Instructions:** {prompt_obj.instructions}
**Expected Format:** {prompt_obj.expected_format}"""

        return [TextContent(type="text", text=response)]

    elif name == "antithesis_prompt":
        from hegelion.core.prompt_dialectic import PromptDrivenDialectic

        query = arguments["query"]
        thesis = arguments["thesis"]
        use_search = arguments.get("use_search", False)
        use_council = arguments.get("use_council", False)

        dialectic = PromptDrivenDialectic()

        if use_council:
            council_prompts = dialectic.generate_council_prompts(query, thesis)
            response_parts = ["# COUNCIL ANTITHESIS PROMPTS\n"]

            for prompt_obj in council_prompts:
                response_parts.append(f"## {prompt_obj.phase.replace('_', ' ').title()}")
                response_parts.append(prompt_obj.prompt)
                response_parts.append(f"**Instructions:** {prompt_obj.instructions}")
                response_parts.append("")

            response = "\n".join(response_parts)
        else:
            prompt_obj = dialectic.generate_antithesis_prompt(query, thesis, use_search)
            response = f"""# ANTITHESIS PROMPT

{prompt_obj.prompt}

**Instructions:** {prompt_obj.instructions}
**Expected Format:** {prompt_obj.expected_format}"""

        return [TextContent(type="text", text=response)]

    elif name == "synthesis_prompt":
        from hegelion.core.prompt_dialectic import PromptDrivenDialectic

        query = arguments["query"]
        thesis = arguments["thesis"]
        antithesis = arguments["antithesis"]

        dialectic = PromptDrivenDialectic()
        prompt_obj = dialectic.generate_synthesis_prompt(query, thesis, antithesis)

        response = f"""# SYNTHESIS PROMPT

{prompt_obj.prompt}

**Instructions:** {prompt_obj.instructions}
**Expected Format:** {prompt_obj.expected_format}"""

        return [TextContent(type="text", text=response)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def run_server() -> None:
    """Run the prompt-driven MCP server.

    Uses a lightweight JSON-RPC loop that supports both Content-Length framed
    messages (MCP stdio clients) and newline-delimited JSON (test harnesses).
    """

    async def _simple_stdio_loop():
        """Minimal line-based JSON-RPC loop for compatibility and tests."""

        def _read_message():
            # Support both Content-Length framed messages and newline-delimited JSON.
            line = sys.stdin.readline()
            if not line:
                return None, False
            stripped = line.strip()
            if stripped.lower().startswith("content-length"):
                try:
                    length = int(stripped.split(":", 1)[1].strip())
                except (ValueError, IndexError):
                    return None, False
                # Consume blank separator line
                sys.stdin.readline()
                payload = sys.stdin.read(length)
                return payload, True
            return stripped, False

        async def _write_message(payload: dict, framed: bool) -> None:
            data = json.dumps(payload)
            if framed:
                encoded = data.encode("utf-8")
                sys.stdout.write(f"Content-Length: {len(encoded)}\r\n\r\n")
                sys.stdout.buffer.write(encoded)
            else:
                sys.stdout.write(data + "\n")
            sys.stdout.flush()

        while True:
            raw, framed = await asyncio.to_thread(_read_message)
            if raw is None:
                break
            if not raw:
                continue
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                continue

            method = message.get("method")
            # Notifications have no id, so we should not respond
            if "id" not in message:
                # If it's a notification we care about, handle it here
                # e.g. notifications/initialized or cancel
                continue

            msg_id = message["id"]
            params = message.get("params", {}) or {}
            response: dict = {"jsonrpc": "2.0", "id": msg_id}

            if method == "initialize":
                init_options = app.create_initialization_options()
                # Match JSON-RPC shape expected by MCP clients/tests.
                capabilities = (
                    init_options.capabilities.model_dump(mode="json")
                    if hasattr(init_options.capabilities, "model_dump")
                    else init_options.capabilities
                )
                response["result"] = {
                    "serverInfo": {
                        "name": getattr(init_options, "server_name", "hegelion-server"),
                        "version": getattr(init_options, "server_version", "unknown"),
                    },
                    "capabilities": capabilities,
                }
            elif method == "tools/list":
                tools = await list_tools()
                response["result"] = {"tools": [tool.model_dump() for tool in tools]}
            elif method == "tools/call":
                name = params.get("name")
                arguments = params.get("arguments", {})
                contents = await call_tool(name=name, arguments=arguments)
                # The MCP spec wraps tool outputs in a list of contents
                response["result"] = {
                    "content": [content.model_dump() for content in contents],
                    "isError": False,
                }
            else:
                response["error"] = {"code": -32601, "message": f"Method not found: {method}"}

            await _write_message(response, framed)

    await _simple_stdio_loop()


def main() -> None:
    """Main entry point for the prompt-driven MCP server."""
    parser = argparse.ArgumentParser(
        description="Hegelion Prompt-Driven MCP Server - Works with any LLM",
        add_help=True,
    )
    # Remove the redundant --help argument
    parser.parse_args()

    asyncio.run(run_server())


if __name__ == "__main__":
    main()

# Expose decorated handlers on the app instance for test convenience
app.list_tools = list_tools  # type: ignore[attr-defined]
app.call_tool = call_tool  # type: ignore[attr-defined]

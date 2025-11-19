"""Model-agnostic MCP server for dialectical reasoning.

This version works with whatever LLM is calling the MCP server,
rather than making its own API calls. Perfect for Cursor, Claude Desktop,
VS Code, or any MCP-compatible environment.
"""

from __future__ import annotations

import asyncio
import argparse
import json

from mcp.server import Server
from mcp.types import TextContent, Tool

from .prompt_dialectic import (
    create_dialectical_workflow,
    create_single_shot_dialectic_prompt,
)

app = Server("hegelion-prompt-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return dialectical reasoning tools that work with any LLM."""

    return [
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
                "and returns structured results. Great for powerful models like Gemini 3, Claude 3.5, etc."
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


@app.call_tool()
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
        from .prompt_dialectic import PromptDrivenDialectic

        query = arguments["query"]
        dialectic = PromptDrivenDialectic()
        prompt_obj = dialectic.generate_thesis_prompt(query)

        response = f"""# THESIS PROMPT

{prompt_obj.prompt}

**Instructions:** {prompt_obj.instructions}
**Expected Format:** {prompt_obj.expected_format}"""

        return [TextContent(type="text", text=response)]

    elif name == "antithesis_prompt":
        from .prompt_dialectic import PromptDrivenDialectic

        query = arguments["query"]
        thesis = arguments["thesis"]
        use_search = arguments.get("use_search", False)
        use_council = arguments.get("use_council", False)

        dialectic = PromptDrivenDialectic()

        if use_council:
            council_prompts = dialectic.generate_council_prompts(query, thesis)
            response_parts = ["# COUNCIL ANTITHESIS PROMPTS\n"]

            for prompt_obj in council_prompts:
                response_parts.append(
                    f"## {prompt_obj.phase.replace('_', ' ').title()}"
                )
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
        from .prompt_dialectic import PromptDrivenDialectic

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
    """Run the prompt-driven MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


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

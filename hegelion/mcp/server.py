"""Model-agnostic MCP server for dialectical reasoning.

This version works with whatever LLM is calling the MCP server,
rather than making its own API calls. Perfect for Cursor, Claude Desktop,
VS Code, or any MCP-compatible environment.
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent, Tool
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


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return dialectical reasoning tools that work with any LLM."""
    tools = [
        Tool(
            name="dialectical_workflow",
            description=(
                "Step-by-step prompts for dialectical reasoning (thesis → antithesis → synthesis). "
                "Set response_style to control output: 'json' (structured, agent-friendly), "
                "'sections' (full text), or 'synthesis_only' (just the resolution). "
                "Example: {'query': 'Should AI be regulated?', 'response_style': 'json'}."
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
                    "response_style": {
                        "type": "string",
                        "enum": [
                            "sections",
                            "synthesis_only",
                            "json",
                        ],
                        "description": (
                            "Shape of the final output you want from the LLM: full thesis/antithesis/synthesis sections,"
                            " synthesis-only, or JSON with all fields."
                        ),
                        "default": "sections",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="dialectical_single_shot",
            description=(
                "One comprehensive prompt that makes the LLM do thesis → antithesis → synthesis in one go. "
                "Use response_style: 'json' (structured), 'sections' (full text), or 'synthesis_only' (just the resolution)."
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
                    "response_style": {
                        "type": "string",
                        "enum": [
                            "sections",
                            "synthesis_only",
                            "json",
                        ],
                        "description": (
                            "Format you want the model to return: full sections, synthesis-only, or JSON with thesis/antithesis/synthesis."
                        ),
                        "default": "sections",
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


def _response_style_summary(style: str) -> str:
    """Short human-readable description of response style."""
    match style:
        case "json":
            return "LLM should return a JSON object with thesis/antithesis/synthesis fields."
        case "synthesis_only":
            return "LLM should only return the synthesis (no thesis/antithesis sections)."
        case _:
            return "LLM should return full Thesis → Antithesis → Synthesis sections."


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]):
    """Execute dialectical reasoning tools."""

    if name == "dialectical_workflow":
        query = arguments["query"]
        use_search = arguments.get("use_search", False)
        use_council = arguments.get("use_council", False)
        use_judge = arguments.get("use_judge", False)
        format_type = arguments.get("format", "workflow")
        response_style = arguments.get("response_style", "sections")

        if format_type == "single_prompt":
            prompt = create_single_shot_dialectic_prompt(
                query=query,
                use_search=use_search,
                use_council=use_council,
                response_style=response_style,
            )
            structured = {
                "query": query,
                "format": "single_prompt",
                "use_search": use_search,
                "use_council": use_council,
                "response_style": response_style,
                "prompt": prompt,
            }
            return ([TextContent(type="text", text=prompt)], structured)
        else:
            workflow = create_dialectical_workflow(
                query=query,
                use_search=use_search,
                use_council=use_council,
                use_judge=use_judge,
            )
            workflow.setdefault("instructions", {})
            workflow["instructions"]["response_style"] = response_style
            workflow["instructions"]["response_style_note"] = _response_style_summary(
                response_style
            )

            serialized = json.dumps(workflow, indent=2)
            summary = (
                "Hegelion dialectical workflow ready. Agents should read the structuredContent JSON. "
                f"Human-readable summary: query='{query}', response_style='{response_style}'."
            )
            contents: List[TextContent] = [
                TextContent(type="text", text=summary),
                TextContent(type="text", text=serialized),
            ]
            return (contents, workflow)

    elif name == "dialectical_single_shot":
        query = arguments["query"]
        use_search = arguments.get("use_search", False)
        use_council = arguments.get("use_council", False)

        response_style = arguments.get("response_style", "sections")
        prompt = create_single_shot_dialectic_prompt(
            query=query,
            use_search=use_search,
            use_council=use_council,
            response_style=response_style,
        )

        structured = {
            "query": query,
            "use_search": use_search,
            "use_council": use_council,
            "response_style": response_style,
            "prompt": prompt,
        }
        note = _response_style_summary(response_style)
        contents = [
            TextContent(type="text", text=f"{note}\n\n{prompt}"),
        ]
        return (contents, structured)

    elif name == "thesis_prompt":
        from hegelion.core.prompt_dialectic import PromptDrivenDialectic

        query = arguments["query"]
        dialectic = PromptDrivenDialectic()
        prompt_obj = dialectic.generate_thesis_prompt(query)

        structured = {
            "phase": prompt_obj.phase,
            "prompt": prompt_obj.prompt,
            "instructions": prompt_obj.instructions,
            "expected_format": prompt_obj.expected_format,
        }

        response = f"""# THESIS PROMPT

{prompt_obj.prompt}

**Instructions:** {prompt_obj.instructions}
**Expected Format:** {prompt_obj.expected_format}"""

        return ([TextContent(type="text", text=response)], structured)

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
            structured_prompts = []

            for prompt_obj in council_prompts:
                response_parts.append(f"## {prompt_obj.phase.replace('_', ' ').title()}")
                response_parts.append(prompt_obj.prompt)
                response_parts.append(f"**Instructions:** {prompt_obj.instructions}")
                response_parts.append("")
                structured_prompts.append(
                    {
                        "phase": prompt_obj.phase,
                        "prompt": prompt_obj.prompt,
                        "instructions": prompt_obj.instructions,
                        "expected_format": prompt_obj.expected_format,
                    }
                )

            structured = {"prompts": structured_prompts, "phase": "antithesis_council"}
            response = "\n".join(response_parts)
        else:
            prompt_obj = dialectic.generate_antithesis_prompt(query, thesis, use_search)
            structured = {
                "phase": prompt_obj.phase,
                "prompt": prompt_obj.prompt,
                "instructions": prompt_obj.instructions,
                "expected_format": prompt_obj.expected_format,
            }
            response = f"""# ANTITHESIS PROMPT

{prompt_obj.prompt}

**Instructions:** {prompt_obj.instructions}
**Expected Format:** {prompt_obj.expected_format}"""

        return ([TextContent(type="text", text=response)], structured)

    elif name == "synthesis_prompt":
        from hegelion.core.prompt_dialectic import PromptDrivenDialectic

        query = arguments["query"]
        thesis = arguments["thesis"]
        antithesis = arguments["antithesis"]

        dialectic = PromptDrivenDialectic()
        prompt_obj = dialectic.generate_synthesis_prompt(query, thesis, antithesis)

        structured = {
            "phase": prompt_obj.phase,
            "prompt": prompt_obj.prompt,
            "instructions": prompt_obj.instructions,
            "expected_format": prompt_obj.expected_format,
        }

        response = f"""# SYNTHESIS PROMPT

{prompt_obj.prompt}

**Instructions:** {prompt_obj.instructions}
**Expected Format:** {prompt_obj.expected_format}"""

        return ([TextContent(type="text", text=response)], structured)

    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {name}")],
            structuredContent={"error": f"Unknown tool: {name}"},
            isError=True,
        )


async def run_server() -> None:
    """Run the prompt-driven MCP server using the standard stdio transport."""

    init_options = app.create_initialization_options()

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            init_options,
            # Stateless keeps older MCP runtimes happy if they call tools/list immediately
            # after initialization or skip explicit initialization notifications.
            stateless=True,
        )


def main() -> None:
    """Main entry point for the prompt-driven MCP server."""
    parser = argparse.ArgumentParser(
        description="Hegelion Prompt-Driven MCP Server - Works with any LLM",
        add_help=True,
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run an in-process tool check (list tools + single-shot prompt) and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        anyio.run(_self_test)
    else:
        anyio.run(run_server)


async def _self_test() -> None:
    """Self-test: list tools and call a sample tool so users see output."""

    print("🔎 Hegelion MCP self-test (in-process)")
    tools = await list_tools()
    tool_names = [t.name for t in tools]
    print("Tools:", ", ".join(tool_names))

    contents, structured = await call_tool(
        name="dialectical_single_shot",
        arguments={
            "query": "Self-test: Can AI be genuinely creative?",
            "use_council": True,
            "response_style": "json",
        },
    )

    print("\nresponse_style: json")
    print("Structured keys:", list(structured.keys()))
    prompt = structured.get("prompt", "")
    print("Prompt preview:\n", prompt[:400], "...", sep="")
    print("\n✅ Self-test complete")


if __name__ == "__main__":
    main()

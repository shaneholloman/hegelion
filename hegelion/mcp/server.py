"""Model-agnostic MCP server for dialectical reasoning.

This version works with whatever LLM is calling the MCP server,
rather than making its own API calls. Perfect for Cursor, Claude Desktop,
ChatGPT/Codex, VS Code, or any MCP-compatible environment.
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
from hegelion.core.autocoding_state import AutocodingState, save_session, load_session
from hegelion.core.prompt_autocoding import (
    PromptDrivenAutocoding,
    create_autocoding_workflow,
)

app = Server("hegelion-server")

MCP_SCHEMA_VERSION = 1
RESPONSE_STYLES = {
    "sections",
    "synthesis_only",
    "json",
    "conversational",
    "bullet_points",
}
WORKFLOW_FORMATS = {"workflow", "single_prompt"}
AUTOCODING_SKILL_MODES = {"init", "workflow", "single_shot"}

DIALECTIC_RESULT_SCHEMA = {
    "type": "object",
    "required": ["query", "thesis", "antithesis", "synthesis"],
    "properties": {
        "query": {"type": "string"},
        "thesis": {"type": "string"},
        "antithesis": {"type": "string"},
        "synthesis": {"type": "string"},
        "contradictions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["description", "evidence"],
                "properties": {
                    "description": {"type": "string"},
                    "evidence": {"type": "string"},
                },
            },
        },
        "research_proposals": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["proposal", "testable_prediction"],
                "properties": {
                    "proposal": {"type": "string"},
                    "testable_prediction": {"type": "string"},
                },
            },
        },
    },
}

DIALECTIC_PHASE_SCHEMAS = {
    "thesis": {
        "type": "object",
        "required": ["phase", "thesis"],
        "properties": {
            "phase": {"type": "string"},
            "thesis": {"type": "string"},
            "assumptions": {"type": "array", "items": {"type": "string"}},
            "uncertainties": {"type": "array", "items": {"type": "string"}},
        },
    },
    "antithesis": {
        "type": "object",
        "required": ["phase", "antithesis", "contradictions"],
        "properties": {
            "phase": {"type": "string"},
            "antithesis": {"type": "string"},
            "contradictions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["description", "evidence"],
                    "properties": {
                        "description": {"type": "string"},
                        "evidence": {"type": "string"},
                    },
                },
            },
        },
    },
    "synthesis": {
        "type": "object",
        "required": ["phase", "synthesis"],
        "properties": {
            "phase": {"type": "string"},
            "synthesis": {"type": "string"},
            "research_proposals": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["proposal", "testable_prediction"],
                    "properties": {
                        "proposal": {"type": "string"},
                        "testable_prediction": {"type": "string"},
                    },
                },
            },
        },
    },
    "judge": {
        "type": "object",
        "required": ["phase", "score", "critique_validity"],
        "properties": {
            "phase": {"type": "string"},
            "score": {"type": "number"},
            "critique_validity": {"type": "boolean"},
            "reasoning": {"type": "string"},
            "strengths": {"type": "string"},
            "improvements": {"type": "string"},
        },
    },
}

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
    response_style_enum = [
        "sections",
        "synthesis_only",
        "json",
        "conversational",
        "bullet_points",
    ]
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
                        "enum": response_style_enum,
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
                        "enum": response_style_enum,
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
                    },
                    "response_style": {
                        "type": "string",
                        "enum": response_style_enum,
                        "description": "Optional response formatting guidance for the thesis output",
                        "default": "sections",
                    },
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
                    "response_style": {
                        "type": "string",
                        "enum": response_style_enum,
                        "description": "Optional response formatting guidance for the antithesis output",
                        "default": "sections",
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
                    "response_style": {
                        "type": "string",
                        "enum": response_style_enum,
                        "description": "Optional response formatting guidance for the synthesis output",
                        "default": "sections",
                    },
                },
                "required": ["query", "thesis", "antithesis"],
            },
        ),
        # === AUTOCODING TOOLS (based on g3 paper) ===
        Tool(
            name="hegelion",
            description=(
                "Brand-first autocoding entrypoint. "
                "Use mode=workflow for a step-by-step recipe, mode=single_shot for a single prompt, "
                "or mode=init to create a session state."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "The requirements document (source of truth). Should be structured as a checklist.",
                    },
                    "mode": {
                        "type": "string",
                        "enum": sorted(AUTOCODING_SKILL_MODES),
                        "description": "Autocoding entrypoint mode",
                        "default": "workflow",
                    },
                    "max_turns": {
                        "type": "integer",
                        "description": "Maximum turns before timeout (default: 10)",
                        "default": 10,
                    },
                    "approval_threshold": {
                        "type": "number",
                        "description": "Minimum compliance score for approval (0-1, default: 0.9)",
                        "default": 0.9,
                    },
                    "session_name": {
                        "type": "string",
                        "description": "Optional human-readable session name (e.g., 'auth-feature')",
                    },
                },
                "required": ["requirements"],
            },
        ),
        Tool(
            name="autocoding_init",
            description=(
                "Initialize a dialectical autocoding session with requirements. "
                "Returns session state to pass to subsequent tool calls. "
                "Based on the g3 paper's coach-player adversarial cooperation paradigm."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "The requirements document (source of truth). Should be structured as a checklist.",
                    },
                    "max_turns": {
                        "type": "integer",
                        "description": "Maximum turns before timeout (default: 10)",
                        "default": 10,
                    },
                    "approval_threshold": {
                        "type": "number",
                        "description": "Minimum compliance score for approval (0-1, default: 0.9)",
                        "default": 0.9,
                    },
                    "session_name": {
                        "type": "string",
                        "description": "Optional human-readable session name (e.g., 'auth-feature')",
                    },
                },
                "required": ["requirements"],
            },
        ),
        Tool(
            name="autocoding_workflow",
            description=(
                "Return a structured autocoding workflow (player/coach loop) for orchestration. "
                "Useful for agents that want a step-by-step recipe before running the tools."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "The requirements document (source of truth)",
                    },
                    "max_turns": {
                        "type": "integer",
                        "description": "Maximum turns before timeout (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["requirements"],
            },
        ),
        Tool(
            name="player_prompt",
            description=(
                "Generate the implementation prompt for the player agent in autocoding. "
                "The player focuses on implementing requirements, NOT declaring success. "
                "Returns an updated state advanced to coach phase for the next call."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "object",
                        "description": "AutocodingState dict from autocoding_init or autocoding_advance",
                    },
                },
                "required": ["state"],
            },
        ),
        Tool(
            name="coach_prompt",
            description=(
                "Generate the validation prompt for the coach agent in autocoding. "
                "The coach verifies implementation against requirements, ignoring player's self-assessment. "
                "Requires state.phase=='coach'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "object",
                        "description": "AutocodingState dict from player phase",
                    },
                },
                "required": ["state"],
            },
        ),
        Tool(
            name="autocoding_advance",
            description=(
                "Advance autocoding state after coach review. "
                "Updates turn count, records feedback, and determines next phase."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "object",
                        "description": "AutocodingState dict from coach phase",
                    },
                    "coach_feedback": {
                        "type": "string",
                        "description": "The coach's feedback text (compliance checklist and actions needed)",
                    },
                    "approved": {
                        "type": "boolean",
                        "description": "Whether the coach approved the implementation (look for 'COACH APPROVED')",
                    },
                    "compliance_score": {
                        "type": "number",
                        "description": "Optional compliance score (0-1) based on checklist items satisfied",
                    },
                },
                "required": ["state", "coach_feedback", "approved"],
            },
        ),
        Tool(
            name="autocoding_single_shot",
            description=(
                "Single comprehensive prompt for self-directed autocoding. "
                "Combines player and coach roles with iterative implementation and self-verification."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "The requirements document (source of truth)",
                    },
                    "max_turns": {
                        "type": "integer",
                        "description": "Maximum iterations to attempt (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["requirements"],
            },
        ),
        Tool(
            name="autocoding_save",
            description=(
                "Save an autocoding session to a JSON file. "
                "Use this to persist session state for later resumption."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {
                        "type": "object",
                        "description": "AutocodingState dict to save",
                    },
                    "filepath": {
                        "type": "string",
                        "description": "Path to save the session JSON file",
                    },
                },
                "required": ["state", "filepath"],
            },
        ),
        Tool(
            name="autocoding_load",
            description=(
                "Load an autocoding session from a JSON file. "
                "Use this to resume a previously saved session."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the session JSON file to load",
                    },
                },
                "required": ["filepath"],
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
        case "conversational":
            return "LLM should return a natural, conversational response."
        case "bullet_points":
            return "LLM should return a concise bulleted list."
        case _:
            return "LLM should return full Thesis → Antithesis → Synthesis sections."


async def _send_progress(message: str, progress: float, total: float = 3.0) -> None:
    """Send a progress notification if a progress token is available."""
    try:
        ctx = app.request_context
        if ctx.meta and ctx.meta.progressToken:
            await ctx.session.send_progress_notification(
                ctx.meta.progressToken,
                progress,
                total=total,
                message=message,
            )
    except (LookupError, AttributeError):
        # No request context or progress token available
        pass


def _state_error(tool_name: str, message: str, *, error: str) -> CallToolResult:
    return CallToolResult(
        content=[TextContent(type="text", text=message)],
        structuredContent={
            "schema_version": MCP_SCHEMA_VERSION,
            "tool": tool_name,
            "error": error,
        },
        isError=True,
    )


def _arg_error(
    tool_name: str,
    message: str,
    *,
    error: str,
    expected: Any | None = None,
    received: Any | None = None,
) -> CallToolResult:
    structured = {
        "schema_version": MCP_SCHEMA_VERSION,
        "tool": tool_name,
        "error": error,
    }
    if expected is not None:
        structured["expected"] = expected
    if received is not None:
        structured["received"] = received
    return CallToolResult(
        content=[TextContent(type="text", text=message)],
        structuredContent=structured,
        isError=True,
    )


def _phase_error(tool_name: str, *, expected: str, received: str, hint: str) -> CallToolResult:
    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=(
                    f"Error: Invalid phase for {tool_name}. "
                    f"Expected '{expected}', got '{received}'.\n\nHint: {hint}"
                ),
            )
        ],
        structuredContent={
            "schema_version": MCP_SCHEMA_VERSION,
            "tool": tool_name,
            "error": f"Invalid phase: {received}",
            "expected": expected,
            "received": received,
            "hint": hint,
        },
        isError=True,
    )


def _require_str_arg(tool_name: str, arguments: Dict[str, Any], key: str) -> str | CallToolResult:
    value = arguments.get(key)
    if not isinstance(value, str) or not value.strip():
        return _arg_error(
            tool_name,
            f"Error: '{key}' must be a non-empty string.",
            error=f"Invalid argument: {key}",
            expected="non-empty string",
            received=value,
        )
    return value


def _get_enum_arg(
    tool_name: str,
    arguments: Dict[str, Any],
    key: str,
    allowed: set[str],
    default: str,
) -> str | CallToolResult:
    value = arguments.get(key, default)
    if value not in allowed:
        return _arg_error(
            tool_name,
            f"Error: '{key}' must be one of {sorted(allowed)}.",
            error=f"Invalid argument: {key}",
            expected=sorted(allowed),
            received=value,
        )
    return value


def _get_optional_bool(
    tool_name: str, arguments: Dict[str, Any], key: str, default: bool
) -> bool | CallToolResult:
    if key not in arguments:
        return default
    value = arguments.get(key)
    if isinstance(value, bool):
        return value
    return _arg_error(
        tool_name,
        f"Error: '{key}' must be a boolean.",
        error=f"Invalid argument: {key}",
        expected="boolean",
        received=value,
    )


def _get_optional_int(
    tool_name: str, arguments: Dict[str, Any], key: str, default: int, *, min_value: int
) -> int | CallToolResult:
    if key not in arguments:
        return default
    value = arguments.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        return _arg_error(
            tool_name,
            f"Error: '{key}' must be an integer.",
            error=f"Invalid argument: {key}",
            expected="integer",
            received=value,
        )
    if value < min_value:
        return _arg_error(
            tool_name,
            f"Error: '{key}' must be >= {min_value}.",
            error=f"Invalid argument: {key}",
            expected=f">={min_value}",
            received=value,
        )
    return value


def _get_optional_number(
    tool_name: str,
    arguments: Dict[str, Any],
    key: str,
    default: float,
    *,
    min_value: float,
    max_value: float,
) -> float | CallToolResult:
    if key not in arguments:
        return default
    value = arguments.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return _arg_error(
            tool_name,
            f"Error: '{key}' must be a number.",
            error=f"Invalid argument: {key}",
            expected="number",
            received=value,
        )
    if not min_value <= float(value) <= max_value:
        return _arg_error(
            tool_name,
            f"Error: '{key}' must be between {min_value} and {max_value}.",
            error=f"Invalid argument: {key}",
            expected=f"{min_value}..{max_value}",
            received=value,
        )
    return float(value)


def _get_optional_str(
    tool_name: str,
    arguments: Dict[str, Any],
    key: str,
    default: str | None = None,
) -> str | None | CallToolResult:
    if key not in arguments:
        return default
    value = arguments.get(key)
    if not isinstance(value, str) or not value.strip():
        return _arg_error(
            tool_name,
            f"Error: '{key}' must be a non-empty string.",
            error=f"Invalid argument: {key}",
            expected="non-empty string",
            received=value,
        )
    return value


def _response_schema_for_style(response_style: str) -> dict | None:
    if response_style != "json":
        return None
    return DIALECTIC_RESULT_SCHEMA


def _phase_schema_for_style(response_style: str, phase: str) -> dict | None:
    if response_style != "json":
        return None
    if phase.startswith("council_"):
        phase = "antithesis"
    return DIALECTIC_PHASE_SCHEMAS.get(phase)


def _parse_autocoding_state(tool_name: str, state_dict: Any) -> AutocodingState | CallToolResult:
    if not isinstance(state_dict, dict):
        return _state_error(
            tool_name,
            "Error: Invalid autocoding state. Expected an object/dict.",
            error="Invalid autocoding state: expected object",
        )
    try:
        return AutocodingState.from_dict(state_dict)
    except (KeyError, TypeError, ValueError) as e:
        return _state_error(
            tool_name,
            f"Error: Invalid autocoding state: {e}",
            error=f"Invalid autocoding state: {e}",
        )


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]):
    """Execute dialectical reasoning tools."""

    if name == "dialectical_workflow":
        query = _require_str_arg(name, arguments, "query")
        if isinstance(query, CallToolResult):
            return query
        use_search = _get_optional_bool(name, arguments, "use_search", False)
        if isinstance(use_search, CallToolResult):
            return use_search
        use_council = _get_optional_bool(name, arguments, "use_council", False)
        if isinstance(use_council, CallToolResult):
            return use_council
        use_judge = _get_optional_bool(name, arguments, "use_judge", False)
        if isinstance(use_judge, CallToolResult):
            return use_judge
        format_type = _get_enum_arg(name, arguments, "format", WORKFLOW_FORMATS, "workflow")
        if isinstance(format_type, CallToolResult):
            return format_type
        response_style = _get_enum_arg(
            name, arguments, "response_style", RESPONSE_STYLES, "sections"
        )
        if isinstance(response_style, CallToolResult):
            return response_style

        # Send progress notification
        await _send_progress("━━━ Preparing dialectical workflow ━━━", 1.0)

        if format_type == "single_prompt":
            await _send_progress("━━━ Generating single-shot prompt ━━━", 2.0)
            prompt = create_single_shot_dialectic_prompt(
                query=query,
                use_search=use_search,
                use_council=use_council,
                response_style=response_style,
            )
            await _send_progress("━━━ Prompt ready ━━━", 3.0)
            structured = {
                "schema_version": MCP_SCHEMA_VERSION,
                "query": query,
                "format": "single_prompt",
                "use_search": use_search,
                "use_council": use_council,
                "response_style": response_style,
                "prompt": prompt,
            }
            response_schema = _response_schema_for_style(response_style)
            if response_schema:
                structured["response_schema"] = response_schema
            return ([TextContent(type="text", text=prompt)], structured)
        else:
            await _send_progress("━━━ THESIS prompt ready ━━━", 1.0)
            await _send_progress("━━━ ANTITHESIS prompt ready ━━━", 2.0)
            await _send_progress("━━━ SYNTHESIS prompt ready ━━━", 3.0)
            workflow = create_dialectical_workflow(
                query=query,
                use_search=use_search,
                use_council=use_council,
                use_judge=use_judge,
                response_style=response_style,
            )
            workflow["schema_version"] = MCP_SCHEMA_VERSION
            workflow.setdefault("instructions", {})
            workflow["instructions"]["response_style"] = response_style
            workflow["instructions"]["response_style_note"] = _response_style_summary(
                response_style
            )
            response_schema = _response_schema_for_style(response_style)
            if response_schema:
                workflow["instructions"]["response_schema"] = response_schema
                workflow["instructions"]["phase_schemas"] = DIALECTIC_PHASE_SCHEMAS

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
        query = _require_str_arg(name, arguments, "query")
        if isinstance(query, CallToolResult):
            return query
        use_search = _get_optional_bool(name, arguments, "use_search", False)
        if isinstance(use_search, CallToolResult):
            return use_search
        use_council = _get_optional_bool(name, arguments, "use_council", False)
        if isinstance(use_council, CallToolResult):
            return use_council
        response_style = _get_enum_arg(
            name, arguments, "response_style", RESPONSE_STYLES, "sections"
        )
        if isinstance(response_style, CallToolResult):
            return response_style
        prompt = create_single_shot_dialectic_prompt(
            query=query,
            use_search=use_search,
            use_council=use_council,
            response_style=response_style,
        )

        structured = {
            "schema_version": MCP_SCHEMA_VERSION,
            "query": query,
            "use_search": use_search,
            "use_council": use_council,
            "response_style": response_style,
            "prompt": prompt,
        }
        response_schema = _response_schema_for_style(response_style)
        if response_schema:
            structured["response_schema"] = response_schema
        note = _response_style_summary(response_style)
        contents = [
            TextContent(type="text", text=f"{note}\n\n{prompt}"),
        ]
        return (contents, structured)

    elif name == "thesis_prompt":
        await _send_progress("━━━ THESIS ━━━ Generating prompt...", 1.0, 1.0)
        from hegelion.core.prompt_dialectic import PromptDrivenDialectic

        query = _require_str_arg(name, arguments, "query")
        if isinstance(query, CallToolResult):
            return query
        response_style = _get_enum_arg(
            name, arguments, "response_style", RESPONSE_STYLES, "sections"
        )
        if isinstance(response_style, CallToolResult):
            return response_style
        dialectic = PromptDrivenDialectic()
        prompt_obj = dialectic.generate_thesis_prompt(query, response_style=response_style)

        structured = {
            "schema_version": MCP_SCHEMA_VERSION,
            "phase": prompt_obj.phase,
            "prompt": prompt_obj.prompt,
            "instructions": prompt_obj.instructions,
            "expected_format": prompt_obj.expected_format,
            "response_style": response_style,
        }
        response_schema = _phase_schema_for_style(response_style, prompt_obj.phase)
        if response_schema:
            structured["response_schema"] = response_schema

        response = f"""# THESIS PROMPT

{prompt_obj.prompt}

**Instructions:** {prompt_obj.instructions}
**Expected Format:** {prompt_obj.expected_format}"""

        return ([TextContent(type="text", text=response)], structured)

    elif name == "antithesis_prompt":
        await _send_progress("━━━ ANTITHESIS ━━━ Generating prompt...", 1.0, 1.0)
        from hegelion.core.prompt_dialectic import PromptDrivenDialectic

        query = _require_str_arg(name, arguments, "query")
        if isinstance(query, CallToolResult):
            return query
        thesis = _require_str_arg(name, arguments, "thesis")
        if isinstance(thesis, CallToolResult):
            return thesis
        use_search = _get_optional_bool(name, arguments, "use_search", False)
        if isinstance(use_search, CallToolResult):
            return use_search
        use_council = _get_optional_bool(name, arguments, "use_council", False)
        if isinstance(use_council, CallToolResult):
            return use_council
        response_style = _get_enum_arg(
            name, arguments, "response_style", RESPONSE_STYLES, "sections"
        )
        if isinstance(response_style, CallToolResult):
            return response_style

        dialectic = PromptDrivenDialectic()

        if use_council:
            council_prompts = dialectic.generate_council_prompts(
                query, thesis, response_style=response_style
            )
            response_parts = ["# COUNCIL ANTITHESIS PROMPTS\n"]
            structured_prompts = []

            for prompt_obj in council_prompts:
                response_parts.append(f"## {prompt_obj.phase.replace('_', ' ').title()}")
                response_parts.append(prompt_obj.prompt)
                response_parts.append(f"**Instructions:** {prompt_obj.instructions}")
                response_parts.append("")
                structured_prompts.append(
                    {
                        "schema_version": MCP_SCHEMA_VERSION,
                        "phase": prompt_obj.phase,
                        "prompt": prompt_obj.prompt,
                        "instructions": prompt_obj.instructions,
                        "expected_format": prompt_obj.expected_format,
                        "response_style": response_style,
                    }
                )
                response_schema = _phase_schema_for_style(response_style, prompt_obj.phase)
                if response_schema:
                    structured_prompts[-1]["response_schema"] = response_schema

            structured = {
                "schema_version": MCP_SCHEMA_VERSION,
                "prompts": structured_prompts,
                "phase": "antithesis_council",
                "response_style": response_style,
            }
            response = "\n".join(response_parts)
        else:
            prompt_obj = dialectic.generate_antithesis_prompt(
                query, thesis, use_search, response_style=response_style
            )
            structured = {
                "schema_version": MCP_SCHEMA_VERSION,
                "phase": prompt_obj.phase,
                "prompt": prompt_obj.prompt,
                "instructions": prompt_obj.instructions,
                "expected_format": prompt_obj.expected_format,
                "response_style": response_style,
            }
            response_schema = _phase_schema_for_style(response_style, prompt_obj.phase)
            if response_schema:
                structured["response_schema"] = response_schema
            response = f"""# ANTITHESIS PROMPT

{prompt_obj.prompt}

**Instructions:** {prompt_obj.instructions}
**Expected Format:** {prompt_obj.expected_format}"""

        return ([TextContent(type="text", text=response)], structured)

    elif name == "synthesis_prompt":
        await _send_progress("━━━ SYNTHESIS ━━━ Generating prompt...", 1.0, 1.0)
        from hegelion.core.prompt_dialectic import PromptDrivenDialectic

        query = _require_str_arg(name, arguments, "query")
        if isinstance(query, CallToolResult):
            return query
        thesis = _require_str_arg(name, arguments, "thesis")
        if isinstance(thesis, CallToolResult):
            return thesis
        antithesis = _require_str_arg(name, arguments, "antithesis")
        if isinstance(antithesis, CallToolResult):
            return antithesis
        response_style = _get_enum_arg(
            name, arguments, "response_style", RESPONSE_STYLES, "sections"
        )
        if isinstance(response_style, CallToolResult):
            return response_style

        dialectic = PromptDrivenDialectic()
        prompt_obj = dialectic.generate_synthesis_prompt(
            query, thesis, antithesis, response_style=response_style
        )

        structured = {
            "schema_version": MCP_SCHEMA_VERSION,
            "phase": prompt_obj.phase,
            "prompt": prompt_obj.prompt,
            "instructions": prompt_obj.instructions,
            "expected_format": prompt_obj.expected_format,
            "response_style": response_style,
        }
        response_schema = _phase_schema_for_style(response_style, prompt_obj.phase)
        if response_schema:
            structured["response_schema"] = response_schema

        response = f"""# SYNTHESIS PROMPT

{prompt_obj.prompt}

**Instructions:** {prompt_obj.instructions}
**Expected Format:** {prompt_obj.expected_format}"""

        return ([TextContent(type="text", text=response)], structured)

    # === AUTOCODING TOOL HANDLERS ===

    elif name == "hegelion":
        await _send_progress("Preparing Hegelion autocoding entrypoint...", 1.0, 2.0)

        requirements = _require_str_arg(name, arguments, "requirements")
        if isinstance(requirements, CallToolResult):
            return requirements
        mode = _get_enum_arg(name, arguments, "mode", AUTOCODING_SKILL_MODES, "workflow")
        if isinstance(mode, CallToolResult):
            return mode
        max_turns = _get_optional_int(name, arguments, "max_turns", 10, min_value=1)
        if isinstance(max_turns, CallToolResult):
            return max_turns
        approval_threshold = _get_optional_number(
            name,
            arguments,
            "approval_threshold",
            0.9,
            min_value=0.0,
            max_value=1.0,
        )
        if isinstance(approval_threshold, CallToolResult):
            return approval_threshold
        session_name = _get_optional_str(name, arguments, "session_name", None)
        if isinstance(session_name, CallToolResult):
            return session_name

        if mode == "init":
            state = AutocodingState.create(
                requirements=requirements,
                max_turns=max_turns,
                approval_threshold=approval_threshold,
                session_name=session_name,
            )

            await _send_progress("Autocoding session initialized", 2.0, 2.0)

            structured = {
                **state.to_dict(),
                "entrypoint": "hegelion",
                "mode": mode,
            }
            if state.session_name:
                session_label = f"{state.session_name} ({state.session_id[:8]}...)"
            else:
                session_label = f"{state.session_id[:8]}..."
            response = f"""# HEGELION AUTOCODING SESSION INITIALIZED

**Session:** {session_label}
**Max Turns:** {max_turns}
**Approval Threshold:** {approval_threshold:.0%}

Next step: call `player_prompt` with the returned state."""

            return ([TextContent(type="text", text=response)], structured)

        if mode == "workflow":
            workflow = create_autocoding_workflow(requirements=requirements, max_turns=max_turns)
            workflow["schema_version"] = MCP_SCHEMA_VERSION
            workflow["entrypoint"] = "hegelion"
            workflow["mode"] = mode

            serialized = json.dumps(workflow, indent=2)
            summary = (
                "Hegelion autocoding workflow ready. Agents should read the structuredContent JSON "
                f"(mode='{mode}')."
            )
            contents: List[TextContent] = [
                TextContent(type="text", text=summary),
                TextContent(type="text", text=serialized),
            ]
            return (contents, workflow)

        await _send_progress("Generating single-shot autocoding prompt...", 2.0, 2.0)

        autocoding = PromptDrivenAutocoding()
        prompt_obj = autocoding.generate_single_shot_prompt(
            requirements=requirements,
            max_turns=max_turns,
        )

        structured = {
            "schema_version": MCP_SCHEMA_VERSION,
            **prompt_obj.to_dict(),
            "requirements": requirements,
            "max_turns": max_turns,
            "entrypoint": "hegelion",
            "mode": mode,
        }

        response = f"""# HEGELION SINGLE-SHOT AUTOCODING PROMPT

{prompt_obj.prompt}

---
**Instructions:** {prompt_obj.instructions}
**Expected Format:** {prompt_obj.expected_format}"""

        return ([TextContent(type="text", text=response)], structured)

    elif name == "autocoding_init":
        await _send_progress("Initializing autocoding session...", 1.0, 2.0)

        requirements = _require_str_arg(name, arguments, "requirements")
        if isinstance(requirements, CallToolResult):
            return requirements
        max_turns = _get_optional_int(name, arguments, "max_turns", 10, min_value=1)
        if isinstance(max_turns, CallToolResult):
            return max_turns
        approval_threshold = _get_optional_number(
            name,
            arguments,
            "approval_threshold",
            0.9,
            min_value=0.0,
            max_value=1.0,
        )
        if isinstance(approval_threshold, CallToolResult):
            return approval_threshold
        session_name = _get_optional_str(name, arguments, "session_name", None)
        if isinstance(session_name, CallToolResult):
            return session_name

        state = AutocodingState.create(
            requirements=requirements,
            max_turns=max_turns,
            approval_threshold=approval_threshold,
            session_name=session_name,
        )

        await _send_progress("Session initialized", 2.0, 2.0)

        structured = state.to_dict()
        if state.session_name:
            session_label = f"{state.session_name} ({state.session_id[:8]}...)"
        else:
            session_label = f"{state.session_id[:8]}..."
        response = f"""# AUTOCODING SESSION INITIALIZED

**Session:** {session_label}
**Max Turns:** {max_turns}
**Approval Threshold:** {approval_threshold:.0%}

The session is ready. Next step: call `player_prompt` with the returned state.

**Workflow:**
1. Call `player_prompt` with state -> Execute returned prompt
2. Call `coach_prompt` with state -> Execute returned prompt
3. Call `autocoding_advance` with coach feedback
4. Repeat until COACH APPROVED or timeout"""

        return ([TextContent(type="text", text=response)], structured)

    elif name == "autocoding_workflow":
        requirements = _require_str_arg(name, arguments, "requirements")
        if isinstance(requirements, CallToolResult):
            return requirements
        max_turns = _get_optional_int(name, arguments, "max_turns", 10, min_value=1)
        if isinstance(max_turns, CallToolResult):
            return max_turns

        workflow = create_autocoding_workflow(requirements=requirements, max_turns=max_turns)
        workflow["schema_version"] = MCP_SCHEMA_VERSION

        serialized = json.dumps(workflow, indent=2)
        summary = (
            "Hegelion autocoding workflow ready. Agents should read the structuredContent JSON "
            f"for step sequencing (max_turns={max_turns})."
        )
        contents = [
            TextContent(type="text", text=summary),
            TextContent(type="text", text=serialized),
        ]
        return (contents, workflow)

    elif name == "player_prompt":
        await _send_progress("Generating player prompt...", 1.0, 1.0)

        parsed_state = _parse_autocoding_state(name, arguments.get("state"))
        if isinstance(parsed_state, CallToolResult):
            return parsed_state
        state = parsed_state

        if state.phase != "player":
            return _phase_error(
                name,
                expected="player",
                received=state.phase,
                hint="If you just called autocoding_init or autocoding_advance, pass that returned state into player_prompt.",
            )

        autocoding = PromptDrivenAutocoding()
        prompt_obj = autocoding.generate_player_prompt(
            requirements=state.requirements,
            coach_feedback=state.last_coach_feedback,
            turn_number=state.current_turn + 1,
            max_turns=state.max_turns,
        )

        # Advance state to coach phase for next call
        new_state = state.advance_to_coach()

        structured = {
            "schema_version": MCP_SCHEMA_VERSION,
            **prompt_obj.to_dict(),
            "current_phase": "player",
            "next_phase": new_state.phase,
            "state": new_state.to_dict(),
        }

        response = f"""# PLAYER PROMPT (Turn {state.current_turn + 1}/{state.max_turns})

{prompt_obj.prompt}

---
**Instructions:** {prompt_obj.instructions}
**Next Step:** After executing this prompt, call `coach_prompt` with the updated state."""

        return ([TextContent(type="text", text=response)], structured)

    elif name == "coach_prompt":
        await _send_progress("Generating coach prompt...", 1.0, 1.0)

        parsed_state = _parse_autocoding_state(name, arguments.get("state"))
        if isinstance(parsed_state, CallToolResult):
            return parsed_state
        state = parsed_state

        if state.phase != "coach":
            return _phase_error(
                name,
                expected="coach",
                received=state.phase,
                hint="Call player_prompt first; then pass the returned state (state.phase should be 'coach') into coach_prompt.",
            )

        autocoding = PromptDrivenAutocoding()
        prompt_obj = autocoding.generate_coach_prompt(
            requirements=state.requirements,
            turn_number=state.current_turn + 1,
            max_turns=state.max_turns,
        )

        structured = {
            "schema_version": MCP_SCHEMA_VERSION,
            **prompt_obj.to_dict(),
            "current_phase": "coach",
            "next_phase": state.phase,
            "state": state.to_dict(),
        }

        response = f"""# COACH PROMPT (Turn {state.current_turn + 1}/{state.max_turns})

{prompt_obj.prompt}

---
**Instructions:** {prompt_obj.instructions}
**Next Step:** After executing this prompt, call `autocoding_advance` with the coach's feedback."""

        return ([TextContent(type="text", text=response)], structured)

    elif name == "autocoding_advance":
        await _send_progress("Advancing autocoding state...", 1.0, 2.0)

        state_dict = arguments.get("state")
        coach_feedback = _require_str_arg(name, arguments, "coach_feedback")
        if isinstance(coach_feedback, CallToolResult):
            return coach_feedback
        approved = arguments.get("approved")
        if not isinstance(approved, bool):
            return _arg_error(
                name,
                "Error: 'approved' is required and must be a boolean.",
                error="Invalid argument: approved",
                expected="boolean",
                received=approved,
            )
        compliance_score = arguments.get("compliance_score")
        if compliance_score is not None:
            compliance_score = _get_optional_number(
                name,
                arguments,
                "compliance_score",
                0.0,
                min_value=0.0,
                max_value=1.0,
            )
            if isinstance(compliance_score, CallToolResult):
                return compliance_score

        parsed_state = _parse_autocoding_state(name, state_dict)
        if isinstance(parsed_state, CallToolResult):
            return parsed_state
        state = parsed_state

        if state.phase != "coach":
            return _phase_error(
                name,
                expected="coach",
                received=state.phase,
                hint="Call coach_prompt first and pass its returned state into autocoding_advance.",
            )

        new_state = state.advance_turn(
            coach_feedback=coach_feedback,
            approved=approved,
            compliance_score=compliance_score,
        )

        await _send_progress("State advanced", 2.0, 2.0)

        structured = new_state.to_dict()

        if new_state.status == "approved":
            response = f"""# AUTOCODING COMPLETE - APPROVED

**Session:** {new_state.session_id[:8]}...
**Turns Used:** {new_state.current_turn}/{new_state.max_turns}
**Final Status:** APPROVED

The implementation has been verified by the coach and meets all requirements."""

        elif new_state.status == "timeout":
            response = f"""# AUTOCODING COMPLETE - TIMEOUT

**Session:** {new_state.session_id[:8]}...
**Turns Used:** {new_state.current_turn}/{new_state.max_turns}
**Final Status:** TIMEOUT

Maximum turns reached without approval. Review the turn history for progress made."""

        else:
            response = f"""# AUTOCODING - CONTINUING

**Session:** {new_state.session_id[:8]}...
**Turn:** {new_state.current_turn + 1}/{new_state.max_turns}
**Status:** {new_state.status}

**Next Step:** Call `player_prompt` with the updated state to continue implementation."""

        return ([TextContent(type="text", text=response)], structured)

    elif name == "autocoding_single_shot":
        await _send_progress("Generating single-shot autocoding prompt...", 1.0, 1.0)

        requirements = _require_str_arg(name, arguments, "requirements")
        if isinstance(requirements, CallToolResult):
            return requirements
        max_turns = _get_optional_int(name, arguments, "max_turns", 10, min_value=1)
        if isinstance(max_turns, CallToolResult):
            return max_turns

        autocoding = PromptDrivenAutocoding()
        prompt_obj = autocoding.generate_single_shot_prompt(
            requirements=requirements,
            max_turns=max_turns,
        )

        structured = {
            "schema_version": MCP_SCHEMA_VERSION,
            **prompt_obj.to_dict(),
            "requirements": requirements,
            "max_turns": max_turns,
        }

        response = f"""# SINGLE-SHOT AUTOCODING PROMPT

{prompt_obj.prompt}

---
**Instructions:** {prompt_obj.instructions}
**Expected Format:** {prompt_obj.expected_format}"""

        return ([TextContent(type="text", text=response)], structured)

    elif name == "autocoding_save":
        state_dict = arguments.get("state")
        filepath = _require_str_arg(name, arguments, "filepath")
        if isinstance(filepath, CallToolResult):
            return filepath

        parsed_state = _parse_autocoding_state(name, state_dict)
        if isinstance(parsed_state, CallToolResult):
            return parsed_state
        state = parsed_state
        save_session(state, filepath)

        structured = {
            "schema_version": MCP_SCHEMA_VERSION,
            "session_id": state.session_id,
            "filepath": filepath,
            "saved": True,
        }
        response = f"""# SESSION SAVED

**Session ID:** {state.session_id[:8]}...
**Saved to:** {filepath}
**Phase:** {state.phase}
**Turn:** {state.current_turn + 1}/{state.max_turns}

Session saved successfully. Use `autocoding_load` with the filepath to restore."""

        return ([TextContent(type="text", text=response)], structured)

    elif name == "autocoding_load":
        filepath = _require_str_arg(name, arguments, "filepath")
        if isinstance(filepath, CallToolResult):
            return filepath

        try:
            state = load_session(filepath)
        except FileNotFoundError:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Error: Session file not found: {filepath}")
                ],
                structuredContent={
                    "schema_version": MCP_SCHEMA_VERSION,
                    "error": f"File not found: {filepath}",
                },
                isError=True,
            )
        except json.JSONDecodeError as e:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Error: Invalid JSON in session file: {e}")
                ],
                structuredContent={
                    "schema_version": MCP_SCHEMA_VERSION,
                    "error": f"Invalid JSON: {str(e)}",
                },
                isError=True,
            )

        structured = state.to_dict()
        response = f"""# SESSION LOADED

**Session ID:** {state.session_id[:8]}...
**Loaded from:** {filepath}
**Phase:** {state.phase}
**Status:** {state.status}
**Turn:** {state.current_turn + 1}/{state.max_turns}

Session restored. Continue with the appropriate tool based on phase:
- If phase is "player": call `player_prompt`
- If phase is "coach": call `coach_prompt`"""

        return ([TextContent(type="text", text=response)], structured)

    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {name}")],
            structuredContent={
                "schema_version": MCP_SCHEMA_VERSION,
                "error": f"Unknown tool: {name}",
            },
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

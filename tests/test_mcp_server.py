"""Tests for model-agnostic MCP server."""

import json
import pytest
from hegelion.mcp.server import app


@pytest.mark.asyncio
class TestPromptMCPServer:

    async def test_list_tools(self):
        """Test that all prompt tools are listed."""
        tools = await app.list_tools()
        tool_names = [t.name for t in tools]

        assert "dialectical_workflow" in tool_names
        assert "dialectical_single_shot" in tool_names
        assert "thesis_prompt" in tool_names
        assert "antithesis_prompt" in tool_names
        assert "synthesis_prompt" in tool_names

    async def test_dialectical_workflow_tool(self):
        """Test dialectical workflow tool execution."""
        args = {"query": "test query"}
        result = await app.call_tool("dialectical_workflow", args)

        assert len(result) == 1
        assert result[0].type == "text"

        workflow = json.loads(result[0].text)
        assert workflow["query"] == "test query"
        assert len(workflow["steps"]) >= 3

    async def test_dialectical_single_shot_tool(self):
        """Test single shot prompt tool."""
        args = {"query": "test query", "use_council": True}
        result = await app.call_tool("dialectical_single_shot", args)

        assert len(result) == 1
        prompt = result[0].text
        assert "test query" in prompt
        assert "THE LOGICIAN" in prompt

    async def test_thesis_prompt_tool(self):
        """Test thesis prompt tool."""
        args = {"query": "test query"}
        result = await app.call_tool("thesis_prompt", args)

        assert len(result) == 1
        content = result[0].text
        assert "THESIS PROMPT" in content
        assert "test query" in content

    async def test_antithesis_prompt_tool(self):
        """Test antithesis prompt tool."""
        args = {"query": "test query", "thesis": "some thesis"}
        result = await app.call_tool("antithesis_prompt", args)

        content = result[0].text
        assert "ANTITHESIS PROMPT" in content
        assert "test query" in content
        assert "some thesis" in content

    async def test_antithesis_council_prompt_tool(self):
        """Test antithesis prompt tool with council."""
        args = {"query": "test query", "thesis": "some thesis", "use_council": True}
        result = await app.call_tool("antithesis_prompt", args)

        content = result[0].text
        assert "COUNCIL ANTITHESIS PROMPTS" in content
        assert "The Logician" in content

    async def test_synthesis_prompt_tool(self):
        """Test synthesis prompt tool."""
        args = {"query": "test query", "thesis": "T", "antithesis": "A"}
        result = await app.call_tool("synthesis_prompt", args)

        content = result[0].text
        assert "SYNTHESIS PROMPT" in content
        assert "T" in content
        assert "A" in content

"""Tests for MCP server functionality."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hegelion.mcp_server import app
from hegelion.models import HegelionResult


@pytest.fixture
def sample_result() -> HegelionResult:
    """Sample result for testing."""
    return HegelionResult(
        query="Test Query",
        mode="synthesis",
        thesis="Thesis text",
        antithesis="Antithesis text",
        synthesis="Synthesis text",
        contradictions=[{"description": "Contradiction 1"}],
        research_proposals=[{"description": "Proposal 1"}],
        metadata={
            "thesis_time_ms": 100.0,
            "antithesis_time_ms": 200.0,
            "synthesis_time_ms": 300.0,
            "total_time_ms": 600.0,
        },
    )


@pytest.mark.asyncio
class TestListTools:
    """Tests for tool listing."""

    async def test_list_tools_returns_tools(self):
        """Test that list_tools returns correct tools."""
        tools = await app.list_tools()

        assert len(tools) == 2
        tool_names = [tool.name for tool in tools]
        assert "run_dialectic" in tool_names
        assert "run_benchmark" in tool_names

    async def test_run_dialectic_tool_schema(self):
        """Test run_dialectic tool schema."""
        tools = await app.list_tools()
        dialectic_tool = next(t for t in tools if t.name == "run_dialectic")

        assert dialectic_tool.description
        assert "thesis" in dialectic_tool.description.lower()
        assert "antithesis" in dialectic_tool.description.lower()
        assert "synthesis" in dialectic_tool.description.lower()

        schema = dialectic_tool.inputSchema
        assert schema["type"] == "object"
        assert "query" in schema["required"]
        assert "properties" in schema
        assert "query" in schema["properties"]
        assert "debug" in schema["properties"]

    async def test_run_benchmark_tool_schema(self):
        """Test run_benchmark tool schema."""
        tools = await app.list_tools()
        benchmark_tool = next(t for t in tools if t.name == "run_benchmark")

        assert benchmark_tool.description
        assert "jsonl" in benchmark_tool.description.lower()

        schema = benchmark_tool.inputSchema
        assert schema["type"] == "object"
        assert "prompts_file" in schema["required"]
        assert "properties" in schema
        assert "prompts_file" in schema["properties"]
        assert "debug" in schema["properties"]


@pytest.mark.asyncio
class TestCallTool:
    """Tests for tool execution."""

    async def test_run_dialectic_tool_execution(self, sample_result: HegelionResult):
        """Test run_dialectic tool execution."""
        with patch("hegelion.mcp_server.run_dialectic", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = sample_result

            # MCP server call_tool is called with name and arguments
            result = await app.call_tool(name="run_dialectic", arguments={"query": "Test query"})

            assert len(result) == 1
            assert result[0].type == "text"
            payload = json.loads(result[0].text)
            assert payload["query"] == "Test Query"
            mock_run.assert_awaited_once_with(query="Test query", debug=False)

    async def test_run_dialectic_with_debug(self, sample_result: HegelionResult):
        """Test run_dialectic tool with debug flag."""
        with patch("hegelion.mcp_server.run_dialectic", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = sample_result

            result = await app.call_tool(name="run_dialectic", arguments={"query": "Test", "debug": True})

            mock_run.assert_awaited_once_with(query="Test", debug=True)

    async def test_run_benchmark_tool_execution(self, tmp_path: Path, sample_result: HegelionResult):
        """Test run_benchmark tool execution."""
        prompts_file = tmp_path / "prompts.jsonl"
        prompts_file.write_text('{"query": "Q1"}\n{"query": "Q2"}\n')

        with patch("hegelion.mcp_server.run_benchmark", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = [sample_result, sample_result]

            result = await app.call_tool(
                name="run_benchmark", arguments={"prompts_file": str(prompts_file)}
            )

            assert len(result) == 1
            assert result[0].type == "text"
            # Should be JSONL (newline-delimited JSON)
            lines = result[0].text.strip().split("\n")
            assert len(lines) == 2
            for line in lines:
                payload = json.loads(line)
                assert payload["query"] == "Test Query"

    async def test_run_benchmark_with_debug(self, tmp_path: Path, sample_result: HegelionResult):
        """Test run_benchmark tool with debug flag."""
        prompts_file = tmp_path / "prompts.jsonl"
        prompts_file.write_text('{"query": "Test"}\n')

        with patch("hegelion.mcp_server.run_benchmark", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = [sample_result]

            await app.call_tool(
                name="run_benchmark", arguments={"prompts_file": str(prompts_file), "debug": True}
            )

            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["debug"] is True

    async def test_run_benchmark_nonexistent_file_raises(self, tmp_path: Path):
        """Test that run_benchmark raises error for nonexistent file."""
        nonexistent = tmp_path / "nonexistent.jsonl"

        with pytest.raises(ValueError) as exc_info:
            await app.call_tool(name="run_benchmark", arguments={"prompts_file": str(nonexistent)})

        assert "not found" in str(exc_info.value).lower()

    async def test_unknown_tool_raises(self):
        """Test that unknown tool raises error."""
        with pytest.raises(ValueError) as exc_info:
            await app.call_tool(name="unknown_tool", arguments={})

        assert "Unknown tool" in str(exc_info.value)


@pytest.mark.asyncio
class TestInputValidation:
    """Tests for input validation."""

    async def test_run_dialectic_missing_query_raises(self):
        """Test that run_dialectic requires query field."""
        with pytest.raises(KeyError):
            await app.call_tool(name="run_dialectic", arguments={})

    async def test_run_benchmark_missing_prompts_file_raises(self):
        """Test that run_benchmark requires prompts_file field."""
        with pytest.raises(KeyError):
            await app.call_tool(name="run_benchmark", arguments={})

    async def test_run_dialectic_debug_defaults_to_false(self, sample_result: HegelionResult):
        """Test that debug defaults to False."""
        with patch("hegelion.mcp_server.run_dialectic", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = sample_result

            await app.call_tool(name="run_dialectic", arguments={"query": "Test"})

            mock_run.assert_awaited_once_with(query="Test", debug=False)

    async def test_run_benchmark_debug_defaults_to_false(self, tmp_path: Path, sample_result: HegelionResult):
        """Test that debug defaults to False for benchmark."""
        prompts_file = tmp_path / "prompts.jsonl"
        prompts_file.write_text('{"query": "Test"}\n')

        with patch("hegelion.mcp_server.run_benchmark", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = [sample_result]

            await app.call_tool(name="run_benchmark", arguments={"prompts_file": str(prompts_file)})

            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["debug"] is False


@pytest.mark.asyncio
class TestErrorHandling:
    """Tests for error handling in MCP server."""

    async def test_run_dialectic_backend_error(self):
        """Test handling of backend errors in run_dialectic."""
        from hegelion.config import ConfigurationError

        with patch("hegelion.mcp_server.run_dialectic", new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = ConfigurationError("No API key")

            with pytest.raises(ConfigurationError):
                await app.call_tool(name="run_dialectic", arguments={"query": "Test"})

    async def test_run_benchmark_file_error(self, tmp_path: Path):
        """Test handling of file errors in run_benchmark."""
        prompts_file = tmp_path / "prompts.jsonl"
        prompts_file.write_text('{"query": "Test"}\n')

        with patch("hegelion.mcp_server.run_benchmark", new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = FileNotFoundError("File not found")

            with pytest.raises(FileNotFoundError):
                await app.call_tool(name="run_benchmark", arguments={"prompts_file": str(prompts_file)})

    async def test_run_benchmark_jsonl_output_format(self, tmp_path: Path, sample_result: HegelionResult):
        """Test that run_benchmark returns proper JSONL format."""
        prompts_file = tmp_path / "prompts.jsonl"
        prompts_file.write_text('{"query": "Q1"}\n{"query": "Q2"}\n')

        with patch("hegelion.mcp_server.run_benchmark", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = [sample_result, sample_result]

            result = await app.call_tool(name="run_benchmark", arguments={"prompts_file": str(prompts_file)})

            # Should be newline-delimited JSON
            text = result[0].text
            lines = text.strip().split("\n")
            assert len(lines) == 2
            # Each line should be valid JSON
            for line in lines:
                json.loads(line)  # Should not raise


"""Tests for Hegelion core API functionality."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from hegelion.core import run_dialectic, run_benchmark, dialectic, quickstart
from hegelion.models import HegelionResult


class MockBackend:
    """Mock LLM backend for testing."""

    def __init__(self, responses=None):
        self.responses = responses or {
            "thesis": "This is a test thesis response.",
            "antithesis": """
            CONTRADICTION: The thesis makes unsupported assumptions.
            EVIDENCE: No evidence provided for key claims.

            CONTRADICTION: The thesis ignores important counterexamples.
            EVIDENCE: Well-known cases contradict the conclusion.
            """,
            "synthesis": """
            A synthesis that transcends both positions.

            RESEARCH_PROPOSAL: Study the relationship between X and Y.
            TESTABLE_PREDICTION: Results will show significant correlation.
            """
        }
        self.call_count = 0

    async def generate(self, prompt, max_tokens=1000, temperature=0.7, system_prompt=None):
        """Mock generate method."""
        self.call_count += 1

        # Determine which phase we're in based on prompt content
        if "SYNTHESIS" in prompt:
            return self.responses["synthesis"]
        elif "ANTITHESIS" in prompt:
            return self.responses["antithesis"]
        elif "THESIS" in prompt:
            return self.responses["thesis"]
        else:
            return "Default response"


@pytest.mark.asyncio
class TestRunDialectic:
    """Test the run_dialectic core function."""

    async def test_run_dialectic_basic(self):
        """Test basic run_dialectic functionality."""
        mock_backend = MockBackend()

        with patch('hegelion.core.get_backend_from_env', return_value=mock_backend):
            with patch('hegelion.core.get_engine_settings') as mock_settings:
                mock_settings.return_value = MockSettings()

                result = await run_dialectic("Test query")

        # Verify it's a HegelionResult
        assert isinstance(result, HegelionResult)

        # Verify basic structure
        assert result.query == "Test query"
        assert result.mode == "synthesis"
        assert result.thesis == "This is a test thesis response."
        assert result.antithesis is not None
        assert result.synthesis is not None
        assert isinstance(result.contradictions, list)
        assert isinstance(result.research_proposals, list)
        assert isinstance(result.metadata, dict)

        # Should have extracted contradictions
        assert len(result.contradictions) == 2
        assert any("unsupported assumptions" in c["description"] for c in result.contradictions)

        # Should have extracted research proposals
        assert len(result.research_proposals) >= 1
        assert any(
            "Study the relationship between X and Y" in proposal["description"]
            for proposal in result.research_proposals
        )
        assert "debug" not in result.metadata

    async def test_run_dialectic_with_debug(self):
        """Test run_dialectic with debug mode."""
        mock_backend = MockBackend()

        with patch('hegelion.core.get_backend_from_env', return_value=mock_backend):
            with patch('hegelion.core.get_engine_settings') as mock_settings:
                mock_settings.return_value = MockSettings()

                result = await run_dialectic("Test query", debug=True)

        # Should include debug information
        assert "debug" in result.metadata
        assert "internal_conflict_score" in result.metadata["debug"]

        # Should include full trace when debug=True
        assert result.trace is not None
        assert "thesis" in result.trace
        assert "antithesis" in result.trace
        assert "synthesis" in result.trace

    async def test_run_dialectic_custom_parameters(self):
        """Test run_dialectic with custom parameters."""
        mock_backend = MockBackend()

        with patch('hegelion.core.get_backend_from_env', return_value=mock_backend):
            with patch('hegelion.core.resolve_backend_for_model', return_value=mock_backend):
                result = await run_dialectic(
                    "Test query",
                    model="custom-model",
                    max_tokens_per_phase=5000
                )

        # Should still work with custom parameters
        assert isinstance(result, HegelionResult)
        assert result.mode == "synthesis"

    async def test_run_dialectic_json_serializable(self):
        """Test that run_dialectic results are JSON serializable."""
        mock_backend = MockBackend()

        with patch('hegelion.core.get_backend_from_env', return_value=mock_backend):
            with patch('hegelion.core.get_engine_settings') as mock_settings:
                mock_settings.return_value = MockSettings()

                result = await run_dialectic("Test query")

        # Should be JSON serializable
        json_str = json.dumps(result.to_dict())
        parsed = json.loads(json_str)

        assert parsed["query"] == "Test query"
        assert parsed["mode"] == "synthesis"
        assert "thesis" in parsed
        assert "antithesis" in parsed
        assert "synthesis" in parsed


class MockSettings:
    """Mock engine settings for testing."""
    def __init__(self):
        self.model = "test-model"
        self.synthesis_threshold = 0.85
        self.max_tokens_per_phase = 10000
        self.validate_results = True
        self.cache_enabled = False
        self.cache_ttl_seconds = 0
        self.cache_dir = "/tmp"


@pytest.mark.asyncio
class TestRunBenchmark:
    """Test the run_benchmark core function."""

    async def test_run_benchmark_with_list(self):
        """Test run_benchmark with prompt list."""
        mock_backend = MockBackend()
        prompts = ["Query 1", "Query 2"]

        with patch('hegelion.core.get_backend_from_env', return_value=mock_backend):
            with patch('hegelion.core.get_engine_settings') as mock_settings:
                mock_settings.return_value = MockSettings()

                results = await run_benchmark(prompts)

        # Should return list of results
        assert len(results) == 2
        assert all(isinstance(r, HegelionResult) for r in results)
        assert results[0].query == "Query 1"
        assert results[1].query == "Query 2"

    async def test_run_benchmark_with_file(self, tmp_path):
        """Test run_benchmark with prompt file."""
        # Create temporary prompt file
        prompts_file = tmp_path / "prompts.jsonl"
        prompts_file.write_text('{"prompt": "Query 1"}\n{"query": "Query 2"}\nSimple query 3\n')

        mock_backend = MockBackend()

        with patch('hegelion.core.get_backend_from_env', return_value=mock_backend):
            with patch('hegelion.core.get_engine_settings') as mock_settings:
                mock_settings.return_value = MockSettings()

                results = await run_benchmark(prompts_file)

        # Should parse all prompts
        assert len(results) == 3
        assert results[0].query == "Query 1"
        assert results[1].query == "Query 2"
        assert results[2].query == "Simple query 3"

    async def test_run_benchmark_with_output_file(self, tmp_path):
        """Test run_benchmark with output file."""
        prompts = ["Query 1", "Query 2"]
        output_file = tmp_path / "output.jsonl"
        mock_backend = MockBackend()

        with patch('hegelion.core.get_backend_from_env', return_value=mock_backend):
            with patch('hegelion.core.get_engine_settings') as mock_settings:
                mock_settings.return_value = MockSettings()

                results = await run_benchmark(prompts, output_file=output_file)

        # Should create output file
        assert output_file.exists()

        # Should contain valid JSONL
        content = output_file.read_text()
        lines = content.strip().split('\n')
        assert len(lines) == 2

        # Each line should be valid JSON
        for line in lines:
            parsed = json.loads(line)
            assert "query" in parsed
            assert "mode" in parsed

    async def test_run_benchmark_empty_prompts(self):
        """Test run_benchmark with empty prompts."""
        mock_backend = MockBackend()

        with patch('hegelion.core.get_backend_from_env', return_value=mock_backend):
            results = await run_benchmark([])

        # Should return empty list
        assert results == []

    async def test_run_benchmark_nonexistent_file(self):
        """Test run_benchmark with nonexistent file."""
        nonexistent_file = Path("/nonexistent/path.jsonl")
        mock_backend = MockBackend()

        with patch('hegelion.core.get_backend_from_env', return_value=mock_backend):
            with pytest.raises(FileNotFoundError):
                await run_benchmark(nonexistent_file)

    async def test_run_benchmark_with_debug(self):
        """Test run_benchmark with debug mode."""
        prompts = ["Query 1"]
        mock_backend = MockBackend()

        with patch('hegelion.core.get_backend_from_env', return_value=mock_backend):
            with patch('hegelion.core.get_engine_settings') as mock_settings:
                mock_settings.return_value = MockSettings()

                results = await run_benchmark(prompts, debug=True)

        # Should include debug information
        result = results[0]
        assert "debug" in result.metadata
        assert result.trace is not None

    async def test_run_benchmark_with_prompt_objects(self):
        """run_benchmark should accept prompt dictionaries."""
        mock_backend = MockBackend()
        prompts = [
            {"query": "Query 1"},
            {"prompt": "Query 2"},
        ]

        with patch('hegelion.core.get_backend_from_env', return_value=mock_backend):
            with patch('hegelion.core.get_engine_settings') as mock_settings:
                mock_settings.return_value = MockSettings()

                results = await run_benchmark(prompts)

        assert [r.query for r in results] == ["Query 1", "Query 2"]


@pytest.mark.asyncio
class TestHighLevelAPIs:
    """Tests for dialectic/quickstart helpers."""

    async def test_dialectic_uses_model_autodetect(self):
        mock_backend = MockBackend()

        with patch('hegelion.core.resolve_backend_for_model', return_value=mock_backend):
            with patch('hegelion.core.get_engine_settings') as mock_settings:
                mock_settings.return_value = MockSettings()

                result = await dialectic("Test query", model="claude-4.5-sonnet")

        assert isinstance(result, HegelionResult)
        assert result.query == "Test query"

    async def test_quickstart_defaults_to_env(self):
        mock_backend = MockBackend()

        with patch('hegelion.core.get_backend_from_env', return_value=mock_backend):
            with patch('hegelion.core.get_engine_settings') as mock_settings:
                mock_settings.return_value = MockSettings()

                result = await quickstart("Test query")

        assert isinstance(result, HegelionResult)
        assert result.query == "Test query"


class TestSynchronousWrappers:
    """Test synchronous wrapper functions."""

    @patch('hegelion.core.asyncio.run')
    def test_run_dialectic_sync(self, mock_run):
        """Test synchronous run_dialectic wrapper."""
        mock_run.return_value = "test_result"

        from hegelion.core import run_dialectic_sync
        result = run_dialectic_sync("test query")

        assert result == "test_result"
        mock_run.assert_called_once()

    @patch('hegelion.core.asyncio.run')
    def test_run_benchmark_sync(self, mock_run):
        """Test synchronous run_benchmark wrapper."""
        mock_run.return_value = "test_results"

        from hegelion.core import run_benchmark_sync
        result = run_benchmark_sync(["test query"])

        assert result == "test_results"
        mock_run.assert_called_once()

    @patch('hegelion.core.asyncio.run')
    def test_dialectic_sync(self, mock_run):
        """Test synchronous dialectic wrapper."""
        mock_run.return_value = "test_result"

        from hegelion.core import dialectic_sync
        result = dialectic_sync("test query")

        assert result == "test_result"
        mock_run.assert_called_once()

    @patch('hegelion.core.asyncio.run')
    def test_quickstart_sync(self, mock_run):
        """Test synchronous quickstart wrapper."""
        mock_run.return_value = "test_result"

        from hegelion.core import quickstart_sync
        result = quickstart_sync("test query")

        assert result == "test_result"
        mock_run.assert_called_once()

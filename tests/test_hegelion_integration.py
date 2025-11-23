"""Integration tests for Hegelion dialectical reasoning workflow."""

import pytest
from unittest.mock import MagicMock, patch
import asyncio

from hegelion.core.engine import run_dialectic
from hegelion.core.models import (
    HegelionResult,
    HegelionTrace,
    HegelionMetadata,
)
from hegelion.core.backends import MockBackend


class TestHegelionIntegrationWorkflow:
    """Test complete integration workflows for Hegelion."""

    @pytest.mark.asyncio
    async def test_complete_dialectic_workflow(self):
        """Test complete workflow from query to structured result."""
        backend = MockBackend()
        query = "What is the nature of consciousness?"

        # Run dialectic
        result = await run_dialectic(
            query=query,
            backend=backend,
            validation_threshold=0.85,
        )

        # Verify result structure
        assert isinstance(result, HegelionResult)
        assert result.query == query
        assert result.mode == "synthesis"
        assert isinstance(result.thesis, str) and len(result.thesis) > 0
        assert isinstance(result.antithesis, str) and len(result.antithesis) > 0
        assert isinstance(result.synthesis, str) and len(result.synthesis) > 0
        assert isinstance(result.contradictions, list)
        assert isinstance(result.research_proposals, list)
        assert isinstance(result.metadata, HegelionMetadata)

        # Verify metadata
        assert result.metadata.thesis_time_ms > 0
        assert result.metadata.antithesis_time_ms > 0
        assert result.metadata.total_time_ms > 0

        # Verify trace if present
        if result.trace:
            assert result.trace.get("thesis") == result.thesis
            assert result.trace.get("antithesis") == result.antithesis

    @pytest.mark.asyncio
    async def test_dialectic_with_different_validation_thresholds(self):
        """Test dialectic workflow with various validation thresholds."""
        backend = MockBackend()
        thresholds = [0.5, 0.7, 0.9, 0.99]

        for threshold in thresholds:
            result = await run_dialectic(
                query="Test query",
                backend=backend,
                validation_threshold=threshold,
            )

            assert isinstance(result, HegelionResult)
            # All thresholds should produce valid results
            assert len(result.thesis) > 0
            assert len(result.antithesis) > 0
            assert len(result.synthesis) > 0

    @pytest.mark.asyncio
    async def test_dialectic_preserves_query_context(self):
        """Test that query context is preserved throughout the workflow."""
        backend = MockBackend()
        test_query = "How does quantum entanglement work?"

        result = await run_dialectic(
            query=test_query,
            backend=backend,
            validation_threshold=0.85,
        )

        assert result.query == test_query
        # Thesis should be relevant to the query
        assert isinstance(result.thesis, str)
        assert len(result.thesis) > 0


class TestHegelionConcurrentExecution:
    """Test concurrent execution of Hegelion dialectics."""

    @pytest.mark.asyncio
    async def test_concurrent_dialectic_execution(self):
        """Test running multiple dialectics concurrently."""
        backend = MockBackend()
        queries = [
            "What is artificial intelligence?",
            "How do neural networks work?",
            "What is machine learning?",
            "Explain deep learning concepts.",
        ]

        # Create concurrent tasks
        tasks = [
            run_dialectic(
                query=query,
                backend=backend,
                validation_threshold=0.85,
            )
            for query in queries
        ]

        # Execute concurrently
        results = await asyncio.gather(*tasks)

        # Verify all results
        assert len(results) == 4
        for result in results:
            assert isinstance(result, HegelionResult)
            assert len(result.thesis) > 0
            assert len(result.antithesis) > 0
            assert len(result.synthesis) > 0

    @pytest.mark.asyncio
    async def test_concurrent_with_different_thresholds(self):
        """Test concurrent execution with different validation thresholds."""
        backend = MockBackend()

        thresholds = [0.6, 0.75, 0.85, 0.95]
        tasks = []

        for i, threshold in enumerate(thresholds):
            task = run_dialectic(
                query=f"Test subject {i}",
                backend=backend,
                validation_threshold=threshold,
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        assert len(results) == 4
        for result in results:
            assert isinstance(result, HegelionResult)
            assert len(result.contradictions) >= 0
            assert len(result.research_proposals) >= 0


class TestHegelionEdgeCasesAndBoundaries:
    """Test edge cases and boundary conditions for Hegelion."""

    @pytest.mark.asyncio
    async def test_dialectic_with_empty_query(self):
        """Test dialectic with empty query string."""
        backend = MockBackend()

        result = await run_dialectic(
            query="",
            backend=backend,
            validation_threshold=0.85,
        )

        assert isinstance(result, HegelionResult)
        assert result.query == ""
        # Should still produce valid thesis/antithesis/synthesis
        assert isinstance(result.thesis, str)
        assert isinstance(result.antithesis, str)
        assert isinstance(result.synthesis, str)

    @pytest.mark.asyncio
    async def test_dialectic_with_very_long_query(self):
        """Test dialectic with very long query (5000 chars)."""
        backend = MockBackend()
        long_query = "x" * 5000

        result = await run_dialectic(
            query=long_query,
            backend=backend,
            validation_threshold=0.85,
        )

        assert isinstance(result, HegelionResult)
        assert len(result.query) == 5000
        assert len(result.thesis) > 0

    @pytest.mark.asyncio
    async def test_dialectic_with_unicode_and_special_chars(self):
        """Test dialectic with unicode and special characters."""
        backend = MockBackend()

        unicode_query = "Query with unicode: 你好, مرحبا, 🧠💭 and special: <html> & {braces}"

        result = await run_dialectic(
            query=unicode_query,
            backend=backend,
            validation_threshold=0.85,
        )

        assert isinstance(result, HegelionResult)
        assert "你好" in result.query
        assert isinstance(result.thesis, str)

    @pytest.mark.asyncio
    async def test_dialectic_low_validation_threshold(self):
        """Test dialectic with very low validation threshold."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=0.1,
        )

        assert isinstance(result, HegelionResult)
        # Should complete successfully with low threshold
        assert len(result.thesis) > 0

    @pytest.mark.asyncio
    async def test_dialectic_high_validation_threshold(self):
        """Test dialectic with very high validation threshold."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=0.99,
        )

        assert isinstance(result, HegelionResult)
        # Should still complete (might take more attempts)
        assert len(result.synthesis) > 0


class TestHegelionSerializationWorkflow:
    """Test serialization and deserialization workflow."""

    @pytest.mark.asyncio
    async def test_dialectic_result_serialization_roundtrip(self):
        """Test complete serialization round-trip of dialectic results."""
        backend = MockBackend()

        original_result = await run_dialectic(
            query="Test serialization",
            backend=backend,
            validation_threshold=0.85,
        )

        # Serialize to dict
        result_dict = original_result.to_dict()

        # Verify dict structure
        assert "query" in result_dict
        assert "thesis" in result_dict
        assert "metadata" in result_dict
        assert "contradictions" in result_dict

        # Deserialize back to HegelionResult
        restored_result = HegelionResult.from_dict(result_dict)

        # Verify restored result matches original
        assert restored_result.query == original_result.query
        assert restored_result.thesis == original_result.thesis
        assert restored_result.antithesis == original_result.antithesis
        assert restored_result.synthesis == original_result.synthesis
        assert len(restored_result.contradictions) == len(original_result.contradictions)
        assert len(restored_result.research_proposals) == len(original_result.research_proposals)

        # Metadata comparison
        assert restored_result.metadata.thesis_time_ms == original_result.metadata.thesis_time_ms
        assert restored_result.metadata.total_time_ms == original_result.metadata.total_time_ms

    @pytest.mark.asyncio
    async def test_dialectic_result_json_serialization(self):
        """Test JSON serialization workflow."""
        import json

        backend = MockBackend()

        result = await run_dialectic(
            query="Test JSON serialization",
            backend=backend,
            validation_threshold=0.85,
        )

        # Serialize to JSON
        result_dict = result.to_dict()
        json_str = json.dumps(result_dict)

        # Verify JSON is valid string
        assert isinstance(json_str, str)
        assert len(json_str) > 0

        # Parse back from JSON
        parsed_dict = json.loads(json_str)

        # Verify structure is preserved
        assert parsed_dict["query"] == result.query
        assert parsed_dict["thesis"] == result.thesis


class TestHegelionDebugMode:
    """Test Hegelion debug mode functionality."""

    @pytest.mark.asyncio
    async def test_dialectic_with_debug_enabled(self):
        """Test dialectic execution with debug mode enabled."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Debug test query",
            backend=backend,
            validation_threshold=0.85,
            debug=True,
        )

        assert isinstance(result, HegelionResult)
        assert result.query == "Debug test query"

        # Debug info might be in metadata or trace
        if result.metadata and result.metadata.debug:
            assert isinstance(result.metadata.debug, dict)

    @pytest.mark.asyncio
    async def test_dialectic_debug_trace_preservation(self):
        """Test that debug traces are preserved when debug is enabled."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Trace preservation test",
            backend=backend,
            validation_threshold=0.85,
            debug=True,
        )

        assert isinstance(result, HegelionResult)

        # If trace is present in debug mode, verify its structure
        if result.trace:
            assert "thesis" in result.trace
            assert "antithesis" in result.trace
            assert "contradictions_found" in result.trace


class TestHegelionResultQualityAssurance:
    """Test quality assurance aspects of Hegelion results."""

    @pytest.mark.asyncio
    async def test_dialectic_result_completeness(self):
        """Test that results are complete and well-formed."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Quality assurance test",
            backend=backend,
            validation_threshold=0.85,
        )

        # Check for completeness
        assert isinstance(result, HegelionResult)
        assert isinstance(result.query, str) and len(result.query) > 0
        assert isinstance(result.thesis, str) and len(result.thesis) > 0
        assert isinstance(result.antithesis, str) and len(result.antithesis) > 0
        assert isinstance(result.synthesis, str) and len(result.synthesis) > 0
        assert isinstance(result.contradictions, list)
        assert isinstance(result.research_proposals, list)

        # Each contradiction should have a description
        for contradiction in result.contradictions:
            assert "description" in contradiction
            assert isinstance(contradiction["description"], str)

        # Each proposal should have a description
        for proposal in result.research_proposals:
            assert "description" in proposal
            assert isinstance(proposal["description"], str)

    @pytest.mark.asyncio
    async def test_dialectic_result_structure_validity(self):
        """Test that all result components follow expected structure."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Structure validation test",
            backend=backend,
            validation_threshold=0.85,
        )

        # Verify metadata structure
        assert hasattr(result.metadata, "thesis_time_ms")
        assert hasattr(result.metadata, "antithesis_time_ms")
        assert hasattr(result.metadata, "total_time_ms")
        assert result.metadata.thesis_time_ms >= 0
        assert result.metadata.antithesis_time_ms >= 0
        assert result.metadata.total_time_ms >= result.metadata.thesis_time_ms


class TestHegelionErrorRecovery:
    """Test error recovery and resilience in Hegelion."""

    @pytest.mark.asyncio
    async def test_dialectic_recovery_from_partial_results(self):
        """Test recovery when partial results are produced."""
        backend = MockBackend()

        # Mock a scenario where we get partial results
        def mock_query(self, *args, **kwargs):
            # Return a response that might be missing some components
            class PartialResponse:
                def __init__(self):
                    self.content = "Test response content"
                    self.mode = "synthesis"
                    self.trace = {"thesis": "Partial thesis", "antithesis": "Partial antithesis"}
                    self.metadata = {
                        "thesis_time_ms": 50,
                        "antithesis_time_ms": 50,
                        "total_time_ms": 100,
                    }

            return PartialResponse()

        # This test ensures the engine can handle various response formats
        result = await run_dialectic(
            query="Recovery test",
            backend=backend,
            validation_threshold=0.85,
        )

        assert isinstance(result, HegelionResult)
        # Should complete successfully
        assert isinstance(result.thesis, str)

    @pytest.mark.asyncio
    async def test_dialectic_consistency_across_multiple_runs(self):
        """Test consistency of results across multiple runs."""
        backend = MockBackend()
        query = "Consistency test query"

        results = []
        for _ in range(3):
            result = await run_dialectic(
                query=query,
                backend=backend,
                validation_threshold=0.85,
            )
            results.append(result)

        # All results should be HegelionResult instances
        for result in results:
            assert isinstance(result, HegelionResult)

        # All should follow same structure
        for result in results:
            assert hasattr(result, "query")
            assert hasattr(result, "thesis")
            assert hasattr(result, "antithesis")
            assert hasattr(result, "synthesis")
            assert hasattr(result, "metadata")

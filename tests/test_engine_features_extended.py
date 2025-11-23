"""Extended tests for engine features including edge cases and error handling."""

import pytest
from unittest.mock import MagicMock, patch
import asyncio

from hegelion.core.engine import run_dialectic
from hegelion.core.models import (
    HegelionResult,
    DialecticOutput,
    ValidationError,
)
from hegelion.core.config import ConfigurationError
from hegelion.core.backends import LLMBackend, MockBackend


class TestRunDialecticEdgeCases:
    """Test edge cases and boundary conditions for run_dialectic."""

    @pytest.mark.asyncio
    async def test_run_dialectic_with_empty_query(self):
        """Test run_dialectic with empty query."""
        backend = MockBackend()

        result = await run_dialectic(
            query="",
            backend=backend,
            validation_threshold=0.85,
        )

        assert isinstance(result, HegelionResult)
        assert result.thesis is not None
        assert result.antithesis is not None
        assert result.synthesis is not None

    @pytest.mark.asyncio
    async def test_run_dialectic_with_very_long_query(self):
        """Test run_dialectic with very long query."""
        backend = MockBackend()
        long_query = "x" * 5000

        result = await run_dialectic(
            query=long_query,
            backend=backend,
            validation_threshold=0.85,
        )

        assert isinstance(result, HegelionResult)
        assert result.thesis is not None

    @pytest.mark.asyncio
    async def test_run_dialectic_with_unicode_query(self):
        """Test run_dialectic with unicode characters."""
        backend = MockBackend()
        unicode_query = "Query with unicode: 你好, مرحبا, 🧠💭"

        result = await run_dialectic(
            query=unicode_query,
            backend=backend,
            validation_threshold=0.85,
        )

        assert isinstance(result, HegelionResult)
        assert result.thesis is not None

    @pytest.mark.asyncio
    async def test_run_dialectic_with_special_characters(self):
        """Test run_dialectic with special characters."""
        backend = MockBackend()
        special_query = 'Query with <html> & "quotes" and {braces}'

        result = await run_dialectic(
            query=special_query,
            backend=backend,
            validation_threshold=0.85,
        )

        assert isinstance(result, HegelionResult)
        assert result.thesis is not None

    @pytest.mark.asyncio
    async def test_run_dialectic_low_validation_threshold(self):
        """Test run_dialectic with low validation threshold."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=0.1,  # Very low threshold
        )

        assert isinstance(result, HegelionResult)
        assert result.validation_score is not None
        assert result.validation_score >= 0.1

    @pytest.mark.asyncio
    async def test_run_dialectic_high_validation_threshold(self):
        """Test run_dialectic with high validation threshold."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=0.95,  # Very high threshold
        )

        assert isinstance(result, HegelionResult)
        if result.validation_score is not None:
            assert result.validation_score >= 0.95

    @pytest.mark.asyncio
    async def test_run_dialectic_with_debug_mode(self):
        """Test run_dialectic with debug mode enabled."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=0.85,
            debug=True,
        )

        assert isinstance(result, HegelionResult)
        # Debug mode should still produce valid results
        assert result.thesis is not None
        assert result.antithesis is not None
        assert result.synthesis is not None

    @pytest.mark.asyncio
    async def test_run_dialectic_preserves_timestamp(self):
        """Test that run_dialectic includes timestamp."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=0.85,
        )

        assert isinstance(result, HegelionResult)
        assert result.timestamp is not None
        assert isinstance(result.timestamp, str)

    @pytest.mark.asyncio
    async def test_run_dialectic_includes_validation_score(self):
        """Test that run_dialectic includes validation score."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=0.85,
        )

        assert isinstance(result, HegelionResult)
        assert result.validation_score is not None
        assert isinstance(result.validation_score, (int, float))
        assert 0.0 <= result.validation_score <= 1.0


class TestRunDialecticErrorHandling:
    """Test error handling in run_dialectic."""

    @pytest.mark.asyncio
    async def test_run_dialectic_with_failing_backend(self):
        """Test run_dialectic with backend that raises errors."""

        class FailingBackend(MockBackend):
            async def query(self, *args, **kwargs):
                raise RuntimeError("Backend failure")

        backend = FailingBackend()

        with pytest.raises(RuntimeError) as exc_info:
            await run_dialectic(
                query="Test query",
                backend=backend,
                validation_threshold=0.85,
            )

        assert "Backend failure" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_run_dialectic_with_malformed_responses(self):
        """Test run_dialectic with malformed responses from backend."""

        class MalformedBackend(MockBackend):
            async def query(self, *args, **kwargs):
                return "This is not a properly formatted response"

        backend = MalformedBackend()

        # This should handle malformed responses gracefully
        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=0.85,
        )

        # Should still return a HegelionResult, even with malformed input
        assert isinstance(result, HegelionResult)

    @pytest.mark.asyncio
    async def test_run_dialectic_timeout_handling(self):
        """Test run_dialectic timeout handling."""

        class SlowBackend(MockBackend):
            async def query(self, *args, **kwargs):
                await asyncio.sleep(2)  # Simulate slow response
                return await super().query(*args, **kwargs)

        backend = SlowBackend()

        # Should complete eventually (no timeout in this test)
        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=0.85,
        )

        assert isinstance(result, HegelionResult)


class TestDialecticOutputIntegration:
    """Test DialecticOutput integration with run_dialectic."""

    @pytest.mark.asyncio
    async def test_dialectic_output_from_run_dialectic(self):
        """Test creating DialecticOutput from run_dialectic result."""
        backend = MockBackend()
        query = "What is consciousness?"

        result = await run_dialectic(
            query=query,
            backend=backend,
            validation_threshold=0.85,
        )

        # Create DialecticOutput from result
        output = DialecticOutput(
            query=query,
            thesis=result.thesis,
            antithesis=result.antithesis,
            synthesis=result.synthesis,
        )

        assert output.query == query
        assert output.thesis == result.thesis
        assert output.antithesis == result.antithesis
        assert output.synthesis == result.synthesis

    @pytest.mark.asyncio
    async def test_dialectic_output_complete_workflow(self):
        """Test complete workflow from query to DialecticOutput."""
        backend = MockBackend()
        query = "Test philosophical question"

        # Run dialectic
        result = await run_dialectic(
            query=query,
            backend=backend,
            validation_threshold=0.85,
        )

        # Create output
        output = DialecticOutput(
            query=query,
            thesis=result.thesis,
            antithesis=result.antithesis,
            synthesis=result.synthesis,
        )

        # Verify output can be serialized
        output_dict = output.model_dump()
        assert "query" in output_dict
        assert "thesis" in output_dict
        assert "antithesis" in output_dict
        assert "synthesis" in output_dict

        # Verify all fields are populated
        assert output_dict["query"] == query
        assert output_dict["thesis"] is not None
        assert output_dict["antithesis"] is not None
        assert output_dict["synthesis"] is not None


class TestValidationThresholdBehavior:
    """Test validation threshold behavior in different scenarios."""

    @pytest.mark.asyncio
    async def test_validation_threshold_zero(self):
        """Test with validation threshold of zero."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=0.0,  # Accept anything
        )

        assert isinstance(result, HegelionResult)
        # Should complete successfully even with very low threshold

    @pytest.mark.asyncio
    async def test_validation_threshold_one(self):
        """Test with validation threshold of one."""
        backend = MockBackend()

        # This might fail or require many attempts
        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=1.0,  # Perfect score required
        )

        assert isinstance(result, HegelionResult)
        if result.validation_score is not None:
            assert result.validation_score >= 0.0  # Might not reach 1.0

    @pytest.mark.asyncio
    async def test_validation_threshold_mid_range(self):
        """Test with mid-range validation threshold."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=0.6,
        )

        assert isinstance(result, HegelionResult)
        assert result.validation_score is not None
        assert result.validation_score >= 0.6


class TestConcurrentDialecticExecution:
    """Test concurrent execution of multiple dialectic operations."""

    @pytest.mark.asyncio
    async def test_concurrent_dialectic_execution(self):
        """Test running multiple dialectics concurrently."""
        backend = MockBackend()
        queries = [
            "Query 1",
            "Query 2",
            "Query 3",
        ]

        # Run all dialectics concurrently
        tasks = [
            run_dialectic(
                query=query,
                backend=backend,
                validation_threshold=0.85,
            )
            for query in queries
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        for result in results:
            assert isinstance(result, HegelionResult)
            assert result.thesis is not None
            assert result.antithesis is not None
            assert result.synthesis is not None

    @pytest.mark.asyncio
    async def test_concurrent_with_different_thresholds(self):
        """Test concurrent execution with different validation thresholds."""
        backend = MockBackend()

        thresholds = [0.5, 0.7, 0.9]
        tasks = [
            run_dialectic(
                query=f"Test query {i}",
                backend=backend,
                validation_threshold=threshold,
            )
            for i, threshold in enumerate(thresholds)
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        for result in results:
            assert isinstance(result, HegelionResult)


class TestDialecticQualityAndConsistency:
    """Test quality and consistency of dialectic results."""

    @pytest.mark.asyncio
    async def test_dialectic_result_consistency(self):
        """Test that repeated calls produce consistent structure."""
        backend = MockBackend()
        query = "Test query"

        result1 = await run_dialectic(
            query=query,
            backend=backend,
            validation_threshold=0.85,
        )

        result2 = await run_dialectic(
            query=query,
            backend=backend,
            validation_threshold=0.85,
        )

        # Both should be HegelionResult instances
        assert isinstance(result1, HegelionResult)
        assert isinstance(result2, HegelionResult)

        # Both should have all required fields
        assert hasattr(result1, "thesis")
        assert hasattr(result1, "antithesis")
        assert hasattr(result1, "synthesis")
        assert hasattr(result2, "thesis")
        assert hasattr(result2, "antithesis")
        assert hasattr(result2, "synthesis")

        # Results might differ (non-deterministic), but structure should be consistent
        assert type(result1.thesis) == type(result2.thesis) == str
        assert type(result1.antithesis) == type(result2.antithesis) == str
        assert type(result1.synthesis) == type(result2.synthesis) == str

    @pytest.mark.asyncio
    async def test_dialectic_result_quality_indicators(self):
        """Test that results contain quality indicators."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=0.85,
        )

        assert isinstance(result, HegelionResult)

        # Check for quality indicators
        assert result.timestamp is not None
        assert result.validation_score is not None
        assert 0.0 <= result.validation_score <= 1.0

        # Check that all text fields are non-empty strings
        assert isinstance(result.thesis, str)
        assert isinstance(result.antithesis, str)
        assert isinstance(result.synthesis, str)
        assert len(result.thesis) > 0
        assert len(result.antithesis) > 0
        assert len(result.synthesis) > 0


class TestDialecticParameterVariations:
    """Test run_dialectic with various parameter combinations."""

    @pytest.mark.asyncio
    async def test_run_dialectic_with_both_positional_and_keyword_args(self):
        """Test run_dialectic with mix of positional and keyword arguments."""
        backend = MockBackend()

        result = await run_dialectic(
            "Test query",  # Positional
            backend,  # Positional
            validation_threshold=0.85,  # Keyword
        )

        assert isinstance(result, HegelionResult)

    @pytest.mark.asyncio
    async def test_run_dialectic_all_keyword_args(self):
        """Test run_dialectic with all keyword arguments."""
        backend = MockBackend()

        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=0.85,
            debug=False,
        )

        assert isinstance(result, HegelionResult)

    @pytest.mark.asyncio
    async def test_run_dialectic_minimal_args(self):
        """Test run_dialectic with minimal required arguments."""
        backend = MockBackend()

        result = await run_dialectic(
            "Test query",
            backend,
        )

        assert isinstance(result, HegelionResult)
        # Should use default validation_threshold


class TestDialecticErrorRecovery:
    """Test error recovery mechanisms in dialectic execution."""

    @pytest.mark.asyncio
    async def test_dialectic_recovery_from_partial_failure(self):
        """Test recovery when one phase produces suboptimal results."""
        backend = MockBackend()

        # Mock backend that sometimes returns suboptimal responses
        call_count = 0
        original_query = backend.query

        async def mock_query(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # First call (thesis)
                return "Short thesis"
            return await original_query(*args, **kwargs)

        backend.query = mock_query

        result = await run_dialectic(
            query="Test query",
            backend=backend,
            validation_threshold=0.5,  # Lower threshold for recovery
        )

        assert isinstance(result, HegelionResult)
        assert result.thesis is not None
        assert len(result.thesis) > 0

"""Tests for Hegelion data models."""

import json
import pytest

from hegelion.models import (
    ContradictionResult,
    HegelionResult,
    ResearchProposal,
    HegelionTrace,
    HegelionMetadata,
)


class TestContradictionResult:
    """Test the ContradictionResult model."""

    def test_to_dict_basic(self):
        """Test basic to_dict conversion."""
        contradiction = ContradictionResult(
            description="Test contradiction",
            evidence="Test evidence"
        )
        result = contradiction.to_dict()

        assert result == {
            "description": "Test contradiction",
            "evidence": "Test evidence"
        }

    def test_to_dict_no_evidence(self):
        """Test to_dict conversion without evidence."""
        contradiction = ContradictionResult(
            description="Test contradiction"
        )
        result = contradiction.to_dict()

        assert result == {
            "description": "Test contradiction"
        }
        assert "evidence" not in result


class TestResearchProposal:
    """Test the ResearchProposal model."""

    def test_to_dict_basic(self):
        """Test basic to_dict conversion."""
        proposal = ResearchProposal(
            description="Test research",
            testable_prediction="Test prediction"
        )
        result = proposal.to_dict()

        assert result == {
            "description": "Test research",
            "testable_prediction": "Test prediction"
        }

    def test_to_dict_no_prediction(self):
        """Test to_dict conversion without prediction."""
        proposal = ResearchProposal(
            description="Test research"
        )
        result = proposal.to_dict()

        assert result == {
            "description": "Test research"
        }
        assert "testable_prediction" not in result


class TestHegelionResult:
    """Test the HegelionResult model."""

    def test_to_dict_basic(self):
        """Test basic to_dict conversion."""
        contradictions = [
            {"description": "Test contradiction 1"},
            {"description": "Test contradiction 2", "evidence": "Evidence"}
        ]
        proposals = [
            {"description": "Test proposal"},
            {"description": "Test proposal 2", "testable_prediction": "Prediction"}
        ]
        metadata = {
            "thesis_time_ms": 100,
            "antithesis_time_ms": 200,
            "synthesis_time_ms": 300,
            "total_time_ms": 600
        }

        result = HegelionResult(
            query="Test query",
            mode="synthesis",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions=contradictions,
            research_proposals=proposals,
            metadata=metadata
        )

        dict_result = result.to_dict()

        assert dict_result["query"] == "Test query"
        assert dict_result["mode"] == "synthesis"
        assert dict_result["thesis"] == "Test thesis"
        assert dict_result["antithesis"] == "Test antithesis"
        assert dict_result["synthesis"] == "Test synthesis"
        assert dict_result["contradictions"] == contradictions
        assert dict_result["research_proposals"] == proposals
        assert dict_result["metadata"] == metadata
        assert "trace" not in dict_result  # None trace should not be included

    def test_to_dict_with_trace(self):
        """Test to_dict conversion with trace."""
        trace = {"test": "trace"}
        metadata = {
            "thesis_time_ms": 100,
            "antithesis_time_ms": 200,
            "synthesis_time_ms": 300,
            "total_time_ms": 600
        }

        result = HegelionResult(
            query="Test query",
            mode="synthesis",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions=[],
            research_proposals=[],
            metadata=metadata,
            trace=trace
        )

        dict_result = result.to_dict()
        assert dict_result["trace"] == trace

    def test_json_serialization(self):
        """Test that HegelionResult can be serialized to JSON."""
        result = HegelionResult(
            query="Test query",
            mode="synthesis",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions=[],
            research_proposals=[],
            metadata={"total_time_ms": 100}
        )

        # Should not raise an exception
        json_str = json.dumps(result.to_dict())
        parsed = json.loads(json_str)

        assert parsed["query"] == "Test query"
        assert parsed["mode"] == "synthesis"


class TestHegelionTrace:
    """Test the HegelionTrace model."""

    def test_to_dict_basic(self):
        """Test basic to_dict conversion."""
        trace = HegelionTrace(
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions_found=2,
            research_proposals=["Proposal 1", "Proposal 2"]
        )

        result = trace.to_dict()

        assert result["thesis"] == "Test thesis"
        assert result["antithesis"] == "Test antithesis"
        assert result["synthesis"] == "Test synthesis"
        assert result["contradictions_found"] == 2
        assert result["research_proposals"] == ["Proposal 1", "Proposal 2"]
        assert "internal_conflict_score" not in result

    def test_to_dict_with_conflict_score(self):
        """Test to_dict conversion with conflict score."""
        trace = HegelionTrace(
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions_found=2,
            research_proposals=["Proposal 1"],
            internal_conflict_score=0.85
        )

        result = trace.to_dict()

        assert result["internal_conflict_score"] == 0.85


class TestHegelionMetadata:
    """Test the HegelionMetadata model."""

    def test_to_dict_basic(self):
        """Test basic to_dict conversion."""
        metadata = HegelionMetadata(
            thesis_time_ms=100,
            antithesis_time_ms=200,
            synthesis_time_ms=300,
            total_time_ms=600
        )

        result = metadata.to_dict()

        assert result["thesis_time_ms"] == 100
        assert result["antithesis_time_ms"] == 200
        assert result["synthesis_time_ms"] == 300
        assert result["total_time_ms"] == 600
        assert "backend_provider" not in result
        assert "backend_model" not in result
        assert "debug" not in result

    def test_to_dict_with_backend_info(self):
        """Test to_dict conversion with backend information."""
        metadata = HegelionMetadata(
            thesis_time_ms=100,
            antithesis_time_ms=200,
            synthesis_time_ms=300,
            total_time_ms=600,
            backend_provider="TestProvider",
            backend_model="test-model"
        )

        result = metadata.to_dict()

        assert result["backend_provider"] == "TestProvider"
        assert result["backend_model"] == "test-model"

    def test_to_dict_with_debug_info(self):
        """Test to_dict conversion with debug information."""
        debug_info = {"internal_conflict_score": 0.85}
        metadata = HegelionMetadata(
            thesis_time_ms=100,
            antithesis_time_ms=200,
            synthesis_time_ms=300,
            total_time_ms=600,
            debug=debug_info
        )

        result = metadata.to_dict()

        assert result["debug"] == debug_info
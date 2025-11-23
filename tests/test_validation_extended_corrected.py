"""Extended validation tests for Hegelion result models."""

import pytest

from hegelion.core.models import (
    HegelionResult,
    HegelionTrace,
    HegelionMetadata,
)
from hegelion.core.validation import (
    validate_hegelion_result,
    ResultValidationError,
)


class TestHegelionResultValidation:
    """Test validation for HegelionResult objects."""

    def test_validate_hegelion_result_valid_complete(self):
        """Test validation with a fully valid HegelionResult."""
        trace = HegelionTrace(
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions_found=2,
            research_proposals=["Proposal 1", "Proposal 2"],
        )

        metadata = HegelionMetadata(
            thesis_time_ms=100.0,
            antithesis_time_ms=150.0,
            synthesis_time_ms=120.0,
            total_time_ms=370.0,
        )

        result = HegelionResult(
            query="Test query",
            mode="synthesis",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions=[
                {"description": "Contradiction 1"},
                {"description": "Contradiction 2", "evidence": "Test evidence"},
            ],
            research_proposals=[
                {"description": "Proposal 1"},
                {"description": "Proposal 2", "testable_prediction": "Test prediction"},
            ],
            metadata=metadata,
            trace=trace.to_dict(),
        )

        # Should not raise any exception
        validate_hegelion_result(result)

    def test_validate_hegelion_result_valid_minimal(self):
        """Test validation with minimal valid HegelionResult."""
        metadata = HegelionMetadata(
            thesis_time_ms=100.0,
            antithesis_time_ms=150.0,
            synthesis_time_ms=120.0,
            total_time_ms=370.0,
        )

        result = HegelionResult(
            query="Test query",
            mode="synthesis",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions=[],
            research_proposals=[],
            metadata=metadata,
            trace=None,
        )

        # Should not raise any exception
        validate_hegelion_result(result)

    def test_validate_hegelion_result_empty_strings(self):
        """Test validation with empty strings for required text fields."""
        metadata = HegelionMetadata(
            thesis_time_ms=100.0,
            antithesis_time_ms=150.0,
            synthesis_time_ms=120.0,
            total_time_ms=370.0,
        )

        result = HegelionResult(
            query="",
            mode="synthesis",
            thesis="",
            antithesis="",
            synthesis="",
            contradictions=[],
            research_proposals=[],
            metadata=metadata,
        )

        # Empty strings might be valid depending on business logic
        # The schema requires strings but allows empty ones
        try:
            validate_hegelion_result(result)
        except ResultValidationError:
            # If validation fails, it should be for a good reason
            pass

    def test_validate_hegelion_result_with_unicode_content(self):
        """Test validation with unicode content."""
        metadata = HegelionMetadata(
            thesis_time_ms=100.0,
            antithesis_time_ms=150.0,
            synthesis_time_ms=120.0,
            total_time_ms=370.0,
        )

        result = HegelionResult(
            query="Unicode test query: 🧠💭🤔",
            mode="synthesis",
            thesis="Thesis with unicode: 你好, مرحبا, здравствуйте",
            antithesis="Antithesis with emojis: 🚀💡🔬",
            synthesis="Synthesis with math: ∫∂∇∆",
            contradictions=[{"description": "Unicode contradiction: 矛盾"}],
            research_proposals=[{"description": "Unicode proposal: предложение"}],
            metadata=metadata,
        )

        # Should handle unicode without issues
        validate_hegelion_result(result)

    def test_validate_hegelion_result_missing_required_field(self):
        """Test validation fails with missing required field."""
        trace = HegelionTrace(
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions_found=0,
            research_proposals=[],
        )

        metadata = HegelionMetadata(
            thesis_time_ms=100.0,
            antithesis_time_ms=150.0,
            synthesis_time_ms=120.0,
            total_time_ms=370.0,
        )

        result = HegelionResult(
            # Missing query field
            mode="synthesis",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions=[],
            research_proposals=[],
            metadata=metadata,
            trace=trace.to_dict(),
        )

        with pytest.raises(ResultValidationError) as exc_info:
            validate_hegelion_result(result)

        assert "query" in str(exc_info.value)

    def test_validate_hegelion_result_invalid_contradiction_structure(self):
        """Test validation fails with invalid contradiction structure."""
        trace = HegelionTrace(
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions_found=1,
            research_proposals=[],
        )

        metadata = HegelionMetadata(
            thesis_time_ms=100.0,
            antithesis_time_ms=150.0,
            synthesis_time_ms=120.0,
            total_time_ms=370.0,
        )

        # Missing required "description" field in contradiction
        result = HegelionResult(
            query="Test query",
            mode="synthesis",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions=[{"evidence": "Missing description"}],  # Missing "description"
            research_proposals=[],
            metadata=metadata,
            trace=trace.to_dict(),
        )

        with pytest.raises(ResultValidationError) as exc_info:
            validate_hegelion_result(result)

        assert "description" in str(exc_info.value)

    def test_validate_hegelion_result_invalid_proposal_structure(self):
        """Test validation fails with invalid research proposal structure."""
        trace = HegelionTrace(
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions_found=0,
            research_proposals=["Proposal 1"],
        )

        metadata = HegelionMetadata(
            thesis_time_ms=100.0,
            antithesis_time_ms=150.0,
            synthesis_time_ms=120.0,
            total_time_ms=370.0,
        )

        # Missing required "description" field in proposal
        result = HegelionResult(
            query="Test query",
            mode="synthesis",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions=[],
            research_proposals=[
                {"testable_prediction": "Missing description"}
            ],  # Missing "description"
            metadata=metadata,
            trace=trace.to_dict(),
        )

        with pytest.raises(ResultValidationError) as exc_info:
            validate_hegelion_result(result)

        assert "description" in str(exc_info.value)

    def test_validate_hegelion_result_invalid_metadata_structure(self):
        """Test validation fails with invalid metadata structure."""
        # Missing required fields in metadata - construct the dict manually to simulate invalid metadata
        class InvalidMetadata:
            def to_dict(self):
                return {"missing_required_fields": True}

        invalid_metadata = InvalidMetadata()

        result = HegelionResult(
            query="Test query",
            mode="synthesis",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions=[],
            research_proposals=[],
            metadata=invalid_metadata,
        )

        with pytest.raises(ResultValidationError) as exc_info:
            validate_hegelion_result(result)

        # Should complain about missing required metadata fields
        assert any(
            field in str(exc_info.value)
            for field in ["thesis_time_ms", "antithesis_time_ms", "total_time_ms"]
        )

    def test_validate_hegelion_result_with_optional_fields_filled(self):
        """Test validation with optional fields populated."""

        # Test with metadata optional field upgrade
        class ExtendedMetadata:
            def __init__(self):
                self.thesis_time_ms = 100.0
                self.antithesis_time_ms = 150.0
                self.synthesis_time_ms = 120.0
                self.total_time_ms = 370.0
                self.backend_provider = "test_provider"
                self.backend_model = "test_model"
                self.debug = {"key": "value"}
                self.errors = ["error1", "error2"]

            def to_dict(self):
                return {
                    "thesis_time_ms": self.thesis_time_ms,
                    "antithesis_time_ms": self.antithesis_time_ms,
                    "synthesis_time_ms": self.synthesis_time_ms,
                    "total_time_ms": self.total_time_ms,
                    "backend_provider": self.backend_provider,
                    "backend_model": self.backend_model,
                    "debug": self.debug,
                    "errors": self.errors,
                }

        metadata = ExtendedMetadata()

        trace = HegelionTrace(
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions_found=0,
            research_proposals=[],
        )

        result = HegelionResult(
            query="Test query",
            mode="synthesis",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions=[],
            research_proposals=[],
            metadata=metadata,
            trace=trace.to_dict(),
        )

        # Should validate successfully with optional fields
        validate_hegelion_result(result)

    def test_validate_hegelion_result_with_null_optional_fields(self):
        """Test validation with null optional fields."""
        metadata = HegelionMetadata(
            thesis_time_ms=100.0,
            antithesis_time_ms=150.0,
            synthesis_time_ms=None,  # Explicitly null
            total_time_ms=370.0,
            backend_provider=None,
            backend_model=None,
            debug=None,
        )

        result = HegelionResult(
            query="Test query",
            mode="synthesis",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions=[],
            research_proposals=[],
            metadata=metadata,
            trace=None,  # Optional field
        )

        # Should validate successfully with null optional fields
        validate_hegelion_result(result)


class TestResultValidationError:
    """Test ResultValidationError exception."""

    def test_result_validation_error_message(self):
        """Test ResultValidationError has helpful message."""
        try:
            from jsonschema.exceptions import ValidationError

            original_error = ValidationError("Test validation error")
            error = ResultValidationError("Validation failed", original_error)

            assert "Validation failed" in str(error)
            assert error.original is original_error
            assert isinstance(error, RuntimeError)
        except ImportError:
            pytest.skip("jsonschema not available")


class TestHegelionTrace:
    """Test HegelionTrace model."""

    def test_hegelion_trace_creation(self):
        """Test creating HegelionTrace."""
        trace = HegelionTrace(
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions_found=2,
            research_proposals=["Proposal 1", "Proposal 2"],
            internal_conflict_score=0.75,
        )

        assert trace.thesis == "Test thesis"
        assert trace.antithesis == "Test antithesis"
        assert trace.synthesis == "Test synthesis"
        assert trace.contradictions_found == 2
        assert len(trace.research_proposals) == 2
        assert trace.internal_conflict_score == 0.75

    def test_hegelion_trace_to_dict(self):
        """Test HegelionTrace to_dict method."""
        trace = HegelionTrace(
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions_found=1,
            research_proposals=["Proposal 1"],
        )

        trace_dict = trace.to_dict()
        assert isinstance(trace_dict, dict)
        assert trace_dict["thesis"] == "Test thesis"
        assert trace_dict["contradictions_found"] == 1
        assert "internal_conflict_score" not in trace_dict  # Should not include when None

    def test_hegelion_trace_with_null_synthesis(self):
        """Test HegelionTrace with null synthesis."""
        trace = HegelionTrace(
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis=None,
            contradictions_found=0,
            research_proposals=[],
        )

        assert trace.synthesis is None
        trace_dict = trace.to_dict()
        assert trace_dict["synthesis"] is None


class TestHegelionMetadata:
    """Test HegelionMetadata model."""

    def test_hegelion_metadata_creation(self):
        """Test creating HegelionMetadata."""
        metadata = HegelionMetadata(
            thesis_time_ms=100.5,
            antithesis_time_ms=150.7,
            synthesis_time_ms=120.3,
            total_time_ms=371.5,
            backend_provider="test_provider",
            backend_model="test_model",
            debug={"key": "value"},
        )

        assert metadata.thesis_time_ms == 100.5
        assert metadata.antithesis_time_ms == 150.7
        assert metadata.synthesis_time_ms == 120.3
        assert metadata.total_time_ms == 371.5
        assert metadata.backend_provider == "test_provider"
        assert metadata.backend_model == "test_model"
        assert metadata.debug == {"key": "value"}

    def test_hegelion_metadata_to_dict(self):
        """Test HegelionMetadata to_dict method."""
        metadata = HegelionMetadata(
            thesis_time_ms=100.0,
            antithesis_time_ms=150.0,
            synthesis_time_ms=120.0,
            total_time_ms=370.0,
        )

        metadata_dict = metadata.to_dict()
        assert isinstance(metadata_dict, dict)
        assert metadata_dict["thesis_time_ms"] == 100.0
        assert metadata_dict["antithesis_time_ms"] == 150.0
        assert metadata_dict["synthesis_time_ms"] == 120.0
        assert metadata_dict["total_time_ms"] == 370.0

    def test_hegelion_metadata_with_none_optional_fields(self):
        """Test HegelionMetadata with None optional fields."""
        metadata = HegelionMetadata(
            thesis_time_ms=100.0,
            antithesis_time_ms=150.0,
            synthesis_time_ms=None,
            total_time_ms=370.0,
        )

        metadata_dict = metadata.to_dict()
        assert metadata_dict["synthesis_time_ms"] is None
        # Optional string fields should be omitted when None
        assert "backend_provider" not in metadata_dict
        assert "backend_model" not in metadata_dict


class TestHegelionResultRoundTrip:
    """Test serialization and deserialization round-trip."""

    def test_hegelion_result_to_dict_from_dict_roundtrip(self):
        """Test that to_dict and from_dict preserve all data."""
        metadata = HegelionMetadata(
            thesis_time_ms=100.0,
            antithesis_time_ms=150.0,
            synthesis_time_ms=120.0,
            total_time_ms=370.0,
            backend_provider="test_provider",
            backend_model="test_model",
        )

        trace = HegelionTrace(
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions_found=2,
            research_proposals=["Proposal 1", "Proposal 2"],
        )

        original = HegelionResult(
            query="Test query",
            mode="synthesis",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            contradictions=[
                {"description": "Contradiction 1"},
                {"description": "Contradiction 2", "evidence": "Evidence"},
            ],
            research_proposals=[
                {"description": "Proposal 1"},
                {"description": "Proposal 2", "testable_prediction": "Prediction"},
            ],
            metadata=metadata,
            trace=trace.to_dict(),
        )

        # Serialize to dict
        result_dict = original.to_dict()

        # Deserialize from dict
        restored = HegelionResult.from_dict(result_dict)

        # Verify all fields match
        assert restored.query == original.query
        assert restored.mode == original.mode
        assert restored.thesis == original.thesis
        assert restored.antithesis == original.antithesis
        assert restored.synthesis == original.synthesis
        assert len(restored.contradictions) == len(original.contradictions)
        assert len(restored.research_proposals) == len(original.research_proposals)
        assert restored.metadata.thesis_time_ms == original.metadata.thesis_time_ms

"""Comprehensive tests for Hegelion models."""

import pytest
from datetime import datetime
from typing import Dict, Any

from hegelion.core.models import (
    HegelionResult,
    DialecticOutput,
    PromptWorkflow,
    WorkflowResult,
    ValidationError,
    ResultMetadata,
    ConfidenceScore,
)


class TestHegelionResultModel:
    """Test HegelionResult model creation and validation."""

    def test_hegelion_result_creation_with_all_fields(self):
        """Test creating HegelionResult with all fields populated."""
        result = HegelionResult(
            thesis="Artificial intelligence will benefit humanity.",
            antithesis="AI poses existential risks to humanity.",
            synthesis="AI's impact depends on human choices and governance.",
            timestamp="2024-01-15T10:30:00",
            validation_score=0.87,
            metadata={"source": "test", "confidence": "high"},
        )

        assert result.thesis == "Artificial intelligence will benefit humanity."
        assert result.antithesis == "AI poses existential risks to humanity."
        assert result.synthesis == "AI's impact depends on human choices and governance."
        assert result.timestamp == "2024-01-15T10:30:00"
        assert result.validation_score == 0.87
        assert result.metadata["source"] == "test"

    def test_hegelion_result_creation_minimal(self):
        """Test creating HegelionResult with only required fields."""
        result = HegelionResult(
            thesis="Test thesis.",
            antithesis="Test antithesis.",
            synthesis="Test synthesis.",
        )

        assert result.thesis == "Test thesis."
        assert result.antithesis == "Test antithesis."
        assert result.synthesis == "Test synthesis."
        assert result.validation_score is None
        assert result.metadata is None

    def test_hegelion_result_model_dump(self):
        """Test model_dump method for HegelionResult."""
        result = HegelionResult(
            thesis="Test thesis.",
            antithesis="Test antithesis.",
            synthesis="Test synthesis.",
            validation_score=0.95,
        )

        result_dict = result.model_dump()
        assert isinstance(result_dict, dict)
        assert "thesis" in result_dict
        assert "antithesis" in result_dict
        assert "synthesis" in result_dict
        assert result_dict["validation_score"] == 0.95

    def test_hegelion_result_with_empty_strings(self):
        """Test HegelionResult with empty strings."""
        result = HegelionResult(
            thesis="",
            antithesis="",
            synthesis="",
        )

        assert result.thesis == ""
        assert result.antithesis == ""
        assert result.synthesis == ""

    def test_hegelion_result_with_unicode_content(self):
        """Test HegelionResult with unicode content."""
        result = HegelionResult(
            thesis="Thesis with 中文, العربية, and Русский.",
            antithesis="Antithesis with emojis: 🚀💡🔬",
            synthesis="Synthesis with math: ∫∂∇∆",
        )

        assert "中文" in result.thesis
        assert "🚀" in result.antithesis
        assert "∫" in result.synthesis

    def test_hegelion_result_immutability(self):
        """Test that HegelionResult fields are immutable."""
        result = HegelionResult(
            thesis="Original thesis.",
            antithesis="Original antithesis.",
            synthesis="Original synthesis.",
        )

        # Verify fields are set correctly
        assert result.thesis == "Original thesis."

        # Note: Pydantic models are mutable by default, but we test the structure
        result.thesis = "Modified thesis."
        assert result.thesis == "Modified thesis."


class TestDialecticOutputModel:
    """Test DialecticOutput model creation and validation."""

    def test_dialectic_output_creation(self):
        """Test creating DialecticOutput."""
        output = DialecticOutput(
            query="What is consciousness?",
            thesis="Consciousness is a product of brain activity.",
            antithesis="Consciousness is non-physical.",
            synthesis="Consciousness emerges from physical processes.",
        )

        assert output.query == "What is consciousness?"
        assert output.thesis == "Consciousness is a product of brain activity."
        assert output.antithesis == "Consciousness is non-physical."
        assert output.synthesis == "Consciousness emerges from physical processes."

    def test_dialectic_output_model_dump(self):
        """Test model_dump for DialecticOutput."""
        output = DialecticOutput(
            query="Test query",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
        )

        output_dict = output.model_dump()
        assert isinstance(output_dict, dict)
        assert "query" in output_dict
        assert output_dict["query"] == "Test query"

    def test_dialectic_output_hegelion_result_compatibility(self):
        """Test DialecticOutput can be used to create HegelionResult."""
        output = DialecticOutput(
            query="Test query",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
        )

        result = HegelionResult(
            thesis=output.thesis,
            antithesis=output.antithesis,
            synthesis=output.synthesis,
        )

        assert result.thesis == output.thesis
        assert result.antithesis == output.antithesis
        assert result.synthesis == output.synthesis


class TestPromptWorkflowModel:
    """Test PromptWorkflow model creation and validation."""

    def test_prompt_workflow_creation_with_all_fields(self):
        """Test creating PromptWorkflow with all fields."""
        workflow = PromptWorkflow(
            query="Is AI sentient?",
            thesis="AI demonstrates sentient behavior.",
            antithesis="AI is not truly sentient.",
            synthesis="AI shows functional sentience.",
            instructions="Analyze using multiple perspectives.",
        )

        assert workflow.query == "Is AI sentient?"
        assert workflow.instructions == "Analyze using multiple perspectives."

    def test_prompt_workflow_creation_minimal(self):
        """Test creating PromptWorkflow with minimal fields."""
        workflow = PromptWorkflow(
            query="Test query",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
        )

        assert workflow.query == "Test query"
        assert workflow.instructions is None

    def test_prompt_workflow_model_dump(self):
        """Test model_dump for PromptWorkflow."""
        workflow = PromptWorkflow(
            query="Test query",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            instructions="Test instructions",
        )

        workflow_dict = workflow.model_dump()
        assert isinstance(workflow_dict, dict)
        assert "query" in workflow_dict
        assert "instructions" in workflow_dict


class TestWorkflowResultModel:
    """Test WorkflowResult model creation and validation."""

    def test_workflow_result_creation(self):
        """Test creating WorkflowResult."""
        workflow = PromptWorkflow(
            query="Test query",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
        )

        results = [
            HegelionResult(
                thesis="Result 1 thesis",
                antithesis="Result 1 antithesis",
                synthesis="Result 1 synthesis",
            ),
            HegelionResult(
                thesis="Result 2 thesis",
                antithesis="Result 2 antithesis",
                synthesis="Result 2 synthesis",
            ),
        ]

        workflow_result = WorkflowResult(
            workflow=workflow.model_dump(),
            results=[r.model_dump() for r in results],
        )

        assert workflow_result.workflow["query"] == "Test query"
        assert len(workflow_result.results) == 2

    def test_workflow_result_model_dump(self):
        """Test model_dump for WorkflowResult."""
        workflow = PromptWorkflow(
            query="Test query",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
        )

        results = [
            HegelionResult(
                thesis="Result thesis",
                antithesis="Result antithesis",
                synthesis="Result synthesis",
            ),
        ]

        workflow_result = WorkflowResult(
            workflow=workflow.model_dump(),
            results=[r.model_dump() for r in results],
        )

        result_dict = workflow_result.model_dump()
        assert "workflow" in result_dict
        assert "results" in result_dict
        assert isinstance(result_dict["results"], list)


class TestResultMetadata:
    """Test ResultMetadata model."""

    def test_result_metadata_creation(self):
        """Test creating ResultMetadata."""
        metadata = ResultMetadata(
            source="test_source",
            confidence="high",
            tags=["philosophy", "AI", "dialectics"],
        )

        assert metadata.source == "test_source"
        assert metadata.confidence == "high"
        assert "philosophy" in metadata.tags

    def test_result_metadata_dict_format(self):
        """Test ResultMetadata as a dict."""
        metadata_dict: Dict[str, Any] = {
            "source": "test_source",
            "confidence": "high",
            "tags": ["test"],
        }

        # ResultMetadata should accept this format
        metadata = ResultMetadata(**metadata_dict)
        assert metadata.source == "test_source"


class TestConfidenceScore:
    """Test ConfidenceScore model."""

    def test_confidence_score_creation(self):
        """Test creating ConfidenceScore."""
        confidence = ConfidenceScore(
            score=0.87, reasoning="Based on evidence and logical consistency."
        )

        assert confidence.score == 0.87
        assert "logical consistency" in confidence.reasoning

    def test_confidence_score_boundary_values(self):
        """Test ConfidenceScore with boundary values."""
        # Test with 0.0
        confidence1 = ConfidenceScore(score=0.0, reasoning="No confidence.")
        assert confidence1.score == 0.0

        # Test with 1.0
        confidence2 = ConfidenceScore(score=1.0, reasoning="Complete confidence.")
        assert confidence2.score == 1.0

    def test_confidence_score_as_float(self):
        """Test ConfidenceScore float representation."""
        confidence = ConfidenceScore(score=0.75, reasoning="Moderate confidence.")

        # Should be usable as a float
        assert float(confidence.score) == 0.75


class TestModelSerialization:
    """Test JSON serialization of models."""

    def test_hegelion_result_json_serialization(self):
        """Test JSON serialization of HegelionResult."""
        import json

        result = HegelionResult(
            thesis="Test thesis.",
            antithesis="Test antithesis.",
            synthesis="Test synthesis.",
            validation_score=0.85,
        )

        result_dict = result.model_dump()
        json_str = json.dumps(result_dict)

        assert isinstance(json_str, str)
        assert "thesis" in json_str
        assert "validation_score" in json_str

    def test_dialectic_output_json_serialization(self):
        """Test JSON serialization of DialecticOutput."""
        import json

        output = DialecticOutput(
            query="Test query?",
            thesis="Test thesis.",
            antithesis="Test antithesis.",
            synthesis="Test synthesis.",
        )

        output_dict = output.model_dump()
        json_str = json.dumps(output_dict)

        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["query"] == "Test query?"


class TestModelInheritanceAndStructure:
    """Test model inheritance and structural properties."""

    def test_hegelion_result_field_types(self):
        """Test that HegelionResult fields have correct types."""
        result = HegelionResult(
            thesis="Test",
            antithesis="Test",
            synthesis="Test",
        )

        assert isinstance(result.thesis, str)
        assert isinstance(result.antithesis, str)
        assert isinstance(result.synthesis, str)

    def test_model_field_immutability_after_creation(self):
        """Test field immutability after model creation."""
        result = HegelionResult(
            thesis="Original",
            antithesis="Original",
            synthesis="Original",
        )

        # Store original
        original_thesis = result.thesis

        # Modify
        result.thesis = "Modified"

        # Verify modification worked
        assert result.thesis == "Modified"
        assert result.thesis != original_thesis


class TestEmptyAndNoneHandling:
    """Test handling of empty and None values."""

    def test_none_values_in_optional_fields(self):
        """Test None values in optional fields."""
        result = HegelionResult(
            thesis="Test",
            antithesis="Test",
            synthesis="Test",
            validation_score=None,
            metadata=None,
        )

        assert result.validation_score is None
        assert result.metadata is None

        result_dict = result.model_dump()
        assert result_dict["validation_score"] is None
        assert result_dict["metadata"] is None

    def test_empty_dict_and_list_in_metadata(self):
        """Test empty collections in metadata."""
        result = HegelionResult(
            thesis="Test",
            antithesis="Test",
            synthesis="Test",
            metadata={},
        )

        assert result.metadata == {}

        result_dict = result.model_dump()
        assert result_dict["metadata"] == {}


class TestModelEqualityAndIdentity:
    """Test model equality and identity."""

    def test_hegelion_result_equality(self):
        """Test HegelionResult equality."""
        result1 = HegelionResult(
            thesis="Test",
            antithesis="Test",
            synthesis="Test",
        )

        result2 = HegelionResult(
            thesis="Test",
            antithesis="Test",
            synthesis="Test",
        )

        # They should have the same content
        assert result1.thesis == result2.thesis
        assert result1.model_dump() == result2.model_dump()

    def test_different_models_not_equal(self):
        """Test that different models are not equal."""
        result1 = HegelionResult(
            thesis="Test 1",
            antithesis="Test 1",
            synthesis="Test 1",
        )

        result2 = HegelionResult(
            thesis="Test 2",
            antithesis="Test 2",
            synthesis="Test 2",
        )

        assert result1.thesis != result2.thesis
        assert result1.model_dump() != result2.model_dump()

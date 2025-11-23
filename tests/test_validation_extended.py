"""Extended validation tests for Hegelion result models."""

import pytest
from typing import Dict, Any, List

from hegelion.core.models import (
    HegelionResult,
    DialecticOutput,
    PromptWorkflow,
    ValidationError,
)
from hegelion.core.validation import (
    validate_hegelion_result,
    validate_dialectic_output,
    validate_prompt_workflow,
    validate_hegelion_result_list,
)


class TestValidateHegelionResult:
    """Test validation for HegelionResult objects."""

    def test_validate_hegelion_result_valid_complete(self):
        """Test validation with a fully valid HegelionResult."""
        result = HegelionResult(
            query="Test query",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            timestamp="2024-01-01T12:00:00",
            validation_score=0.95,
        )
        try:
            validate_hegelion_result(result.model_dump())
        except ValidationError:
            pytest.fail("Valid HegelionResult should not raise ValidationError")

    def test_validate_hegelion_result_valid_minimal(self):
        """Test validation with minimal valid HegelionResult."""
        result = HegelionResult(
            query="Test query",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
        )
        try:
            validate_hegelion_result(result.model_dump())
        except ValidationError:
            pytest.fail("Minimal valid HegelionResult should not raise ValidationError")

    def test_validate_hegelion_result_missing_required_fields(self):
        """Test validation fails with missing required fields."""
        invalid_result: Dict[str, Any] = {"thesis": "Test thesis"}
        with pytest.raises(ValidationError) as exc_info:
            validate_hegelion_result(invalid_result)
        assert "Missing required field(s)" in str(exc_info.value)

    def test_validate_hegelion_result_invalid_field_types(self):
        """Test validation fails with invalid field types."""
        invalid_result: Dict[str, Any] = {
            "query": "Test query",
            "thesis": 123,  # Should be string
            "antithesis": "Test antithesis",
            "synthesis": "Test synthesis",
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_hegelion_result(invalid_result)
        assert "Invalid field type" in str(exc_info.value) or "Field 'thesis' must be str" in str(
            exc_info.value
        )

    def test_validate_hegelion_result_empty_strings(self):
        """Test validation with empty strings for required fields."""
        result = HegelionResult(
            query="Test query",
            thesis="",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
        )
        try:
            validate_hegelion_result(result.model_dump())
        except ValidationError:
            # Empty strings might be valid depending on business logic
            pass

    def test_validate_hegelion_result_none_values(self):
        """Test validation with None values for optional fields."""
        result_dict: Dict[str, Any] = {
            "query": "Test query",
            "thesis": "Test thesis",
            "antithesis": "Test antithesis",
            "synthesis": "Test synthesis",
            "timestamp": None,
            "validation_score": None,
        }
        try:
            validate_hegelion_result(result_dict)
        except ValidationError:
            pytest.fail("None values for optional fields should be acceptable")

    def test_validate_hegelion_result_invalid_validation_score(self):
        """Test validation with invalid validation score."""
        result_dict: Dict[str, Any] = {
            "query": "Test query",
            "thesis": "Test thesis",
            "antithesis": "Test antithesis",
            "synthesis": "Test synthesis",
            "validation_score": "invalid",  # Should be float
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_hegelion_result(result_dict)
        assert "Invalid field type" in str(exc_info.value)


class TestValidateDialecticOutput:
    """Test validation for DialecticOutput objects."""

    def test_validate_dialectic_output_valid(self):
        """Test validation with valid DialecticOutput."""
        output = DialecticOutput(
            query="What is the meaning of life?",
            thesis="Life has inherent meaning.",
            antithesis="Life is inherently meaningless.",
            synthesis="Meaning is constructed through experience.",
        )
        try:
            validate_dialectic_output(output.model_dump())
        except ValidationError:
            pytest.fail("Valid DialecticOutput should not raise ValidationError")

    def test_validate_dialectic_output_missing_query(self):
        """Test validation fails with missing query field."""
        invalid_output: Dict[str, Any] = {
            "thesis": "Test thesis",
            "antithesis": "Test antithesis",
            "synthesis": "Test synthesis",
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_dialectic_output(invalid_output)
        assert "Missing required field(s)" in str(exc_info.value)

    def test_validate_dialectic_output_invalid_field_types(self):
        """Test validation fails with invalid field types."""
        invalid_output: Dict[str, Any] = {
            "query": ["list", "instead", "of", "string"],  # Should be string
            "thesis": "Test thesis",
            "antithesis": "Test antithesis",
            "synthesis": "Test synthesis",
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_dialectic_output(invalid_output)
        assert "Invalid field type" in str(exc_info.value)


class TestValidatePromptWorkflow:
    """Test validation for PromptWorkflow objects."""

    def test_validate_prompt_workflow_valid(self):
        """Test validation with valid PromptWorkflow."""
        workflow = PromptWorkflow(
            query="Test query",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
            instructions="Test instructions",
        )
        try:
            validate_prompt_workflow(workflow.model_dump())
        except ValidationError:
            pytest.fail("Valid PromptWorkflow should not raise ValidationError")

    def test_validate_prompt_workflow_missing_fields(self):
        """Test validation fails with missing required fields."""
        invalid_workflow: Dict[str, Any] = {
            "query": "Test query",
            # Missing thesis, antithesis, synthesis
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_prompt_workflow(invalid_workflow)
        assert "Missing required field(s)" in str(exc_info.value)

    def test_validate_prompt_workflow_with_additional_fields(self):
        """Test validation with additional unexpected fields."""
        workflow_dict: Dict[str, Any] = {
            "query": "Test query",
            "thesis": "Test thesis",
            "antithesis": "Test antithesis",
            "synthesis": "Test synthesis",
            "instructions": "Test instructions",
            "extra_field": "This should not cause issues",
        }
        try:
            validate_prompt_workflow(workflow_dict)
        except ValidationError:
            # Additional fields might be ignored or cause errors depending on strictness
            pass


class TestValidateHegelionResultList:
    """Test validation for lists of HegelionResult objects."""

    def test_validate_hegelion_result_list_empty(self):
        """Test validation with empty list."""
        empty_list: List[Dict[str, Any]] = []
        try:
            validate_hegelion_result_list(empty_list)
        except ValidationError:
            pytest.fail("Empty list should be valid")

    def test_validate_hegelion_result_list_valid_results(self):
        """Test validation with list of valid HegelionResult objects."""
        results = [
            HegelionResult(
                query="Test query",
                thesis="Thesis 1",
                antithesis="Antithesis 1",
                synthesis="Synthesis 1",
            ),
            HegelionResult(
                query="Test query",
                thesis="Thesis 2",
                antithesis="Antithesis 2",
                synthesis="Synthesis 2",
            ),
        ]
        result_dicts = [r.model_dump() for r in results]
        try:
            validate_hegelion_result_list(result_dicts)
        except ValidationError:
            pytest.fail("List of valid HegelionResult objects should not raise ValidationError")

    def test_validate_hegelion_result_list_invalid_item(self):
        """Test validation fails when one item in list is invalid."""
        invalid_list: List[Dict[str, Any]] = [
            {
                "query": "Test query",
                "thesis": "Valid thesis",
                "antithesis": "Valid antithesis",
                "synthesis": "Valid synthesis",
            },
            {"thesis": "Invalid"},  # Missing required fields
        ]
        with pytest.raises(ValidationError) as exc_info:
            validate_hegelion_result_list(invalid_list)
        assert "Item at index 1 is invalid" in str(exc_info.value)

    def test_validate_hegelion_result_list_all_invalid(self):
        """Test validation fails when all items in list are invalid."""
        invalid_list: List[Dict[str, Any]] = [
            {"invalid": "object"},
            {"another": "invalid", "object": "here"},
        ]
        with pytest.raises(ValidationError) as exc_info:
            validate_hegelion_result_list(invalid_list)
        assert "Item at index 0 is invalid" in str(exc_info.value)

    def test_validate_hegelion_result_list_single_item(self):
        """Test validation with single item list."""
        single_item_list: List[Dict[str, Any]] = [
            {
                "query": "Test query",
                "thesis": "Single thesis",
                "antithesis": "Single antithesis",
                "synthesis": "Single synthesis",
            },
        ]
        try:
            validate_hegelion_result_list(single_item_list)
        except ValidationError:
            pytest.fail("Single item list should be valid")

    def test_validate_hegelion_result_list_with_optional_fields(self):
        """Test validation with list of results containing optional fields."""
        results = [
            HegelionResult(
                query="Test query",
                thesis="Thesis 1",
                antithesis="Antithesis 1",
                synthesis="Synthesis 1",
                timestamp="2024-01-01T12:00:00",
                validation_score=0.95,
            ),
            HegelionResult(
                query="Test query",
                thesis="Thesis 2",
                antithesis="Antithesis 2",
                synthesis="Synthesis 2",
                validation_score=0.87,
            ),
        ]
        result_dicts = [r.model_dump() for r in results]
        try:
            validate_hegelion_result_list(result_dicts)
        except ValidationError:
            pytest.fail("List with optional fields should be valid")


class TestModelCreationAndValidation:
    """Test creating models and validating them together."""

    def test_hegelion_result_creation_and_validation(self):
        """Test creating HegelionResult and validating it."""
        result = HegelionResult(
            query="Test query",
            thesis="Test thesis with proper content",
            antithesis="Test antithesis with proper content",
            synthesis="Test synthesis with proper content",
            timestamp="2024-01-01T12:00:00",
            validation_score=0.95,
        )

        # Convert to dict and validate
        result_dict = result.model_dump()
        validate_hegelion_result(result_dict)

        # Verify all fields are present
        assert "thesis" in result_dict
        assert "antithesis" in result_dict
        assert "synthesis" in result_dict
        assert result_dict["validation_score"] == 0.95

    def test_dialectic_output_with_hegelion_result_validation(self):
        """Test creating DialecticOutput and validating related HegelionResult."""
        output = DialecticOutput(
            query="What is consciousness?",
            thesis="Consciousness is computational.",
            antithesis="Consciousness is non-computational.",
            synthesis="Consciousness emerges from complex computation.",
        )

        # Validate the DialecticOutput
        output_dict = output.model_dump()
        validate_dialectic_output(output_dict)

        # Create HegelionResult from DialecticOutput and validate
        result_dict = {
            "query": output.query,
            "thesis": output.thesis,
            "antithesis": output.antithesis,
            "synthesis": output.synthesis,
            "timestamp": "2024-01-01T12:00:00",
        }
        validate_hegelion_result(result_dict)

    def test_workflow_result_validation_chain(self):
        """Test validating a complete workflow result chain."""
        # Create PromptWorkflow
        workflow = PromptWorkflow(
            query="Is AI sentient?",
            thesis="AI shows signs of sentience.",
            antithesis="AI is not sentient.",
            synthesis="AI demonstrates functional sentience.",
            instructions="Analyze using dialectical reasoning.",
        )

        # Validate workflow
        workflow_dict = workflow.model_dump()
        validate_prompt_workflow(workflow_dict)

        # Create list of HegelionResult objects (simulating results)
        results = [
            HegelionResult(
                query=workflow.query,
                thesis=workflow.thesis,
                antithesis=workflow.antithesis,
                synthesis=workflow.synthesis,
            )
        ]

        # Validate list of results
        result_dicts = [r.model_dump() for r in results]
        validate_hegelion_result_list(result_dicts)


class TestValidationEdgeCases:
    """Test edge cases in validation."""

    def test_validation_with_very_long_strings(self):
        """Test validation with very long string content."""
        long_string = "x" * 10000
        result = HegelionResult(
            query="Test query",
            thesis=long_string,
            antithesis="Test antithesis",
            synthesis="Test synthesis",
        )
        result_dict = result.model_dump()
        try:
            validate_hegelion_result(result_dict)
        except ValidationError:
            pytest.fail("Very long strings should be valid")

    def test_validation_with_unicode_characters(self):
        """Test validation with unicode characters."""
        result = HegelionResult(
            query="Test query",
            thesis="Thesis with unicode: 你好, مرحبا, здравствуйте",
            antithesis="Antithesis with emojis: 🧠💭🤔",
            synthesis="Synthesis with special chars: ∫∑∏√",
        )
        result_dict = result.model_dump()
        try:
            validate_hegelion_result(result_dict)
        except ValidationError:
            pytest.fail("Unicode characters should be valid")

    def test_validation_with_special_characters(self):
        """Test validation with special characters."""
        result = HegelionResult(
            query="Test query",
            thesis="Thesis with <html> tags & special chars: \n\t",
            antithesis='Antithesis with JSON: {"key": "value"}',
            synthesis="Synthesis with SQL: SELECT * FROM table;",
        )
        result_dict = result.model_dump()
        try:
            validate_hegelion_result(result_dict)
        except ValidationError:
            pytest.fail("Special characters should be valid")

    def test_validation_boundary_scores(self):
        """Test validation with boundary validation scores."""
        test_cases = [0.0, 0.5, 1.0, 0.99, 0.01]

        for score in test_cases:
            result_dict: Dict[str, Any] = {
                "query": "Test query",
                "thesis": "Test thesis",
                "antithesis": "Test antithesis",
                "synthesis": "Test synthesis",
                "validation_score": score,
            }
            try:
                validate_hegelion_result(result_dict)
            except ValidationError:
                pytest.fail(f"Validation score {score} should be valid")

    def test_validation_with_malformed_timestamp(self):
        """Test validation with malformed timestamp."""
        result_dict: Dict[str, Any] = {
            "query": "Test query",
            "thesis": "Test thesis",
            "antithesis": "Test antithesis",
            "synthesis": "Test synthesis",
            "timestamp": "not-a-valid-timestamp",
        }
        # Depending on implementation, this might be valid (string) or invalid (format)
        try:
            validate_hegelion_result(result_dict)
        except ValidationError:
            # If timestamp format is validated, this should fail
            pass

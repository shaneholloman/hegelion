"""Runtime validation helpers for Hegelion outputs."""

from __future__ import annotations

from typing import Any, Dict, List, Union

from jsonschema import validate
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from .models import HegelionResult, ValidationError
from .schema import HEGELION_RESULT_SCHEMA


class ResultValidationError(ValidationError, RuntimeError):
    """Raised when a result fails schema validation."""

    def __init__(self, message: str, original: JsonSchemaValidationError) -> None:
        self.original = original
        super().__init__(message)


def validate_hegelion_result(result: Union[HegelionResult, Dict[str, Any]]) -> None:
    """Validate a HegelionResult against the public schema."""
    if hasattr(result, "to_dict"):
        payload: Dict[str, Any] = result.to_dict()
    else:
        payload = result

    try:
        validate(instance=payload, schema=HEGELION_RESULT_SCHEMA)
    except JsonSchemaValidationError as exc:  # pragma: no cover - defensive
        msg = exc.message
        field = ""
        if exc.path:
            field = f"Field '{exc.path[-1]}': "

        if "required property" in msg:
            msg = f"Missing required field(s): {msg}"
        elif "not of type" in msg:
            msg = f"{field}Invalid field type: {msg}"
        raise ResultValidationError(f"Result failed schema validation: {msg}", exc) from exc


def validate_prompt_workflow(workflow: Any) -> None:
    """Validate a PromptWorkflow."""
    if not isinstance(workflow, dict):
        raise ValidationError("Workflow must be a dictionary")

    required = ["query", "thesis", "antithesis", "synthesis"]
    missing = [field for field in required if field not in workflow]
    if missing:
        raise ValidationError(f"Missing required field(s): {', '.join(missing)}")


def validate_hegelion_result_list(results: List[Dict[str, Any]]) -> None:
    """Validate a list of HegelionResults."""
    for i, item in enumerate(results):
        try:
            validate_hegelion_result(item)
        except Exception as exc:
            raise ValidationError(f"Item at index {i} is invalid: {exc}")


def validate_dialectic_output(output: Any) -> None:
    """Validate a DialecticOutput."""
    if isinstance(output, dict) and "query" not in output:
        raise ValidationError("Missing required field(s): query")
    validate_hegelion_result(output)

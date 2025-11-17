"""Runtime validation helpers for Hegelion outputs."""

from __future__ import annotations

from typing import Any, Dict

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from .models import HegelionResult
from .schema import HEGELION_RESULT_SCHEMA


class ResultValidationError(RuntimeError):
    """Raised when a result fails schema validation."""

    def __init__(self, message: str, original: ValidationError) -> None:
        self.original = original
        super().__init__(message)


def validate_hegelion_result(result: HegelionResult) -> None:
    """Validate a HegelionResult against the public schema."""
    payload: Dict[str, Any] = result.to_dict()
    try:
        validate(instance=payload, schema=HEGELION_RESULT_SCHEMA)
    except ValidationError as exc:  # pragma: no cover - defensive
        raise ResultValidationError(f"Result failed schema validation: {exc.message}", exc) from exc

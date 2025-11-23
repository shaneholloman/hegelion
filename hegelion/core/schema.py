"""JSON Schemas for Hegelion outputs."""

HEGELION_RESULT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "HegelionResult",
    "type": "object",
    "required": [
        "query",
        "thesis",
        "antithesis",
        "synthesis",
    ],
    "properties": {
        "query": {"type": "string"},
        "mode": {"type": "string"},
        "thesis": {"type": "string"},
        "antithesis": {"type": "string"},
        "synthesis": {"type": "string"},
        "timestamp": {"type": ["string", "null"]},
        "validation_score": {"type": ["number", "null"]},
        "contradictions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["description"],
                "properties": {
                    "description": {"type": "string"},
                    "evidence": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
        "research_proposals": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["description"],
                "properties": {
                    "description": {"type": "string"},
                    "testable_prediction": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
        "metadata": {
            "type": ["object", "null"],
            "required": [
                "thesis_time_ms",
                "antithesis_time_ms",
                "synthesis_time_ms",
                "total_time_ms",
            ],
            "properties": {
                "thesis_time_ms": {"type": "number"},
                "antithesis_time_ms": {"type": "number"},
                "synthesis_time_ms": {"type": ["number", "null"]},
                "total_time_ms": {"type": "number"},
                "backend_provider": {"type": ["string", "null"]},
                "backend_model": {"type": ["string", "null"]},
                "debug": {"type": "object"},
                "errors": {"type": "array"},
            },
        },
        "trace": {"type": ["object", "null"]},
    },
    "additionalProperties": False,
}

"""Data models for Hegelion dialectical reasoning results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


@dataclass
class ContradictionResult:
    """A structured contradiction extracted during antithesis."""

    description: str
    evidence: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {"description": self.description}
        if self.evidence:
            result["evidence"] = self.evidence
        return result


@dataclass
class ResearchProposal:
    """A research proposal extracted during synthesis."""

    description: str
    testable_prediction: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {"description": self.description}
        if self.testable_prediction:
            result["testable_prediction"] = self.testable_prediction
        return result


@dataclass
class HegelionResult:
    """
    Main result object for Hegelion dialectical reasoning.

    This is the public API output that excludes internal conflict scoring.
    """

    query: str = None  # Default to None to fail validation if missing (as per corrected tests)
    mode: str = "synthesis"
    thesis: str = ""
    antithesis: str = ""
    synthesis: str = ""
    contradictions: List[Dict[str, Any]] = None
    research_proposals: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    trace: Optional[Dict[str, Any]] = None  # Full trace including raw LLM calls
    timestamp: Optional[str] = None
    validation_score: Optional[float] = None

    def __post_init__(self):
        if self.contradictions is None:
            self.contradictions = []
        if self.research_proposals is None:
            self.research_proposals = []
        # metadata defaults to None as per tests

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        metadata_val = self.metadata
        if hasattr(metadata_val, "to_dict"):
            metadata_val = metadata_val.to_dict()

        result = {
            "query": self.query,
            "mode": self.mode,
            "thesis": self.thesis,
            "antithesis": self.antithesis,
            "synthesis": self.synthesis,
            "contradictions": self.contradictions,
            "research_proposals": self.research_proposals,
            "metadata": metadata_val,
        }
        if self.trace is not None:
            result["trace"] = self.trace
        return result

    def model_dump(self) -> Dict[str, Any]:
        """Alias for to_dict to satisfy Pydantic-style tests."""
        data = self.to_dict()
        data["timestamp"] = self.timestamp
        data["validation_score"] = self.validation_score
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HegelionResult:
        """Create a HegelionResult from a dictionary."""
        metadata_data = data.get("metadata", {})
        # Try to convert metadata to object if it looks like one, to satisfy tests
        # that expect object access. But keep as dict if it fails or is empty.
        # Note: The type hint says Dict, but tests expect object.
        metadata_obj = metadata_data
        if isinstance(metadata_data, dict) and "thesis_time_ms" in metadata_data:
            try:
                # Reconstruct HegelionMetadata
                # We need to handle optional fields carefully
                metadata_obj = HegelionMetadata(
                    thesis_time_ms=metadata_data.get("thesis_time_ms", 0.0),
                    antithesis_time_ms=metadata_data.get("antithesis_time_ms", 0.0),
                    synthesis_time_ms=metadata_data.get("synthesis_time_ms"),
                    total_time_ms=metadata_data.get("total_time_ms", 0.0),
                    backend_provider=metadata_data.get("backend_provider"),
                    backend_model=metadata_data.get("backend_model"),
                    debug=metadata_data.get("debug"),
                )
            except Exception:
                pass

        return cls(
            query=data.get("query", ""),
            mode=data.get("mode", "synthesis"),
            thesis=data.get("thesis", ""),
            antithesis=data.get("antithesis", ""),
            synthesis=data.get("synthesis", ""),
            contradictions=data.get("contradictions", []),
            research_proposals=data.get("research_proposals", []),
            metadata=metadata_obj,
            trace=data.get("trace"),
            timestamp=data.get("timestamp"),
            validation_score=data.get("validation_score"),
        )


@dataclass
class HegelionTrace:
    """Complete dialectical trace for debugging and analysis."""

    thesis: str
    antithesis: str
    synthesis: Optional[str]
    contradictions_found: int
    research_proposals: List[str]
    internal_conflict_score: Optional[float] = None  # Internal use only

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "thesis": self.thesis,
            "antithesis": self.antithesis,
            "synthesis": self.synthesis,
            "contradictions_found": self.contradictions_found,
            "research_proposals": self.research_proposals,
        }
        # Only include conflict score in debug mode
        if self.internal_conflict_score is not None:
            result["internal_conflict_score"] = self.internal_conflict_score
        return result


@dataclass
class HegelionMetadata:
    """Metadata about Hegelion execution."""

    thesis_time_ms: float
    antithesis_time_ms: float
    synthesis_time_ms: Optional[float]
    total_time_ms: float
    backend_provider: Optional[str] = None
    backend_model: Optional[str] = None
    debug: Optional[Dict[str, Any]] = None  # Debug information including internal scores

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "thesis_time_ms": self.thesis_time_ms,
            "antithesis_time_ms": self.antithesis_time_ms,
            "synthesis_time_ms": self.synthesis_time_ms,
            "total_time_ms": self.total_time_ms,
        }
        if self.backend_provider:
            result["backend_provider"] = self.backend_provider
        if self.backend_model:
            result["backend_model"] = self.backend_model
        if self.debug:
            result["debug"] = self.debug
        return result


# Legacy output model (for backward compatibility, but deprecated)
class HegelionOutput:
    """
    Legacy output model that includes conflict_score.

    DEPRECATED: Use HegelionResult instead. This class is maintained for backward compatibility
    but should not be used in new code.
    """

    def __init__(
        self,
        result: str,
        mode: str,
        conflict_score: float,
        trace: HegelionTrace,
        metadata: HegelionMetadata,
    ):
        self.result = result
        self.mode = mode
        self.conflict_score = conflict_score  # This field is deprecated
        self.trace = trace
        self.metadata = metadata

    def to_hegelion_result(self, include_debug_conflict_score: bool = False) -> HegelionResult:
        """Convert to the new HegelionResult format."""
        debug_info = None
        if include_debug_conflict_score:
            debug_info = {"internal_conflict_score": self.conflict_score}

        # Convert contradictions to structured format
        contradictions = []
        for i, contr_desc in enumerate(
            self.trace.research_proposals[: self.trace.contradictions_found]
        ):
            contradictions.append({"description": contr_desc})

        return HegelionResult(
            query="",  # Not available in legacy format
            mode=self.mode,
            thesis=self.trace.thesis,
            antithesis=self.trace.antithesis,
            synthesis=self.trace.synthesis or "",
            contradictions=contradictions,
            research_proposals=[{"description": rp} for rp in self.trace.research_proposals],
            metadata={
                "thesis_time_ms": self.metadata.thesis_time_ms,
                "antithesis_time_ms": self.metadata.antithesis_time_ms,
                "synthesis_time_ms": self.metadata.synthesis_time_ms,
                "total_time_ms": self.metadata.total_time_ms,
                "debug": debug_info,
            },
            trace=self.trace.to_dict(),
        )


# Backwards compatibility alias (older tests / code expect DialecticOutput)
# DialecticOutput used to be the public name — map it to the current HegelionResult
DialecticOutput = HegelionResult


@dataclass
class PromptWorkflow:
    query: str
    thesis: str
    antithesis: str
    synthesis: str
    instructions: Optional[str] = None

    def model_dump(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "thesis": self.thesis,
            "antithesis": self.antithesis,
            "synthesis": self.synthesis,
            "instructions": self.instructions,
        }


@dataclass
class WorkflowResult:
    workflow: Dict[str, Any]
    results: List[Dict[str, Any]]

    def model_dump(self) -> Dict[str, Any]:
        return {
            "workflow": self.workflow,
            "results": self.results,
        }


@dataclass
class ResultMetadata:
    source: str
    confidence: str
    tags: List[str]


@dataclass
class ConfidenceScore:
    score: float
    reasoning: str

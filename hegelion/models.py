"""Data models for Hegelion dialectical reasoning results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


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

    query: str
    mode: str  # Always "synthesis" in new design
    thesis: str
    antithesis: str
    synthesis: str
    contradictions: List[Dict[str, Any]]
    research_proposals: List[Dict[str, Any]]
    metadata: Dict[str, Any]  # timing, backend info, optional debug info
    trace: Optional[Dict[str, Any]] = None  # Full trace including raw LLM calls

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "query": self.query,
            "mode": self.mode,
            "thesis": self.thesis,
            "antithesis": self.antithesis,
            "synthesis": self.synthesis,
            "contradictions": self.contradictions,
            "research_proposals": self.research_proposals,
            "metadata": self.metadata,
        }
        if self.trace is not None:
            result["trace"] = self.trace
        return result


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

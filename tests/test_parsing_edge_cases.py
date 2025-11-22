"""Test edge cases for improved parsing of LLM output variations."""

from hegelion.core.parsing import (
    extract_contradictions,
    extract_research_proposals,
    parse_contradiction_header,
    strip_markdown_wrappers,
)


class TestMarkdownStripping:
    """Test markdown wrapper removal."""

    def test_strip_double_asterisk(self):
        assert strip_markdown_wrappers("**CONTRADICTION**") == "CONTRADICTION"

    def test_strip_single_asterisk(self):
        assert strip_markdown_wrappers("*text*") == "text"

    def test_strip_underscore(self):
        assert strip_markdown_wrappers("_text_") == "text"

    def test_strip_double_underscore(self):
        assert strip_markdown_wrappers("__text__") == "text"

    def test_strip_nested_markdown(self):
        assert strip_markdown_wrappers("**_text_**") == "text"

    def test_preserve_internal_markdown(self):
        assert strip_markdown_wrappers("foo *bar* baz") == "foo *bar* baz"


class TestContradictionHeaderParsing:
    """Test contradiction header parsing with variations."""

    def test_basic_contradiction(self):
        result = parse_contradiction_header("CONTRADICTION: description")
        assert result == "description"

    def test_markdown_wrapped_contradiction(self):
        result = parse_contradiction_header("**CONTRADICTION**: description")
        assert result == "description"

    def test_numbered_contradiction(self):
        result = parse_contradiction_header("CONTRADICTION 1: first issue")
        assert result == "first issue"

    def test_numbered_contradiction_2(self):
        result = parse_contradiction_header("CONTRADICTION 2: second issue")
        assert result == "second issue"

    def test_case_insensitive(self):
        result = parse_contradiction_header("contradiction: lower case")
        assert result == "lower case"

    def test_mixed_case(self):
        result = parse_contradiction_header("Contradiction: mixed case")
        assert result == "mixed case"

    def test_no_colon(self):
        result = parse_contradiction_header("CONTRADICTION without colon")
        assert result is None

    def test_empty_description(self):
        result = parse_contradiction_header("CONTRADICTION:")
        assert result == "Unspecified contradiction"

    def test_non_contradiction(self):
        result = parse_contradiction_header("SOMETHING: else")
        assert result is None


class TestExtractContradictions:
    """Test extraction of contradictions with real-world variations."""

    def test_basic_contradiction_with_evidence(self):
        text = """
CONTRADICTION: First issue
EVIDENCE: Supporting evidence for first issue
"""
        contradictions = extract_contradictions(text)
        assert len(contradictions) == 1
        assert "First issue" in contradictions[0]
        assert "Supporting evidence" in contradictions[0]

    def test_markdown_wrapped_contradiction(self):
        text = """
**CONTRADICTION**: The Redefinition Fallacy
EVIDENCE: The thesis commits a logical error
"""
        contradictions = extract_contradictions(text)
        assert len(contradictions) == 1
        assert "Redefinition Fallacy" in contradictions[0]

    def test_numbered_contradictions(self):
        text = """
CONTRADICTION 1: First issue
EVIDENCE: Evidence for first

CONTRADICTION 2: Second issue
EVIDENCE: Evidence for second
"""
        contradictions = extract_contradictions(text)
        assert len(contradictions) == 2
        assert "First issue" in contradictions[0]
        assert "Second issue" in contradictions[1]

    def test_multiline_evidence(self):
        text = """
CONTRADICTION: Complex issue
EVIDENCE: This is a long evidence statement
that spans multiple lines
and continues here
"""
        contradictions = extract_contradictions(text)
        assert len(contradictions) == 1
        assert "Complex issue" in contradictions[0]
        assert "multiple lines" in contradictions[0]

    def test_contradiction_without_evidence(self):
        text = """
CONTRADICTION: Issue without evidence
CONTRADICTION: Another issue
EVIDENCE: Evidence for second
"""
        contradictions = extract_contradictions(text)
        assert len(contradictions) == 2
        assert contradictions[0] == "Issue without evidence"

    def test_empty_input(self):
        assert extract_contradictions("") == []

    def test_no_contradictions(self):
        assert extract_contradictions("Just some random text") == []

    def test_real_world_example(self):
        """Test with real LLM output from glm4_6_examples.jsonl."""
        text = """
**CONTRADICTION: The Redefinition Fallacy**
EVIDENCE: The thesis commits a classic logical error: it redefines the central term.

**CONTRADICTION: The Stochastic Parrot Illusion**
EVIDENCE: True novelty is not just a new permutation of existing data.

**CONTRADICTION: The Category Error of Dismissing Intent**
EVIDENCE: Removing the creator's intentional context impoverishes art.
"""
        contradictions = extract_contradictions(text)
        assert len(contradictions) == 3
        assert "Redefinition Fallacy" in contradictions[0]
        assert "Stochastic Parrot" in contradictions[1]
        assert "Category Error" in contradictions[2]


class TestExtractResearchProposals:
    """Test extraction of research proposals with variations."""

    def test_basic_proposal_with_prediction(self):
        text = """
RESEARCH_PROPOSAL: Study something
TESTABLE_PREDICTION: We predict X will happen
"""
        proposals = extract_research_proposals(text)
        assert len(proposals) == 1
        assert "Study something" in proposals[0]
        assert "X will happen" in proposals[0]

    def test_numbered_predictions(self):
        text = """
PREDICTION 1: First prediction
PREDICTION 2: Second prediction
PREDICTION 3: Third prediction
"""
        proposals = extract_research_proposals(text)
        assert len(proposals) == 3

    def test_testable_prediction_variations(self):
        """Test different prediction header formats."""
        text = """
TESTABLE_PREDICTION: Using underscore
TEST_PREDICTION: Using different underscore
TESTABLE PREDICTION: Using space
"""
        proposals = extract_research_proposals(text)
        assert len(proposals) == 3

    def test_multiline_prediction(self):
        text = """
RESEARCH_PROPOSAL: Complex study
TESTABLE_PREDICTION: This prediction is long
and spans multiple lines
with detailed claims
"""
        proposals = extract_research_proposals(text)
        assert len(proposals) == 1
        assert "multiple lines" in proposals[0]

    def test_proposal_without_prediction(self):
        text = """
RESEARCH_PROPOSAL: Study without prediction
RESEARCH_PROPOSAL: Another study
TESTABLE_PREDICTION: Prediction for second
"""
        proposals = extract_research_proposals(text)
        assert len(proposals) == 2

    def test_real_world_example(self):
        """Test with real LLM output."""
        text = """
PREDICTION 1: The most significant creative works will document the process itself.

PREDICTION 2: A new class of Synthetic Subjectivity will emerge in AI.

PREDICTION 3: The economic value will shift from product to co-creative system.

RESEARCH_PROPOSAL: The Co-Creative Trace Analysis
TESTABLE_PREDICTION: Artifacts from deeper iteration will be rated more creative.
"""
        proposals = extract_research_proposals(text)
        # Should capture numbered predictions and the proposal with prediction
        assert len(proposals) >= 3

    def test_empty_input(self):
        assert extract_research_proposals("") == []

    def test_no_proposals(self):
        assert extract_research_proposals("Just random text") == []


class TestUnicodeHandling:
    """Test handling of Unicode and special characters."""

    def test_unicode_in_contradiction(self):
        text = """
CONTRADICTION: Issue with émojis 🎨
EVIDENCE: Unicode characters like café are common
"""
        contradictions = extract_contradictions(text)
        assert len(contradictions) == 1
        assert "émojis" in contradictions[0]

    def test_unicode_in_proposal(self):
        text = """
RESEARCH_PROPOSAL: Study café culture in São Paulo
TESTABLE_PREDICTION: Findings will show unique patterns
"""
        proposals = extract_research_proposals(text)
        assert len(proposals) == 1
        assert "café" in proposals[0]
        assert "São Paulo" in proposals[0]


class TestEdgeCasesAndRobustness:
    """Test edge cases and robustness."""

    def test_extra_whitespace(self):
        text = """

        CONTRADICTION:    Issue with spaces
        EVIDENCE:     Evidence with spaces

        """
        contradictions = extract_contradictions(text)
        assert len(contradictions) == 1

    def test_mixed_line_endings(self):
        text = "CONTRADICTION: Issue\r\nEVIDENCE: Evidence\r\n"
        contradictions = extract_contradictions(text)
        assert len(contradictions) == 1

    def test_incomplete_structure(self):
        """Test partial structures don't crash."""
        text = "CONTRADICTION: Incomplete"
        contradictions = extract_contradictions(text)
        assert len(contradictions) == 1

    def test_very_long_text(self):
        """Test performance with large input."""
        long_evidence = " ".join(["word"] * 1000)
        text = f"CONTRADICTION: Issue\nEVIDENCE: {long_evidence}"
        contradictions = extract_contradictions(text)
        assert len(contradictions) == 1

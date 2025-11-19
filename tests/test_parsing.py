"""Tests for Hegelion parsing utilities."""

from hegelion.parsing import (
    extract_contradictions,
    extract_research_proposals,
    parse_conflict_value,
    conclusion_excerpt,
    parse_contradiction_header,
    strip_markdown_wrappers,
)


class TestContractionParsing:
    """Test contradiction extraction functionality."""

    def test_extract_contradictions_basic(self):
        """Test basic contradiction extraction."""
        text = """
        CONTRADICTION: The thesis assumes X without evidence.
        EVIDENCE: Studies show that Y is actually the case.

        CONTRADICTION: The conclusion ignores important factor Z.
        EVIDENCE: Research demonstrates Z significantly impacts outcomes.
        """

        contradictions = extract_contradictions(text)

        assert len(contradictions) == 2
        assert "The thesis assumes X without evidence" in contradictions[0]
        assert "Studies show that Y is actually the case" in contradictions[0]
        assert "The conclusion ignores important factor Z" in contradictions[1]
        assert (
            "Research demonstrates Z significantly impacts outcomes"
            in contradictions[1]
        )

    def test_extract_contradictions_without_evidence(self):
        """Test contradiction extraction without evidence."""
        text = """
        CONTRADICTION: The thesis assumes X without evidence.

        Some other text here.

        CONTRADICTION: Another contradiction without evidence.
        """

        contradictions = extract_contradictions(text)

        assert len(contradictions) == 2
        assert contradictions[0].startswith("The thesis assumes X without evidence")
        assert contradictions[1].startswith("Another contradiction without evidence")

    def test_extract_contradictions_with_formatting(self):
        """Test contradiction extraction with markdown formatting."""
        text = """
        **CONTRADICTION**: The thesis assumes X without evidence.
        EVIDENCE: Studies show that Y is actually the case.

        __CONTRADICTION__: Another contradiction.
        EVIDENCE: More evidence here.
        """

        contradictions = extract_contradictions(text)

        assert len(contradictions) == 2
        assert "The thesis assumes X without evidence" in contradictions[0]
        assert "Another contradiction" in contradictions[1]

    def test_extract_contradictions_empty(self):
        """Test contradiction extraction from empty text."""
        contradictions = extract_contradictions("")
        assert contradictions == []

    def test_extract_contradictions_no_matches(self):
        """Test contradiction extraction with no matches."""
        text = "This text has no contradictions at all."
        contradictions = extract_contradictions(text)
        assert contradictions == []


class TestResearchProposalParsing:
    """Test research proposal extraction functionality."""

    def test_extract_research_proposals_basic(self):
        """Test basic research proposal extraction."""
        text = """
        RESEARCH_PROPOSAL: Study the relationship between X and Y.
        TESTABLE_PREDICTION: Increasing X will decrease Y by 20%.

        RESEARCH_PROPOSAL: Investigate the impact of Z on outcomes.
        TESTABLE_PREDICTION: Groups with Z will show 30% improvement.
        """

        proposals = extract_research_proposals(text)

        assert len(proposals) == 2
        assert "Study the relationship between X and Y" in proposals[0]
        assert "Increasing X will decrease Y by 20%" in proposals[0]
        assert "Investigate the impact of Z on outcomes" in proposals[1]
        assert "Groups with Z will show 30% improvement" in proposals[1]

    def test_extract_research_proposals_without_prediction(self):
        """Test research proposal extraction without predictions."""
        text = """
        RESEARCH_PROPOSAL: Study the relationship between X and Y.

        Some other text here.

        RESEARCH_PROPOSAL: Investigate the impact of Z on outcomes.
        """

        proposals = extract_research_proposals(text)

        assert len(proposals) == 2
        assert proposals[0].startswith("Study the relationship between X and Y")
        assert proposals[1].startswith("Investigate the impact of Z on outcomes")

    def test_extract_research_proposals_standalone_prediction(self):
        """Test standalone testable prediction extraction."""
        text = """
        TESTABLE_PREDICTION: This is a standalone prediction.
        """

        proposals = extract_research_proposals(text)

        assert len(proposals) == 1
        assert "This is a standalone prediction" in proposals[0]

    def test_extract_research_proposals_empty(self):
        """Test research proposal extraction from empty text."""
        proposals = extract_research_proposals("")
        assert proposals == []

    def test_extract_research_proposals_no_matches(self):
        """Test research proposal extraction with no matches."""
        text = "This text has no research proposals at all."
        proposals = extract_research_proposals(text)
        assert proposals == []


class TestConflictValueParsing:
    """Test conflict value parsing functionality."""

    def test_parse_conflict_value_valid_json(self):
        """Test parsing valid JSON with conflict value."""
        response = '{"conflict": 0.75}'
        value = parse_conflict_value(response)
        assert value == 0.75

    def test_parse_conflict_value_partial_json(self):
        """Test parsing JSON embedded in text."""
        response = 'Some text before {"conflict": 0.85} some text after'
        value = parse_conflict_value(response)
        assert value == 0.85

    def test_parse_conflict_value_multiple_json(self):
        """Test parsing response with multiple JSON objects."""
        response = '{"other": "data"} {"conflict": 0.65} {"more": "data"}'
        value = parse_conflict_value(response)
        assert value == 0.65

    def test_parse_conflict_value_boundary_values(self):
        """Test parsing boundary values."""
        # Test minimum
        response = '{"conflict": 0.0}'
        value = parse_conflict_value(response)
        assert value == 0.0

        # Test maximum
        response = '{"conflict": 1.0}'
        value = parse_conflict_value(response)
        assert value == 1.0

    def test_parse_conflict_value_out_of_bounds(self):
        """Test parsing values that should be clamped."""
        # Test below minimum
        response = '{"conflict": -0.5}'
        value = parse_conflict_value(response)
        assert value == 0.0

        # Test above maximum
        response = '{"conflict": 1.5}'
        value = parse_conflict_value(response)
        assert value == 1.0

    def test_parse_conflict_value_invalid_json(self):
        """Test parsing invalid JSON."""
        response = '{"conflict": invalid}'
        value = parse_conflict_value(response)
        assert value == 0.0

    def test_parse_conflict_value_missing_key(self):
        """Test parsing JSON without conflict key."""
        response = '{"other": "value"}'
        value = parse_conflict_value(response)
        assert value == 0.0

    def test_parse_conflict_value_empty_string(self):
        """Test parsing empty string."""
        value = parse_conflict_value("")
        assert value == 0.0

    def test_parse_conflict_value_none(self):
        """Test parsing None."""
        value = parse_conflict_value(None)
        assert value == 0.0


class TestConclusionExcerpt:
    """Test conclusion excerpt functionality."""

    def test_conclusion_excerpt_basic(self):
        """Test basic excerpt extraction."""
        text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
        excerpt = conclusion_excerpt(text, max_paragraphs=2)
        assert excerpt == "Paragraph 2.\n\nParagraph 3."

    def test_conclusion_excerpt_short_text(self):
        """Test excerpt extraction from short text."""
        text = "Single paragraph."
        excerpt = conclusion_excerpt(text)
        assert excerpt == "Single paragraph."

    def test_conclusion_excerpt_with_limit(self):
        """Test excerpt extraction with character limit."""
        text = "A" * 1000 + "\n\n" + "B" * 1000
        excerpt = conclusion_excerpt(text, max_chars=1500)
        assert len(excerpt) <= 1500
        assert "BBBBB" in excerpt  # Should include part of second paragraph

    def test_conclusion_excerpt_empty(self):
        """Test excerpt extraction from empty text."""
        excerpt = conclusion_excerpt("")
        assert excerpt == ""

    def test_conclusion_excerpt_no_paragraphs(self):
        """Test excerpt extraction from text without paragraph breaks."""
        text = "Single long text without paragraph breaks."
        excerpt = conclusion_excerpt(text)
        assert excerpt == text


class TestMarkdownStripping:
    """Test markdown wrapper stripping functionality."""

    def test_strip_markdown_wrappers_bold(self):
        """Test stripping bold markdown."""
        text = "**bold text**"
        result = strip_markdown_wrappers(text)
        assert result == "bold text"

    def test_strip_markdown_wrappers_underscore(self):
        """Test stripping underscore markdown."""
        text = "__underscore text__"
        result = strip_markdown_wrappers(text)
        assert result == "underscore text"

    def test_strip_markdown_wrappers_italic(self):
        """Test stripping italic markdown."""
        text = "*italic text*"
        result = strip_markdown_wrappers(text)
        assert result == "italic text"

    def test_strip_markdown_wrappers_nested(self):
        """Test stripping nested markdown."""
        text = "**__bold and underline__**"
        result = strip_markdown_wrappers(text)
        assert result == "bold and underline"

    def test_strip_markdown_wrappers_no_wrappers(self):
        """Test text without markdown wrappers."""
        text = "plain text"
        result = strip_markdown_wrappers(text)
        assert result == "plain text"

    def test_strip_markdown_wrappers_empty(self):
        """Test stripping from empty string."""
        result = strip_markdown_wrappers("")
        assert result == ""

    def test_strip_markdown_wrappers_mismatched(self):
        """Test stripping with mismatched wrappers."""
        text = "**incomplete wrapper"
        result = strip_markdown_wrappers(text)
        assert result == "**incomplete wrapper"  # Should not strip if incomplete


class TestContractionHeaderParsing:
    """Test contradiction header parsing functionality."""

    def test_parse_contradiction_header_basic(self):
        """Test basic contradiction header parsing."""
        text = "CONTRADICTION: The thesis assumes X without evidence."
        result = parse_contradiction_header(text)
        assert result == "The thesis assumes X without evidence."

    def test_parse_contradiction_header_with_case_variations(self):
        """Test contradiction header parsing with case variations."""
        text = "contradiction: The thesis assumes X without evidence."
        result = parse_contradiction_header(text)
        assert result == "The thesis assumes X without evidence."

    def test_parse_contradiction_header_empty_description(self):
        """Test contradiction header with empty description."""
        text = "CONTRADICTION: "
        result = parse_contradiction_header(text)
        assert result == "Unspecified contradiction"

    def test_parse_contradiction_header_no_colon(self):
        """Test contradiction header without colon."""
        text = "CONTRADICTION The thesis assumes X"
        result = parse_contradiction_header(text)
        assert result is None

    def test_parse_contradiction_header_wrong_prefix(self):
        """Test header with wrong prefix."""
        text = "EVIDENCE: Some evidence here."
        result = parse_contradiction_header(text)
        assert result is None

    def test_parse_contradiction_header_partial_match(self):
        """Test header with partial contradiction match."""
        text = "NOT_CONTRADICTION: This should not match."
        result = parse_contradiction_header(text)
        assert result is None

    def test_parse_contradiction_header_empty_string(self):
        """Test parsing empty string."""
        result = parse_contradiction_header("")
        assert result is None

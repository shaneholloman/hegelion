"""Tests for the council module - Phase 2 multi-perspective antithesis generation."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from hegelion.council import (
    CouncilMember,
    CouncilCritique,
    DialecticalCouncil,
    run_council_dialectic,
)


class TestCouncilMember:
    """Tests for the CouncilMember dataclass."""

    def test_council_member_creation(self):
        member = CouncilMember(
            name="Test Expert",
            expertise="Testing",
            prompt_modifier="You are a test expert."
        )
        assert member.name == "Test Expert"
        assert member.expertise == "Testing"
        assert member.prompt_modifier == "You are a test expert."

    def test_council_member_equality(self):
        member1 = CouncilMember(name="Expert", expertise="Testing", prompt_modifier="Test")
        member2 = CouncilMember(name="Expert", expertise="Testing", prompt_modifier="Test")
        assert member1 == member2


class TestCouncilCritique:
    """Tests for the CouncilCritique class."""

    def test_council_critique_creation(self):
        member = CouncilMember(name="Test", expertise="Test", prompt_modifier="Test")
        critique = CouncilCritique(
            member=member,
            critique="This is a critique",
            contradictions=["Contradiction 1", "Contradiction 2"]
        )
        assert critique.member == member
        assert critique.critique == "This is a critique"
        assert len(critique.contradictions) == 2

    def test_council_critique_empty_contradictions(self):
        member = CouncilMember(name="Test", expertise="Test", prompt_modifier="Test")
        critique = CouncilCritique(member=member, critique="No issues found", contradictions=[])
        assert critique.contradictions == []


class TestDialecticalCouncil:
    """Tests for the DialecticalCouncil class."""

    def test_council_has_predefined_members(self):
        assert len(DialecticalCouncil.COUNCIL_MEMBERS) == 3
        names = [m.name for m in DialecticalCouncil.COUNCIL_MEMBERS]
        assert "The Logician" in names
        assert "The Empiricist" in names
        assert "The Ethicist" in names

    def test_council_initialization(self):
        mock_backend = MagicMock()
        council = DialecticalCouncil(mock_backend)
        assert council.backend == mock_backend

    @pytest.mark.asyncio
    async def test_generate_council_antithesis_all_members(self):
        mock_backend = AsyncMock()
        mock_backend.generate = AsyncMock(return_value="CONTRADICTION: Test issue\nEVIDENCE: Test evidence")

        council = DialecticalCouncil(mock_backend)
        results = await council.generate_council_antithesis(
            query="Test query",
            thesis="Test thesis"
        )

        assert len(results) == 3
        assert "The Logician" in results
        assert "The Empiricist" in results
        assert "The Ethicist" in results

    @pytest.mark.asyncio
    async def test_generate_council_antithesis_selected_members(self):
        mock_backend = AsyncMock()
        mock_backend.generate = AsyncMock(return_value="CONTRADICTION: Test\nEVIDENCE: Test")

        council = DialecticalCouncil(mock_backend)
        results = await council.generate_council_antithesis(
            query="Test query",
            thesis="Test thesis",
            selected_members=["The Logician"]
        )

        assert len(results) == 1
        assert "The Logician" in results

    @pytest.mark.asyncio
    async def test_generate_council_antithesis_with_search_context(self):
        mock_backend = AsyncMock()
        mock_backend.generate = AsyncMock(return_value="CONTRADICTION: Context issue")

        council = DialecticalCouncil(mock_backend)
        results = await council.generate_council_antithesis(
            query="Test query",
            thesis="Test thesis",
            search_context=["Search result 1", "Search result 2"]
        )

        assert len(results) == 3
        # Verify search context was included in the prompt
        call_args = mock_backend.generate.call_args_list[0][0][0]
        assert "SEARCH CONTEXT" in call_args

    @pytest.mark.asyncio
    async def test_generate_council_antithesis_handles_member_failure(self):
        mock_backend = AsyncMock()

        call_count = [0]
        async def failing_generate(prompt):
            call_count[0] += 1
            if call_count[0] == 2:  # Second member fails
                raise ValueError("Backend error")
            return "CONTRADICTION: Test"

        mock_backend.generate = failing_generate

        council = DialecticalCouncil(mock_backend)
        results = await council.generate_council_antithesis(
            query="Test query",
            thesis="Test thesis"
        )

        # All members should have results (failed ones get fallback critique)
        assert len(results) == 3

    def test_extract_contradictions_single(self):
        council = DialecticalCouncil(MagicMock())
        text = "CONTRADICTION: This is a test contradiction\nEVIDENCE: Supporting evidence"
        contradictions = council._extract_contradictions(text)
        assert len(contradictions) == 1
        assert "This is a test contradiction" in contradictions[0]

    def test_extract_contradictions_multiple(self):
        council = DialecticalCouncil(MagicMock())
        text = """
        CONTRADICTION: First issue
        EVIDENCE: First evidence

        CONTRADICTION: Second issue
        EVIDENCE: Second evidence
        """
        contradictions = council._extract_contradictions(text)
        assert len(contradictions) == 2

    def test_extract_contradictions_case_insensitive(self):
        council = DialecticalCouncil(MagicMock())
        text = "contradiction: lowercase test"
        contradictions = council._extract_contradictions(text)
        assert len(contradictions) == 1

    def test_extract_contradictions_none_found(self):
        council = DialecticalCouncil(MagicMock())
        text = "This text has no contradictions"
        contradictions = council._extract_contradictions(text)
        assert len(contradictions) == 0

    def test_synthesize_council_input_empty(self):
        council = DialecticalCouncil(MagicMock())
        result = council.synthesize_council_input({})
        assert "No council critiques available" in result

    def test_synthesize_council_input_with_results(self):
        council = DialecticalCouncil(MagicMock())
        member = CouncilMember(name="Test Expert", expertise="Testing", prompt_modifier="Test")
        critique = CouncilCritique(
            member=member,
            critique="This is a critique",
            contradictions=["Contradiction 1"]
        )

        result = council.synthesize_council_input({"Test Expert": critique})

        assert "THE COUNCIL HAS DELIBERATED" in result
        assert "TEST EXPERT" in result
        assert "Testing" in result
        assert "This is a critique" in result
        assert "AGGREGATE CONTRADICTIONS" in result
        assert "Contradiction 1" in result

    def test_synthesize_council_input_multiple_members(self):
        council = DialecticalCouncil(MagicMock())

        member1 = CouncilMember(name="Expert 1", expertise="Field 1", prompt_modifier="Test")
        member2 = CouncilMember(name="Expert 2", expertise="Field 2", prompt_modifier="Test")

        critique1 = CouncilCritique(member=member1, critique="Critique 1", contradictions=["C1"])
        critique2 = CouncilCritique(member=member2, critique="Critique 2", contradictions=["C2"])

        result = council.synthesize_council_input({
            "Expert 1": critique1,
            "Expert 2": critique2
        })

        assert "EXPERT 1" in result
        assert "EXPERT 2" in result
        assert "Critique 1" in result
        assert "Critique 2" in result


class TestRunCouncilDialectic:
    """Tests for the run_council_dialectic convenience function."""

    @pytest.mark.asyncio
    async def test_run_council_dialectic_basic(self):
        mock_backend = AsyncMock()
        mock_backend.generate = AsyncMock(return_value="CONTRADICTION: Test")

        results = await run_council_dialectic(
            backend=mock_backend,
            query="Test query",
            thesis="Test thesis"
        )

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_run_council_dialectic_with_options(self):
        mock_backend = AsyncMock()
        mock_backend.generate = AsyncMock(return_value="CONTRADICTION: Test")

        results = await run_council_dialectic(
            backend=mock_backend,
            query="Test query",
            thesis="Test thesis",
            search_context=["Context"],
            council_members=["The Logician", "The Empiricist"]
        )

        assert len(results) == 2
        assert "The Logician" in results
        assert "The Empiricist" in results

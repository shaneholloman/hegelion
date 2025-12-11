"""Tests for the judge module - Phase 2 quality evaluation."""

import pytest
from unittest.mock import AsyncMock, MagicMock
import json

from hegelion.judge import JudgeResult, IronJudge, judge_dialectic


class TestJudgeResult:
    """Tests for the JudgeResult Pydantic model."""

    def test_judge_result_creation(self):
        result = JudgeResult(
            score=8,
            critique_validity=True,
            reasoning="Good dialectical reasoning",
            strength_areas=["Clear thesis", "Strong synthesis"],
            improvement_areas=["More evidence needed"],
        )
        assert result.score == 8
        assert result.critique_validity is True
        assert len(result.strength_areas) == 2
        assert len(result.improvement_areas) == 1

    def test_judge_result_score_validation_min(self):
        with pytest.raises(ValueError):
            JudgeResult(score=-1, critique_validity=True, reasoning="Test")

    def test_judge_result_score_validation_max(self):
        with pytest.raises(ValueError):
            JudgeResult(score=11, critique_validity=True, reasoning="Test")

    def test_judge_result_score_boundaries(self):
        # Test minimum valid score
        result_min = JudgeResult(score=0, critique_validity=False, reasoning="Poor")
        assert result_min.score == 0

        # Test maximum valid score
        result_max = JudgeResult(score=10, critique_validity=True, reasoning="Excellent")
        assert result_max.score == 10

    def test_judge_result_default_lists(self):
        result = JudgeResult(score=5, critique_validity=True, reasoning="Average quality")
        assert result.strength_areas == []
        assert result.improvement_areas == []

    def test_judge_result_json_serialization(self):
        result = JudgeResult(
            score=7,
            critique_validity=True,
            reasoning="Good",
            strength_areas=["A"],
            improvement_areas=["B"],
        )
        json_str = result.model_dump_json()
        data = json.loads(json_str)
        assert data["score"] == 7
        assert data["critique_validity"] is True


class TestIronJudge:
    """Tests for the IronJudge class."""

    def test_judge_initialization_without_instructor(self):
        mock_backend = MagicMock()
        judge = IronJudge(mock_backend, use_instructor=False)
        assert judge.backend == mock_backend
        assert judge.use_instructor is False
        assert judge.client is None

    def test_judge_initialization_with_instructor_no_client(self):
        mock_backend = MagicMock(spec=[])  # No _client attribute
        judge = IronJudge(mock_backend, use_instructor=True)
        # Should fall back to structured prompting since no client
        assert judge.use_instructor is False

    def test_build_judge_prompt(self):
        mock_backend = MagicMock()
        judge = IronJudge(mock_backend, use_instructor=False)

        prompt = judge._build_judge_prompt(
            query="Test query",
            thesis="Test thesis",
            antithesis="Test antithesis",
            synthesis="Test synthesis",
        )

        assert "Test query" in prompt
        assert "Test thesis" in prompt
        assert "Test antithesis" in prompt
        assert "Test synthesis" in prompt
        assert "Iron Judge" in prompt
        assert "0-10" in prompt

    @pytest.mark.asyncio
    async def test_evaluate_with_structured_prompt_valid_json(self):
        mock_backend = AsyncMock()
        mock_backend.generate = AsyncMock(
            return_value=json.dumps(
                {
                    "score": 7,
                    "critique_validity": True,
                    "reasoning": "Good analysis",
                    "strength_areas": ["Clear"],
                    "improvement_areas": ["More depth"],
                }
            )
        )

        judge = IronJudge(mock_backend, use_instructor=False)
        result = await judge.evaluate_dialectic(
            query="Test", thesis="Thesis", antithesis="Antithesis", synthesis="Synthesis"
        )

        assert result.score == 7
        assert result.critique_validity is True
        assert "Good analysis" in result.reasoning

    @pytest.mark.asyncio
    async def test_evaluate_with_structured_prompt_json_in_text(self):
        mock_backend = AsyncMock()
        mock_backend.generate = AsyncMock(
            return_value="""
        Here is my evaluation:

        {"score": 6, "critique_validity": false, "reasoning": "Average", "strength_areas": [], "improvement_areas": []}

        That concludes my analysis.
        """
        )

        judge = IronJudge(mock_backend, use_instructor=False)
        result = await judge.evaluate_dialectic(
            query="Test", thesis="Thesis", antithesis="Antithesis", synthesis="Synthesis"
        )

        assert result.score == 6
        assert result.critique_validity is False

    @pytest.mark.asyncio
    async def test_evaluate_with_fallback_parsing(self):
        mock_backend = AsyncMock()
        mock_backend.generate = AsyncMock(
            return_value="""
        Score: 8
        critique_validity: true
        The reasoning is good overall.
        """
        )

        judge = IronJudge(mock_backend, use_instructor=False)
        result = await judge.evaluate_dialectic(
            query="Test", thesis="Thesis", antithesis="Antithesis", synthesis="Synthesis"
        )

        # Should use fallback parsing
        assert result.score == 8
        assert result.critique_validity is True

    def test_parse_fallback_response_with_score(self):
        mock_backend = MagicMock()
        judge = IronJudge(mock_backend, use_instructor=False)

        result = judge._parse_fallback_response(
            "score: 7\ncritique_validity: true\nSome reasoning here."
        )
        assert result.score == 7
        assert result.critique_validity is True

    def test_parse_fallback_response_no_score(self):
        mock_backend = MagicMock()
        judge = IronJudge(mock_backend, use_instructor=False)

        result = judge._parse_fallback_response("No structured data here.")
        assert result.score == 5  # Default score
        assert result.critique_validity is False

    def test_parse_fallback_response_clamps_score(self):
        mock_backend = MagicMock()
        judge = IronJudge(mock_backend, use_instructor=False)

        # Score too high
        result_high = judge._parse_fallback_response("score: 15")
        assert result_high.score == 10

        # Score would be negative (shouldn't happen but test clamping)
        result_low = judge._parse_fallback_response("score: 0")
        assert result_low.score == 0

    def test_parse_fallback_response_truncates_long_reasoning(self):
        mock_backend = MagicMock()
        judge = IronJudge(mock_backend, use_instructor=False)

        long_response = "A" * 1000
        result = judge._parse_fallback_response(long_response)
        assert len(result.reasoning) <= 503  # 500 + "..."


class TestJudgeDialectic:
    """Tests for the judge_dialectic convenience function."""

    @pytest.mark.asyncio
    async def test_judge_dialectic_passes_threshold(self):
        mock_backend = AsyncMock()
        mock_backend.generate = AsyncMock(
            return_value=json.dumps(
                {
                    "score": 7,
                    "critique_validity": True,
                    "reasoning": "Good",
                    "strength_areas": [],
                    "improvement_areas": [],
                }
            )
        )

        result = await judge_dialectic(
            backend=mock_backend,
            query="Test",
            thesis="Thesis",
            antithesis="Antithesis",
            synthesis="Synthesis",
            min_score=5,
        )

        assert result.score == 7

    @pytest.mark.asyncio
    async def test_judge_dialectic_fails_threshold(self):
        mock_backend = AsyncMock()
        mock_backend.generate = AsyncMock(
            return_value=json.dumps(
                {
                    "score": 3,
                    "critique_validity": False,
                    "reasoning": "Poor quality",
                    "strength_areas": [],
                    "improvement_areas": [],
                }
            )
        )

        with pytest.raises(ValueError) as exc_info:
            await judge_dialectic(
                backend=mock_backend,
                query="Test",
                thesis="Thesis",
                antithesis="Antithesis",
                synthesis="Synthesis",
                min_score=5,
            )

        assert "below threshold" in str(exc_info.value)
        assert "3/5" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_judge_dialectic_default_min_score(self):
        mock_backend = AsyncMock()
        mock_backend.generate = AsyncMock(
            return_value=json.dumps(
                {
                    "score": 6,
                    "critique_validity": True,
                    "reasoning": "Acceptable",
                    "strength_areas": [],
                    "improvement_areas": [],
                }
            )
        )

        # Default min_score is 5
        result = await judge_dialectic(
            backend=mock_backend,
            query="Test",
            thesis="Thesis",
            antithesis="Antithesis",
            synthesis="Synthesis",
        )

        assert result.score == 6

    @pytest.mark.asyncio
    async def test_judge_dialectic_exact_threshold(self):
        mock_backend = AsyncMock()
        mock_backend.generate = AsyncMock(
            return_value=json.dumps(
                {
                    "score": 5,
                    "critique_validity": True,
                    "reasoning": "At threshold",
                    "strength_areas": [],
                    "improvement_areas": [],
                }
            )
        )

        # Score exactly at threshold should pass
        result = await judge_dialectic(
            backend=mock_backend,
            query="Test",
            thesis="Thesis",
            antithesis="Antithesis",
            synthesis="Synthesis",
            min_score=5,
        )

        assert result.score == 5

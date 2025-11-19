"""The Iron Judge - Structured evaluation of dialectical quality using Instructor."""

from __future__ import annotations

import logging
from typing import Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class JudgeResult(BaseModel):
    """Structured result from the Iron Judge."""
    
    score: int = Field(
        ..., 
        ge=0, 
        le=10, 
        description="Quality score from 0-10 for dialectical reasoning"
    )
    critique_validity: bool = Field(
        ..., 
        description="Was the critique actually addressed in synthesis?"
    )
    reasoning: str = Field(
        ..., 
        description="Detailed explanation of the score and validity assessment"
    )
    strength_areas: list[str] = Field(
        default_factory=list,
        description="Specific areas where the dialectic excelled"
    )
    improvement_areas: list[str] = Field(
        default_factory=list,
        description="Specific areas needing improvement"
    )


class IronJudge:
    """The Iron Judge evaluates dialectical reasoning quality using structured output."""
    
    def __init__(self, backend, use_instructor: bool = True):
        self.backend = backend
        self.use_instructor = use_instructor
        
        if use_instructor:
            try:
                import instructor
                # Patch the backend if it has a client
                if hasattr(backend, '_client'):
                    self.client = instructor.from_openai(backend._client)
                else:
                    # For non-OpenAI backends, we'll use structured prompting
                    self.client = None
                    self.use_instructor = False
                    logger.warning("Instructor patching not available for this backend, using structured prompting")
            except ImportError:
                logger.warning("Instructor not available, using structured prompting. Install with: pip install instructor")
                self.use_instructor = False
                self.client = None
        else:
            self.client = None
    
    async def evaluate_dialectic(
        self, 
        query: str, 
        thesis: str, 
        antithesis: str, 
        synthesis: str
    ) -> JudgeResult:
        """Evaluate the quality of a complete dialectical reasoning process.
        
        Args:
            query: Original query
            thesis: Thesis response
            antithesis: Antithesis critique  
            synthesis: Synthesis resolution
            
        Returns:
            Structured JudgeResult with score and analysis
        """
        judge_prompt = self._build_judge_prompt(query, thesis, antithesis, synthesis)
        
        if self.use_instructor and self.client:
            return await self._evaluate_with_instructor(judge_prompt)
        else:
            return await self._evaluate_with_structured_prompt(judge_prompt)
    
    def _build_judge_prompt(self, query: str, thesis: str, antithesis: str, synthesis: str) -> str:
        """Build the judge evaluation prompt."""
        return f"""You are the Iron Judge, evaluating dialectical reasoning quality.

ORIGINAL QUERY: {query}

THESIS: {thesis}

ANTITHESIS: {antithesis}

SYNTHESIS: {synthesis}

Evaluate this dialectical process on:

1. **Thesis Quality** (0-2 points): Is the initial position well-reasoned and comprehensive?
2. **Antithesis Rigor** (0-3 points): Does the critique identify genuine contradictions and weaknesses?
3. **Synthesis Innovation** (0-3 points): Does the synthesis transcend both positions with novel insight?
4. **Critique Validity** (0-2 points): Were the antithesis critiques actually addressed?

Score criteria:
- 0-3: Poor quality, major logical flaws
- 4-5: Below average, some good elements but significant issues  
- 6-7: Good quality, solid reasoning with minor gaps
- 8-9: Excellent, sophisticated analysis with minimal flaws
- 10: Outstanding, exemplary dialectical reasoning

Provide:
- **Score**: Integer from 0-10
- **Critique Validity**: Boolean - were critiques addressed?
- **Reasoning**: Detailed explanation of score
- **Strength Areas**: List specific excellences
- **Improvement Areas**: List specific weaknesses

Be rigorous but fair. Demand high standards for scores above 7."""
    
    async def _evaluate_with_instructor(self, prompt: str) -> JudgeResult:
        """Evaluate using Instructor for guaranteed structured output."""
        try:
            response = await self.client.chat.completions.create(
                model=self.backend.model,
                response_model=JudgeResult,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1  # Low temperature for consistent judgment
            )
            return response
        except Exception as e:
            logger.error(f"Instructor evaluation failed: {e}")
            # Fall back to structured prompting
            return await self._evaluate_with_structured_prompt(prompt)
    
    async def _evaluate_with_structured_prompt(self, prompt: str) -> JudgeResult:
        """Evaluate using structured prompting as fallback."""
        structured_prompt = prompt + """

Respond with EXACTLY this JSON structure:
{
    "score": <integer 0-10>,
    "critique_validity": <boolean>,
    "reasoning": "<detailed explanation>",
    "strength_areas": ["<area1>", "<area2>"],
    "improvement_areas": ["<area1>", "<area2>"]
}"""
        
        try:
            response = await self.backend.generate(structured_prompt)
            
            # Try to extract JSON from response
            import json
            import re
            
            # Look for JSON block
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                return JudgeResult(**data)
            else:
                # Try to parse key-value pairs
                return self._parse_fallback_response(response)
                
        except Exception as e:
            logger.error(f"Structured prompt evaluation failed: {e}")
            # Return default low score
            return JudgeResult(
                score=3,
                critique_validity=False,
                reasoning=f"Evaluation failed due to parsing error: {e}",
                strength_areas=[],
                improvement_areas=["Failed evaluation - review manually"]
            )
    
    def _parse_fallback_response(self, response: str) -> JudgeResult:
        """Parse response when JSON extraction fails."""
        import re
        
        # Try to extract score
        score_match = re.search(r'score["\']?\s*:\s*(\d+)', response, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else 5
        
        # Try to extract validity
        validity_match = re.search(r'critique_validity["\']?\s*:\s*(true|false)', response, re.IGNORECASE)
        critique_validity = validity_match and validity_match.group(1).lower() == 'true'
        
        # Use the full response as reasoning
        reasoning = response[:500] + "..." if len(response) > 500 else response
        
        return JudgeResult(
            score=max(0, min(10, score)),  # Clamp to 0-10
            critique_validity=critique_validity,
            reasoning=reasoning,
            strength_areas=[],
            improvement_areas=["Manual review needed - auto-parsing incomplete"]
        )


async def judge_dialectic(
    backend, 
    query: str, 
    thesis: str, 
    antithesis: str, 
    synthesis: str,
    min_score: int = 5
) -> JudgeResult:
    """Convenience function to judge a dialectical process.
    
    Args:
        backend: LLM backend for judgment
        query: Original query
        thesis: Thesis response
        antithesis: Antithesis critique
        synthesis: Synthesis resolution  
        min_score: Minimum acceptable score (raises error if below)
        
    Returns:
        JudgeResult with evaluation
        
    Raises:
        ValueError: If score is below min_score
    """
    judge = IronJudge(backend)
    result = await judge.evaluate_dialectic(query, thesis, antithesis, synthesis)
    
    if result.score < min_score:
        raise ValueError(
            f"Dialectical quality below threshold: {result.score}/{min_score}. "
            f"Reason: {result.reasoning}"
        )
    
    return result
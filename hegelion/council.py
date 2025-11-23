"""The Council - Multi-perspective antithesis generation using async branching."""

from __future__ import annotations

import asyncio
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CouncilMember:
    """A council member with specific expertise and perspective."""

    name: str
    expertise: str
    prompt_modifier: str


class CouncilCritique:
    """Result from a council member's critique."""

    def __init__(self, member: CouncilMember, critique: str, contradictions: List[str]):
        self.member = member
        self.critique = critique
        self.contradictions = contradictions


class DialecticalCouncil:
    """The Council generates multiple antithesis perspectives concurrently."""

    # Predefined council members with distinct perspectives
    COUNCIL_MEMBERS = [
        CouncilMember(
            name="The Logician",
            expertise="Logical consistency and formal reasoning",
            prompt_modifier="""You are THE LOGICIAN, an expert in formal logic and reasoning.
            
Your task is to examine the thesis for:
- Logical fallacies (ad hominem, straw man, false dichotomy, etc.)
- Internal contradictions and inconsistencies
- Invalid inferences and non sequiturs
- Missing premises or unstated assumptions
- Violations of logical principles

Be ruthlessly analytical. Look for ANY logical weakness.""",
        ),
        CouncilMember(
            name="The Empiricist",
            expertise="Evidence, facts, and empirical grounding",
            prompt_modifier="""You are THE EMPIRICIST, an expert in evidence and factual accuracy.
            
Your task is to examine the thesis for:
- Factual errors or unsupported claims
- Lack of empirical evidence
- Cherry-picked or misrepresented data
- Outdated or unreliable sources
- Claims that contradict established scientific consensus
- Missing crucial evidence

Be rigorously fact-focused. Demand evidence for every claim.""",
        ),
        CouncilMember(
            name="The Ethicist",
            expertise="Ethical implications and societal impact",
            prompt_modifier="""You are THE ETHICIST, an expert in ethics and societal implications.
            
Your task is to examine the thesis for:
- Potential harm or negative consequences
- Ethical blind spots or problematic assumptions
- Issues of fairness, justice, and equity
- Unintended social ramifications
- Power dynamics and systemic biases
- Rights and dignity concerns

Be morally rigorous. Consider who might be harmed.""",
        ),
    ]

    def __init__(self, backend):
        self.backend = backend

    async def generate_council_antithesis(
        self,
        query: str,
        thesis: str,
        search_context: Optional[List[str]] = None,
        selected_members: Optional[List[str]] = None,
    ) -> Dict[str, CouncilCritique]:
        """Generate critiques from multiple council members concurrently.

        Args:
            query: Original query
            thesis: Thesis to critique
            search_context: Optional search results for grounding
            selected_members: Optional list of member names to use (default: all)

        Returns:
            Dictionary mapping member names to their critiques
        """
        # Select council members
        if selected_members:
            members = [m for m in self.COUNCIL_MEMBERS if m.name in selected_members]
        else:
            members = self.COUNCIL_MEMBERS

        # Generate critiques concurrently
        tasks = []
        for member in members:
            task = self._generate_member_critique(member, query, thesis, search_context)
            tasks.append(task)

        # Wait for all critiques
        critiques = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        council_results = {}
        for member, critique_result in zip(members, critiques):
            if isinstance(critique_result, Exception):
                logger.error(f"Council member {member.name} failed: {critique_result}")
                # Create fallback critique
                council_results[member.name] = CouncilCritique(
                    member=member,
                    critique=f"Critique failed due to: {critique_result}",
                    contradictions=[],
                )
            else:
                council_results[member.name] = critique_result

        return council_results

    async def _generate_member_critique(
        self,
        member: CouncilMember,
        query: str,
        thesis: str,
        search_context: Optional[List[str]] = None,
    ) -> CouncilCritique:
        """Generate a critique from a specific council member."""

        # Build context section
        context_section = ""
        if search_context:
            context_section = f"""
SEARCH CONTEXT (for fact-checking and grounding):
{chr(10).join(f"- {context}" for context in search_context)}
"""

        prompt = f"""{member.prompt_modifier}

ORIGINAL QUERY: {query}

THESIS TO CRITIQUE: {thesis}
{context_section}
Your specialty: {member.expertise}

Generate a rigorous critique from your perspective. Focus specifically on issues within your domain of expertise.

For each significant problem you identify, use this format:
CONTRADICTION: [brief description]
EVIDENCE: [detailed explanation of why this is problematic]

Be thorough but focused on your area of expertise."""

        try:
            response = await self.backend.generate(prompt)

            # Extract contradictions from the response
            contradictions = self._extract_contradictions(response)

            return CouncilCritique(member=member, critique=response, contradictions=contradictions)

        except Exception as e:
            logger.error(f"Failed to generate critique for {member.name}: {e}")
            raise

    def _extract_contradictions(self, critique_text: str) -> List[str]:
        """Extract contradiction statements from critique text."""
        import re

        # Look for CONTRADICTION: pattern
        pattern = r"CONTRADICTION:\s*([^\n]+)"
        matches = re.findall(pattern, critique_text, re.IGNORECASE)

        return [match.strip() for match in matches]

    def synthesize_council_input(self, council_results: Dict[str, CouncilCritique]) -> str:
        """Synthesize multiple council critiques into unified antithesis input.

        Args:
            council_results: Results from council members

        Returns:
            Unified critique text for synthesis phase
        """
        if not council_results:
            return "No council critiques available."

        synthesis_sections = []

        # Add header
        synthesis_sections.append("THE COUNCIL HAS DELIBERATED AND PRESENTS THESE CRITIQUES:")
        synthesis_sections.append("")

        # Add each member's perspective
        for member_name, critique in council_results.items():
            member = critique.member
            synthesis_sections.append(f"=== {member.name.upper()} ({member.expertise}) ===")
            synthesis_sections.append(critique.critique)
            synthesis_sections.append("")

        # Aggregate contradictions
        all_contradictions = []
        for critique in council_results.values():
            all_contradictions.extend(critique.contradictions)

        if all_contradictions:
            synthesis_sections.append("=== AGGREGATE CONTRADICTIONS ===")
            for i, contradiction in enumerate(all_contradictions, 1):
                synthesis_sections.append(f"{i}. {contradiction}")
            synthesis_sections.append("")

        synthesis_sections.append(
            "The synthesis must address critiques from ALL council perspectives."
        )

        return "\n".join(synthesis_sections)


async def run_council_dialectic(
    backend,
    query: str,
    thesis: str,
    search_context: Optional[List[str]] = None,
    council_members: Optional[List[str]] = None,
) -> Dict[str, CouncilCritique]:
    """Convenience function to run a council-based dialectical process.

    Args:
        backend: LLM backend
        query: Original query
        thesis: Thesis to critique
        search_context: Optional search results
        council_members: Optional specific members to use

    Returns:
        Dictionary of council critiques
    """
    council = DialecticalCouncil(backend)
    return await council.generate_council_antithesis(
        query=query, thesis=thesis, search_context=search_context, selected_members=council_members
    )

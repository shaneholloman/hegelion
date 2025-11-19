"""Prompt-driven dialectical reasoning for any LLM via MCP.

This module provides a way to run dialectical reasoning without making external API calls.
Instead, it returns structured prompts that guide the calling LLM through the process.
Perfect for Cursor, Claude Desktop, or any MCP-compatible environment.
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class DialecticalPrompt:
    """A structured prompt for dialectical reasoning."""

    phase: str
    prompt: str
    instructions: str
    expected_format: str


class PromptDrivenDialectic:
    """Orchestrates dialectical reasoning using prompts instead of API calls."""

    def __init__(self):
        self.conversation_state = {}

    def generate_thesis_prompt(self, query: str) -> DialecticalPrompt:
        """Generate a prompt for the thesis phase."""
        return DialecticalPrompt(
            phase="thesis",
            prompt=f"""You are in the THESIS phase of Hegelian dialectical reasoning.

QUERY: {query}

Your task:
1. Provide a comprehensive, well-reasoned initial position on this query
2. Consider multiple perspectives and build a strong foundational argument
3. Be thorough but clear in your reasoning
4. Acknowledge uncertainty where appropriate
5. Think step by step, then present a polished thesis

Generate your THESIS response now.""",
            instructions="Respond with a clear, well-structured thesis that establishes your initial position on the query.",
            expected_format="Free-form text thesis response",
        )

    def generate_antithesis_prompt(
        self, query: str, thesis: str, use_search_context: bool = False
    ) -> DialecticalPrompt:
        """Generate a prompt for the antithesis phase."""

        search_instruction = ""
        if use_search_context:
            search_instruction = """
IMPORTANT: Before critiquing, use available search tools to find current information about this topic. Ground your critique in real-world evidence and recent developments."""

        return DialecticalPrompt(
            phase="antithesis",
            prompt=f"""You are in the ANTITHESIS phase of Hegelian dialectical reasoning.

ORIGINAL QUERY: {query}

THESIS TO CRITIQUE: {thesis}
{search_instruction}

Your task as the critical voice:
1. Find contradictions, inconsistencies, or logical gaps in the thesis
2. Identify unexamined assumptions and hidden premises  
3. Propose alternative framings that challenge the thesis
4. Find edge cases or scenarios where the thesis breaks down
5. Be adversarial but intellectually honest

For each significant problem you identify, use this EXACT format:
CONTRADICTION: [brief description]
EVIDENCE: [detailed explanation of why this is problematic]

Generate your ANTITHESIS critique now.""",
            instructions="Respond with a rigorous critique that identifies specific contradictions and weaknesses in the thesis.",
            expected_format="Text with embedded CONTRADICTION: and EVIDENCE: sections",
        )

    def generate_council_prompts(
        self, query: str, thesis: str
    ) -> List[DialecticalPrompt]:
        """Generate prompts for multi-perspective council critique."""

        council_members = [
            {
                "name": "The Logician",
                "expertise": "Logical consistency and formal reasoning",
                "focus": "logical fallacies, internal contradictions, invalid inferences, missing premises",
            },
            {
                "name": "The Empiricist",
                "expertise": "Evidence, facts, and empirical grounding",
                "focus": "factual errors, unsupported claims, missing evidence, contradictions with established science",
            },
            {
                "name": "The Ethicist",
                "expertise": "Ethical implications and societal impact",
                "focus": "potential harm, ethical blind spots, fairness issues, unintended consequences",
            },
        ]

        prompts = []
        for member in council_members:
            prompt = DialecticalPrompt(
                phase=f"council_{member['name'].lower().replace(' ', '_')}",
                prompt=f"""You are {member['name'].upper()}, an expert in {member['expertise']}.

ORIGINAL QUERY: {query}

THESIS TO CRITIQUE: {thesis}

Your expertise: {member['expertise']}
Focus specifically on: {member['focus']}

Examine the thesis from your specialized perspective and identify problems within your domain.

For each issue you identify, use this format:
CONTRADICTION: [brief description]
EVIDENCE: [detailed explanation from your expert perspective]

Generate your specialized critique now.""",
                instructions=f"Respond as {member['name']} with critiques specific to {member['expertise']}",
                expected_format="Text with embedded CONTRADICTION: and EVIDENCE: sections",
            )
            prompts.append(prompt)

        return prompts

    def generate_synthesis_prompt(
        self,
        query: str,
        thesis: str,
        antithesis: str,
        contradictions: Optional[List[str]] = None,
    ) -> DialecticalPrompt:
        """Generate a prompt for the synthesis phase."""

        contradictions_text = ""
        if contradictions:
            contradictions_text = f"""

IDENTIFIED CONTRADICTIONS:
{chr(10).join(f"- {contradiction}" for contradiction in contradictions)}"""

        return DialecticalPrompt(
            phase="synthesis",
            prompt=f"""You are in the SYNTHESIS phase of Hegelian dialectical reasoning.

ORIGINAL QUERY: {query}

THESIS: {thesis}

ANTITHESIS (critique): {antithesis}
{contradictions_text}

Your task:
1. Generate a SYNTHESIS that TRANSCENDS both thesis and antithesis
2. Resolve or reframe the contradictions by finding a higher-level perspective
3. Make predictions that NEITHER thesis nor antithesis would make alone
4. Ensure your synthesis is testable or falsifiable when possible
5. Propose research directions or experiments if appropriate

Requirements for a valid SYNTHESIS:
- Must not simply say "the thesis is right" or "the antithesis is right"
- Must not just say "both have merit" 
- Must offer a genuinely novel perspective
- Should be more sophisticated than either original position

If the synthesis suggests new research, use this format:
RESEARCH_PROPOSAL: [brief description]
TESTABLE_PREDICTION: [specific falsifiable claim]

Generate your SYNTHESIS now.""",
            instructions="Respond with a synthesis that transcends both positions and offers novel insights",
            expected_format="Text with optional RESEARCH_PROPOSAL: and TESTABLE_PREDICTION: sections",
        )

    def generate_judge_prompt(
        self, query: str, thesis: str, antithesis: str, synthesis: str
    ) -> DialecticalPrompt:
        """Generate a prompt for quality evaluation."""

        return DialecticalPrompt(
            phase="judge",
            prompt=f"""You are the Iron Judge, evaluating dialectical reasoning quality.

ORIGINAL QUERY: {query}
THESIS: {thesis}
ANTITHESIS: {antithesis} 
SYNTHESIS: {synthesis}

Evaluate this dialectical process on:

1. **Thesis Quality** (0-2 points): Is the initial position well-reasoned?
2. **Antithesis Rigor** (0-3 points): Does the critique identify genuine problems?
3. **Synthesis Innovation** (0-3 points): Does the synthesis transcend both positions?
4. **Critique Validity** (0-2 points): Were critiques actually addressed?

Score criteria:
- 0-3: Poor quality, major logical flaws
- 4-5: Below average, some good elements but significant issues
- 6-7: Good quality, solid reasoning with minor gaps  
- 8-9: Excellent, sophisticated analysis with minimal flaws
- 10: Outstanding, exemplary dialectical reasoning

Respond with EXACTLY this format:
SCORE: [integer 0-10]
CRITIQUE_VALIDITY: [true/false]
REASONING: [detailed explanation]
STRENGTHS: [specific areas of excellence]
IMPROVEMENTS: [specific areas needing work]""",
            instructions="Evaluate the dialectical quality and provide structured feedback",
            expected_format="Structured response with SCORE:, CRITIQUE_VALIDITY:, REASONING:, STRENGTHS:, IMPROVEMENTS:",
        )


def create_dialectical_workflow(
    query: str,
    use_search: bool = False,
    use_council: bool = False,
    use_judge: bool = False,
) -> Dict[str, Any]:
    """Create a complete dialectical workflow as structured prompts.

    Returns a workflow that can be executed by any LLM via MCP.
    """

    dialectic = PromptDrivenDialectic()
    workflow = {"query": query, "workflow_type": "prompt_driven_dialectic", "steps": []}

    # Step 1: Thesis
    workflow["steps"].append(
        {
            "step": 1,
            "name": "Generate Thesis",
            "prompt": dialectic.generate_thesis_prompt(query).__dict__,
        }
    )

    # Step 2: Antithesis (standard or council-based)
    if use_council:
        council_prompts = dialectic.generate_council_prompts(
            query, "{{thesis_from_step_1}}"
        )
        for i, council_prompt in enumerate(council_prompts):
            workflow["steps"].append(
                {
                    "step": 2 + i,
                    "name": f"Council Critique: {council_prompt.phase}",
                    "prompt": council_prompt.__dict__,
                }
            )
        antithesis_step = 2 + len(council_prompts)
    else:
        workflow["steps"].append(
            {
                "step": 2,
                "name": "Generate Antithesis",
                "prompt": dialectic.generate_antithesis_prompt(
                    query, "{{thesis_from_step_1}}", use_search
                ).__dict__,
            }
        )
        antithesis_step = 3

    # Step 3: Synthesis
    workflow["steps"].append(
        {
            "step": antithesis_step,
            "name": "Generate Synthesis",
            "prompt": dialectic.generate_synthesis_prompt(
                query, "{{thesis_from_step_1}}", "{{antithesis_from_step_2}}"
            ).__dict__,
        }
    )

    # Step 4: Judge (optional)
    if use_judge:
        workflow["steps"].append(
            {
                "step": antithesis_step + 1,
                "name": "Evaluate Quality",
                "prompt": dialectic.generate_judge_prompt(
                    query,
                    "{{thesis_from_step_1}}",
                    "{{antithesis_from_step_2}}",
                    f"{{synthesis_from_step_{antithesis_step}}}",
                ).__dict__,
            }
        )

    workflow["instructions"] = {
        "execution_mode": "sequential",
        "description": "Execute each step in order, using outputs from previous steps as inputs to later steps",
        "variable_substitution": "Replace {{variable_name}} with actual outputs from previous steps",
        "final_output": "Combine all outputs into a structured HegelionResult",
    }

    return workflow


def create_single_shot_dialectic_prompt(
    query: str, use_search: bool = False, use_council: bool = False
) -> str:
    """Create a single comprehensive prompt for dialectical reasoning.

    This is for models that can handle complex multi-step reasoning in one go.
    """

    search_instruction = ""
    if use_search:
        search_instruction = """
Before beginning, use available search tools to gather current information about this topic."""

    council_instruction = ""
    if use_council:
        council_instruction = """
For the ANTITHESIS phase, adopt three distinct critical perspectives:
- THE LOGICIAN: Focus on logical consistency and formal reasoning
- THE EMPIRICIST: Focus on evidence, facts, and empirical grounding  
- THE ETHICIST: Focus on ethical implications and societal impact

Generate critiques from each perspective, then synthesize them."""

    return f"""You will now perform Hegelian dialectical reasoning on the following query using a three-phase process: THESIS → ANTITHESIS → SYNTHESIS.
{search_instruction}

QUERY: {query}

Execute the following phases:

**PHASE 1 - THESIS:**
Generate a comprehensive initial position on the query. Be thorough, well-reasoned, and consider multiple perspectives while establishing your foundational argument.

**PHASE 2 - ANTITHESIS:**{council_instruction}
Critically examine your thesis. Find contradictions, logical gaps, unexamined assumptions, and alternative framings. For each problem, use:
CONTRADICTION: [description]
EVIDENCE: [explanation]

**PHASE 3 - SYNTHESIS:**
Transcend both thesis and antithesis with a novel perspective that resolves the contradictions. Make predictions neither position would make alone. Include research proposals if appropriate:
RESEARCH_PROPOSAL: [description]  
TESTABLE_PREDICTION: [falsifiable claim]

Structure your complete response as:

# DIALECTICAL ANALYSIS: {query}

## THESIS
[Your initial position]

## ANTITHESIS  
[Your critical examination]

## SYNTHESIS
[Your transcendent resolution]

## CONTRADICTIONS IDENTIFIED
1. [Contradiction 1]: [Evidence]
2. [Contradiction 2]: [Evidence]

## RESEARCH PROPOSALS
1. [Proposal 1]: [Testable prediction]

Begin your dialectical analysis now."""

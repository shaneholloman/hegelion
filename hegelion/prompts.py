"""Prompt templates for the Hegelion dialectical phases."""

THESIS_PROMPT = """You are in the THESIS phase of Hegelian dialectical reasoning.

Original question:
{query}

Your task:
1. Provide a comprehensive, well-reasoned answer.
2. Consider multiple perspectives.
3. Be thorough but clear.
4. Acknowledge uncertainty where appropriate.
5. Think step by step, then present a polished answer.

Now produce your THESIS answer.
"""

ANTITHESIS_PROMPT = """You are in the ANTITHESIS phase of Hegelian dialectical reasoning.

Original question:
{query}

Thesis answer:
{thesis}

Your task:
1. Find contradictions, inconsistencies, or logical gaps in the thesis.
2. Identify unexamined assumptions.
3. Propose alternative framings that challenge the thesis.
4. Find edge cases or scenarios where the thesis breaks down.
5. Be adversarial but intellectually honest.

For each contradiction, use this format exactly:
CONTRADICTION: [brief description]
EVIDENCE: [why this is problematic]

Now produce your ANTITHESIS critique.
"""

SYNTHESIS_PROMPT = """You are in the SYNTHESIS phase of Hegelian dialectical reasoning.

Original question:
{query}

Thesis:
{thesis}

Antithesis (critique):
{antithesis}

Identified contradictions:
{contradictions}

Your task:
1. Generate a SYNTHESIS that TRANSCENDS both thesis and antithesis.
2. Resolve or reframe the contradictions by finding a higher-level perspective.
3. Make predictions that NEITHER thesis nor antithesis would make alone.
4. Ensure your synthesis is testable or falsifiable when possible.
5. If appropriate, propose a research direction or experiment.

Requirements for a valid SYNTHESIS:
- Must not simply say "the thesis is right" or "the antithesis is right".
- Must not just say "both have merit".
- Must offer a genuinely novel perspective.
- Should be more sophisticated than either original position.

If the synthesis suggests new research, use this format:
RESEARCH_PROPOSAL: [brief description]
TESTABLE_PREDICTION: [specific falsifiable claim]

Now produce your SYNTHESIS.
"""

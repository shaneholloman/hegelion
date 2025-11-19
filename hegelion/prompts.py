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
{search_instruction}

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

PERSONA_ANTITHESIS_PROMPT = """You are {persona_name}.
{persona_description}

Original question:
{query}

Thesis answer:
{thesis}
{search_instruction}

Your expertise: {persona_focus}
Your instructions: {persona_instructions}

Examine the thesis from your specialized perspective. Identify problems within your domain.

For each issue you identify, use this format:
CONTRADICTION: [brief description]
EVIDENCE: [detailed explanation from your expert perspective]

Generate your specialized critique now.
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

MULTI_PERSPECTIVE_SYNTHESIS_PROMPT = """You are in the SYNTHESIS phase of Hegelian dialectical reasoning.

Original question:
{query}

Thesis:
{thesis}

CRITIQUES (Multiple Perspectives):
{antithesis}

Identified contradictions:
{contradictions}

Your task:
1. Synthesize the thesis with ALL the critiques provided above.
2. Resolve the tensions between the initial position and the various critical perspectives.
3. Find a higher-level perspective that satisfies the valid points raised by all critics.
4. Make predictions that transcend the initial debate.

Requirements for a valid SYNTHESIS:
- Must not simply say "everyone is right".
- Must offer a genuinely novel perspective that integrates these diverse viewpoints.
- Should be more sophisticated than any single position.

If the synthesis suggests new research, use this format:
RESEARCH_PROPOSAL: [brief description]
TESTABLE_PREDICTION: [specific falsifiable claim]

Now produce your SYNTHESIS.
"""

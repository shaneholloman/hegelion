#!/usr/bin/env python3
"""
Subagent prompts for unbiased response generation.

This file contains the exact prompts to use when spawning subagents
to generate benchmark responses without benchmark context.
"""

# Raw baseline - just the question, nothing else
RAW_BASELINE_PROMPT = """Answer this question thoroughly:

{question}

Provide a complete, well-reasoned response."""


# Enhanced baseline - structured thinking (simulates system prompt + question)
ENHANCED_BASELINE_PROMPT = """You are a rigorous analytical thinker. For every question:
1. First, articulate the strongest position on the topic
2. Then, identify the most compelling counterarguments and tensions
3. Finally, synthesize a nuanced conclusion that transcends simple for/against framing

Be thorough. Acknowledge uncertainty. Identify where reasonable people disagree.

Question: {question}

Provide your complete analysis."""


# Hegelion Phase 1: Thesis
THESIS_PROMPT = """You are in the THESIS phase of reasoning.

Question: {question}

Your task:
1. Provide a comprehensive, well-reasoned answer.
2. Consider multiple perspectives.
3. Be thorough but clear.
4. Acknowledge uncertainty where appropriate.

Produce your THESIS answer now."""


# Hegelion Phase 2: Antithesis
ANTITHESIS_PROMPT = """You are in the ANTITHESIS phase of reasoning.

Original question: {question}

Thesis answer:
{thesis}

Your task:
1. Find contradictions, inconsistencies, or logical gaps in the thesis.
2. Identify unexamined assumptions.
3. Propose alternative framings that challenge the thesis.
4. Find edge cases or scenarios where the thesis breaks down.
5. Be adversarial but intellectually honest.

For each contradiction, use this format:
CONTRADICTION: [brief description]
EVIDENCE: [why this is problematic]

Produce your ANTITHESIS critique now."""


# Hegelion Phase 3: Synthesis
SYNTHESIS_PROMPT = """You are in the SYNTHESIS phase of reasoning.

Original question: {question}

Thesis:
{thesis}

Antithesis (critique):
{antithesis}

Your task:
1. Generate a SYNTHESIS that TRANSCENDS both thesis and antithesis.
2. Resolve or reframe the contradictions by finding a higher-level perspective.
3. Make predictions that NEITHER thesis nor antithesis would make alone.
4. Ensure your synthesis is testable or falsifiable when possible.

Requirements:
- Must not simply say "the thesis is right" or "the antithesis is right".
- Must not just say "both have merit".
- Must offer a genuinely novel perspective.
- Should be more sophisticated than either original position.

Produce your SYNTHESIS now."""


# Dry-run prompts (1 per category)
DRY_RUN_PROMPTS = [
    {"id": "P001", "category": "philosophy", "text": "Is there a hard problem of consciousness?"},
    {"id": "P016", "category": "policy", "text": "Should we have open borders?"},
    {"id": "P026", "category": "science", "text": "Is the universe fine-tuned for life?"},
    {"id": "P036", "category": "creative", "text": "Should offensive art be deplatformed?"},
    {"id": "P046", "category": "factual", "text": "Is aging a disease we can cure?"},
]

# The Dialectical Method

Hegelion implements Hegelian dialectics as a computational pattern. This document explains the philosophy behind the architecture.

## The Core Idea

Hegelian dialectic is a thinking pattern:

1. **Thesis (Position)**: State a comprehensive answer
2. **Antithesis (Negation)**: Seriously attack that answer
3. **Synthesis (Sublation)**: Build something new that transcends both

The key insight: genuine understanding emerges from contradiction, not from smooth consensus.

## Why Separate API Calls?

Asking a model for "thesis, antithesis, and synthesis" in a single prompt allows hedging. The model knows where it's going—it can construct a balanced synthesis without genuinely confronting contradictions.

Hegelion forces separation:

1. **Call 1**: Generate the best thesis. Commit fully.
2. **Call 2**: Attack that thesis. No hedging allowed—you already committed.
3. **Call 3**: Reconcile genuinely opposed positions.

This forced redirection surfaces insights the single-call approach shortcuts.

## The Phases

### Thesis

Generate a comprehensive, well-reasoned answer. Consider multiple perspectives. Be thorough but clear.

The thesis phase isn't about finding "the right answer"—it's about building the strongest possible initial position.

### Antithesis

Systematically critique the thesis:

- Find contradictions and logical gaps
- Identify unexamined assumptions
- Propose alternative framings
- Find edge cases where the thesis breaks down

The antithesis phase forces the model to inhabit the negative—to seriously attack its own work. This is where the dialectic earns its value.

### Synthesis

Transcend both positions. The synthesis cannot simply:

- Say "thesis is right"
- Say "antithesis is right"
- Say "both have merit" without deeper insight

It must offer a genuinely novel perspective that resolves the tension at a higher level.

## Research Proposals

Hegelion encourages the synthesis to generate testable predictions and research proposals. This grounds the dialectic in actionable outcomes:

```
RESEARCH_PROPOSAL: [description]
TESTABLE_PREDICTION: [falsifiable claim]
```

## The Council

When `use_council=True`, the antithesis phase spawns three concurrent critics:

- **Logician**: Attacks logical consistency and reasoning structure
- **Empiricist**: Challenges empirical claims and evidence
- **Ethicist**: Examines moral implications and value assumptions

This multi-perspective critique produces richer contradictions for the synthesis to resolve.

## Not Just Philosophy

Hegelion is a practical tool, not an academic exercise. The dialectical structure:

- Forces genuine engagement with counterarguments
- Produces auditable reasoning traces
- Catches blind spots that single-pass generation misses
- Generates novel frameworks rather than literature summaries

The philosophy serves the engineering. The format forces the content.

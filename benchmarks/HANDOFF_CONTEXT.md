# Hegelion Benchmark Context - Handoff Document

## What You Need to Know

### What Hegelion Is

Hegelion is a **multi-call LLM orchestration system** that structures reasoning into thesis→antithesis→synthesis phases. It's NOT a single clever prompt - it makes **3-7 separate API calls** per query.

```
Query: "Is AI creative?"
       ↓
[Call 1] Generate THESIS (initial position)
       ↓
[Call 2] Generate ANTITHESIS (critique thesis, find contradictions)
       ↓
[Call 3] Generate SYNTHESIS (transcend both, novel insight)
       ↓
Output: Structured result with contradictions identified, research proposals, etc.
```

**Council mode** adds 3 concurrent critic calls (Logician, Empiricist, Ethicist) = 5 calls total.
**Judge mode** adds a quality evaluation call that can trigger retries = 4-10+ calls.

---

## The Core Benchmarking Problem

### Cost Structure

| Approach | API Calls | Token Cost (rough) |
|----------|-----------|-------------------|
| Raw completion | 1 | 1× |
| Chain-of-thought (single call) | 1 | ~1.5× (longer output) |
| **Hegelion Basic** | 3 | **3-4×** |
| **Hegelion Council** | 5 | **5-7×** |
| Hegelion + Judge | 6+ | **6-10×** |

### The Question We Need to Answer

> **Does Hegelion produce enough additional insight to justify 3-7× the cost?**

This is NOT:
- "Is Hegelion output better?" (trivially yes - more tokens = more content)
- "Does structure help?" (probably yes, but at what cost?)

This IS:
- "Is the **insight-per-dollar** better than alternatives?"
- "Could we get the same quality by just asking for a longer, more thorough single response?"

---

## The Key Metric: Quality-Adjusted Cost Efficiency

### Naive Comparison (Wrong)

```
Hegelion score: 8.5/10
Baseline score: 6.0/10
∴ Hegelion is better!
```

This ignores that Hegelion costs 3-4× more.

### Cost-Adjusted Comparison (Right)

```
Hegelion: 8.5 quality / 3.5× cost = 2.43 quality-per-dollar
Baseline: 6.0 quality / 1× cost = 6.0 quality-per-dollar
Enhanced baseline (3× tokens): 7.5 quality / 1.2× cost = 6.25 quality-per-dollar
∴ Enhanced baseline might be more efficient!
```

### What "Hegelion Wins" Actually Means

Hegelion wins if:
```
(Hegelion_Quality - Baseline_Quality) / (Hegelion_Cost - Baseline_Cost) > threshold
```

Or more simply: **the marginal quality gain exceeds the marginal cost.**

---

## Fair Comparison Groups

To isolate what Hegelion actually adds, we need:

### Group A: Raw Baseline (1 call, ~500 tokens out)
```
Prompt: "Answer this question: {query}"
```

### Group B: Enhanced Baseline (1 call, ~1500 tokens out)
```
Prompt: "Think through this carefully. Consider:
1. The strongest argument for one position
2. The strongest counterarguments
3. A nuanced conclusion that addresses tensions
Query: {query}"
```

**This is the critical comparison.** If Group B matches Hegelion quality, then Hegelion's multi-call structure adds no value - you can get the same result by just asking for more thorough output in a single call.

### Group C: Self-Consistency (3 calls, majority vote)
```
3 independent completions of same prompt → synthesize or vote
```

Tests whether Hegelion's structured phases beat unstructured sampling diversity.

### Group D: Hegelion Basic (3 calls)
The standard thesis→antithesis→synthesis flow.

### Group E: Hegelion Council (5 calls)
Multi-perspective antithesis.

---

## Metrics to Capture "Insight"

### Measurable Proxies for Insight

1. **Contradiction Identification**
   - Does the output acknowledge legitimate counterarguments?
   - Count: How many distinct opposing viewpoints addressed?

2. **Nuance Score** (human or LLM-judge rated 1-5)
   - Does it avoid false dichotomies?
   - Does it acknowledge uncertainty appropriately?
   - Does it distinguish strong vs weak claims?

3. **Novel Synthesis** (hardest to measure)
   - Does the conclusion go beyond "both sides have merit"?
   - Is there a genuinely new framing or insight?
   - Would an expert find something non-obvious?

4. **Testable Predictions**
   - Does it generate falsifiable claims?
   - Are research proposals actionable?

### The Insight-Per-Token Formula

```
Efficiency = (Nuance + Contradiction_Handling + Synthesis_Quality) / Total_Tokens
```

Or cost-based:
```
Efficiency = Quality_Score / (Input_Tokens × $input_rate + Output_Tokens × $output_rate)
```

---

## The Honest Hypothesis

**Hegelion's value proposition:**

For **complex, contested questions** (ethics, philosophy, policy), the structured dialectical process produces insights that a single-pass completion misses, even with chain-of-thought prompting.

For **simple factual questions**, Hegelion is overkill - the extra calls add cost without adding value.

**Expected outcome:**
- Hegelion >> Baseline on philosophical/ethical questions
- Hegelion ≈ Enhanced Baseline on factual questions
- Hegelion's sweet spot is medium-complexity contested topics

---

## What the Benchmark Needs to Prove

### Minimum Bar (Hegelion is useful)
Hegelion Basic beats Enhanced Baseline on at least ONE quality metric, for at least SOME query types, with cost-adjusted efficiency > 0.5× baseline.

### Strong Claim (Hegelion is worth the cost)
Hegelion Basic has higher cost-adjusted quality than all single-call alternatives across contested topics.

### Ideal Outcome (Hegelion is optimal)
Council mode shows diminishing returns (basic is the sweet spot), and there's a clear query-type → mode mapping.

---

## Practical Next Steps

1. **Generate comparison data** for 50-100 queries:
   - Raw baseline responses
   - Enhanced baseline responses (same model, longer output)
   - Hegelion basic responses

2. **Measure costs precisely:**
   - Track input/output tokens per response
   - Calculate actual $ cost per query per method

3. **Evaluate quality:**
   - LLM-as-judge (blind) rates each response
   - Focus on: nuance, contradiction handling, synthesis quality

4. **Compute efficiency:**
   - Quality / Cost for each method
   - Statistical comparison (paired tests)

5. **Segment by query type:**
   - Does Hegelion win on ethics but lose on factual?
   - Find the crossover point

---

## Key Files in Repo

```
benchmarks/
├── ARCHITECTURE_ANALYSIS.md   # How Hegelion works (3-7 API calls)
├── BENCHMARK_PROPOSAL.md      # Full methodology
├── EXISTING_DATA_AUDIT.md     # What data we have (580 prompts, 4 examples)
├── HANDOFF_CONTEXT.md         # This file
└── examples_basic.jsonl       # 15 starter queries

hegelion-data/
├── prompts/hegelion_prompts_500.txt  # 580 benchmark prompts
└── examples/glm4_6_examples.jsonl    # 4 high-quality output examples
```

---

## TL;DR for Other Claude

**Hegelion = 3-7 API calls in structured thesis→antithesis→synthesis flow.**

**The benchmark question = Does it produce enough extra insight to justify 3-7× cost?**

**Key comparison = Hegelion (3 calls) vs Enhanced Single Prompt (1 call, ~3× output tokens)**

**Metric = Quality per dollar, not just quality.**

**Hypothesis = Hegelion wins on complex contested topics, loses on simple factual queries.**

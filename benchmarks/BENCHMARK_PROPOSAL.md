# Proposed Benchmark Strategy for Hegelion

## What We're Actually Testing

Based on the architecture analysis, Hegelion is **multi-call orchestration** that:
1. Makes 3-7+ API calls per query
2. Uses specialized prompts for each dialectical phase
3. Optionally parallelizes critique generation (council mode)
4. Optionally gates quality with retry loops (judge mode)

**The core hypothesis to test:**
> Does structuring LLM reasoning into thesis→antithesis→synthesis phases produce more reliable, nuanced, and well-reasoned outputs than equivalent-cost alternatives?

This is NOT testing:
- Whether a magic prompt makes models smarter
- Whether fine-tuned models outperform base models
- Whether more API calls always equal better results

---

## Comparison Groups

### Group A: Raw Baseline (1 call)
Single completion with no structure.

```
Prompt: "Answer this question thoroughly: {query}"
Calls: 1
Cost: 1×
```

**What this tests:** Does any structure help at all?

---

### Group B: Enhanced Baseline (1 call, ~3× tokens)
Single completion with chain-of-thought, using similar token budget to Hegelion.

```
Prompt: "Think through this question step by step. Consider:
1. The main argument for one position
2. Counterarguments and weaknesses
3. A balanced conclusion that addresses both sides
Query: {query}"
Calls: 1
Cost: ~1× (but ~3× output tokens)
```

**What this tests:** Is the benefit from multi-call structure or just from asking for more thorough responses?

---

### Group C: Self-Consistency (3 calls)
Three independent completions, synthesized or majority-voted.

```
Calls: 3 independent completions of the same prompt
Synthesis: Either majority vote or prompt asking to reconcile
Cost: ~3×
```

**What this tests:** Is structured T-A-S better than just sampling multiple times?

---

### Group D: Hegelion Basic (3 calls)
Standard thesis→antithesis→synthesis flow.

```
Calls: 3 sequential (thesis, antithesis, synthesis)
Cost: ~3-4×
```

**What this tests:** The core dialectical structure.

---

### Group E: Hegelion Council (5 calls)
Multi-perspective antithesis with concurrent critics.

```
Calls: 5 (thesis + 3 concurrent critics + synthesis)
Cost: ~5-6×
```

**What this tests:** Does diversity of criticism improve synthesis?

---

### Group F: Hegelion Council + Judge (6+ calls)
Full pipeline with quality gating.

```
Calls: 6+ (council + judge, potential retries)
Cost: ~6-10×
```

**What this tests:** Does quality gating produce better final outputs?

---

## Metrics That Make Sense

Given that Hegelion emphasizes nuance and addressing contradictions, we should measure:

### 1. Factual Accuracy (for factual queries)
- Ground truth comparison for questions with known answers
- Error rate on verifiable claims
- **Tool:** Automated fact-checking against knowledge base

### 2. Contradiction Identification
- Does the output acknowledge relevant counterarguments?
- Are edge cases mentioned?
- **Tool:** Human evaluation or LLM-as-judge

### 3. Nuance Score
- Does the output avoid false dichotomies?
- Are qualifications and caveats appropriate?
- **Tool:** Human evaluation rubric (1-5 scale)

### 4. Synthesis Quality
- Does the conclusion genuinely integrate opposing views?
- Is there a novel insight beyond "both sides have merit"?
- **Tool:** Human evaluation, blind comparison

### 5. Research Proposal Quality (for complex queries)
- Is a testable prediction generated?
- Is the proposed investigation feasible?
- **Tool:** Domain expert evaluation

### 6. Cost-Adjusted Performance
- Performance gain per dollar spent
- **Calculation:** (Metric Score - Baseline) / (Cost Multiplier)

---

## Proposed Methodology

### Phase 1: Query Selection (N=100-500)

**Query Categories:**
| Category | Count | Example | Ground Truth |
|----------|-------|---------|--------------|
| Factual | 20 | "What causes tides?" | Verifiable |
| Historical | 20 | "Why did Rome fall?" | Expert consensus |
| Ethical | 30 | "Should we edit human embryos?" | No ground truth |
| Philosophical | 30 | "Is consciousness physical?" | No ground truth |
| Policy | 20 | "Should AI be regulated?" | No ground truth |

**Selection Criteria:**
- Questions that genuinely have multiple valid perspectives
- Avoid trivia or purely factual lookups
- Include some with "correct" answers (factual) and some without (ethical)

**Source:** Draw from `hegelion-data/prompts/hegelion_prompts_500.txt` for consistency.

---

### Phase 2: Response Generation

For each query, generate responses using:
- Group A: Raw baseline
- Group B: Enhanced baseline
- Group C: Self-consistency (3×)
- Group D: Hegelion Basic
- Group E: Hegelion Council

Record:
- Full response text
- Token counts (input/output)
- Latency
- Cost

**Important:** Use the SAME model (e.g., Claude Sonnet 4, GPT-4) across all groups to isolate the effect of structure.

---

### Phase 3: Evaluation

#### Automated Metrics
1. **Response length** - Longer isn't always better, but track it
2. **Contradiction count** - Number of `CONTRADICTION:` patterns found
3. **Research proposal presence** - Boolean
4. **Readability score** - Flesch-Kincaid or similar

#### LLM-as-Judge Evaluation
Use a separate, more capable model (e.g., Claude Opus) to rate:
- Overall quality (1-10)
- Nuance (1-5)
- Contradiction handling (1-5)
- Synthesis quality (1-5)

**Important:** Blind the judge to which method produced each response.

#### Human Evaluation (subset)
For N=50-100 queries:
- Side-by-side blind comparison
- "Which response is more thorough and balanced?"
- Domain experts for specialized topics

---

### Phase 4: Analysis

#### Primary Comparisons
1. **Hegelion Basic vs Enhanced Baseline** (same cost tier)
   - Tests: Is T-A-S structure better than just asking for thorough response?

2. **Hegelion Basic vs Self-Consistency** (same call count)
   - Tests: Is structured dialectic better than sampling diversity?

3. **Hegelion Council vs Hegelion Basic** (5 vs 3 calls)
   - Tests: Does multi-perspective criticism help?

4. **Cost-Adjusted Comparison** (all groups)
   - Tests: Which approach gives best quality per dollar?

#### Statistical Methods
- Paired t-tests or Wilcoxon signed-rank for score comparisons
- Bootstrap confidence intervals for cost-adjusted metrics
- Effect size (Cohen's d) for practical significance

---

## Expected Outcomes

### Scenario: "Hegelion Wins"
- Hegelion Basic scores significantly higher than Enhanced Baseline on nuance and contradiction handling
- Hegelion Council shows diminishing returns but higher ceiling
- Cost-adjusted performance is competitive (within 1.5×)

**Evidence pattern:**
| Group | Nuance Score | Cost | Score/Cost |
|-------|-------------|------|------------|
| Baseline | 3.0 | 1× | 3.0 |
| Enhanced | 3.5 | 1× | 3.5 |
| **Hegelion** | **4.5** | **3×** | **1.5** |
| Council | 4.8 | 5× | 0.96 |

### Scenario: "No Difference"
- Hegelion scores similarly to Enhanced Baseline
- Self-consistency performs as well or better
- The structure provides no benefit over just asking for more

**Evidence pattern:**
| Group | Nuance Score | Cost | Score/Cost |
|-------|-------------|------|------------|
| Baseline | 3.0 | 1× | 3.0 |
| Enhanced | 4.2 | 1× | 4.2 |
| Hegelion | 4.3 | 3× | 1.4 |
| Self-Consistency | 4.4 | 3× | 1.5 |

### Scenario: "Query-Type Dependent"
- Hegelion excels on ethical/philosophical queries
- No benefit on factual queries
- Sweet spot exists for certain complexity levels

**Evidence pattern:**
| Query Type | Hegelion Advantage |
|------------|-------------------|
| Factual | -5% (worse, overkill) |
| Historical | +10% |
| **Ethical** | **+35%** |
| **Philosophical** | **+40%** |
| Policy | +25% |

---

## Honest Limitations

### What This Benchmark Cannot Prove

1. **Generalization across models**
   - Results may differ between Claude, GPT, Llama
   - Need separate benchmarks per model family

2. **Long-term reliability**
   - Single snapshot, not longitudinal
   - Model updates may change results

3. **Real-world impact**
   - Lab metrics ≠ user satisfaction
   - No measurement of downstream decision quality

4. **Optimal configuration**
   - Cannot test all parameter combinations
   - Council member composition is fixed

### Confounding Variables

1. **Prompt quality**
   - Hegelion prompts are well-engineered
   - Baselines may not be optimally prompted

2. **Evaluator bias**
   - LLM-as-judge may prefer verbose responses
   - Humans may have Hegelion exposure

3. **Query selection bias**
   - Questions chosen may favor dialectical structure
   - Need diverse query sources

### Mitigations

- Use multiple evaluator models
- Include trivial queries where Hegelion should NOT help
- Report confidence intervals, not just point estimates
- Pre-register analysis plan

---

## Minimum Viable Benchmark

**Goal:** Quick proof-of-concept in 1-2 days

| Component | Specification |
|-----------|---------------|
| Queries | 50 (10 per category) |
| Groups | A, B, D only (baseline, enhanced, Hegelion basic) |
| Model | Claude Sonnet 4 or GPT-4 |
| Evaluation | LLM-as-judge only (Claude Opus) |
| Metrics | Overall quality, nuance, cost |

**Expected output:**
- Bar chart comparing groups
- Statistical significance test
- Cost-adjusted comparison table

---

## Stretch Goal: Publication-Quality Benchmark

**Goal:** Rigorous evaluation suitable for paper/blog post

| Component | Specification |
|-----------|---------------|
| Queries | 300+ across 6 categories |
| Groups | All 5 (A through E) |
| Models | Claude Sonnet 4, GPT-4, Llama 3 70B |
| Evaluation | LLM-as-judge + human evaluation (N=100) |
| Metrics | Full suite (accuracy, nuance, synthesis, cost) |
| Analysis | Statistical tests, effect sizes, confidence intervals |

**Additional requirements:**
- Pre-registration of hypotheses
- Blind human evaluation protocol
- Release of all prompts, responses, and evaluation data
- Reproducibility package

---

## Recommended Next Steps

### Immediate (This Week)
1. **Run MVB with 50 queries** using existing `hegelion-data/prompts/`
2. **Implement LLM-as-judge** evaluation script
3. **Generate baseline responses** for comparison

### Short-Term (Next 2 Weeks)
4. **Expand to 300 queries** with category balance
5. **Add self-consistency baseline** (Group C)
6. **Human evaluation protocol** for subset

### Medium-Term (1 Month)
7. **Multi-model comparison** (Claude, GPT, Llama)
8. **Ablation study** (vary council composition, judge threshold)
9. **Write up findings** for blog/paper

---

## Files to Create

```
benchmarks/
├── ARCHITECTURE_ANALYSIS.md    # This analysis
├── BENCHMARK_PROPOSAL.md       # This proposal
├── EXISTING_DATA_AUDIT.md      # Data inventory
├── queries/
│   ├── factual_50.jsonl
│   ├── ethical_50.jsonl
│   └── ...
├── baselines/
│   ├── raw_baseline.py
│   ├── enhanced_baseline.py
│   └── self_consistency.py
├── evaluation/
│   ├── llm_judge.py
│   ├── human_eval_protocol.md
│   └── metrics.py
└── results/
    └── (generated)
```

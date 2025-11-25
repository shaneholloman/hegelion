# Existing Data Audit

## Summary

| Asset | Location | Count | Usable for Benchmark |
|-------|----------|-------|---------------------|
| Prompt library | `hegelion-data/prompts/hegelion_prompts_500.txt` | 580 | Yes |
| Example outputs | `hegelion-data/examples/glm4_6_examples.jsonl` | 4 | Reference only |
| Basic benchmark queries | `benchmarks/examples_basic.jsonl` | 15 | Yes |
| Generated datasets | `hegelion-data/data/` | 0 (empty) | N/A |

---

## Detailed Inventory

### 1. Prompt Library

**File:** `hegelion-data/prompts/hegelion_prompts_500.txt`
**Format:** Plain text, one prompt per line with category headers
**Count:** 580 prompts across 30+ categories

**Categories Found:**
- Philosophy & Metaphysics (~20)
- Ethics & Moral Philosophy (~20)
- Political Philosophy (~20)
- Science & Epistemology (~20)
- Technology & Society (~20)
- Economics (~20)
- Psychology & Mind (~20)
- Art & Aesthetics (~20)
- Law & Justice (~20)
- Environment & Sustainability (~20)
- Education (~20)
- Healthcare (~20)
- Media & Communication (~20)
- Religion & Spirituality (~20)
- Identity & Culture (~20)
- Work & Labor (~20)
- Relationships (~20)
- Future & Speculation (~20)
- Paradoxes & Puzzles (~20)
- Meta-questions (~20)

**Quality Assessment:**
- Well-suited for dialectical reasoning (questions naturally invite multiple perspectives)
- Mix of empirical and normative questions
- Some may be too broad ("What is the meaning of life?")
- Some may be too narrow for interesting dialectic

**Usability:** ✅ Primary source for benchmark queries

---

### 2. Example Outputs

**File:** `hegelion-data/examples/glm4_6_examples.jsonl`
**Format:** JSONL with full HegelionResult structure
**Count:** 4 examples
**Model:** GLM-4.6 (via AnthropicLLMBackend wrapper)

**Schema per record:**
```json
{
  "query": "string",
  "mode": "synthesis",
  "thesis": "string (full text)",
  "antithesis": "string (full text)",
  "synthesis": "string (full text)",
  "contradictions": [
    {"description": "string", "evidence": "string"}
  ],
  "research_proposals": [
    {"description": "string", "testable_prediction": "string"}
  ],
  "metadata": {
    "thesis_time_ms": number,
    "antithesis_time_ms": number,
    "synthesis_time_ms": number,
    "total_time_ms": number,
    "backend_provider": "string",
    "backend_model": "string",
    "debug": {
      "internal_conflict_score": number
    }
  },
  "trace": {
    "thesis": "string",
    "antithesis": "string",
    "synthesis": "string",
    "contradictions_found": number,
    "research_proposals": ["string"],
    "internal_conflict_score": number
  }
}
```

**Example Queries in Dataset:**
1. "Can AI be genuinely creative?" (~19,000 chars total)
2. "What is the capital of France?" (~3,500 chars)
3. "Explain what photosynthesis does for a plant." (~4,000 chars)
4. "When was the first moon landing?" (~4,000 chars)

**Quality Assessment:**
- Very high quality outputs (long, detailed thesis/antithesis/synthesis)
- Include structured contradictions and research proposals
- Include timing metadata for performance analysis
- Mix of complex philosophical and simple factual questions

**Usability:** ✅ Reference quality standard, too small for statistical analysis

---

### 3. Basic Benchmark Queries

**File:** `benchmarks/examples_basic.jsonl`
**Format:** JSONL with query and category
**Count:** 15 queries

**Schema:**
```json
{
  "category": "factual|scientific|historical|philosophical|ethical",
  "prompt": "string"
}
```

**Distribution:**
| Category | Count | Examples |
|----------|-------|----------|
| factual | 3 | Printing press year, moon landing, Australia capital |
| scientific | 3 | Photosynthesis, climate change, vaccines |
| historical | 3 | WWI causes, Roman fall, Industrial Revolution |
| philosophical | 3 | AI consciousness, meaning of life, free will |
| ethical | 3 | AI surveillance, genetic engineering, privacy vs security |

**Quality Assessment:**
- Good category balance
- Mix of factual (verifiable) and open-ended questions
- Small but well-structured

**Usability:** ✅ Good starting point, needs expansion

---

### 4. Generated Datasets

**Directory:** `hegelion-data/data/`
**Status:** Empty (gitignored, user-generated)

The README describes expected files:
- `test_10.jsonl` - Test runs
- `hegelion_500.jsonl` - Raw generation
- `hegelion_500_clean.jsonl` - Final cleaned dataset

**Usability:** ❌ No existing generated data to analyze

---

## Data Gaps

### What We Have
1. **Prompts:** 580+ questions ready to use
2. **Schema:** Well-defined output format
3. **Examples:** 4 high-quality reference outputs
4. **Categories:** Balanced prompt categories

### What We Need

| Need | Priority | Effort |
|------|----------|--------|
| **Baseline responses** (raw completion) | High | Medium - generate with same model |
| **Enhanced baseline responses** (CoT) | High | Medium - single prompt per query |
| **More Hegelion outputs** | High | Medium - run `hegelion-bench` |
| **Human evaluation labels** | Medium | High - requires annotators |
| **Ground truth for factual queries** | Medium | Low - lookup answers |
| **Self-consistency baselines** | Medium | Medium - 3× generation |

---

## Data Quality Checks

### Existing Example Analysis

From `glm4_6_examples.jsonl`:

| Metric | Example 1 (AI creative) | Example 2 (France capital) | Example 3 (Photosynthesis) | Example 4 (Moon landing) |
|--------|------------------------|---------------------------|---------------------------|-------------------------|
| Total chars | ~19,000 | ~3,500 | ~4,000 | ~4,000 |
| Thesis chars | ~3,500 | ~400 | ~600 | ~600 |
| Antithesis chars | ~5,000 | ~400 | ~500 | ~600 |
| Synthesis chars | ~8,000 | ~600 | ~600 | ~700 |
| Contradictions | 3 | 2 | 2 | 2 |
| Research proposals | 1 | 1 | 1 | 1 |
| Conflict score | 0.95 | 0.41 | 0.53 | 0.47 |
| Total time (ms) | 37,564 | 6,646 | 7,494 | 6,988 |

**Observations:**
- Complex philosophical questions generate much longer outputs
- Factual questions still produce dialectical structure but shorter
- Conflict score correlates with question complexity
- All examples have valid contradictions and proposals

---

## Extractable Components

### Can We Extract Original Prompts?
**Yes** - The `query` field contains the original prompt.

### Can We Extract Raw Model Outputs?
**Yes** - The `thesis`, `antithesis`, `synthesis` fields contain full text.

### Do We Have Phase-by-Phase Timing?
**Yes** - `metadata` includes `thesis_time_ms`, `antithesis_time_ms`, `synthesis_time_ms`.

### Do We Have Mode Information?
**Yes** - `mode` field indicates "synthesis" (full dialectic), could be "thesis_only" etc.

### Do We Have Model Information?
**Yes** - `metadata.backend_model` and `metadata.backend_provider`.

---

## Recommendations

### Immediate Actions

1. **Generate baseline dataset**
   - Use prompts from `hegelion_prompts_500.txt`
   - Generate raw completions for same prompts
   - Store in `benchmarks/baselines/raw_responses.jsonl`

2. **Expand Hegelion outputs**
   - Run `hegelion-bench` on 100+ prompts
   - Use consistent model (Claude Sonnet 4)
   - Store in `benchmarks/hegelion_outputs.jsonl`

3. **Create ground truth for factual subset**
   - Select 20 factual questions from prompts
   - Document correct answers
   - Store in `benchmarks/ground_truth/factual.jsonl`

### Data Storage Schema

Standardize on this schema for all benchmark data:

```json
{
  "id": "unique-query-id",
  "query": "The original question",
  "category": "factual|ethical|philosophical|...",
  "ground_truth": "correct answer if applicable",
  "responses": {
    "raw_baseline": {
      "text": "response text",
      "tokens_in": 50,
      "tokens_out": 500,
      "latency_ms": 1200,
      "model": "claude-sonnet-4"
    },
    "enhanced_baseline": {...},
    "hegelion_basic": {
      "thesis": "...",
      "antithesis": "...",
      "synthesis": "...",
      "contradictions": [...],
      "research_proposals": [...],
      "total_tokens_in": 1500,
      "total_tokens_out": 1800,
      "latency_ms": 4500,
      "model": "claude-sonnet-4"
    },
    "hegelion_council": {...}
  },
  "evaluations": {
    "llm_judge": {
      "raw_baseline_score": 6.5,
      "hegelion_basic_score": 8.2,
      "...": "..."
    },
    "human_eval": {...}
  }
}
```

---

## Generation Scripts Available

### For Hegelion Outputs
- `hegelion/scripts/hegelion_bench.py` - CLI benchmark runner
- `hegelion/scripts/hegelion_cli.py` - Single query runner
- `hegelion-data/scripts/generate_with_kimi.py` - Batch generator

### For Baseline Outputs
- Need to create: `benchmarks/baselines/raw_baseline.py`
- Need to create: `benchmarks/baselines/enhanced_baseline.py`

### For Evaluation
- Need to create: `benchmarks/evaluation/llm_judge.py`

---

## Conclusion

**We have good prompts but limited generated data.** The 4 example outputs demonstrate the quality achievable but are insufficient for statistical analysis.

**Priority actions:**
1. Generate 100+ Hegelion outputs using existing prompts
2. Generate matching baseline outputs for fair comparison
3. Create evaluation infrastructure (LLM-as-judge)
4. Expand to 300+ for publication-quality benchmark

The infrastructure exists (`hegelion-bench`, generation scripts), we just need to run the data generation pipeline.

# Hegelion Architecture Analysis

## Executive Summary

**Hegelion is a multi-call orchestration system**, not a single-call prompt engineering trick. It makes 3-7+ separate API calls per query depending on configuration, with each phase (thesis, antithesis, synthesis) being a distinct LLM invocation.

---

## API Call Structure

### Basic Mode: 3 Sequential Calls

```
Query → [API 1: Thesis] → [API 2: Antithesis] → [API 3: Synthesis] → Result
```

| Phase | API Calls | Concurrency |
|-------|-----------|-------------|
| Thesis | 1 | Sequential |
| Antithesis | 1 | Sequential (waits for thesis) |
| Synthesis | 1 | Sequential (waits for antithesis) |
| **Total** | **3** | |

**Code Path:** `core/core.py:run_dialectic()` → `engine.py:process_query()` → `engine.py:_run_cycle()`

Each call is `await`ed before proceeding to the next phase.

---

### Council Mode: 5 Calls (3 Concurrent)

```
Query → [API 1: Thesis] → [API 2-4: Council (concurrent)] → [API 5: Synthesis] → Result
                              ├─ Logician critique
                              ├─ Empiricist critique
                              └─ Ethicist critique
```

| Phase | API Calls | Concurrency |
|-------|-----------|-------------|
| Thesis | 1 | Sequential |
| Council Antithesis | 3 | **Concurrent** (`asyncio.gather`) |
| Synthesis | 1 | Sequential |
| **Total** | **5** | 3 concurrent in antithesis |

**Key Code** (`council.py:85-116`):
```python
tasks = []
for member in members:
    task = self._generate_member_critique(member, query, thesis, search_context)
    tasks.append(task)
critiques = await asyncio.gather(*tasks, return_exceptions=True)  # CONCURRENT
```

The three council members (Logician, Empiricist, Ethicist) each make their own API call.

---

### Judge Mode: 4+ Calls (Iterative)

```
Query → [Standard 3 calls] → [API 4: Judge] → IF score < threshold → Retry entire cycle
```

| Phase | API Calls | Notes |
|-------|-----------|-------|
| T-A-S Cycle | 3 | Standard or Council mode |
| Judge Evaluation | 1 | Uses structured output |
| **Total (pass)** | **4** | Single iteration |
| **Total (fail + retry)** | **7+** | Re-runs entire T-A-S |

The judge can trigger up to `max_iterations` retry loops.

---

### Full Configuration: 6-10+ Calls

With `use_council=True` + `use_judge=True` + `max_iterations=2`:

| Scenario | Calls |
|----------|-------|
| Pass on first try | 6 (1 thesis + 3 council + 1 synthesis + 1 judge) |
| Fail once, pass retry | 12 (6 × 2 iterations) |
| Maximum (3 iterations) | 18 (6 × 3) |

---

## Where the Dialectical Logic Lives

### 1. System Prompts (`core/prompts.py`)

Each phase has a dedicated prompt template:

**THESIS_PROMPT** (~15 lines):
- "You are in the THESIS phase of Hegelian dialectical reasoning"
- Instructions: comprehensive answer, multiple perspectives, acknowledge uncertainty

**ANTITHESIS_PROMPT** (~20 lines):
- "Find contradictions, inconsistencies, or logical gaps"
- Required format: `CONTRADICTION: [...] / EVIDENCE: [...]`
- "Be adversarial but intellectually honest"

**SYNTHESIS_PROMPT** (~30 lines):
- "Generate a SYNTHESIS that TRANSCENDS both thesis and antithesis"
- Requirements: cannot just agree with either side, must offer novel perspective
- Optional format: `RESEARCH_PROPOSAL: [...] / TESTABLE_PREDICTION: [...]`

**MULTI_PERSPECTIVE_SYNTHESIS_PROMPT** (for council mode):
- Synthesizes with "ALL the critiques" from multiple perspectives

### 2. Council Personas (`council.py`)

Three hardcoded critics with specialized prompts:

```python
COUNCIL_MEMBERS = [
    CouncilMember(
        name="The Logician",
        expertise="Logical consistency and formal reasoning",
        prompt_modifier="Look for logical fallacies, contradictions, invalid inferences..."
    ),
    CouncilMember(
        name="The Empiricist",
        expertise="Evidence, facts, and empirical grounding",
        prompt_modifier="Look for factual errors, unsupported claims, missing evidence..."
    ),
    CouncilMember(
        name="The Ethicist",
        expertise="Ethical implications and societal impact",
        prompt_modifier="Look for potential harm, ethical blind spots, fairness issues..."
    ),
]
```

### 3. Judge Evaluation (`judge.py`)

Structured scoring on 4 dimensions (0-10 total):
- Thesis Quality (0-2 points)
- Antithesis Rigor (0-3 points)
- Synthesis Innovation (0-3 points)
- Critique Validity (0-2 points)

Uses `instructor` library for structured output when available.

### 4. Post-Processing (`core/parsing.py`)

Regex extraction of structured elements:
- `extract_contradictions()` - parses `CONTRADICTION: [...] EVIDENCE: [...]`
- `extract_research_proposals()` - parses `RESEARCH_PROPOSAL: [...] TESTABLE_PREDICTION: [...]`

---

## The Actual Mechanism

**Hegelion is prompt-engineered multi-agent orchestration.**

It is NOT:
- A single clever prompt asking the model to roleplay thesis/antithesis/synthesis
- Post-processing of a single response
- A fine-tuned model

It IS:
- Multiple separate API calls with specialized prompts per phase
- Orchestration code that chains outputs (thesis feeds into antithesis prompt)
- Optional concurrency (council mode parallelizes antithesis)
- Optional quality gating (judge mode with retry loops)

### Comparison to Other Approaches

| Approach | API Calls | Mechanism |
|----------|-----------|-----------|
| Raw completion | 1 | Single prompt |
| Chain-of-thought | 1 | Single prompt with "think step by step" |
| Self-consistency | N | Multiple completions, majority vote |
| **Hegelion Basic** | **3** | **Sequential T-A-S prompts** |
| **Hegelion Council** | **5** | **3 concurrent critics** |
| ReAct/Tool-use | Variable | Action-observation loops |
| Multi-agent debate | Variable | Multiple models arguing |

---

## Token/Cost Implications

### Baseline Estimation (Claude Sonnet)

Assumptions:
- Average query: 50 tokens
- Thesis response: ~500 tokens
- Antithesis response: ~600 tokens
- Synthesis response: ~700 tokens
- Each prompt template: ~200 tokens overhead

| Mode | Input Tokens | Output Tokens | Multiplier vs Raw |
|------|-------------|---------------|-------------------|
| Raw completion | ~50 | ~500 | 1× |
| **Basic Hegelion** | ~1,500 | ~1,800 | **~3-4×** |
| **Council Mode** | ~2,500 | ~3,200 | **~6×** |
| **Council + Judge** | ~3,000 | ~3,600 | **~7×** |

### Real Cost Multipliers

Based on actual usage patterns:
- **Basic mode**: 3-4× cost of raw completion
- **Council mode**: 5-7× cost of raw completion
- **Judge mode with retries**: Up to 15× in worst case

### Latency Implications

| Mode | Sequential Calls | Parallel Calls | Total Latency |
|------|-----------------|----------------|---------------|
| Basic | 3 | 0 | ~3× single call |
| Council | 2 | 3 (concurrent) | ~3× single call |
| Judge (pass) | 4 | 0 | ~4× single call |
| Judge (retry) | 7+ | 0 | ~7×+ single call |

Council mode's concurrency helps—3 critics run in parallel, so latency is ~3 calls, not 5.

---

## MCP Server Mode: Zero API Calls

The MCP server (`mcp/server.py`) is different—it returns **prompts, not completions**.

When integrated with Claude Desktop or Cursor:
- Hegelion provides the dialectical prompt structure
- The host LLM (Claude/GPT) executes the prompts
- No Hegelion backend API calls are made

This is useful for:
- Zero additional API cost
- Testing the prompt structure itself
- Integration with existing chat interfaces

---

## Data Flow Diagram

```
run_dialectic(query, use_council=True, use_judge=True)
│
├─ Check cache → hit? Return cached result
│
├─ [API 1] Generate Thesis
│   └─ prompt = THESIS_PROMPT.format(query=query)
│   └─ thesis = await backend.generate(prompt)
│
├─ [Optional] Web Search
│   └─ search_context = await search_for_context(query)
│
├─ [API 2-4] Generate Antithesis (Council Mode)
│   ├─ [Concurrent] Logician: critique thesis for logic errors
│   ├─ [Concurrent] Empiricist: critique thesis for factual errors
│   └─ [Concurrent] Ethicist: critique thesis for ethical issues
│   └─ antithesis = synthesize_council_input(critiques)
│
├─ [API 5] Generate Synthesis
│   └─ prompt = SYNTHESIS_PROMPT.format(thesis, antithesis, contradictions)
│   └─ synthesis = await backend.generate(prompt)
│
├─ [API 6] Judge Evaluation (optional)
│   └─ judge_result = await judge.evaluate_dialectic(...)
│   └─ IF score < threshold: goto [API 1] (retry)
│
├─ Parse structured elements
│   └─ contradictions = extract_contradictions(antithesis)
│   └─ proposals = extract_research_proposals(synthesis)
│
└─ Return HegelionResult
```

---

## Key Files Reference

| File | Lines | Purpose |
|------|-------|---------|
| `core/core.py` | 649 | Public API, orchestration |
| `core/engine.py` | 826 | T-A-S cycle execution |
| `core/prompts.py` | 128 | Prompt templates |
| `council.py` | 255 | Multi-critic antithesis |
| `judge.py` | 231 | Quality evaluation |
| `core/parsing.py` | 140+ | Extract structured elements |
| `core/backends.py` | 400+ | LLM provider abstractions |

---

## Conclusions

1. **Hegelion makes real multi-call orchestration**, not prompt tricks
2. **Minimum 3 API calls** per query (thesis + antithesis + synthesis)
3. **Council mode adds concurrency**, not just more prompts
4. **Judge mode adds quality gating** with potential retry loops
5. **Cost is 3-7× raw completion** depending on mode
6. **The dialectical structure is enforced by orchestration**, not model behavior

This is legitimate multi-agent architecture, comparable to debate/refinement frameworks in AI safety research, not marketing fluff around a single prompt.

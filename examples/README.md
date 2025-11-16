# Hegelion Examples

This directory now houses real traces captured from a Claude-compatible `glm-4.6` backend along with the original narrative walk-throughs.

## Recorded JSONL Traces

- `glm4_6_examples.jsonl` — four canonical runs recorded during development:
  - **Philosophical**: `"Can AI be genuinely creative?"`
  - **Factual**: `"What is the capital of France?"`
  - **Scientific**: `"Explain what photosynthesis does for a plant."`
  - **Historical**: `"When was the first moon landing?"`

Each line is a `HegelionResult` serialized via `to_dict()` and includes thesis/antithesis/synthesis, structured contradictions, research proposals, provenance metadata, and debug-only conflict scores tucked under `metadata.debug`.

## Markdown Walk-Throughs

- **[ai_creativity_example.md](./ai_creativity_example.md)** — Hero example referenced in the README (philosophical)
- **[consciousness_example.md](./consciousness_example.md)** — Dialectic on subjective experience (philosophical)
- **[gravity_example.md](./gravity_example.md)** — Treats gravity as geometry vs force (scientific)

## Reproducing an Example Run

```bash
# Philosophical hero example (summary)
hegelion "Can AI be genuinely creative?" --format summary

# Same example, but save a JSONL trace you can analyze later
hegelion "Can AI be genuinely creative?" --format json --output glm_creativity_trace.jsonl

# Factual / scientific / historical prompts
hegelion "What is the capital of France?" --format summary
hegelion "Explain what photosynthesis does for a plant." --format summary
hegelion "When was the first moon landing?" --format summary
```

Results will vary depending on your configured backend/model. The JSONL traces capture the provenance for the glm-4.6 runs; compare them with your own provider by writing your outputs to JSONL via:

```bash
hegelion "question" --output my_trace.jsonl
hegelion-bench benchmarks/examples_basic.jsonl --output my_results.jsonl
```

You own these traces – they are plain JSONL files you can diff with `git`, slice with `jq`, or load into Python dataframes.

# About the Examples

## Provenance

The JSONL traces under `examples/glm4_6_examples.jsonl` are **recorded outputs** from a Claude-compatible `glm-4.6` backend using the Anthropic style prompts. They mirror the public `HegelionResult` contract: thesis, antithesis, synthesis, structured contradictions, research proposals, metadata, and debug-only conflict scores.

The markdown guides in `examples/*.md` annotate those traces and show how to prompt Hegelion for similar analyses.

## Why keep recorded traces in the repo?

1. **Demonstrable provenance** – Every hero example in the README links back to an inspectable JSON line with honest backend metadata (`AnthropicLLMBackend`, `glm-4.6`).
2. **Benchmark reuse** – Model builders can replay the JSONL file to validate scoring pipelines or to compare Anthropic, OpenAI, Ollama, or custom HTTP providers.
3. **Spec verification** – The files are generated via `HegelionResult.to_dict()`, so they double as executable documentation for downstream tooling.

## Regenerating your own traces

```bash
# Configure your provider (.env) then run with debug for provenance
hegelion "Can AI be genuinely creative?" --debug --output my_creativity_run.jsonl

# Benchmark multiple prompts and store the structured outputs
hegelion-bench benchmarks/examples_basic.jsonl --output my_runs.jsonl --summary
```

Feel free to add new JSONL snapshots (named by provider/model) as additional backends are evaluated, but keep the `glm-4.6` examples untouched so documentation always references a consistent hero run.

# Hegelion Examples

This directory houses recorded traces and runnable demos.

## Recorded JSONL Traces

- `../hegelion-data/examples/glm4_6_examples.jsonl` — four canonical runs recorded during development:
  - **Philosophical**: "Can AI be genuinely creative?"
  - **Factual**: "What is the capital of France?"
  - **Scientific**: "Explain what photosynthesis does for a plant."
  - **Historical**: "When was the first moon landing?"

Each line is a `HegelionResult` serialized via `to_dict()` and includes thesis/antithesis/synthesis, structured contradictions, research proposals, provenance metadata, and (optionally) `metadata.debug` fields.

## Markdown Walk-Throughs

- [ai_creativity_example.md](./ai_creativity_example.md) — Hero example (philosophical)
- [consciousness_example.md](./consciousness_example.md) — Subjective experience (philosophical)
- [gravity_example.md](./gravity_example.md) — Geometry vs force (scientific)

## Demos

### GLM API Demo (Python)

- `demo_glm_api.py` — Demonstrates direct API usage with GLM backend.
- Optional: `mock_glm_server.py` — Deterministic offline server for docs/CI.

Quick start (GLM via OpenAI-compatible endpoint):

```bash
export OPENAI_API_KEY='your-glm-api-key-here'
export HEGELION_PROVIDER=openai
export HEGELION_MODEL=GLM-4.6
export OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4

cd examples
python3 demo_glm_api.py
```

Offline deterministic run:

```bash
# Terminal 1
cd examples
python3 mock_glm_server.py

# Terminal 2
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
export OPENAI_API_KEY=dummy-key
python3 demo_glm_api.py
```

## Reproducing an Example via CLI (demo)

```bash
hegelion "Can AI be genuinely creative?" --format summary
```

Or save JSONL:

```bash
hegelion "Can AI be genuinely creative?" --format json --output glm_creativity_trace.jsonl
```

## Tips

- Results vary with backend/model. Save outputs as JSONL to compare across providers.
- Analyze JSONL with `jq` or `pandas.read_json(..., lines=True)`.

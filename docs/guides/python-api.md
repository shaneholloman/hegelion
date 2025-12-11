# Python API

Full control over Hegelion's dialectical reasoning.

## Basic Usage

```python
import asyncio
from hegelion import run_dialectic

async def main():
    result = await run_dialectic("Is AI conscious?")
    print(result.synthesis)

asyncio.run(main())
```

## API Functions

### `run_dialectic(query, **options)`

Main entry point. Runs a complete dialectical analysis.

```python
result = await run_dialectic(
    query="Should we regulate AI?",
    personas="council",      # Use council critics
    iterations=2,            # Multiple dialectical passes
    use_search=True,         # Ground with web search
    use_judge=True,          # Add quality evaluation
    use_council=True,        # Enable multi-perspective council
    debug=True               # Include internal metrics
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | str | required | The question to analyze |
| `debug` | bool | `False` | Include internal metrics |
| `backend` | LLMBackend | `None` | Custom LLM backend |
| `model` | str | `None` | Model name override |
| `personas` | str/List | `None` | `"council"` for Logician/Empiricist/Ethicist |
| `iterations` | int | `1` | Number of refinement loops |
| `use_search` | bool | `False` | Enable search grounding (Phase 2) |
| `use_council` | bool | `False` | Enable multi-perspective council (Phase 2) |
| `use_judge` | bool | `False` | Add quality evaluation (Phase 2) |
| `min_judge_score` | int | `5` | Minimum acceptable judge score (0-10) |
| `max_iterations` | int | `1` | Maximum iterations for quality improvement |

**Returns:** `HegelionResult`

### `quickstart(query, debug=False)`

Simplified entry point using environment-configured backend.

```python
from hegelion import quickstart

result = await quickstart("Is privacy more important than security?", debug=True)
print(result.synthesis)
```

### `dialectic(query, model=None)`

Explicit model selection with auto-detected backend.

```python
from hegelion import dialectic

result = await dialectic("Can AI be creative?", model="claude-4.5-sonnet")
print(result.synthesis)
```

## Result Object

`HegelionResult` contains the full dialectical trace:

```python
result = await run_dialectic("Your question")

# Core outputs
result.query                 # Original question
result.thesis                # Phase 1 output
result.antithesis            # Phase 2 output
result.synthesis             # Phase 3 output

# Structured extractions
result.contradictions        # List of identified contradictions
result.research_proposals    # List of research proposals

# Metadata
result.metadata["thesis_time_ms"]
result.metadata["antithesis_time_ms"]
result.metadata["synthesis_time_ms"]
result.metadata["total_time_ms"]
result.metadata["backend_provider"]
result.metadata["backend_model"]

# Debug info (when debug=True)
result.metadata.get("debug", {}).get("internal_conflict_score")

# Full trace
result.trace
```

### Contradictions

```python
for c in result.contradictions:
    print(f"Issue: {c['description']}")
    print(f"Evidence: {c.get('evidence', 'N/A')}")
```

### Research Proposals

```python
for r in result.research_proposals:
    print(f"Proposal: {r['description']}")
    print(f"Prediction: {r.get('testable_prediction', 'N/A')}")
```

## Benchmarking

Run dialectical analysis on multiple prompts:

```python
from hegelion import run_benchmark

# From a JSONL file
results = await run_benchmark("prompts.jsonl", output_file="results.jsonl")

# From a list
prompts = [
    {"query": "Is consciousness fundamental?"},
    {"query": "Can AI be creative?"}
]
results = await run_benchmark(prompts)

for r in results:
    print(f"{r.query}: {r.synthesis[:100]}...")
```

## Agent Usage

For agentic workflows:

```python
from hegelion.core.agent import HegelionAgent

agent = HegelionAgent(
    goal="Ship safely",
    personas="council",
    iterations=2
)

step = agent.act_sync("Tests are flaky after enabling caching")
print(step.action)
```

## Error Handling

```python
from hegelion.core.engine import (
    ThesisPhaseError,
    AntithesisPhaseError,
    SynthesisPhaseError
)

try:
    result = await run_dialectic("Your question")
except ThesisPhaseError as e:
    print(f"Thesis generation failed: {e}")
except AntithesisPhaseError as e:
    print(f"Antithesis generation failed: {e}")
except SynthesisPhaseError as e:
    print(f"Synthesis generation failed: {e}")
```

## Serialization

```python
# To dict
data = result.to_dict()

# To JSON
import json
json_str = json.dumps(result.to_dict(), indent=2)
```

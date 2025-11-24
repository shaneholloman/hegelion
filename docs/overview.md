# Hegelion Overview

Hegelion wraps any LLM in a dialectical loop: **Thesis → Antithesis → Synthesis**. It ships as a model-agnostic MCP server, so tools like Claude Desktop, Cursor, and VS Code can use it with zero API keys.

## Why it matters
- **Eval / safety:** Structured adversarial traces you can diff and score.
- **Agent devs / IDEs:** Drop-in MCP server that upgrades reasoning without changing your backend.
- **Researchers:** Reusable prompts + datasets + training pipeline for dialectical thinking.

## How it works
- Tools return **prompts**, not API calls. Your current LLM does the reasoning.
- Feature toggles: `use_search`, `use_council` (Logician/Empiricist/Ethicist), `use_judge`, `response_style` (`sections` | `synthesis_only` | `json`).
- Workflow mode returns structured steps; single-shot mode returns one comprehensive prompt.

## Example: step-by-step workflow
```python
workflow = await dialectical_workflow(
    query="Should we implement universal basic income?",
    use_council=True,
    use_judge=True,
    format="workflow",
    response_style="json",
)
```

## Example: single-shot
```python
prompt = await dialectical_single_shot(
    query="Is consciousness fundamental or emergent?",
    use_search=True,
    use_council=True,
    response_style="sections",
)
```
[View the full output of this query in our Showcase →](../docs/showcase.md)

## Structural bias: why it produces different answers
- **Forced conflict:** Antithesis step attacks the thesis.
- **Hard constraints:** Council (logic/evidence/ethics) pushes toward grounded arguments.
- **Creativity via destruction:** Synthesis must resolve contradictions, producing novel third paths.

## Training and data
- Dialectical traces collected for training a small open model (DeepSeek-R1-Distill-Qwen-1.5B).
- SCU (Shannon Control Unit) for adaptive regularization on training runs.
- See `README_TRAINING.md` and `hegelion-data/README.md` for details.

## Where to go next
- Quickstart for humans: `docs/QUICKSTART.md`
- Quickstart for AIs/agents: `AI_README.md`
- MCP reference and common issues: `docs/MCP.md`
- In-process smoke test: `python examples/mcp/inprocess_check.py`

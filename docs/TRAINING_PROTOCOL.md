# Hegelion Training Protocol

This guide outlines how to use Hegelion to generate synthetic training data for fine-tuning models. By capturing the "Thesis → Antithesis → Synthesis" loop, you can create high-quality preference datasets (DPO) or instruction tuning datasets (SFT) that encode dialectical reasoning.

## Overview

The process consists of three phases:
1.  **Collection:** Running agents to generate raw reasoning traces.
2.  **Curation:** Converting traces into standard training formats.
3.  **Training:** Using the data to fine-tune models.

---

## Phase 1: Data Collection

Use the `hegelion-agent` CLI with the `--log-file` flag to capture reasoning traces. Each run appends a JSON object to the specified file.

### Example: generating coding data
```bash
# Run an agent on a task and log the result
hegelion-agent "Fix the memory leak in the image processor" \
  --coding \
  --iterations 2 \
  --log-file collected_data/coding_traces.jsonl
```

### Scaling Collection
You can wrap the CLI in a shell script or Python loop to run against a benchmark file:

```bash
#!/bin/bash
while read -r prompt; do
  hegelion-agent "$prompt" --log-file collected_data/batch_1.jsonl
done < my_prompts.txt
```

---

## Phase 2: Dataset Curation

Once you have raw logs, use the `hegelion-dataset` tool to convert them into training-ready formats.

### Direct Preference Optimization (DPO)
DPO datasets consist of `(prompt, chosen, rejected)` triples. Hegelion treats the **Synthesis** as "chosen" and the **Thesis** (or Antithesis) as "rejected," teaching the model to prefer the refined, conflict-resolved answer.

```bash
# Default conversion (Synthesis > Thesis)
hegelion-dataset collected_data/coding_traces.jsonl train_dpo.jsonl

# Prefer Synthesis over Antithesis
hegelion-dataset collected_data/coding_traces.jsonl train_dpo_anti.jsonl --rejected antithesis
```

### Instruction Tuning (SFT)
Standard instruction datasets consist of `(instruction, output)` pairs. This fine-tunes the model to produce the Synthesis directly.

```bash
hegelion-dataset collected_data/coding_traces.jsonl train_sft.jsonl --format instruction
```

---

## Phase 3: Training (Theory)

Hegelion datasets are compatible with standard fine-tuning libraries like Hugging Face `trl`, `axolotl`, or `unsloth`.

### Fine-tuning with TRL (DPO)
```python
from trl import DPOTrainer
from datasets import load_dataset

# Load your Hegelion dataset
dataset = load_dataset("json", data_files="train_dpo.jsonl", split="train")

trainer = DPOTrainer(
    model=model,
    train_dataset=dataset,
    tokenizer=tokenizer,
    # ... other args
)
trainer.train()
```

### Expected Outcome
Models trained on this data should exhibit:
1.  **Self-Correction:** Reduced hallucination by internalizing the "Antithesis" critique pattern.
2.  **Nuance:** Preference for synthesized answers that resolve contradictions rather than ignoring them.


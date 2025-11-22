# The Hegelion Agent Method

This document explains how to train an AI agent to "Think Dialectically" using the Hegelion Method.

## The Concept

Most AI models answer questions linearly: they retrieve information and predict the most likely next token.
**The Hegelion Agent** answers structurally: it forces a conflict (Thesis vs. Antithesis) and generates a novel resolution (Synthesis).

We achieve this by **Knowledge Distillation**:
1.  **Teacher**: A smart model (Moonshot Kimi / Claude) is forced to output full dialectical traces.
2.  **Student**: A smaller model (OLMo 7B / Llama 3 8B) is fine-tuned on these traces.
3.  **Result**: The student internalizes the *habit* of challenging its own assumptions before answering.

## Step 1: Generate the "Thought" Data

We use the `hegelion.training.generator` script to create a lesson plan.

**Using Kimi CLI (Recommended for personal use):**
If you have `kimi` installed and logged in via `kimi /setup`:

```bash
# No API key needed if you are logged into the CLI
python -m hegelion.training.generator \
  --dataset HuggingFaceH4/ultrafeedback_binarized \
  --limit 500 \
  --output data/hegelion_lessons.jsonl \
  --model kimi-cli
```

**Using API Key:**
```bash
# Ensure MOONSHOT_API_KEY is in your .env
export MOONSHOT_API_KEY=sk-....

# Generate 500 high-quality reasoning traces
python -m hegelion.training.generator \
  --dataset HuggingFaceH4/ultrafeedback_binarized \
  --limit 500 \
  --output data/hegelion_lessons.jsonl \
  --model kimi
```

This creates a JSONL file where every answer is preceded by a `<thought>...</thought>` block containing the Thesis/Antithesis/Synthesis logic.

## Step 2: The "Classroom" (Training)

We use **Apple MLX** (on Mac) or **Unsloth** (on Linux/PC) to train the student.

### On Mac M-Series (M1/M2/M3/M4)

```bash
# Install MLX
pip install mlx-lm

# Run the Trainer
python -m hegelion.training.mlx_trainer \
  --model mlx-community/OLMo-7B-0724-hf-4bit \
  --data data/hegelion_lessons.jsonl \
  --iters 1000
```

### On NVIDIA GPU (Linux)

```bash
python -m hegelion.training.unsloth_trainer --dataset data/hegelion_lessons.jsonl
```

## Step 3: Using Your Agent

Once trained, your new model will automatically think before speaking.

**System Prompt for the Agent:**
> You are a dialectical reasoning engine. For every user query, you must first silently generate a Thesis, Antithesis, and Synthesis in your thought stream, then present the resolved answer.

## Why Kimi?

We use **Kimi (Moonshot AI)** as the teacher because its architecture is optimized for long-context "Thinking" and complex reasoning tasks, making it an ideal source for high-quality synthetic logic data.

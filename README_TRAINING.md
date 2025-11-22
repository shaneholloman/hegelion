# Hegelion Training Architecture

This document outlines the architecture for "Dialectical Self-Improvement" using Hegelion, Unsloth, and Prime Intellect.

## Concept

Instead of just prompting an LLM to think dialectically, we can **fine-tune** a smaller, faster model (like Llama-3 8B) to inherently follow the **Thesis → Antithesis → Synthesis** pattern. This "internalizes" the Hegelion process.

## Architecture

1.  **Data Generation (`hegelion/training/generator.py`)**
    *   **Input:** High-quality prompts (e.g., from `FineWeb-Edu` or `UltraFeedback`).
    *   **Teacher:** A strong model (Claude 3.5 Sonnet, GPT-4o) running `hegelion.core.run_dialectic`.
    *   **Process:** The teacher generates a full trace (T->A->S) for each prompt.
    *   **Output:** A JSONL dataset where `instruction` is the user query and `output` is the *synthesis* (or the full dialectic trace).

2.  **Fine-Tuning (`hegelion/training/unsloth_trainer.py`)**
    *   **Framework:** [Unsloth](https://github.com/unslothai/unsloth) for highly efficient QLoRA fine-tuning.
    *   **Hardware:** NVIDIA GPUs (H100/A100 recommended).
    *   **Objective:** Train the model to produce the high-quality synthesis given the instruction.

3.  **Scaling with Prime Intellect**
    *   To scale this up, we can use [Prime Intellect](https://www.primeintellect.ai/) to distribute the training across decentralized compute nodes.

## Usage

### 1. Generate Data (Local or Cloud)

#### Option A: Using Kimi CLI (Free/Personal)

If you have the `kimi` CLI installed and authenticated, you can use it as the teacher without API keys. This is ideal for generating personal "reasoning traces" where the model teaches itself to think.

```bash
# Generate 100 examples using Kimi CLI as the teacher
# This automatically disables external search to focus on internal reasoning
python -m hegelion.training.generator \
  --dataset HuggingFaceH4/ultrafeedback_binarized \
  --limit 100 \
  --output hegelion_kimi_training_data.jsonl \
  --model kimi-cli
```

**Note on Data Format:**
The generator produces a JSONL file where each entry has:
- `instruction`: The user query.
- `output`: The full response, starting with `<thought>...trace...</thought>` followed by the final answer.
- `hegelion_trace`: A structured object containing `thesis`, `antithesis`, `synthesis` fields (parsed from the output).

#### Option B: Using API Keys (Scalable)

```bash
# Generate 100 examples using a teacher model via API
python -m hegelion.training.generator \
  --dataset HuggingFaceH4/ultrafeedback_binarized \
  --limit 100 \
  --output dialectic_data.jsonl \
  --model kimi
```

### 2. Train (Linux/GPU)

On a machine with NVIDIA GPU (e.g., Lambda Labs, Google Colab):

```bash
# Install dependencies
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps "xformers<0.0.27" "trl<0.9.0" peft accelerate bitsandbytes

# Run training
python -m hegelion.training.unsloth_trainer --dataset dialectic_data.jsonl
```

### 3. Train (Mac/Apple Silicon) - NEW

We support efficient training on Mac using **MLX** and the **Shannon Control Unit (SCU)** for adaptive regularization.

**Prerequisites:**
```bash
pip install mlx-lm ai2-olmo
```

**Running the SCU Trainer:**
This trainer combines Hegelion's dialectical data with the SCU optimizer to produce "VibeThinker" models.

```bash
# 1. Convert data to SCU format
python scripts/convert_for_scu.py hegelion_kimi_training_data.jsonl hegelion_scu_ready.jsonl

# 2. Run Training (Prototype)
python -m hegelion.training.mlx_scu_trainer \
  --model mlx-community/OLMo-7B-0724-hf-4bit \
  --data hegelion_scu_ready.jsonl \
  --adapter_path adapters/hegelion_mlx_scu
```

> **Note:** The `mlx_scu_trainer.py` is currently in experimental state. It implements the SCU control loop logic (DataBPT vs ParamBPT) on top of MLX.

### 4. Deploy with Prime Intellect

(Conceptual)

```bash
prime-intellect deploy \
  --image unsloth/llama-3-8b \
  --script hegelion/training/unsloth_trainer.py \
  --data ./dialectic_data.jsonl \
  --gpus 8
```

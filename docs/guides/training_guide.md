# Hegelion Training Guide

Complete guide for training dialectical reasoning models using Hegelion's data generation and fine-tuning pipeline.

## 📋 Quick Start

Get from zero to trained model in 3 steps:

```bash
# Step 1: Generate 500 training samples (6-8 hours, runs in background)
python -m hegelion.training.generator \
  --dataset HuggingFaceH4/ultrafeedback_binarized \
  --output artifacts/data/hegelion_kimi_training_data.jsonl \
  --limit 500 --model kimi-cli --split train_prefs \
  > generator.log 2>&1 &

# Step 2: Convert to [SCU](https://github.com/Shannon-Labs/shannon-control-unit) training format
python scripts/convert_for_scu.py \
  artifacts/data/hegelion_kimi_training_data.jsonl \
  artifacts/data/hegelion_scu_ready.jsonl

# Step 3: Train with DeepSeek 1.5B (2-3 hours on M2/M3)
uv run python -m hegelion.training.mlx_scu_trainer \
  --model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
  --data artifacts/data/hegelion_scu_ready.jsonl \
  --adapter_path artifacts/adapters/hegelion_1.5b_v1 \
  --batch_size 4 --iters 500
```

## 🔧 Prerequisites

### Python Environment
- Python 3.10 or higher
- uv package manager (recommended)

### Training Framework
For Apple Silicon (Mac M1/M2/M3/M4):
```bash
pip install mlx-lm ai2-olmo datasets
```

For NVIDIA GPUs:
```bash
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps "xformers<0.0.27" "trl<0.9.0" peft accelerate bitsandbytes
```

### Kimi CLI (for data generation)
```bash
pip install kimi-cli  # No API key needed
```

## 📊 Data Generation

### Single Generator (Standard)
Generates 500 samples sequentially:

```bash
python -m hegelion.training.generator \
  --dataset HuggingFaceH4/ultrafeedback_binarized \
  --output artifacts/data/hegelion_kimi_training_data.jsonl \
  --limit 500 \
  --model kimi-cli \
  --split train_prefs \
  > generator_ultrafeedback.log 2>&1 &
```

**Monitor progress:**
```bash
# Check sample count every 30 seconds
watch -n 30 'wc -l artifacts/data/hegelion_kimi_training_data.jsonl'

# View current activity
tail -f generator_ultrafeedback.log

# See recent samples
tail -3 artifacts/data/hegelion_kimi_training_data.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        data = json.loads(line)
        print(f'✓ {data[\"instruction\"][:60]}...')
    except:
        pass
"
```

**Expected output format:**
```json
{
  "instruction": "original prompt from dataset",
  "input": "",
  "output": "<thought>\n**THESIS**: ...\n**ANTITHESIS**: ...\n**SYNTHESIS**: ...\n</thought>\n[Final answer]",
  "system": "You are a dialectical reasoning engine.",
  "hegelion_trace": {...}
}
```

### Parallel Generation (2x Speed)
Run two generators with different random seeds:

```bash
# Generator 1 (seed 42, default)
python -m hegelion.training.generator \
  --dataset HuggingFaceH4/ultrafeedback_binarized \
  --output artifacts/data/hegelion_kimi_training_data.jsonl \
  --limit 500 --model kimi-cli \
  --split train_prefs \
  > generator1.log 2>&1 &

# Generator 2 (seed 123, different shuffle)
python -m hegelion.training.generator \
  --dataset HuggingFaceH4/ultrafeedback_binarized \
  --output artifacts/data/hegelion_kimi_training_data.jsonl \
  --limit 500 --model kimi-cli \
  --split train_prefs \
  --seed 123 \
  > generator2.log 2>&1 &
```

Both append to the **same file** (auto-resume prevents duplicates).

**Timeline:**
- Single generator: ~6-8 hours for 500 samples
- Parallel (2x): ~3-4 hours for 500 samples

### Custom Prompts
Use your own questions instead of UltraFeedback:

```bash
# Create prompts file (one per line)
cat > my_prompts.txt << 'EOF'
How do I design a fault-tolerant microservices architecture?
What are the tradeoffs between SQL and NoSQL for analytics?
Should we use GraphQL or REST for our public API?

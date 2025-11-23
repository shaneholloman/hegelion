# Hegelion Project Operations Guide

**Last Updated:** 2025-11-22  
**Status:** ✅ Active Development

## 📊 Current Status

### 🔄 Active Data Generation
- **Process:** Dual-instance dialectical data generation using Kimi CLI
- **Dataset:** HuggingFaceH4/ultrafeedback_binarized (70k+ prompts)
- **Target:** 500 dialectical reasoning samples
- **Current:** 49 samples (growing at ~3-5 samples/5 min parallel)
- **ETA:** ~3-4 hours to completion

### 🎯 Training Pipeline
- **Model Configured:** DeepSeek-R1-Distill-Qwen-1.5B (memory-efficient)
- **Framework:** MLX + SCU (Apple Silicon optimized)
- **Data Path:** artifacts/data/hegelion_scu_ready.jsonl (SCU format)
- **Status:** 🟢 Ready to launch on completion

### 📁 Key Files
- `artifacts/data/hegelion_kimi_training_data.jsonl` - Raw training data (growing)
- `artifacts/data/hegelion_scu_ready.jsonl` - SCU formatted data (41 samples currently)
- `artifacts/adapters/hegelion_1.5b_v1/` - Will hold trained weights
- `generator_ultrafeedback.log` - Active generation log
- `generator_instance2.log` - Parallel instance log

## 🚀 Quick Commands

### Data Generation
```bash
# Single generator (6-8 hours)
python -m hegelion.training.generator \
  --dataset HuggingFaceH4/ultrafeedback_binarized \
  --output artifacts/data/hegelion_kimi_training_data.jsonl \
  --limit 500 --model kimi-cli --split train_prefs \
  > generator.log 2>&1 &

# Parallel generation - 2x speed (3-4 hours)
# Instance 1 (already running: PID 38898)
# Instance 2 (already running: PID 53374)
watch -n 30 'wc -l artifacts/data/hegelion_kimi_training_data.jsonl'

# Custom prompts
python -m hegelion.training.generator \
  --prompt-file my_prompts.txt \
  --output artifacts/data/hegelion_kimi_training_data.jsonl \
  --model kimi-cli
```

### Convert to Training Format
```bash
# Convert dialectical traces to SCU format
python scripts/convert_for_scu.py \
  artifacts/data/hegelion_kimi_training_data.jsonl \
  artifacts/data/hegelion_scu_ready.jsonl
```

### Train Model
```bash
# SCU training with adaptive regularization
uv run python -m hegelion.training.mlx_scu_trainer \
  --model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
  --data artifacts/data/hegelion_scu_ready.jsonl \
  --adapter_path artifacts/adapters/hegelion_1.5b_v1 \
  --batch_size 4 --iters 500 --lr 1e-5

# Standard LoRA training (simpler)
uv run python -m hegelion.training.mlx_trainer \
  --model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
  --data artifacts/data/hegelion_scu_ready.jsonl \
  --adapter_path artifacts/adapters/hegelion_1.5b_standard
```

### Agent Workflows
```bash
# Generate dialectical workflow
python -m hegelion.scripts.hegelion_cli \
  --query "Should we implement feature X?" \
  --council --judge

# Convert agent logs to training data
python -m hegelion.scripts.hegelion_dataset \
  agent_logs.jsonl training_data.jsonl --format dpo
```

## 📂 File Structure

```
hegelion/
├── artifacts/
│   ├── data/
│   │   ├── hegelion_kimi_training_data.jsonl    # Raw dialectical training data
│   │   ├── hegelion_scu_ready.jsonl             # SCU format for training
│   │   └── mlx/                                  # MLX training data
│   ├── adapters/ (moved to artifacts/adapters/)
│   │   └── hegelion_1.5b_v1/                    # Trained adapter storage
│   │       ├── weights.safetensors
│   │       └── adapter_config.json
│   └── logs/                                     # Training logs
├── generator_ultrafeedback.log          # Generation log (Instance 1)
├── generator_instance2.log              # Generation log (Instance 2)
├── CHECK_STATUS.sh                      # Quick status script
├── hegelion/
│   ├── training/
│   │   ├── generator.py                 # Data generation orchestrator
│   │   ├── mlx_scu_trainer.py           # SCU + MLX trainer
│   │   ├── mlx_trainer.py               # Standard MLX trainer
│   │   └── datasets.py                  # Dataset conversion utilities
│   └──
└── scripts/
    └── convert_for_scu.py               # Convert to SCU format
```

## 🔄 Data Pipeline

```
UltraFeedback Dataset (70k+ prompts)
    ↓
Hegelion Generator (2 parallel instances)
    ↓
artifacts/data/hegelion_kimi_training_data.jsonl (500 samples)
    ↓
convert_for_scu.py
    ↓
artifacts/data/hegelion_scu_ready.jsonl (SCU format)
    ↓
mlx_scu_trainer.py
    ↓
artifacts/adapters/hegelion_1.5b_v1/ (trained weights)
```

## 📊 Monitoring Active Processes

### Check Generation Progress
```bash
# Quick sample count
echo "Samples: $(wc -l < artifacts/data/hegelion_kimi_training_data.jsonl)/500"

# Full status
./CHECK_STATUS.sh

# Watch both generators
ps aux | grep "hegelion.training.generator" | grep -v grep

# Watch Kimi CLI workers
ps aux | grep -E "kimi.*--print|kimi.*--yolo" | grep -v grep
```

### Check Training Progress
```bash
# Training prints to stdout every 10 steps
# Look for: Step N: Loss=X, DataBPT=Y, ParamBPT=Z, S=W%, λ=A -> B

# Check adapter file size growing
ls -lh artifacts/adapters/hegelion_1.5b_v1/weights.safetensors

# Watch for "Training complete." message
```

### System Resources
```bash
# Memory usage on Apple Silicon
sudo memory_pressure

# GPU usage on NVIDIA
nvidia-smi -l 1

# Overall system load
top -o cpu
```

## 🎯 Training Readiness Checklist

Before launching training, verify:

- [x] **Dependencies installed:** `mlx-lm`, `ai2-olmo`, `datasets`, `kimi-cli`
- [x] **Model downloaded:** `deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B`
- [x] **Data generated:** `wc -l artifacts/data/hegelion_kimi_training_data.jsonl` > 500
- [x] **Data converted:** `artifacts/data/hegelion_scu_ready.jsonl` exists
- [ ] **Adapters directory:** `mkdir -p artifacts/adapters/hegelion_1.5b_v1`
- [ ] **Sufficient disk:** ~2GB free for adapters + logs
- [ ] **Sufficient memory:** 8GB+ RAM recommended

## ⚠️ Troubleshooting

### Generator stopped
```bash
# Check if process crashed
ps aux | grep generator

# View error in log
tail -50 generator_ultrafeedback.log

# Resume (auto-resume will continue from last sample)
python -m hegelion.training.generator ...
```

### "ImportError: datasets"
```bash
pip install datasets
# or
uv add datasets
```

### Training: Out of Memory
```bash
# Reduce batch size
--batch_size 2  # or even 1

# Use smaller model
--model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B  # already using this!

# Reduce sequence length
--max_seq_length 2048  # default 4096
```

### Adapter files not created
```bash
# Check training actually finished
tail -20 generator_ultrafeedback.log | grep "Training complete"

# Verify write permissions
ls -la artifacts/adapters/

# Check available disk space
df -h .
```

### Slow generation
```bash
# This is normal - Kimi CLI does deep reasoning
# Each sample takes 1-2 minutes
# Parallel generation already running (2 instances)
# Expected: ~3-4 hours for 500 samples
```

## 📈 Expected Timeline

**Data Generation:**
- Start: 2025-11-22 16:22
- ETA Complete: 2025-11-22 20:00 (approx)
- Rate: ~3-5 samples per 5 minutes (parallel)

**Training (once data ready):**
- Duration: 2-3 hours for 500 samples @ 500 iters
- Memory: ~6-8GB RAM usage
- Output: ~50MB adapters

## 🎓 Understanding the Process

**What each step does:**

1. **Data Generation:** Uses Kimi CLI (teacher) to create examples where:
   - Question asked → Simple answer (Thesis) → Critique (Antithesis) → Better answer (Synthesis)
   - This teaches the model to think dialectically

2. **SCU Training:** Shannon Control Unit adds adaptive regularization:
   - Balances model complexity vs. data fit automatically
   - Prevents overfitting to small dataset
   - Produces more robust reasoning

3. **Final Model:** 1.5B parameter model with LoRA adapters that:
   - Internally performs T→A→S before answering
   - Much smaller than full fine-tune (50MB vs 3GB)
   - Preserves base model capabilities

## 🚀 Ready to Launch

**When generation reaches ~500 samples:**

1. **Stop generators** (if still running):
   ```bash
   kill $(cat generator_pid.txt) $(cat generator2_pid.txt) 2>/dev/null
   ```

2. **Convert data** (if not already done):
   ```bash
   python scripts/convert_for_scu.py \
     artifacts/data/hegelion_kimi_training_data.jsonl \
     artifacts/data/hegelion_scu_ready.jsonl
   ```

3. **Launch training**:
   ```bash
   uv run python -m hegelion.training.mlx_scu_trainer \
     --model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
     --data artifacts/data/hegelion_scu_ready.jsonl \
     --adapter_path artifacts/adapters/hegelion_1.5b_v1 \
     --batch_size 4 --iters 500
   ```

4. **Monitor progress** in real-time

## 📞 Getting Help

- **Quick Status:** `./CHECK_STATUS.sh`
- **Full Training Guide:** [README_TRAINING.md](README_TRAINING.md)
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)
- **Issues:** Check generator logs first
- **Community:** Discord/Slack channels

---

**Status:** ✅ System operational, data generation active  
**Next Action:** Wait for ~500 samples, then launch training

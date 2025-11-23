# Quick Start: Generate 500 Hegelian Dialectical Samples

## 🎯 Goal
Create 500 high-quality training samples with full Hegelian dialectical reasoning:
- **THESIS** → **ANTITHESIS** → **SYNTHESIS**
- Contradictions with evidence
- Testable predictions and research proposals

## ✅ What's Already Done

1. **500+ Diverse Prompts** (`hegelion_prompts_500.txt`)
   - 30+ domains (philosophy, AI, ethics, science, etc.)
   - Designed for genuine dialectical reasoning

2. **Generation Scripts**
   - `scripts/generate_with_kimi.py` - Direct API generation
   - `scripts/generate_500_samples.py` - Full Hegelion engine

3. **Quality Tools**
   - `scripts/validate_hegelian_dataset.py` - Validate dialectical structure
   - `scripts/clean_dataset.py` - Deduplicate and filter

4. **Example Data**
   - `examples/glm4_6_examples.jsonl` - 4 high-quality examples

## 🚀 Three Ways to Generate

### Option 1: Use Standard Moonshot Kimi API (Recommended)

The "Kimi For Coding" API is IDE-specific. Use the standard Moonshot API instead:

```bash
# Get API key from: https://platform.moonshot.cn/
export OPENAI_API_KEY="sk-..." # Your Moonshot API key
export OPENAI_BASE_URL="https://api.moonshot.cn/v1"

# Generate 500 samples
python scripts/generate_with_kimi.py \
  --prompts hegelion_prompts_500.txt \
  --output data/hegelion_500.jsonl \
  --limit 500 \
  --base-url "https://api.moonshot.cn/v1" \
  --model "moonshot-v1-128k"
```

### Option 2: Use Anthropic Claude (Best Quality)

```bash
# Get API key from: https://console.anthropic.com/
export ANTHROPIC_API_KEY="sk-ant-..."

# Install anthropic package
pip install anthropic

# Modify script to use Anthropic (or use Hegelion engine)
python scripts/generate_500_samples.py \
  --prompts hegelion_prompts_500.txt \
  --output data/hegelion_500.jsonl \
  --provider anthropic \
  --model claude-sonnet-4
```

### Option 3: Use OpenAI GPT-4

```bash
export OPENAI_API_KEY="sk-..."

python scripts/generate_with_kimi.py \
  --prompts hegelion_prompts_500.txt \
  --output data/hegelion_500.jsonl \
  --limit 500 \
  --base-url "https://api.openai.com/v1" \
  --model "gpt-4"
```

## 📝 Step-by-Step Workflow

### 1. Test First (10 samples)

```bash
# Test with 10 samples to verify quality
python scripts/generate_with_kimi.py \
  --prompts hegelion_prompts_500.txt \
  --output data/test_10.jsonl \
  --limit 10

# Validate quality
python scripts/validate_hegelian_dataset.py data/test_10.jsonl

# Check output manually
head -1 data/test_10.jsonl | jq '.'
```

### 2. Generate Full Dataset

```bash
# Generate all 500 (resumes automatically if interrupted)
python scripts/generate_with_kimi.py \
  --prompts hegelion_prompts_500.txt \
  --output data/hegelion_500.jsonl \
  --limit 500 \
  --resume
```

### 3. Clean and Validate

```bash
# Remove duplicates and low-quality samples
python scripts/clean_dataset.py \
  data/hegelion_500.jsonl \
  --output data/hegelion_500_clean.jsonl

# Final validation
python scripts/validate_hegelian_dataset.py \
  data/hegelion_500_clean.jsonl
```

### 4. Use for Training

```bash
# The clean dataset is ready for fine-tuning!
# Format: JSONL with thesis/antithesis/synthesis structure

# Convert to training format if needed
# (Your existing convert scripts can handle this)
```

## 🔧 Troubleshooting

### API Access Issues

If you get 403 errors:
- ✅ **Kimi For Coding API** is IDE-only (doesn't work in scripts)
- ✅ **Use Standard Moonshot API** instead: `https://api.moonshot.cn/v1`
- ✅ **Or use Anthropic/OpenAI** for highest quality

### SSL Certificate Errors

```bash
# Add SSL verify=False for testing (not recommended for production)
# Or ensure your system certificates are up to date
```

### Rate Limiting

```bash
# The script includes 1-second delays between requests
# Adjust in generate_with_kimi.py: time.sleep(1) -> time.sleep(2)
```

### Low Quality Outputs

- Use better models: Claude Sonnet 4 or GPT-4
- Increase max_tokens: `--max-tokens 6000`
- Manually review and filter after generation

## 📊 Expected Results

After generating and cleaning:

- ✅ **~450-500 unique samples** (after deduplication)
- ✅ **95%+ quality rate** (proper dialectical structure)
- ✅ **4000+ chars average** per dialectical trace
- ✅ **2+ contradictions** per sample
- ✅ **1+ research proposal** per sample

## 💰 Cost Estimates

Based on 500 samples × 4500 tokens average:

| Provider | Model | Cost |
|----------|-------|------|
| Moonshot | moonshot-v1-128k | ~$5-10 |
| OpenAI | GPT-4 | ~$15-20 |
| Anthropic | Claude Sonnet 4 | ~$30-40 |
| OpenAI | GPT-3.5-Turbo | ~$2-5 |

## 🎓 Next Steps

After generating your dataset:

1. **Train Your Model**
   ```bash
   cd hegelion/training
   python mlx_trainer.py \
     --data ../../data/hegelion_500_clean.jsonl \
     --model allenai/OLMo-7B-0724-hf
   ```

2. **Benchmark Results**
   ```bash
   python benchmark.py \
     --model models/olmo-7b-hegelian \
     --prompts ../../benchmarks/examples_basic.jsonl
   ```

3. **Iterate**
   - Review failure cases
   - Add more prompts in underperforming domains
   - Regenerate with better prompts

## 📚 File Structure

```
Hegelion/
├── hegelion_prompts_500.txt          # 500+ dialectical prompts
├── scripts/
│   ├── generate_with_kimi.py         # Direct API generation
│   ├── validate_hegelian_dataset.py  # Quality checking
│   └── clean_dataset.py              # Deduplication
├── examples/
│   └── glm4_6_examples.jsonl         # 4 reference examples
└── data/
    ├── hegelion_500.jsonl            # Generated raw data
    └── hegelion_500_clean.jsonl      # Cleaned final dataset
```

## 🆘 Need Help?

1. Check existing examples: `cat examples/glm4_6_examples.jsonl | jq '.'`
2. Review validation output for specific issues
3. Manually inspect random samples for quality
4. Adjust prompts in `hegelion_prompts_500.txt` if needed

## ✨ Success Criteria

Your dataset is ready when:
- [x] 500+ samples generated
- [x] 95%+ pass validation (dialectical structure)
- [x] < 5% duplicates
- [x] 50+ unique topic domains
- [x] Average 4000+ chars per trace
- [x] Each sample has contradictions + research proposals

---

**Ready to start?** Run the test generation with 10 samples first!

```bash
python scripts/generate_with_kimi.py --limit 10 --output data/test_10.jsonl
```

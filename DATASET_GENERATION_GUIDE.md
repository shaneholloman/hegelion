# Hegelian Training Dataset Generation Guide

This guide explains how to generate 500+ high-quality Hegelian dialectical training samples for fine-tuning models to think using the THESIS → ANTITHESIS → SYNTHESIS framework.

## Overview

The Hegelian method produces training data where models learn to:
1. **THESIS**: Present a strong initial position
2. **ANTITHESIS**: Critically examine contradictions with evidence
3. **SYNTHESIS**: Transcend the conflict with novel predictions

## Quick Start

### 1. Set Up Environment

```bash
# Install dependencies
pip install -e .

# Set your API key (choose one)
export ANTHROPIC_API_KEY='your-key-here'
# OR
export OPENAI_API_KEY='your-key-here'
# OR
export MOONSHOT_API_KEY='your-key-here'
```

### 2. Generate 500 Samples

```bash
# Generate all 500 samples
python scripts/generate_500_samples.py \
  --prompts hegelion_prompts_500.txt \
  --output data/hegelion_500_samples.jsonl \
  --limit 500

# Or start with a small test (10 samples)
python scripts/generate_500_samples.py \
  --prompts hegelion_prompts_500.txt \
  --output data/hegelion_test_10.jsonl \
  --limit 10
```

### 3. Validate Quality

```bash
python scripts/validate_hegelian_dataset.py data/hegelion_500_samples.jsonl
```

### 4. Clean & Deduplicate

```bash
python scripts/clean_dataset.py data/hegelion_500_samples.jsonl \
  --output data/hegelion_500_clean.jsonl
```

## Detailed Instructions

### Prompt Library

The `hegelion_prompts_500.txt` file contains 500+ diverse prompts across 30+ domains:

- Philosophy & Metaphysics
- Ethics & Moral Philosophy
- Political Philosophy
- Science & Epistemology
- Technology & Society
- Artificial Intelligence
- Economics & Markets
- Education & Learning
- And 22 more domains...

Each prompt is designed to trigger genuine dialectical reasoning with natural thesis/antithesis tensions.

### Generation Options

```bash
# Resume from interruption
python scripts/generate_500_samples.py \
  --prompts hegelion_prompts_500.txt \
  --output data/hegelion_500_samples.jsonl \
  --resume

# Use specific provider/model
python scripts/generate_500_samples.py \
  --prompts hegelion_prompts_500.txt \
  --output data/hegelion_500_samples.jsonl \
  --provider anthropic \
  --model claude-sonnet-4

# Batch processing (faster but more expensive)
python scripts/generate_500_samples.py \
  --prompts hegelion_prompts_500.txt \
  --output data/hegelion_500_samples.jsonl \
  --batch-size 5
```

### Data Quality Standards

Each sample must include:

✅ **Query**: Clear, thought-provoking question
✅ **Thesis**: Initial position (min 200 chars)
✅ **Antithesis**: Contradictions with evidence (min 200 chars)
✅ **Synthesis**: Transcendent resolution with predictions (min 300 chars)
✅ **Contradictions**: List of identified contradictions
✅ **Research Proposals**: Testable predictions

### Expected Output Format

```json
{
  "query": "Can artificial intelligence be truly creative?",
  "mode": "synthesis",
  "thesis": "THESIS: The Creative Machine\n\nYes, Artificial Intelligence can be genuinely creative...",
  "antithesis": "ANTITHESIS: The Sophisticated Mirror\n\nCONTRADICTION: The Redefinition Fallacy\nEVIDENCE: ...",
  "synthesis": "SYNTHESIS: The Co-Creative Process\n\nPREDICTION 1: ...\nRESEARCH_PROPOSAL: ...",
  "contradictions": [
    {
      "description": "The Redefinition Fallacy",
      "evidence": "The thesis narrows 'creativity' to computational procedure..."
    }
  ],
  "research_proposals": [
    {
      "description": "The Co-Creative Trace Analysis",
      "testable_prediction": "Artifacts from iterative human-AI loops will be rated more creative..."
    }
  ],
  "metadata": {...},
  "trace": {...}
}
```

## Validation Metrics

The validator checks:
- ✅ Proper dialectical structure (THESIS/ANTITHESIS/SYNTHESIS)
- ✅ Minimum length requirements
- ✅ Contradiction identification
- ✅ Research proposals with predictions
- ✅ No duplicate queries
- ✅ Topic diversity

**Target**: 95%+ samples pass validation

## Cleaning Pipeline

The cleaner performs:
1. **Exact Deduplication**: Removes identical queries (keeps highest quality)
2. **Quality Filtering**: Removes samples that are too short or lack structure
3. **Ranking**: Sorts by quality score (length + contradictions + markers + conflict score)

## Troubleshooting

### No API Key Found

```bash
# Make sure you've exported your API key
echo $ANTHROPIC_API_KEY
# Should print your key

# Or add to .env file
cat > .env << EOF
ANTHROPIC_API_KEY=your-key-here
EOF
```

### Generation is Slow

- Use `--batch-size 3` to process multiple samples concurrently
- Use faster models: `--model claude-haiku` or `--model gpt-3.5-turbo`
- Generate in chunks of 100 and resume later

### Low Quality Samples

- Use better models: Claude Sonnet 4 or GPT-4
- Increase `--max-tokens 6000` for longer dialectical traces
- Review and manually curate the top 500 from a larger set

### Out of Memory

- Reduce `--batch-size 1` (sequential processing)
- Generate in smaller batches (100 at a time)
- Use `--resume` to continue from checkpoint

## Training Pipeline

After generating clean data:

### 1. Convert for Training Framework

```bash
# For Unsloth/HuggingFace
python scripts/convert_for_training.py \
  data/hegelion_500_clean.jsonl \
  --format alpaca \
  --output data/hegelion_alpaca.jsonl

# For MLX
python scripts/convert_for_training.py \
  data/hegelion_500_clean.jsonl \
  --format mlx \
  --output data/hegelion_mlx.jsonl
```

### 2. Train Model

```bash
# MLX Training (Apple Silicon)
cd hegelion/training
python mlx_trainer.py \
  --data ../../data/hegelion_alpaca.jsonl \
  --model allenai/OLMo-7B-0724-hf \
  --output models/olmo-7b-hegelian

# Unsloth Training (CUDA)
python unsloth_trainer.py \
  --data ../../data/hegelion_alpaca.jsonl \
  --model allenai/OLMo-7B-0724-hf \
  --output models/olmo-7b-hegelian
```

## Benchmarking

Test the fine-tuned model:

```bash
# Run on benchmark prompts
python hegelion/training/benchmark.py \
  --model models/olmo-7b-hegelian \
  --prompts benchmarks/examples_basic.jsonl
```

## Cost Estimates

### Using Claude Sonnet 4
- ~$3/million input tokens, ~$15/million output tokens
- Avg 500 tokens input, 4000 tokens output per sample
- **500 samples ≈ $30-40**

### Using GPT-4
- ~$3/million input tokens, ~$6/million output tokens
- Avg 500 tokens input, 4000 tokens output per sample
- **500 samples ≈ $15-20**

### Using Moonshot Kimi
- Lower cost than OpenAI/Anthropic
- **500 samples ≈ $5-10**

## Quality vs Speed Trade-offs

| Model | Quality | Speed | Cost | Recommended |
|-------|---------|-------|------|-------------|
| Claude Sonnet 4 | ⭐⭐⭐⭐⭐ | Medium | $$$ | ✅ Best quality |
| GPT-4 | ⭐⭐⭐⭐ | Medium | $$ | ✅ Good balance |
| Claude Haiku | ⭐⭐⭐ | Fast | $ | Quick tests |
| Moonshot Kimi | ⭐⭐⭐⭐ | Medium | $ | ✅ Budget option |

## Best Practices

1. **Start Small**: Generate 10 samples first to verify quality
2. **Use Resume**: Always use `--resume` to avoid losing progress
3. **Validate Early**: Check quality after first 50 samples
4. **Diverse Topics**: Use all 500 prompts for maximum diversity
5. **Manual Review**: Inspect top 10 and bottom 10 by quality score
6. **Iterate**: If quality is low, adjust prompts or model

## Example Workflow

```bash
# 1. Test with 10 samples
python scripts/generate_500_samples.py \
  --prompts hegelion_prompts_500.txt \
  --output data/test_10.jsonl \
  --limit 10

# 2. Validate test
python scripts/validate_hegelian_dataset.py data/test_10.jsonl

# 3. If quality is good, generate full set
python scripts/generate_500_samples.py \
  --prompts hegelion_prompts_500.txt \
  --output data/hegelion_500.jsonl \
  --limit 500 \
  --resume

# 4. Clean and deduplicate
python scripts/clean_dataset.py data/hegelion_500.jsonl

# 5. Final validation
python scripts/validate_hegelian_dataset.py data/hegelion_500_cleaned.jsonl

# 6. Ready for training!
```

## Success Criteria

✅ 500+ unique samples
✅ 95%+ pass quality validation
✅ Average 4000+ chars dialectical trace
✅ 2+ contradictions per sample
✅ 1+ research proposal per sample
✅ 50+ unique topic domains

## Support

If you encounter issues:
1. Check the error logs
2. Validate your API keys
3. Review sample outputs manually
4. Adjust quality thresholds in `clean_dataset.py`

## Next Steps

After generating your dataset:
1. Train a base model (OLMo, Llama, etc.)
2. Benchmark against standard reasoning tasks
3. Compare dialectical depth vs base model
4. Iterate on prompt design based on weaknesses

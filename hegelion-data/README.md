# Hegelian Dialectical Training Dataset - Complete Infrastructure

## 🎯 Mission
Generate 500+ high-quality training samples to teach language models Hegelian dialectical reasoning: **THESIS → ANTITHESIS → SYNTHESIS**.

> All paths and commands assume you're working from the `hegelion-data/` directory. You can copy this folder into a private repository and keep iterating without touching the rest of the project.

## 📦 What's Included

### 1. Prompt Library
- **File**: `prompts/hegelion_prompts_500.txt`
- **Contents**: 580 carefully curated questions across 30+ domains
- **Domains**: Philosophy, Ethics, AI, Science, Politics, Economics, and more
- **Design**: Each prompt naturally invites dialectical tension

### 2. Generation Scripts

#### Primary Generator
- **File**: `scripts/generate_with_kimi.py`
- **Purpose**: Direct API generation using any OpenAI-compatible endpoint
- **Features**:
  - Automatic retry with exponential backoff
  - Resume from interruption
  - Token tracking
  - Quality validation
- **Supports**: Kimi/Moonshot, OpenAI, Anthropic, or any OpenAI-compatible API

#### Alternative Generator
- **File**: `scripts/generate_500_samples.py`
- **Purpose**: Uses full Hegelion engine for generation
- **Requires**: Hegelion package dependencies
- **Best for**: Advanced users with Hegelion installed

### 3. Quality Assurance Tools

#### Validator
- **File**: `scripts/validate_hegelian_dataset.py`
- **Checks**:
  - Proper dialectical structure (THESIS/ANTITHESIS/SYNTHESIS)
  - Minimum length requirements (T:200, A:200, S:300 chars)
  - Contradiction identification
  - Research proposal inclusion
  - Duplicate detection
  - Topic diversity analysis
- **Usage**:
  ```bash
  python scripts/validate_hegelian_dataset.py data/your_dataset.jsonl
  ```

#### Cleaner
- **File**: `scripts/clean_dataset.py`
- **Functions**:
  - Remove exact duplicates (keeps highest quality)
  - Filter by quality thresholds
  - Rank by quality score
  - Remove incomplete samples
- **Usage**:
  ```bash
  python scripts/clean_dataset.py data/raw.jsonl --output data/clean.jsonl
  ```

### 4. Documentation

- **QUICKSTART_500_SAMPLES.md**: Step-by-step generation guide
- **DATASET_GENERATION_GUIDE.md**: Comprehensive reference
- **manual_dialectic_template.md**: Manual generation fallback
- **claude_system_prompt.md**: Drop-in instructions for Claude/Anthropic workflows

### 5. Reference Examples

- **File**: `examples/glm4_6_examples.jsonl`
- **Count**: 4 high-quality reference samples
- **Quality**: 100% validation pass rate
- **Avg Length**: 4795 chars per trace

## 🚀 Quick Start

### Test Run (10 Samples)

```bash
# 1. Set your API key
export OPENAI_API_KEY="your-api-key"

# 2. Generate 10 test samples
python scripts/generate_with_kimi.py \
  --prompts prompts/hegelion_prompts_500.txt \
  --output data/test_10.jsonl \
  --limit 10 \
  --base-url "https://api.moonshot.cn/v1" \
  --model "moonshot-v1-128k"

# 3. Validate quality
python scripts/validate_hegelian_dataset.py data/test_10.jsonl

# 4. Review manually
head -1 data/test_10.jsonl | jq '.'
```

### Full Generation (500 Samples)

```bash
# Generate all 500 (auto-resumes if interrupted)
python scripts/generate_with_kimi.py \
  --prompts prompts/hegelion_prompts_500.txt \
  --output data/hegelion_500.jsonl \
  --limit 500 \
  --resume

# Clean and deduplicate
python scripts/clean_dataset.py \
  data/hegelion_500.jsonl \
  --output data/hegelion_500_clean.jsonl

# Final validation
python scripts/validate_hegelian_dataset.py \
  data/hegelion_500_clean.jsonl
```

## 🤖 Claude Plug-and-Play Workflow

This folder is ready to copy into its own private repository while reusing your existing Anthropic tokens.

1. `python scripts/batch_generate_claude.py` — surfaces the next prompts and remaining sample count.
2. Open Claude (Desktop, claude.ai, Claude Code, or API) and load `claude_system_prompt.md` as the system prompt.
3. Paste the user template from that file, drop in the next prompt, and let Claude produce THESIS/ANTITHESIS/SYNTHESIS plus the JSON object.
4. Append each JSON line to `data/hegelion_dialectical_500.jsonl` (or any file you configure in the scripts).
5. Every 25–50 samples, run `python scripts/validate_hegelian_dataset.py data/hegelion_dialectical_500.jsonl` and `python scripts/clean_dataset.py` to dedupe.
6. Track spending with Claude's usage console; the scripts never transmit your keys—you're operating entirely within your own sandbox.

**API option:**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python scripts/generate_500_samples.py \
  --provider anthropic \
  --model claude-sonnet-4 \
  --prompts prompts/hegelion_prompts_500.txt \
  --output data/hegelion_500_samples.jsonl
```

## 🎨 Sample Output Structure

```json
{
  "query": "Can artificial intelligence be truly creative?",
  "mode": "synthesis",
  "thesis": "THESIS: The Creative Machine\n\nYes, AI can be genuinely creative...",
  "antithesis": "ANTITHESIS: The Sophisticated Mirror\n\nCONTRADICTION: The Redefinition Fallacy\nEVIDENCE: ...",
  "synthesis": "SYNTHESIS: The Co-Creative Process\n\nPREDICTION 1: ...\nRESEARCH_PROPOSAL: ...",
  "contradictions": [
    {
      "description": "The Redefinition Fallacy",
      "evidence": "Specific evidence of the contradiction"
    }
  ],
  "research_proposals": [
    {
      "description": "The Co-Creative Trace Analysis",
      "testable_prediction": "Specific testable prediction"
    }
  ],
  "metadata": {
    "source": "kimi-for-coding",
    "backend_provider": "kimi",
    "backend_model": "kimi-for-coding"
  },
  "trace": {
    "thesis": "...",
    "antithesis": "...",
    "synthesis": "...",
    "contradictions_found": 3,
    "research_proposals": ["Proposal | Prediction: ..."]
  }
}
```

## 📊 Quality Metrics

Target metrics for final dataset:

| Metric | Target | Validation |
|--------|--------|------------|
| Total Samples | 500+ | ✓ Count |
| Unique Queries | 95%+ | ✓ Dedup check |
| Valid Structure | 95%+ | ✓ Has T/A/S |
| Avg Trace Length | 4000+ chars | ✓ Length check |
| Contradictions | 2+ per sample | ✓ Parse count |
| Research Proposals | 1+ per sample | ✓ Parse count |
| Topic Diversity | 50+ domains | ✓ Diversity analysis |

## 🔧 API Configuration

### Moonshot Kimi (Recommended - Budget Option)

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.moonshot.cn/v1"

python scripts/generate_with_kimi.py \
  --base-url "https://api.moonshot.cn/v1" \
  --model "moonshot-v1-128k"
```

### Anthropic Claude (Recommended - Best Quality)

```bash
# Requires modifying script or using Hegelion engine
export ANTHROPIC_API_KEY="sk-ant-..."

python scripts/generate_500_samples.py \
  --provider anthropic \
  --model claude-sonnet-4
```

### OpenAI GPT-4

```bash
export OPENAI_API_KEY="sk-..."

python scripts/generate_with_kimi.py \
  --base-url "https://api.openai.com/v1" \
  --model "gpt-4"
```

## 💡 Generation Tips

### For Best Quality
1. **Use high-quality models**: Claude Sonnet 4 or GPT-4
2. **Increase max tokens**: 4000-6000 per response
3. **Review samples manually**: Check first 10, last 10
4. **Iterate on failures**: Regenerate low-quality samples

### For Speed
1. **Use faster models**: GPT-3.5-Turbo or Claude Haiku
2. **Increase batch size**: Process multiple in parallel
3. **Accept lower quality**: Filter heavily in cleaning step

### For Cost Efficiency
1. **Use Moonshot**: ~$5-10 for 500 samples
2. **Generate extras**: Make 600, keep best 500
3. **Use lower temperature**: 0.7 instead of 0.9

## 🐛 Troubleshooting

### API Key Issues

| Error | Solution |
|-------|----------|
| 403 Forbidden | Wrong endpoint or key type (e.g., IDE-only key) |
| 401 Unauthorized | Check API key is set correctly |
| SSL Certificate | Use standard Moonshot endpoint, not IDE-specific |

### Quality Issues

| Problem | Solution |
|---------|----------|
| Short responses | Increase `max_tokens` to 6000 |
| Missing structure | Use better model (Claude/GPT-4) |
| Low diversity | Ensure all prompts are unique |
| Weak contradictions | Improve system prompt specificity |

### Technical Issues

| Error | Solution |
|-------|----------|
| `httpx` not found | Run: `pip install openai` |
| Import errors | Run: `pip install -e .` |
| Memory issues | Reduce batch size to 1 |
| Timeout | Increase timeout in script |

## 📁 File Organization

```
Hegelion/
├── hegelion-data/
│   ├── README.md                      # This file
│   ├── claude_system_prompt.md        # Drop-in Claude system prompt
│   ├── prompts/
│   │   └── hegelion_prompts_500.txt   # 580 prompts
│   ├── scripts/
│   │   ├── generate_with_kimi.py          # Main generator
│   │   ├── generate_500_samples.py        # Hegelion engine generator
│   │   ├── validate_hegelian_dataset.py   # Quality validator
│   │   ├── clean_dataset.py               # Deduplicator
│   │   ├── batch_generate_claude.py       # Manual batching helper
│   │   ├── format_manual_dialectic.py     # Markdown → JSONL formatter
│   │   └── manual_dialectic_template.md   # Manual generation guide
│   ├── examples/
│   │   └── glm4_6_examples.jsonl      # 4 reference samples
│   └── data/                          # Generated datasets (gitignored)
│       ├── test_10.jsonl              # Test runs
│       ├── hegelion_500.jsonl         # Raw generation
│       └── hegelion_500_clean.jsonl   # Final cleaned dataset
├── hegelion/
│   └── training/                      # Training infrastructure
│       ├── mlx_trainer.py             # MLX training (Apple Silicon)
│       ├── unsloth_trainer.py         # Unsloth training (CUDA)
│       └── generator.py               # Original generator
└── ...
```

## 🎓 Training Pipeline

After generating clean dataset:

```bash
# 1. Validate final dataset
python scripts/validate_hegelian_dataset.py data/hegelion_500_clean.jsonl

# 2. Train model (MLX - Apple Silicon)
cd ../hegelion/training
python mlx_trainer.py \
  --data ../../hegelion-data/data/hegelion_500_clean.jsonl \
  --model allenai/OLMo-7B-0724-hf \
  --output models/olmo-7b-hegelian

# 3. Benchmark results
python benchmark.py \
  --model models/olmo-7b-hegelian \
  --prompts ../../benchmarks/examples_basic.jsonl
```

## 📈 Success Metrics

Your dataset is production-ready when:

- [x] ✅ 500+ unique samples
- [x] ✅ 95%+ validation pass rate
- [x] ✅ < 5% duplicates
- [x] ✅ 4000+ avg chars per trace
- [x] ✅ 2+ contradictions per sample
- [x] ✅ 1+ research proposal per sample
- [x] ✅ 50+ unique topic domains

## 🔬 Research Applications

This dataset enables:

1. **Dialectical Reasoning Fine-Tuning**: Train models to think in T→A→S structure
2. **Contradiction Detection**: Learn to identify logical tensions
3. **Synthesis Generation**: Practice creating transcendent resolutions
4. **Research Proposal Generation**: Generate testable hypotheses
5. **Multi-Perspective Analysis**: See issues from thesis AND antithesis

## 📝 Citation

If you use this dataset or infrastructure in research:

```bibtex
@misc{hegelion_dataset_2024,
  title={Hegelian Dialectical Training Dataset},
  author={Hegelion Project},
  year={2024},
  howpublished={\url{https://github.com/Hmbown/Hegelion}}
}
```

## 🤝 Contributing

To improve this infrastructure:

1. **Add prompts**: Contribute to `prompts/hegelion_prompts_500.txt`
2. **Improve scripts**: Enhance generation/validation logic
3. **Share results**: Report quality metrics from different models
4. **Fix bugs**: Submit issues or PRs

## 📞 Support

Need help?

1. Check `QUICKSTART_500_SAMPLES.md` for step-by-step
2. Review existing examples: `cat examples/glm4_6_examples.jsonl | jq '.'`
3. Test with 10 samples first
4. Use manual generation template as fallback

## 🎯 Next Steps

1. **Test Run**: Generate 10 samples to verify setup
2. **Full Generation**: Create 500 samples
3. **Quality Check**: Validate and clean
4. **Train Model**: Fine-tune OLMo or Llama
5. **Benchmark**: Compare dialectical depth
6. **Iterate**: Improve prompts based on weaknesses

---

**Ready to start?**

```bash
# Test with 10 samples
python scripts/generate_with_kimi.py --limit 10

# Validate results
python scripts/validate_hegelian_dataset.py data/test_10.jsonl
```

Good luck creating your Hegelian thinking dataset! 🚀

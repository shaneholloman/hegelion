# Claude Code Handoff - Hegelian Data Generation

## 🎯 Quick Start Command

When the user says **"go"**, continue generating Hegelian dialectical samples following the workflow below.

## 📊 Current Progress

- **Total Samples Completed**: 148 samples
- **Current Batch**: Batch 4 (prompts 146-155) - **3 of 10 completed**
- **Remaining in Batch 4**: 7 samples (prompts 149-155)
- **Overall Target**: 500+ samples
- **Remaining to Target**: 352 samples

### Completed Batches
- ✅ Batch 1 (116-125): 10 AI/ML and Economics samples
- ✅ Batch 2 (126-135): 10 Economics/Policy samples (no AI topics)
- ✅ Batch 3 (136-145): 10 Economics/Education samples
- ⏳ Batch 4 (146-148 done, 149-155 pending): Education topics

## 🔄 Generation Workflow

### Step 1: Check Current Progress
```bash
# Count existing samples
wc -l data/hegelion_dialectical_500.jsonl

# View last few queries to see where you left off
tail -5 data/hegelion_dialectical_500.jsonl | jq -r '.query'
```

### Step 2: Get Next Prompts
The next prompts to work on are **149-155** from `prompts/hegelion_prompts_500.txt`.

Read prompts:
```bash
# Get specific prompts (adjust line numbers as needed)
sed -n '149,155p' prompts/hegelion_prompts_500.txt
```

### Step 3: Generate Each Sample

For each prompt, follow the **Hegelian Dialectical Structure**:

#### Required Structure:
1. **THESIS** (≥200 chars): Strongest affirmative position with mechanisms/evidence
2. **ANTITHESIS** (≥200 chars): Rigorous critique with labeled contradictions
   - Format: `CONTRADICTION: <name>\nEVIDENCE: <concrete evidence>`
3. **SYNTHESIS** (≥300 chars): Integrated resolution with predictions and research
   - Format: `PREDICTION N: <testable claim>\nRESEARCH_PROPOSAL: <study design>`

#### Quality Requirements:
- ✅ Minimum lengths: T≥200, A≥200, S≥300 characters
- ✅ At least 2 contradictions with concrete evidence
- ✅ At least 1 research proposal with falsifiable prediction
- ✅ Total trace length ≥1,000 characters (target: 6,000-7,000+)
- ✅ Topic diversity (rotate domains across prompts)

#### JSON Schema:
```json
{
  "query": "<original question>",
  "mode": "synthesis",
  "thesis": "<full thesis text>",
  "antithesis": "<full antithesis with CONTRADICTION/EVIDENCE labels>",
  "synthesis": "<full synthesis with PREDICTION/RESEARCH_PROPOSAL>",
  "contradictions": [
    {"description": "<contradiction name>", "evidence": "<evidence text>"}
  ],
  "research_proposals": [
    {"description": "<proposal>", "testable_prediction": "<prediction>"}
  ],
  "metadata": {
    "source": "claude-code",
    "backend_provider": "anthropic",
    "backend_model": "claude-sonnet-4-5"
  },
  "trace": {
    "thesis": "<same as thesis>",
    "antithesis": "<same as antithesis>",
    "synthesis": "<same as synthesis>",
    "contradictions_found": <count>,
    "research_proposals": ["<description> | Prediction: <prediction>"]
  }
}
```

### Step 4: Append to Dataset

After generating each sample, append it to the dataset file:

```bash
cat >> data/hegelion_dialectical_500.jsonl << 'EOF'
{"query":"...","mode":"synthesis",...}
EOF
```

**IMPORTANT**: Each JSON object must be on a single line (JSONL format).

### Step 5: Quality Check (Optional but Recommended)

After every 5-10 samples, run quick validation:
```bash
# Check last sample structure
tail -1 data/hegelion_dialectical_500.jsonl | jq '.'

# Count total samples
wc -l data/hegelion_dialectical_500.jsonl
```

### Step 6: Commit and Push (After Each Batch of 10)

```bash
git add data/hegelion_dialectical_500.jsonl
git commit -m "Add batch N: 10 samples on <topic> (prompts X-Y)"
git push -u origin claude/hegelian-data-creation-014UHrKFsFrKys8JXL7y6GKh
```

## 📝 Generation Tips

### Topic Diversity
- **Avoid AI topics** - user specifically requested no more AI/ML topics after batch 1
- Rotate through: Economics, Politics, Ethics, Education, Science, Philosophy, Technology (non-AI), Social Issues, etc.
- Check prompts file for domain variety

### Quality Over Speed
- Take time to develop rich contradictions with specific evidence
- Make predictions falsifiable and testable
- Ensure synthesis truly integrates both perspectives (not just compromise)
- Aim for 6,000-7,000+ character traces (well above minimum)

### Common Pitfalls to Avoid
- ❌ Generic contradictions without specific evidence
- ❌ Vague predictions that aren't falsifiable
- ❌ Synthesis that just picks a middle ground (need transcendence)
- ❌ Too similar to previous samples (diversity is key)
- ❌ Falling back to AI topics (explicitly forbidden)

## 🎓 Example High-Quality Sample

See `/home/user/hegelion-data/examples/glm4_6_examples.jsonl` for reference samples that achieve 100% validation pass rate.

Quick view:
```bash
head -1 examples/glm4_6_examples.jsonl | jq '.'
```

## 🚀 Batch Generation Strategy

### Efficient Batch Workflow:
1. Generate 10 samples (one complete batch)
2. Append all to dataset file
3. Quick quality check
4. Commit and push
5. Repeat for next batch

### Token Management:
- Each sample requires ~2,000-3,000 tokens to generate
- Each batch of 10 ≈ 20,000-30,000 tokens
- Monitor token usage and generate as many batches as possible
- Aim for 2-5 batches per session

## 📦 Next Immediate Steps

When you continue:

1. **Complete Batch 4** (prompts 149-155, 7 remaining):
   - Generate samples for prompts 149-155
   - Append to `data/hegelion_dialectical_500.jsonl`
   - Commit: "Add batch 4 completion: 7 education samples (149-155)"
   - Push to branch

2. **Continue with Batch 5** (prompts 156-165):
   - Read next 10 prompts from file
   - Generate following same quality standards
   - Continue pattern

3. **Periodic Validation** (every 50 samples):
   ```bash
   python scripts/validate_hegelian_dataset.py data/hegelion_dialectical_500.jsonl
   ```

4. **When approaching 500 samples**:
   - Run full validation
   - Run cleaning script if needed:
     ```bash
     python scripts/clean_dataset.py data/hegelion_dialectical_500.jsonl --output data/hegelion_500_clean.jsonl
     ```
   - Create final PR

## 🌲 Git Branch Info

- **Working Branch**: `claude/hegelian-data-creation-014UHrKFsFrKys8JXL7y6GKh`
- **Main Branch**: (check with `git branch -r`)
- **Always push to working branch**: `git push -u origin claude/hegelian-data-creation-014UHrKFsFrKys8JXL7y6GKh`

## 📋 Reference Commands

```bash
# Get next prompts to generate
python scripts/batch_generate_claude.py

# View last generated sample
tail -1 data/hegelion_dialectical_500.jsonl | jq '.'

# Count samples
wc -l data/hegelion_dialectical_500.jsonl

# Validate dataset
python scripts/validate_hegelian_dataset.py data/hegelion_dialectical_500.jsonl

# Clean dataset (removes duplicates)
python scripts/clean_dataset.py data/hegelion_dialectical_500.jsonl --output data/hegelion_500_clean.jsonl

# Check git status
git status

# Commit batch
git add data/hegelion_dialectical_500.jsonl
git commit -m "Add batch N: description"
git push -u origin claude/hegelian-data-creation-014UHrKFsFrKys8JXL7y6GKh
```

## 🎯 User Preferences

Based on previous session feedback:
- ✅ "Keep going if you feel like you're in a flow" - generate multiple batches per session
- ✅ "No more AI topics lol" - diversify away from AI/ML
- ✅ Quality over quantity - all samples have passed quality standards so far
- ✅ Autonomous generation - minimal interruption needed once in flow

## 💯 Success Metrics

Current quality standards being achieved:
- ✅ 100% structural validity (all have T/A/S)
- ✅ Average trace length: 6,000-7,000+ characters
- ✅ Average contradictions: 3-4 per sample
- ✅ All samples include research proposals with testable predictions
- ✅ No duplicates so far
- ✅ Good topic diversity across batches

**Keep this quality bar high!**

---

## 🚀 Ready to Continue?

When user says "go":
1. Read prompts 149-155 from `prompts/hegelion_prompts_500.txt`
2. Generate 7 remaining samples for Batch 4
3. Append to `data/hegelion_dialectical_500.jsonl`
4. Commit and push
5. Continue with Batch 5 (prompts 156-165)
6. Repeat until tokens run low
7. Final commit and update this file with new progress

Good luck! The previous session generated 33 high-quality samples across 3.5 batches. Continue that excellence! 🎓

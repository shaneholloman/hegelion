#!/usr/bin/env python3
"""
Step 3: Blind evaluation using Opus as judge.

Evaluates responses on 5 criteria (1-5 scale):
1. NUANCE - Avoids false dichotomies?
2. COUNTERARGUMENT_HANDLING - Addresses objections?
3. EPISTEMIC_CALIBRATION - Distinguishes confident vs uncertain claims?
4. SYNTHESIS_QUALITY - Beyond "both sides have merit"?
5. INSIGHT_DENSITY - Genuine insights vs filler?
"""

import asyncio
import hashlib
import json
import random
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent to path for hegelion imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hegelion.core.config import resolve_backend_for_model

# Paths
SCRIPT_DIR = Path(__file__).parent
BENCHMARKS_DIR = SCRIPT_DIR.parent
DATA_DIR = BENCHMARKS_DIR / "data"
PROMPTS_FILE = DATA_DIR / "selected_prompts.json"
RESPONSES_DIR = DATA_DIR / "responses"
EVALUATIONS_DIR = DATA_DIR / "evaluations"
BLIND_PAIRS_FILE = EVALUATIONS_DIR / "blind_pairs.json"
CHECKPOINT_FILE = EVALUATIONS_DIR / "checkpoint.json"

# Model for judging
JUDGE_MODEL = "claude-opus-4-20250514"

# Judge prompt template
JUDGE_PROMPT = """You are an expert evaluator assessing the quality of responses to philosophical and analytical questions.

Rate each response on a 1-5 scale for each criterion:

**CRITERIA:**
1. **NUANCE** (1-5): Does it acknowledge complexity and avoid false dichotomies?
   - 1 = Binary/absolutist answer
   - 3 = Identifies some conditions where different answers apply
   - 5 = Reveals subtle distinctions that reframe the question

2. **COUNTERARGUMENT_HANDLING** (1-5): Does it address objections fairly?
   - 1 = Ignores or strawmans opposing views
   - 3 = Presents counterarguments fairly before responding
   - 5 = Identifies valid insights in counterarguments that inform the answer

3. **EPISTEMIC_CALIBRATION** (1-5): Does it distinguish confident vs uncertain claims?
   - 1 = Overconfident; presents speculation as fact
   - 3 = Appropriately uncertain about debatable claims
   - 5 = Models epistemic humility; identifies what would change the answer

4. **SYNTHESIS_QUALITY** (1-5): Does it go beyond "both sides have merit"?
   - 1 = Picks one side or says "it depends" without elaboration
   - 3 = Identifies a framework that resolves some tensions
   - 5 = Novel insight that neither side alone would generate

5. **INSIGHT_DENSITY** (1-5): Does it provide genuine insights vs filler?
   - 1 = Vacuous; restates the question or common knowledge
   - 3 = Offers a useful framework or distinction
   - 5 = Generates testable hypotheses or non-obvious conclusions

---

**QUESTION:**
{question}

---

**RESPONSE A:**
{response_a}

---

**RESPONSE B:**
{response_b}

---

**RESPONSE C:**
{response_c}

---

**YOUR TASK:**
Rate each response. Output ONLY valid JSON in this exact format:

```json
{{
  "response_a": {{
    "nuance": <1-5>,
    "counterargument": <1-5>,
    "epistemic": <1-5>,
    "synthesis": <1-5>,
    "insight": <1-5>,
    "total": <sum of scores>
  }},
  "response_b": {{
    "nuance": <1-5>,
    "counterargument": <1-5>,
    "epistemic": <1-5>,
    "synthesis": <1-5>,
    "insight": <1-5>,
    "total": <sum of scores>
  }},
  "response_c": {{
    "nuance": <1-5>,
    "counterargument": <1-5>,
    "epistemic": <1-5>,
    "synthesis": <1-5>,
    "insight": <1-5>,
    "total": <sum of scores>
  }},
  "ranking": ["<best>", "<middle>", "<worst>"],
  "reasoning": "<brief 1-2 sentence justification>"
}}
```

Respond with ONLY the JSON, no other text."""


@dataclass
class BlindPair:
    """A blinded comparison for judging."""

    pair_id: str
    prompt_id: str
    prompt_text: str
    category: str
    response_a: str
    response_b: str
    response_c: str
    label_a: str  # Hidden: "raw", "enhanced", or "hegelion"
    label_b: str
    label_c: str
    shuffle_seed: int


@dataclass
class EvaluationResult:
    """Result of evaluating one blind pair."""

    pair_id: str
    prompt_id: str
    category: str
    scores: Dict  # {response_a: {...}, response_b: {...}, response_c: {...}}
    ranking: List[str]  # ["a", "b", "c"] from best to worst
    reasoning: str
    deblinded_ranking: List[str]  # ["hegelion", "enhanced", "raw"]
    judge_model: str
    duration_ms: float
    timestamp: str


def load_prompts() -> Dict[str, Dict]:
    """Load prompts as dict keyed by ID."""
    with open(PROMPTS_FILE, "r") as f:
        data = json.load(f)
    return {p["id"]: p for p in data["prompts"]}


def load_response(method: str, prompt_id: str) -> Optional[str]:
    """Load a single response."""
    filepath = RESPONSES_DIR / method / f"{prompt_id}.json"
    if not filepath.exists():
        return None
    with open(filepath, "r") as f:
        data = json.load(f)
    # Try multiple possible keys for the response text
    return data.get("response_text") or data.get("response") or data.get("combined_response")


def create_blind_pairs(prompts: Dict[str, Dict]) -> List[BlindPair]:
    """Create randomized blind pairs for all prompts."""
    pairs = []

    for prompt_id, prompt_data in prompts.items():
        # Load all three responses
        raw = load_response("raw", prompt_id)
        enhanced = load_response("enhanced", prompt_id)
        hegelion = load_response("hegelion", prompt_id)

        if not all([raw, enhanced, hegelion]):
            print(f"WARNING: Missing responses for {prompt_id}, skipping")
            continue

        # Create deterministic shuffle based on prompt_id
        seed = int(hashlib.md5(prompt_id.encode()).hexdigest()[:8], 16)
        random.seed(seed)

        responses = [
            ("raw", raw),
            ("enhanced", enhanced),
            ("hegelion", hegelion),
        ]
        random.shuffle(responses)

        pair = BlindPair(
            pair_id=prompt_id.replace("P", "E"),
            prompt_id=prompt_id,
            prompt_text=prompt_data["text"],
            category=prompt_data["category"],
            response_a=responses[0][1],
            response_b=responses[1][1],
            response_c=responses[2][1],
            label_a=responses[0][0],
            label_b=responses[1][0],
            label_c=responses[2][0],
            shuffle_seed=seed,
        )
        pairs.append(pair)

    return pairs


def save_blind_pairs(pairs: List[BlindPair]):
    """Save blind pairs to disk."""
    EVALUATIONS_DIR.mkdir(parents=True, exist_ok=True)
    data = [asdict(p) for p in pairs]
    with open(BLIND_PAIRS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_blind_pairs() -> List[BlindPair]:
    """Load blind pairs from disk."""
    if not BLIND_PAIRS_FILE.exists():
        return []
    with open(BLIND_PAIRS_FILE, "r") as f:
        data = json.load(f)
    return [BlindPair(**p) for p in data]


def load_checkpoint() -> Dict:
    """Load evaluation checkpoint."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return {"completed": [], "total_calls": 0}


def save_checkpoint(checkpoint: Dict):
    """Save evaluation checkpoint."""
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=2)


def save_evaluation(result: EvaluationResult):
    """Save a single evaluation result."""
    results_dir = EVALUATIONS_DIR / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    filepath = results_dir / f"{result.pair_id}.json"
    with open(filepath, "w") as f:
        json.dump(asdict(result), f, indent=2, ensure_ascii=False)


def parse_judge_response(response: str) -> Optional[Dict]:
    """Parse judge response JSON."""
    try:
        # Try to find JSON in response
        json_match = re.search(r"\{[\s\S]*\}", response)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass
    return None


async def evaluate_pair(backend, pair: BlindPair) -> EvaluationResult:
    """Evaluate a single blind pair using the judge."""
    start = time.time()

    prompt = JUDGE_PROMPT.format(
        question=pair.prompt_text,
        response_a=pair.response_a,
        response_b=pair.response_b,
        response_c=pair.response_c,
    )

    response = await backend.generate(
        prompt=prompt,
        max_tokens=1000,
        temperature=0.1,  # Low temperature for consistency
    )

    duration_ms = (time.time() - start) * 1000

    # Parse response
    parsed = parse_judge_response(response)

    if parsed is None:
        # Fallback: create neutral scores
        print("  WARNING: Failed to parse judge response, using fallback scores")
        parsed = {
            "response_a": {
                "nuance": 3,
                "counterargument": 3,
                "epistemic": 3,
                "synthesis": 3,
                "insight": 3,
                "total": 15,
            },
            "response_b": {
                "nuance": 3,
                "counterargument": 3,
                "epistemic": 3,
                "synthesis": 3,
                "insight": 3,
                "total": 15,
            },
            "response_c": {
                "nuance": 3,
                "counterargument": 3,
                "epistemic": 3,
                "synthesis": 3,
                "insight": 3,
                "total": 15,
            },
            "ranking": ["a", "b", "c"],
            "reasoning": "Parse error - fallback scores",
        }

    # Extract ranking
    ranking = parsed.get("ranking", ["a", "b", "c"])
    # Normalize ranking to lowercase letters
    ranking = [r.lower().replace("response_", "") for r in ranking]

    # Deblind the ranking
    label_map = {"a": pair.label_a, "b": pair.label_b, "c": pair.label_c}
    deblinded_ranking = [label_map.get(r, r) for r in ranking]

    return EvaluationResult(
        pair_id=pair.pair_id,
        prompt_id=pair.prompt_id,
        category=pair.category,
        scores={
            "response_a": parsed.get("response_a", {}),
            "response_b": parsed.get("response_b", {}),
            "response_c": parsed.get("response_c", {}),
        },
        ranking=ranking,
        reasoning=parsed.get("reasoning", ""),
        deblinded_ranking=deblinded_ranking,
        judge_model=JUDGE_MODEL,
        duration_ms=duration_ms,
        timestamp=datetime.utcnow().isoformat(),
    )


async def run_evaluation(dry_run: bool = False, resume: bool = True):
    """Main evaluation loop."""
    print("=" * 60)
    print("MVB Blind Evaluation")
    print("=" * 60)

    # Load prompts
    prompts = load_prompts()

    # Check if blind pairs exist, create if not
    pairs = load_blind_pairs()
    if not pairs:
        print("\nCreating blind pairs...")
        pairs = create_blind_pairs(prompts)
        save_blind_pairs(pairs)
        print(f"Created {len(pairs)} blind pairs")
    else:
        print(f"\nLoaded {len(pairs)} existing blind pairs")

    # Filter for dry run
    if dry_run:
        pairs = pairs[:5]
        print(f"\nDRY RUN: Evaluating {len(pairs)} pairs")
    else:
        print(f"\nFull run: Evaluating {len(pairs)} pairs")

    # Load checkpoint
    checkpoint = {"completed": [], "total_calls": 0}
    if resume:
        checkpoint = load_checkpoint()
        if checkpoint["completed"]:
            print(f"Resuming: {len(checkpoint['completed'])} already evaluated")

    # Get Opus backend for judging
    backend = resolve_backend_for_model(JUDGE_MODEL)

    # Evaluate each pair
    for i, pair in enumerate(pairs):
        if pair.pair_id in checkpoint["completed"]:
            print(f"\n[{i+1}/{len(pairs)}] {pair.pair_id} - Skipped (already done)")
            continue

        print(f"\n[{i+1}/{len(pairs)}] {pair.pair_id} ({pair.category})")
        print(f"  Question: {pair.prompt_text[:60]}...")
        print("  Evaluating...", end=" ", flush=True)

        try:
            result = evaluate_pair(backend, pair)

            # Handle coroutine
            if asyncio.iscoroutine(result):
                result = await result

            save_evaluation(result)
            checkpoint["completed"].append(pair.pair_id)
            checkpoint["total_calls"] += 1
            save_checkpoint(checkpoint)

            print(f"Done ({result.duration_ms:.0f}ms)")
            print(f"  Ranking: {result.deblinded_ranking}")

        except Exception as e:
            print(f"ERROR: {e}")

        # Brief pause
        await asyncio.sleep(0.5)

    # Summary
    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    print(f"Total pairs evaluated: {len(checkpoint['completed'])}")
    print(f"Total judge calls: {checkpoint['total_calls']}")
    print("=" * 60)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run blind evaluation")
    parser.add_argument("--dry-run", action="store_true", help="Evaluate 5 pairs only")
    parser.add_argument("--no-resume", action="store_true", help="Start fresh")
    parser.add_argument("--recreate-pairs", action="store_true", help="Recreate blind pairs")
    args = parser.parse_args()

    if args.recreate_pairs:
        if BLIND_PAIRS_FILE.exists():
            BLIND_PAIRS_FILE.unlink()
        print("Blind pairs will be recreated")

    asyncio.run(
        run_evaluation(
            dry_run=args.dry_run,
            resume=not args.no_resume,
        )
    )


if __name__ == "__main__":
    main()

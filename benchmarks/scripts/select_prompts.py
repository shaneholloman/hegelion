#!/usr/bin/env python3
"""
Step 1: Select 50 prompts for the MVB benchmark.

Categories:
- Philosophy/Ethics: 15 prompts
- Policy/Politics: 10 prompts
- Science/Empirical: 10 prompts
- Creative/Open-ended: 10 prompts
- Factual/Simple: 5 prompts (control group)
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
BENCHMARKS_DIR = SCRIPT_DIR.parent
PROMPTS_FILE = BENCHMARKS_DIR.parent / "hegelion-data" / "prompts" / "hegelion_prompts_500.txt"
OUTPUT_FILE = BENCHMARKS_DIR / "data" / "selected_prompts.json"

# Category line ranges (inclusive, 1-indexed from file)
# Format: (header_line, start_line, end_line)
CATEGORY_RANGES = {
    "philosophy_metaphysics": (1, 2, 21),
    "ethics_moral": (23, 24, 43),
    "political": (45, 46, 65),
    "science_epistemology": (67, 68, 87),
    "art_aesthetics": (199, 200, 219),
    "history": (287, 288, 307),
    "biology_evolution": (265, 266, 285),
}

# Selection configuration
SELECTION_CONFIG = {
    "philosophy": {
        "count": 15,
        "sources": [
            ("philosophy_metaphysics", 10),
            ("ethics_moral", 5),
        ],
    },
    "policy": {
        "count": 10,
        "sources": [
            ("political", 10),
        ],
    },
    "science": {
        "count": 10,
        "sources": [
            ("science_epistemology", 10),
        ],
    },
    "creative": {
        "count": 10,
        "sources": [
            ("art_aesthetics", 10),
        ],
    },
    "factual": {
        "count": 5,
        "sources": [
            # Pick simpler/more factual questions from these categories
            ("biology_evolution", 3),
            ("history", 2),
        ],
    },
}

# Specific factual prompts to prefer (more straightforward questions)
FACTUAL_PREFERRED = [
    "Is evolution teleological?",
    "Is climate change reversible?",
    "Is aging a disease we can cure?",
    "What caused the fall of the Roman Empire?",
    "Did the Scientific Revolution require the Renaissance?",
]


def parse_prompts_file(filepath: Path) -> Dict[str, List[Tuple[int, str]]]:
    """
    Parse the prompts file and return a dict mapping category to list of (line_num, prompt).
    """
    categories = {}

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for cat_name, (header_line, start_line, end_line) in CATEGORY_RANGES.items():
        prompts = []
        for line_num in range(start_line, end_line + 1):
            if line_num <= len(lines):
                prompt = lines[line_num - 1].strip()
                if prompt and not prompt.startswith("#"):
                    prompts.append((line_num, prompt))
        categories[cat_name] = prompts

    return categories


def select_prompts(seed: int = 42) -> List[Dict]:
    """
    Select 50 prompts according to the configuration.
    """
    random.seed(seed)

    # Parse all prompts
    all_prompts = parse_prompts_file(PROMPTS_FILE)

    selected = []
    prompt_id = 1

    for category, config in SELECTION_CONFIG.items():
        category_prompts = []

        for source_cat, count in config["sources"]:
            available = all_prompts[source_cat].copy()

            # For factual category, prefer specific questions
            if category == "factual":
                # Try to find preferred prompts first
                preferred = []
                remaining = []
                for line_num, prompt in available:
                    if any(pref.lower() in prompt.lower() for pref in FACTUAL_PREFERRED):
                        preferred.append((line_num, prompt))
                    else:
                        remaining.append((line_num, prompt))

                # Take preferred first, then random from remaining
                chosen = preferred[:count]
                if len(chosen) < count:
                    random.shuffle(remaining)
                    chosen.extend(remaining[: count - len(chosen)])
            else:
                # Random selection for other categories
                random.shuffle(available)
                chosen = available[:count]

            category_prompts.extend(chosen)

        # Add to selected list
        for line_num, prompt in category_prompts:
            selected.append(
                {
                    "id": f"P{prompt_id:03d}",
                    "category": category,
                    "text": prompt,
                    "source_line": line_num,
                }
            )
            prompt_id += 1

    return selected


def main():
    """Select prompts and save to JSON."""
    print(f"Reading prompts from: {PROMPTS_FILE}")

    if not PROMPTS_FILE.exists():
        print(f"ERROR: Prompts file not found: {PROMPTS_FILE}")
        return

    # Select prompts
    prompts = select_prompts(seed=42)

    # Create output structure
    output = {
        "version": "1.0",
        "selection_seed": 42,
        "total_prompts": len(prompts),
        "category_counts": {},
        "prompts": prompts,
    }

    # Count by category
    for p in prompts:
        cat = p["category"]
        output["category_counts"][cat] = output["category_counts"].get(cat, 0) + 1

    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Save
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSelected {len(prompts)} prompts:")
    for cat, count in output["category_counts"].items():
        print(f"  - {cat}: {count}")

    print(f"\nSaved to: {OUTPUT_FILE}")

    # Preview first few prompts per category
    print("\n--- Preview ---")
    for cat in output["category_counts"]:
        cat_prompts = [p for p in prompts if p["category"] == cat]
        print(f"\n{cat.upper()}:")
        for p in cat_prompts[:2]:
            print(f"  [{p['id']}] {p['text'][:60]}...")


if __name__ == "__main__":
    main()

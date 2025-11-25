#!/usr/bin/env python3
"""
Reselect prompts to maximize use of existing Hegelion data.
Prioritizes prompts that already have Hegelion responses.
"""

import json
from pathlib import Path
from collections import defaultdict

# Paths
SCRIPT_DIR = Path(__file__).parent
BENCHMARKS_DIR = SCRIPT_DIR.parent
HEGELION_DATA = BENCHMARKS_DIR.parent / "hegelion-data" / "data" / "hegelion_dialectical_500.jsonl"
PROMPTS_FILE = BENCHMARKS_DIR.parent / "hegelion-data" / "prompts" / "hegelion_prompts_500.txt"
OUTPUT_FILE = BENCHMARKS_DIR / "data" / "selected_prompts.json"

# Category mapping from prompts file
CATEGORY_RANGES = {
    "philosophy": [(2, 21), (24, 43)],  # Philosophy & Metaphysics + Ethics
    "policy": [(46, 65)],  # Political Philosophy
    "science": [(68, 87)],  # Science & Epistemology
    "creative": [(200, 219)],  # Art & Aesthetics
    "factual": [(266, 285), (288, 307)],  # Biology & History (simpler questions)
}

TARGET_COUNTS = {
    "philosophy": 15,
    "policy": 10,
    "science": 10,
    "creative": 10,
    "factual": 5,
}


def load_existing_hegelion():
    """Load existing Hegelion data as set of queries."""
    existing = {}
    with open(HEGELION_DATA, "r") as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                query = data["query"].strip()
                existing[query.lower()] = {
                    "query": query,
                    "thesis": data.get("thesis", ""),
                    "antithesis": data.get("antithesis", ""),
                    "synthesis": data.get("synthesis", ""),
                }
            except Exception:
                continue
    return existing


def load_all_prompts():
    """Load all prompts from the prompts file."""
    prompts = []
    with open(PROMPTS_FILE, "r") as f:
        for i, line in enumerate(f, 1):
            text = line.strip()
            if text and not text.startswith("#"):
                prompts.append({"line": i, "text": text})
    return prompts


def categorize_prompt(line_num):
    """Determine category based on line number."""
    for category, ranges in CATEGORY_RANGES.items():
        for start, end in ranges:
            if start <= line_num <= end:
                return category
    return None


def main():
    print("Loading existing Hegelion data...")
    existing = load_existing_hegelion()
    print(f"Found {len(existing)} existing Hegelion responses")

    print("\nLoading all prompts...")
    all_prompts = load_all_prompts()
    print(f"Found {len(all_prompts)} total prompts")

    # Categorize and check for existing data
    categorized = defaultdict(list)
    for p in all_prompts:
        category = categorize_prompt(p["line"])
        if category:
            has_existing = p["text"].lower() in existing
            categorized[category].append(
                {
                    "line": p["line"],
                    "text": p["text"],
                    "has_existing": has_existing,
                }
            )

    print("\n--- Available prompts by category ---")
    for cat, prompts in categorized.items():
        with_data = sum(1 for p in prompts if p["has_existing"])
        print(f"  {cat}: {len(prompts)} total, {with_data} with existing Hegelion data")

    # Select prompts - prioritize those with existing data
    selected = []
    prompt_id = 1

    for category, target in TARGET_COUNTS.items():
        available = categorized[category]

        # Sort: existing data first
        available.sort(key=lambda p: (not p["has_existing"], p["line"]))

        chosen = available[:target]

        with_data = sum(1 for p in chosen if p["has_existing"])
        print(f"\n{category}: Selected {len(chosen)}/{target}, {with_data} with existing data")

        for p in chosen:
            selected.append(
                {
                    "id": f"P{prompt_id:03d}",
                    "category": category,
                    "text": p["text"],
                    "source_line": p["line"],
                    "has_existing_hegelion": p["has_existing"],
                }
            )
            prompt_id += 1

    # Summary
    total_with_existing = sum(1 for p in selected if p["has_existing_hegelion"])
    print("\n=== SUMMARY ===")
    print(f"Total selected: {len(selected)}")
    print(f"With existing Hegelion data: {total_with_existing}")
    print(f"Need to generate: {len(selected) - total_with_existing}")

    # Save
    output = {
        "version": "2.0",
        "selection_strategy": "prioritize_existing_hegelion_data",
        "total_prompts": len(selected),
        "with_existing_data": total_with_existing,
        "needs_generation": len(selected) - total_with_existing,
        "category_counts": {cat: TARGET_COUNTS[cat] for cat in TARGET_COUNTS},
        "prompts": selected,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {OUTPUT_FILE}")

    # Show which need generation
    needs_gen = [p for p in selected if not p["has_existing_hegelion"]]
    if needs_gen:
        print(f"\n--- Prompts needing Hegelion generation ({len(needs_gen)}) ---")
        for p in needs_gen:
            print(f"  [{p['id']}] {p['category']}: {p['text'][:50]}...")


if __name__ == "__main__":
    main()

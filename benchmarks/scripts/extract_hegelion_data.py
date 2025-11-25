#!/usr/bin/env python3
"""Extract existing Hegelion responses from JSONL and save to benchmark format."""

import json
from pathlib import Path

# Paths
JSONL_PATH = Path("/Volumes/VIXinSSD/hegelion/hegelion-data/data/hegelion_dialectical_500.jsonl")
PROMPTS_PATH = Path("/Volumes/VIXinSSD/hegelion/benchmarks/data/selected_prompts.json")
OUTPUT_DIR = Path("/Volumes/VIXinSSD/hegelion/benchmarks/data/responses/hegelion")

# Dry run prompt IDs
DRY_RUN_IDS = {"P001", "P016", "P026", "P036", "P046"}


def load_jsonl(path: Path) -> dict[str, dict]:
    """Load JSONL and index by query text."""
    data = {}
    errors = 0
    with open(path) as f:
        for i, line in enumerate(f):
            try:
                entry = json.loads(line)
                query = entry["query"]
                # Keep the first occurrence for each query
                if query not in data:
                    data[query] = entry
            except json.JSONDecodeError:
                errors += 1
                print(f"  [WARN] Skipping malformed line {i+1}")
    if errors:
        print(f"  Skipped {errors} malformed lines")
    return data


def load_prompts(path: Path, dry_run_only: bool = True) -> list[dict]:
    """Load selected prompts."""
    with open(path) as f:
        data = json.load(f)

    prompts = data["prompts"]
    if dry_run_only:
        prompts = [p for p in prompts if p["id"] in DRY_RUN_IDS]
    return prompts


def extract_and_save(prompts: list[dict], jsonl_data: dict[str, dict], output_dir: Path):
    """Extract matching Hegelion responses and save to individual JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted = 0
    missing = []

    for prompt in prompts:
        prompt_id = prompt["id"]
        query = prompt["text"]

        if query in jsonl_data:
            entry = jsonl_data[query]

            # Create output format
            output = {
                "prompt_id": prompt_id,
                "query": query,
                "category": prompt["category"],
                "method": "hegelion",
                "thesis": entry["thesis"],
                "antithesis": entry["antithesis"],
                "synthesis": entry["synthesis"],
                "contradictions": entry.get("contradictions", []),
                "research_proposals": entry.get("research_proposals", []),
                "combined_response": f"""# DIALECTICAL ANALYSIS: {query}

## THESIS
{entry["thesis"]}

## ANTITHESIS
{entry["antithesis"]}

## SYNTHESIS
{entry["synthesis"]}""",
            }

            # Save to file
            output_path = output_dir / f"{prompt_id}.json"
            with open(output_path, "w") as f:
                json.dump(output, f, indent=2)

            print(f"[OK] {prompt_id}: {query[:50]}...")
            extracted += 1
        else:
            print(f"[MISSING] {prompt_id}: {query[:50]}...")
            missing.append(prompt_id)

    print(f"\nExtracted: {extracted}")
    print(f"Missing: {len(missing)}")
    if missing:
        print(f"Missing IDs: {missing}")

    return extracted, missing


if __name__ == "__main__":
    import sys

    dry_run_only = "--all" not in sys.argv

    if dry_run_only:
        print("=== DRY RUN: Extracting 5 prompts ===\n")
    else:
        print("=== FULL RUN: Extracting all prompts with existing data ===\n")

    # Load data
    print("Loading JSONL data...")
    jsonl_data = load_jsonl(JSONL_PATH)
    print(f"Found {len(jsonl_data)} unique queries in JSONL\n")

    print("Loading selected prompts...")
    prompts = load_prompts(PROMPTS_PATH, dry_run_only=dry_run_only)
    if not dry_run_only:
        # Filter to only those with existing data
        prompts = [p for p in prompts if p["has_existing_hegelion"]]
    print(f"Processing {len(prompts)} prompts\n")

    # Extract and save
    extract_and_save(prompts, jsonl_data, OUTPUT_DIR)

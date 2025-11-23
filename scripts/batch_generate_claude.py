#!/usr/bin/env python3
"""
Batch Hegelian Dialectical Sample Generator using Claude Code
This script helps generate samples in batches by reading prompts and formatting them for generation.
"""

import json
import sys
from pathlib import Path


def load_prompts(prompt_file, start=0, limit=10):
    """Load a batch of prompts"""
    with open(prompt_file, "r") as f:
        prompts = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    return prompts[start : start + limit]


def count_existing(output_file):
    """Count how many samples already exist"""
    if not Path(output_file).exists():
        return 0

    with open(output_file, "r") as f:
        return sum(1 for line in f if line.strip())


def main():
    prompt_file = "hegelion_prompts_500.txt"
    output_file = "data/hegelion_dialectical_500.jsonl"

    existing = count_existing(output_file)
    print(f"✓ Existing samples: {existing}")

    # Get next batch
    batch_size = 10
    prompts = load_prompts(prompt_file, start=existing, limit=batch_size)

    print(f"📋 Next {len(prompts)} prompts to generate:\n")
    for i, prompt in enumerate(prompts, existing + 1):
        print(f"{i}. {prompt}")

    print(f"\n💡 Generate dialectical samples for these prompts and append to:")
    print(f"   {output_file}")
    print(f"\n🎯 Target: {500 - existing} more samples needed to reach 500")


if __name__ == "__main__":
    main()

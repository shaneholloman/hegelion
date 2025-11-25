#!/usr/bin/env python3
"""
Step 2: Generate responses for all prompts using 3 methods.

Methods:
- Raw Baseline: Simple single prompt (1 call)
- Enhanced Baseline: Structured thinking prompt (1 call, ~3x tokens)
- Hegelion Basic: Full dialectic (3 calls)

Supports:
- Resume from checkpoint
- Dry-run mode (5 prompts)
- Token estimation
"""

import asyncio
import json
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent to path for hegelion imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hegelion import run_dialectic
from hegelion.core.config import get_backend_from_env, resolve_backend_for_model

# Paths
SCRIPT_DIR = Path(__file__).parent
BENCHMARKS_DIR = SCRIPT_DIR.parent
DATA_DIR = BENCHMARKS_DIR / "data"
PROMPTS_FILE = DATA_DIR / "selected_prompts.json"
RESPONSES_DIR = DATA_DIR / "responses"
CHECKPOINT_FILE = RESPONSES_DIR / "checkpoint.json"

# Model configuration
MODEL = "claude-sonnet-4-5-20250929"

# Enhanced baseline system prompt
ENHANCED_SYSTEM = """You are a rigorous analytical thinker. For every question:
1. First, articulate the strongest position on the topic
2. Then, identify the most compelling counterarguments and tensions
3. Finally, synthesize a nuanced conclusion that transcends simple for/against framing

Be thorough. Acknowledge uncertainty. Identify where reasonable people disagree."""


@dataclass
class ResponseResult:
    """Result from generating a single response."""

    prompt_id: str
    method: str
    response_text: str
    estimated_tokens: int
    call_count: int
    duration_ms: float
    timestamp: str

    # Hegelion-specific fields
    thesis: Optional[str] = None
    antithesis: Optional[str] = None
    synthesis: Optional[str] = None


@dataclass
class Checkpoint:
    """Tracks generation progress."""

    run_id: str
    started_at: str
    last_updated: str
    raw_completed: List[str]
    enhanced_completed: List[str]
    hegelion_completed: List[str]
    total_estimated_tokens: int
    total_call_count: int
    is_dry_run: bool


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 characters per token."""
    return len(text) // 4


def load_checkpoint() -> Optional[Checkpoint]:
    """Load checkpoint if exists."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, "r") as f:
            data = json.load(f)
            return Checkpoint(**data)
    return None


def save_checkpoint(checkpoint: Checkpoint):
    """Save checkpoint to disk."""
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(asdict(checkpoint), f, indent=2)


def save_response(result: ResponseResult, method: str):
    """Save a single response to disk."""
    method_dir = RESPONSES_DIR / method
    method_dir.mkdir(parents=True, exist_ok=True)

    filepath = method_dir / f"{result.prompt_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(asdict(result), f, indent=2, ensure_ascii=False)


def load_prompts() -> List[Dict]:
    """Load selected prompts."""
    with open(PROMPTS_FILE, "r") as f:
        data = json.load(f)
    return data["prompts"]


async def generate_raw_baseline(backend, prompt_id: str, prompt_text: str) -> ResponseResult:
    """Generate raw baseline response (simple prompt)."""
    start = time.time()

    response = await backend.generate(
        prompt=prompt_text,
        max_tokens=1500,
        temperature=0.7,
    )

    duration_ms = (time.time() - start) * 1000

    return ResponseResult(
        prompt_id=prompt_id,
        method="raw",
        response_text=response,
        estimated_tokens=estimate_tokens(response),
        call_count=1,
        duration_ms=duration_ms,
        timestamp=datetime.utcnow().isoformat(),
    )


async def generate_enhanced_baseline(backend, prompt_id: str, prompt_text: str) -> ResponseResult:
    """Generate enhanced baseline response (structured thinking)."""
    start = time.time()

    response = await backend.generate(
        prompt=prompt_text,
        max_tokens=3072,
        temperature=0.7,
        system_prompt=ENHANCED_SYSTEM,
    )

    duration_ms = (time.time() - start) * 1000

    return ResponseResult(
        prompt_id=prompt_id,
        method="enhanced",
        response_text=response,
        estimated_tokens=estimate_tokens(response),
        call_count=1,
        duration_ms=duration_ms,
        timestamp=datetime.utcnow().isoformat(),
    )


async def generate_hegelion(prompt_id: str, prompt_text: str) -> ResponseResult:
    """Generate Hegelion response (3-call dialectic)."""
    start = time.time()

    result = await run_dialectic(
        prompt_text,
        model=MODEL,
        debug=True,
        use_cache=False,  # Fresh generation for benchmark
    )

    duration_ms = (time.time() - start) * 1000

    # Combine for full response (truncate RESEARCH_PROPOSAL sections)
    full_response = f"## Thesis\n{result.thesis}\n\n## Antithesis\n{result.antithesis}\n\n## Synthesis\n{result.synthesis}"

    # Truncate research proposal markers if present
    full_response = re.sub(r"\nRESEARCH_PROPOSAL:.*$", "", full_response, flags=re.MULTILINE)
    full_response = re.sub(r"\nTESTABLE_PREDICTION:.*$", "", full_response, flags=re.MULTILINE)

    return ResponseResult(
        prompt_id=prompt_id,
        method="hegelion",
        response_text=full_response,
        estimated_tokens=estimate_tokens(full_response),
        call_count=3,  # thesis + antithesis + synthesis
        duration_ms=duration_ms,
        timestamp=datetime.utcnow().isoformat(),
        thesis=result.thesis,
        antithesis=result.antithesis,
        synthesis=result.synthesis,
    )


async def run_generation(dry_run: bool = False, resume: bool = True):
    """Main generation loop."""
    print("=" * 60)
    print("MVB Response Generation")
    print("=" * 60)

    # Load prompts
    prompts = load_prompts()
    if dry_run:
        # Take 1 prompt per category for dry run
        categories = {}
        for p in prompts:
            if p["category"] not in categories:
                categories[p["category"]] = p
        prompts = list(categories.values())[:5]
        print(f"\nDRY RUN: Using {len(prompts)} prompts (1 per category)")
    else:
        print(f"\nFull run: {len(prompts)} prompts")

    # Initialize or load checkpoint
    checkpoint = None
    if resume:
        checkpoint = load_checkpoint()
        if checkpoint and checkpoint.is_dry_run != dry_run:
            print("WARNING: Checkpoint mode mismatch. Starting fresh.")
            checkpoint = None

    if checkpoint is None:
        checkpoint = Checkpoint(
            run_id=datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
            started_at=datetime.utcnow().isoformat(),
            last_updated=datetime.utcnow().isoformat(),
            raw_completed=[],
            enhanced_completed=[],
            hegelion_completed=[],
            total_estimated_tokens=0,
            total_call_count=0,
            is_dry_run=dry_run,
        )
    else:
        print(f"\nResuming from checkpoint: {checkpoint.run_id}")
        print(f"  Raw completed: {len(checkpoint.raw_completed)}")
        print(f"  Enhanced completed: {len(checkpoint.enhanced_completed)}")
        print(f"  Hegelion completed: {len(checkpoint.hegelion_completed)}")

    # Get backend for baselines
    backend = resolve_backend_for_model(MODEL)

    # Process each prompt
    for i, prompt in enumerate(prompts):
        pid = prompt["id"]
        text = prompt["text"]
        category = prompt["category"]

        print(f"\n[{i+1}/{len(prompts)}] {pid} ({category})")
        print(f"  Prompt: {text[:60]}...")

        # Generate Raw Baseline
        if pid not in checkpoint.raw_completed:
            print("  [RAW] Generating...", end=" ", flush=True)
            try:
                result = await generate_raw_baseline(backend, pid, text)
                save_response(result, "raw")
                checkpoint.raw_completed.append(pid)
                checkpoint.total_estimated_tokens += result.estimated_tokens
                checkpoint.total_call_count += result.call_count
                checkpoint.last_updated = datetime.utcnow().isoformat()
                save_checkpoint(checkpoint)
                print(f"Done ({result.duration_ms:.0f}ms, ~{result.estimated_tokens} tokens)")
            except Exception as e:
                print(f"ERROR: {e}")
        else:
            print("  [RAW] Skipped (already done)")

        # Generate Enhanced Baseline
        if pid not in checkpoint.enhanced_completed:
            print("  [ENHANCED] Generating...", end=" ", flush=True)
            try:
                result = await generate_enhanced_baseline(backend, pid, text)
                save_response(result, "enhanced")
                checkpoint.enhanced_completed.append(pid)
                checkpoint.total_estimated_tokens += result.estimated_tokens
                checkpoint.total_call_count += result.call_count
                checkpoint.last_updated = datetime.utcnow().isoformat()
                save_checkpoint(checkpoint)
                print(f"Done ({result.duration_ms:.0f}ms, ~{result.estimated_tokens} tokens)")
            except Exception as e:
                print(f"ERROR: {e}")
        else:
            print("  [ENHANCED] Skipped (already done)")

        # Generate Hegelion
        if pid not in checkpoint.hegelion_completed:
            print("  [HEGELION] Generating...", end=" ", flush=True)
            try:
                result = await generate_hegelion(pid, text)
                save_response(result, "hegelion")
                checkpoint.hegelion_completed.append(pid)
                checkpoint.total_estimated_tokens += result.estimated_tokens
                checkpoint.total_call_count += result.call_count
                checkpoint.last_updated = datetime.utcnow().isoformat()
                save_checkpoint(checkpoint)
                print(
                    f"Done ({result.duration_ms:.0f}ms, ~{result.estimated_tokens} tokens, 3 calls)"
                )
            except Exception as e:
                print(f"ERROR: {e}")
        else:
            print("  [HEGELION] Skipped (already done)")

        # Brief pause between prompts
        await asyncio.sleep(0.5)

    # Summary
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"Run ID: {checkpoint.run_id}")
    print(f"Total prompts: {len(prompts)}")
    print(f"Raw completed: {len(checkpoint.raw_completed)}")
    print(f"Enhanced completed: {len(checkpoint.enhanced_completed)}")
    print(f"Hegelion completed: {len(checkpoint.hegelion_completed)}")
    print(f"Total estimated tokens: {checkpoint.total_estimated_tokens:,}")
    print(f"Total API calls: {checkpoint.total_call_count}")
    print("=" * 60)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate MVB responses")
    parser.add_argument("--dry-run", action="store_true", help="Run with 5 prompts only")
    parser.add_argument("--no-resume", action="store_true", help="Start fresh, ignore checkpoint")
    args = parser.parse_args()

    asyncio.run(
        run_generation(
            dry_run=args.dry_run,
            resume=not args.no_resume,
        )
    )


if __name__ == "__main__":
    main()

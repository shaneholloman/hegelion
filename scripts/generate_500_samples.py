#!/usr/bin/env python3
"""
Hegelian Dataset Generator - Create 500+ High-Quality Dialectical Examples

This script generates complete Hegelian dialectical traces using the Hegelion engine.
Each sample includes:
- Query/Question
- THESIS (initial position)
- ANTITHESIS (contradictions with evidence)
- SYNTHESIS (transcendent resolution with predictions)
- Contradictions list
- Research proposals

Usage:
    # Generate using configured backend (Anthropic, OpenAI, Moonshot, etc.)
    python scripts/generate_500_samples.py --prompts hegelion_prompts_500.txt --output data/hegelion_500_samples.jsonl --limit 500

    # Resume from existing file
    python scripts/generate_500_samples.py --prompts hegelion_prompts_500.txt --output data/hegelion_500_samples.jsonl --limit 500 --resume

    # Use specific provider
    python scripts/generate_500_samples.py --prompts hegelion_prompts_500.txt --output data/hegelion_500_samples.jsonl --limit 500 --provider anthropic --model claude-sonnet-4
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional, List
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from hegelion.core.core import run_dialectic
    from hegelion.core.config import get_config, set_config_value
    from hegelion.core.models import HegelionResult

    HEGELION_AVAILABLE = True
except ImportError:
    HEGELION_AVAILABLE = False
    print("⚠ Hegelion core not available. Install with: pip install -e .")


class HegelianDatasetGenerator:
    def __init__(
        self,
        prompt_file: str,
        output_file: str,
        limit: int = 500,
        resume: bool = True,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4000,
        batch_size: int = 1,
    ):
        self.prompt_file = Path(prompt_file)
        self.output_file = Path(output_file)
        self.limit = limit
        self.resume = resume
        self.provider = provider
        self.model = model
        self.max_tokens = max_tokens
        self.batch_size = batch_size

        self.prompts: List[str] = []
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0

    def load_prompts(self) -> bool:
        """Load prompts from file"""
        if not self.prompt_file.exists():
            print(f"❌ Prompt file not found: {self.prompt_file}")
            return False

        with open(self.prompt_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Filter out comments and empty lines
        self.prompts = [
            line.strip() for line in lines if line.strip() and not line.strip().startswith("#")
        ]

        print(f"✓ Loaded {len(self.prompts)} prompts from {self.prompt_file}")
        return True

    def setup_backend(self):
        """Configure the Hegelion backend"""
        if not HEGELION_AVAILABLE:
            print("❌ Hegelion not available. Cannot configure backend.")
            return False

        config = get_config()

        # Check for API keys
        has_anthropic = bool(config.anthropic_key or os.getenv("ANTHROPIC_API_KEY"))
        has_openai = bool(config.openai_key or os.getenv("OPENAI_API_KEY"))
        has_moonshot = bool(config.moonshot_key or os.getenv("MOONSHOT_API_KEY"))

        print(f"\n🔧 Backend Configuration:")
        print(f"  Anthropic API: {'✓' if has_anthropic else '✗'}")
        print(f"  OpenAI API: {'✓' if has_openai else '✗'}")
        print(f"  Moonshot API: {'✓' if has_moonshot else '✗'}")

        if self.provider:
            set_config_value("provider", self.provider)
            print(f"  Using provider: {self.provider}")

        if self.model:
            set_config_value("model", self.model)
            print(f"  Using model: {self.model}")

        # Auto-detect best available provider
        if not self.provider:
            if has_anthropic:
                set_config_value("provider", "anthropic")
                set_config_value("model", "claude-sonnet-4")
                print(f"  Auto-selected: Anthropic Claude Sonnet 4")
            elif has_moonshot:
                set_config_value("provider", "moonshot")
                set_config_value("model", "moonshot-v1-128k")
                print(f"  Auto-selected: Moonshot Kimi")
            elif has_openai:
                set_config_value("provider", "openai")
                set_config_value("model", "gpt-4")
                print(f"  Auto-selected: OpenAI GPT-4")
            else:
                print(f"\n❌ No API keys found!")
                print(f"Set one of these environment variables:")
                print(f"  export ANTHROPIC_API_KEY='your-key'")
                print(f"  export OPENAI_API_KEY='your-key'")
                print(f"  export MOONSHOT_API_KEY='your-key'")
                return False

        return True

    def resume_from_checkpoint(self) -> int:
        """Check existing output and count processed samples"""
        if not self.resume or not self.output_file.exists():
            return 0

        count = 0
        with open(self.output_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1

        print(f"📍 Resuming from checkpoint: {count} samples already processed")
        return count

    async def generate_dialectic(self, query: str, index: int) -> Optional[dict]:
        """Generate a single dialectical trace"""
        try:
            print(f"\n[{index}/{self.limit}] Generating dialectic for: {query[:60]}...")

            # Run the Hegelion dialectical engine
            result: HegelionResult = await run_dialectic(
                query=query,
                max_tokens_per_phase=self.max_tokens,
                use_search=False,  # Pure reasoning, no web search
            )

            # Format as training data
            entry = {
                "query": query,
                "mode": result.mode,
                "thesis": result.thesis,
                "antithesis": result.antithesis,
                "synthesis": result.synthesis,
                "contradictions": [
                    {"description": c.get("description", ""), "evidence": c.get("evidence", "")}
                    for c in result.contradictions
                ],
                "research_proposals": [
                    {
                        "description": rp.get("description", ""),
                        "testable_prediction": rp.get("testable_prediction", ""),
                    }
                    for rp in result.research_proposals
                ],
                "metadata": result.metadata,
                "trace": {
                    "thesis": result.thesis,
                    "antithesis": result.antithesis,
                    "synthesis": result.synthesis,
                    "contradictions_found": len(result.contradictions),
                    "research_proposals": [
                        f"{rp.get('description', '')} | Prediction: {rp.get('testable_prediction', '')}"
                        for rp in result.research_proposals
                    ],
                    "internal_conflict_score": result.metadata.get("debug", {}).get(
                        "internal_conflict_score", 0
                    ),
                },
            }

            # Validate structure
            if not all([result.thesis, result.antithesis, result.synthesis]):
                print(f"  ⚠ Warning: Incomplete dialectical structure")
                return None

            print(
                f"  ✓ Generated {len(result.thesis)} + {len(result.antithesis)} + {len(result.synthesis)} chars"
            )
            print(
                f"  ✓ Found {len(result.contradictions)} contradictions, {len(result.research_proposals)} research proposals"
            )

            return entry

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None

    async def generate_batch(self, start_idx: int, end_idx: int):
        """Generate a batch of samples"""
        tasks = []
        for i in range(start_idx, min(end_idx, len(self.prompts))):
            if i >= self.limit:
                break
            query = self.prompts[i]
            tasks.append(self.generate_dialectic(query, i + 1))

        # Run batch concurrently (if batch_size > 1)
        if self.batch_size > 1:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Sequential for rate limiting
            results = []
            for task in tasks:
                result = await task
                results.append(result)

        return results

    async def generate_all(self):
        """Generate all samples"""
        if not HEGELION_AVAILABLE:
            print("❌ Hegelion engine not available")
            return False

        if not self.load_prompts():
            return False

        if not self.setup_backend():
            return False

        # Create output directory
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        # Resume from checkpoint
        self.processed_count = self.resume_from_checkpoint()

        print(f"\n{'='*70}")
        print(f"GENERATING {self.limit} HEGELIAN DIALECTICAL SAMPLES")
        print(f"{'='*70}")
        print(f"Output: {self.output_file}")
        print(f"Starting from: {self.processed_count}")
        print(f"Target: {self.limit} samples")
        print(f"{'='*70}\n")

        start_time = datetime.now()

        # Open file for appending
        mode = "a" if self.resume and self.output_file.exists() else "w"
        with open(self.output_file, mode, encoding="utf-8") as f:
            current_idx = self.processed_count

            while current_idx < self.limit and current_idx < len(self.prompts):
                batch_end = min(current_idx + self.batch_size, self.limit, len(self.prompts))

                results = await self.generate_batch(current_idx, batch_end)

                for result in results:
                    if result is not None:
                        f.write(json.dumps(result, ensure_ascii=False) + "\n")
                        f.flush()  # Ensure data is written immediately
                        self.success_count += 1
                    else:
                        self.error_count += 1

                    self.processed_count += 1
                    current_idx += 1

                # Progress update
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = self.processed_count / elapsed if elapsed > 0 else 0
                eta = (self.limit - self.processed_count) / rate if rate > 0 else 0

                print(
                    f"\n📊 Progress: {self.processed_count}/{self.limit} ({self.processed_count/self.limit*100:.1f}%)"
                )
                print(f"   Success: {self.success_count}, Errors: {self.error_count}")
                print(f"   Rate: {rate:.2f} samples/sec, ETA: {eta/60:.1f} minutes")

        duration = (datetime.now() - start_time).total_seconds()

        print(f"\n{'='*70}")
        print(f"✅ GENERATION COMPLETE")
        print(f"{'='*70}")
        print(f"Total samples: {self.success_count}")
        print(f"Errors: {self.error_count}")
        print(f"Time: {duration/60:.1f} minutes")
        print(f"Output: {self.output_file}")
        print(f"\nNext steps:")
        print(f"  1. Validate: python scripts/validate_hegelian_dataset.py {self.output_file}")
        print(f"  2. Clean/dedupe: python scripts/clean_dataset.py {self.output_file}")

        return True


async def main():
    parser = argparse.ArgumentParser(
        description="Generate 500+ Hegelian dialectical training samples"
    )
    parser.add_argument(
        "--prompts", default="hegelion_prompts_500.txt", help="Path to prompt file (one per line)"
    )
    parser.add_argument(
        "--output", default="data/hegelion_500_samples.jsonl", help="Output JSONL file"
    )
    parser.add_argument(
        "--limit", type=int, default=500, help="Number of samples to generate (default: 500)"
    )
    parser.add_argument(
        "--resume", action="store_true", default=True, help="Resume from existing output file"
    )
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai", "moonshot", "auto"],
        help="LLM provider to use",
    )
    parser.add_argument("--model", help="Specific model to use (e.g., claude-sonnet-4, gpt-4)")
    parser.add_argument(
        "--max-tokens", type=int, default=4000, help="Max tokens per dialectical phase"
    )
    parser.add_argument(
        "--batch-size", type=int, default=1, help="Number of samples to generate concurrently"
    )

    args = parser.parse_args()

    generator = HegelianDatasetGenerator(
        prompt_file=args.prompts,
        output_file=args.output,
        limit=args.limit,
        resume=args.resume,
        provider=args.provider,
        model=args.model,
        max_tokens=args.max_tokens,
        batch_size=args.batch_size,
    )

    success = await generator.generate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

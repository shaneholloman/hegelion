#!/usr/bin/env python3
"""
MVB: Minimum Viable Benchmark for Hegelion

Orchestrates the full benchmark pipeline:
1. Select prompts
2. Generate responses (raw, enhanced, hegelion)
3. Evaluate with Opus judge
4. Generate report

Usage:
    python run_mvb.py                    # Full 50-prompt run
    python run_mvb.py --dry-run          # Test with 5 prompts
    python run_mvb.py --step generate    # Run specific step only
    python run_mvb.py --resume           # Resume interrupted run
"""

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent / "scripts"


def run_step(script_name: str, args: list = None, check: bool = True) -> int:
    """Run a benchmark step."""
    script_path = SCRIPT_DIR / script_name
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    print(f"\n{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print("=" * 60)

    result = subprocess.run(cmd)

    if check and result.returncode != 0:
        print(f"\nERROR: {script_name} failed with return code {result.returncode}")
        return result.returncode

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Hegelion Minimum Viable Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Steps:
  select     - Select 50 prompts from the prompt library
  generate   - Generate responses using all 3 methods
  evaluate   - Run blind Opus evaluation
  report     - Generate the benchmark report

Examples:
  python run_mvb.py                    # Full pipeline
  python run_mvb.py --dry-run          # Quick test with 5 prompts
  python run_mvb.py --step generate    # Only run generation
  python run_mvb.py --step evaluate --dry-run  # Quick eval test
        """,
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Run with 5 prompts only (for testing)"
    )

    parser.add_argument(
        "--step",
        choices=["select", "generate", "evaluate", "report", "all"],
        default="all",
        help="Run a specific step (default: all)",
    )

    parser.add_argument(
        "--no-resume", action="store_true", help="Start fresh, don't resume from checkpoints"
    )

    args = parser.parse_args()

    # Build step args
    step_args = []
    if args.dry_run:
        step_args.append("--dry-run")
    if args.no_resume:
        step_args.append("--no-resume")

    print("=" * 60)
    print("HEGELION MINIMUM VIABLE BENCHMARK")
    print("=" * 60)
    print(f"Mode: {'DRY RUN (5 prompts)' if args.dry_run else 'FULL (50 prompts)'}")
    print(f"Step: {args.step}")
    print(f"Resume: {not args.no_resume}")
    print("=" * 60)

    # Run steps
    if args.step in ["select", "all"]:
        ret = run_step("select_prompts.py")
        if ret != 0:
            return ret

    if args.step in ["generate", "all"]:
        ret = run_step("generate_responses.py", step_args)
        if ret != 0:
            return ret

    if args.step in ["evaluate", "all"]:
        ret = run_step("evaluate.py", step_args)
        if ret != 0:
            return ret

    if args.step in ["report", "all"]:
        ret = run_step("generate_report.py")
        if ret != 0:
            return ret

    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)

    if args.step == "all" or args.step == "report":
        report_path = Path(__file__).parent / "results" / "BENCHMARK_REPORT.md"
        if report_path.exists():
            print(f"\nReport: {report_path}")
        else:
            print("\nReport not yet generated.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Step 4: Generate the final benchmark report.

Analyzes evaluation results and produces BENCHMARK_REPORT.md with:
- Win rates (which method wins most often)
- Average scores by criterion
- Category breakdown
- Cost-adjusted efficiency
- Statistical analysis
"""

import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
BENCHMARKS_DIR = SCRIPT_DIR.parent
DATA_DIR = BENCHMARKS_DIR / "data"
EVALUATIONS_DIR = DATA_DIR / "evaluations"
RESULTS_DIR = EVALUATIONS_DIR / "results"
RESPONSES_DIR = DATA_DIR / "responses"
REPORT_FILE = BENCHMARKS_DIR / "results" / "BENCHMARK_REPORT.md"


def load_evaluations() -> List[Dict]:
    """Load all evaluation results."""
    results = []
    if not RESULTS_DIR.exists():
        return results

    for filepath in RESULTS_DIR.glob("*.json"):
        with open(filepath, "r") as f:
            results.append(json.load(f))

    return results


def load_response_stats() -> Dict[str, Dict]:
    """Load token estimates from responses."""
    stats = {"raw": [], "enhanced": [], "hegelion": []}

    for method in stats:
        method_dir = RESPONSES_DIR / method
        if not method_dir.exists():
            continue

        for filepath in method_dir.glob("*.json"):
            with open(filepath, "r") as f:
                data = json.load(f)
                stats[method].append(
                    {
                        "tokens": data.get("estimated_tokens", 0),
                        "calls": data.get("call_count", 1),
                    }
                )

    return stats


def calculate_win_rates(evaluations: List[Dict]) -> Dict[str, Dict]:
    """Calculate win/tie/loss rates for each method."""
    results = {
        "raw": {"wins": 0, "second": 0, "third": 0},
        "enhanced": {"wins": 0, "second": 0, "third": 0},
        "hegelion": {"wins": 0, "second": 0, "third": 0},
    }

    for eval_result in evaluations:
        ranking = eval_result.get("deblinded_ranking", [])
        if len(ranking) >= 3:
            if ranking[0] in results:
                results[ranking[0]]["wins"] += 1
            if ranking[1] in results:
                results[ranking[1]]["second"] += 1
            if ranking[2] in results:
                results[ranking[2]]["third"] += 1

    total = len(evaluations) if evaluations else 1
    for method in results:
        results[method]["win_rate"] = results[method]["wins"] / total
        results[method]["total"] = total

    return results


def calculate_average_scores(evaluations: List[Dict]) -> Dict[str, Dict]:
    """Calculate average scores per method per criterion."""
    # Map response labels to methods
    scores_by_method = {
        "raw": defaultdict(list),
        "enhanced": defaultdict(list),
        "hegelion": defaultdict(list),
    }

    criteria = ["nuance", "counterargument", "epistemic", "synthesis", "insight", "total"]

    for eval_result in evaluations:
        # Get the label mapping from blind pair
        scores = eval_result.get("scores", {})

        # We need to deblind: figure out which response_a/b/c is which method
        # This info is in the evaluation result via deblinded_ranking and ranking
        ranking = eval_result.get("ranking", [])
        deblinded = eval_result.get("deblinded_ranking", [])

        # Build mapping from a/b/c to method
        label_to_method = {}
        for i, label in enumerate(ranking):
            if i < len(deblinded):
                label_to_method[label] = deblinded[i]

        # Also need to handle response_a, response_b, response_c in scores
        for response_key in ["response_a", "response_b", "response_c"]:
            label = response_key.split("_")[1]  # "a", "b", or "c"
            method = label_to_method.get(label)

            if method and method in scores_by_method:
                response_scores = scores.get(response_key, {})
                for criterion in criteria:
                    if criterion in response_scores:
                        scores_by_method[method][criterion].append(response_scores[criterion])

    # Calculate averages
    averages = {}
    for method, criterion_scores in scores_by_method.items():
        averages[method] = {}
        for criterion, values in criterion_scores.items():
            if values:
                averages[method][criterion] = {
                    "mean": sum(values) / len(values),
                    "std": (
                        math.sqrt(
                            sum((x - sum(values) / len(values)) ** 2 for x in values) / len(values)
                        )
                        if len(values) > 1
                        else 0
                    ),
                    "n": len(values),
                }
            else:
                averages[method][criterion] = {"mean": 0, "std": 0, "n": 0}

    return averages


def calculate_category_breakdown(evaluations: List[Dict]) -> Dict[str, Dict]:
    """Calculate win rates by category."""
    category_results = defaultdict(lambda: {"raw": 0, "enhanced": 0, "hegelion": 0, "total": 0})

    for eval_result in evaluations:
        category = eval_result.get("category", "unknown")
        ranking = eval_result.get("deblinded_ranking", [])

        category_results[category]["total"] += 1
        if ranking:
            winner = ranking[0]
            if winner in category_results[category]:
                category_results[category][winner] += 1

    return dict(category_results)


def paired_ttest(scores1: List[float], scores2: List[float]) -> Tuple[float, float]:
    """Simple paired t-test implementation."""
    if len(scores1) != len(scores2) or len(scores1) < 2:
        return 0.0, 1.0

    diffs = [s1 - s2 for s1, s2 in zip(scores1, scores2)]
    n = len(diffs)
    mean_diff = sum(diffs) / n
    var_diff = sum((d - mean_diff) ** 2 for d in diffs) / (n - 1)
    se = math.sqrt(var_diff / n) if var_diff > 0 else 1e-10

    t_stat = mean_diff / se

    # Approximate p-value using normal distribution (rough for small n)
    # For proper p-value, would need scipy.stats.t.sf
    z = abs(t_stat)
    p_approx = 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))

    return t_stat, p_approx


def cohens_d(scores1: List[float], scores2: List[float]) -> float:
    """Calculate Cohen's d effect size."""
    if not scores1 or not scores2:
        return 0.0

    mean1 = sum(scores1) / len(scores1)
    mean2 = sum(scores2) / len(scores2)

    var1 = sum((x - mean1) ** 2 for x in scores1) / len(scores1)
    var2 = sum((x - mean2) ** 2 for x in scores2) / len(scores2)

    pooled_std = math.sqrt((var1 + var2) / 2)
    if pooled_std == 0:
        return 0.0

    return (mean1 - mean2) / pooled_std


def get_total_scores_by_method(evaluations: List[Dict]) -> Dict[str, List[float]]:
    """Extract total scores per method from evaluations."""
    scores = {"raw": [], "enhanced": [], "hegelion": []}

    for eval_result in evaluations:
        ranking = eval_result.get("ranking", [])
        deblinded = eval_result.get("deblinded_ranking", [])
        eval_scores = eval_result.get("scores", {})

        label_to_method = {}
        for i, label in enumerate(ranking):
            if i < len(deblinded):
                label_to_method[label] = deblinded[i]

        for response_key in ["response_a", "response_b", "response_c"]:
            label = response_key.split("_")[1]
            method = label_to_method.get(label)

            if method and method in scores:
                total = eval_scores.get(response_key, {}).get("total", 0)
                if total:
                    scores[method].append(total)

    return scores


def generate_report(evaluations: List[Dict], response_stats: Dict) -> str:
    """Generate the full markdown report."""
    if not evaluations:
        return "# MVB Benchmark Report\n\nNo evaluation results found."

    # Calculate metrics
    win_rates = calculate_win_rates(evaluations)
    avg_scores = calculate_average_scores(evaluations)
    category_breakdown = calculate_category_breakdown(evaluations)
    total_scores = get_total_scores_by_method(evaluations)

    # Statistical tests
    hegelion_vs_enhanced = paired_ttest(
        total_scores.get("hegelion", []), total_scores.get("enhanced", [])
    )
    effect_size = cohens_d(total_scores.get("hegelion", []), total_scores.get("enhanced", []))

    # Calculate cost metrics
    total_tokens = {
        method: sum(s["tokens"] for s in stats) for method, stats in response_stats.items()
    }
    total_calls = {
        method: sum(s["calls"] for s in stats) for method, stats in response_stats.items()
    }

    # Build report
    report = []

    # Header
    report.append("# Hegelion MVB Benchmark Report")
    report.append("")
    report.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    report.append(f"**Total Evaluations:** {len(evaluations)}")
    report.append("")

    # Executive Summary
    report.append("## Executive Summary")
    report.append("")

    hegelion_wins = win_rates["hegelion"]["wins"]
    enhanced_wins = win_rates["enhanced"]["wins"]
    raw_wins = win_rates["raw"]["wins"]
    total = win_rates["hegelion"]["total"]

    if hegelion_wins > enhanced_wins:
        verdict = f"**Hegelion outperforms the enhanced baseline**, winning {hegelion_wins}/{total} comparisons ({win_rates['hegelion']['win_rate']*100:.1f}%) vs enhanced baseline's {enhanced_wins}/{total} ({win_rates['enhanced']['win_rate']*100:.1f}%)."
    elif enhanced_wins > hegelion_wins:
        verdict = f"**The enhanced baseline matches or outperforms Hegelion**, winning {enhanced_wins}/{total} comparisons ({win_rates['enhanced']['win_rate']*100:.1f}%) vs Hegelion's {hegelion_wins}/{total} ({win_rates['hegelion']['win_rate']*100:.1f}%)."
    else:
        verdict = f"**Hegelion and enhanced baseline are tied**, each winning {hegelion_wins}/{total} comparisons ({win_rates['hegelion']['win_rate']*100:.1f}%)."

    report.append(verdict)
    report.append("")

    # Interpret effect size
    if abs(effect_size) < 0.2:
        effect_interp = "negligible"
    elif abs(effect_size) < 0.5:
        effect_interp = "small"
    elif abs(effect_size) < 0.8:
        effect_interp = "medium"
    else:
        effect_interp = "large"

    report.append(f"Effect size (Cohen's d): **{effect_size:.2f}** ({effect_interp})")
    report.append(
        f"Statistical significance: t={hegelion_vs_enhanced[0]:.2f}, p≈{hegelion_vs_enhanced[1]:.3f}"
    )
    report.append("")

    # Win Rates Table
    report.append("## Win Rates")
    report.append("")
    report.append("| Method | 1st Place | 2nd Place | 3rd Place | Win Rate |")
    report.append("|--------|-----------|-----------|-----------|----------|")
    for method in ["hegelion", "enhanced", "raw"]:
        r = win_rates[method]
        report.append(
            f"| {method.capitalize()} | {r['wins']} | {r['second']} | {r['third']} | {r['win_rate']*100:.1f}% |"
        )
    report.append("")

    # Average Scores by Criterion
    report.append("## Average Scores by Criterion")
    report.append("")
    report.append("| Criterion | Raw | Enhanced | Hegelion |")
    report.append("|-----------|-----|----------|----------|")
    criteria = ["nuance", "counterargument", "epistemic", "synthesis", "insight", "total"]
    for criterion in criteria:
        raw_score = avg_scores.get("raw", {}).get(criterion, {}).get("mean", 0)
        enhanced_score = avg_scores.get("enhanced", {}).get(criterion, {}).get("mean", 0)
        hegelion_score = avg_scores.get("hegelion", {}).get(criterion, {}).get("mean", 0)
        report.append(
            f"| {criterion.capitalize()} | {raw_score:.2f} | {enhanced_score:.2f} | {hegelion_score:.2f} |"
        )
    report.append("")

    # Category Breakdown
    report.append("## Category Breakdown")
    report.append("")
    report.append("| Category | Raw Wins | Enhanced Wins | Hegelion Wins | Total |")
    report.append("|----------|----------|---------------|---------------|-------|")
    for category, counts in sorted(category_breakdown.items()):
        report.append(
            f"| {category.capitalize()} | {counts['raw']} | {counts['enhanced']} | {counts['hegelion']} | {counts['total']} |"
        )
    report.append("")

    # Cost Analysis
    report.append("## Cost Analysis (Relative)")
    report.append("")
    report.append("| Method | Total Calls | Est. Tokens | Relative Cost |")
    report.append("|--------|-------------|-------------|---------------|")
    raw_calls = total_calls.get("raw", 1)
    for method in ["raw", "enhanced", "hegelion"]:
        calls = total_calls.get(method, 0)
        tokens = total_tokens.get(method, 0)
        relative = calls / raw_calls if raw_calls > 0 else 0
        report.append(f"| {method.capitalize()} | {calls} | {tokens:,} | {relative:.1f}x |")
    report.append("")

    # Key Insight
    report.append("## Key Insight: Control Theory for LLMs")
    report.append("")
    report.append(
        "This benchmark tests whether **staged intervention** (redirecting the model at each dialectical phase) "
    )
    report.append("adds value over giving the same instructions in a single longer turn.")
    report.append("")
    report.append("- **Enhanced Baseline**: Single prompt asking for thesis, antithesis, synthesis")
    report.append("- **Hegelion**: Three separate calls with forced redirection between phases")
    report.append("")

    hegelion_total = avg_scores.get("hegelion", {}).get("total", {}).get("mean", 0)
    enhanced_total = avg_scores.get("enhanced", {}).get("total", {}).get("mean", 0)
    quality_ratio = hegelion_total / enhanced_total if enhanced_total > 0 else 0
    cost_ratio = (
        total_calls.get("hegelion", 3) / total_calls.get("enhanced", 1)
        if total_calls.get("enhanced", 1) > 0
        else 3
    )

    if quality_ratio > cost_ratio:
        report.append(
            f"**Result**: Hegelion's quality improvement ({quality_ratio:.2f}x) exceeds its cost ratio ({cost_ratio:.1f}x). "
        )
        report.append(
            "The structured dialectic process adds value beyond what can be achieved with a single extended prompt."
        )
    elif quality_ratio > 1:
        report.append(
            f"**Result**: Hegelion shows quality improvement ({quality_ratio:.2f}x) but at higher cost ({cost_ratio:.1f}x). "
        )
        report.append(
            "The value proposition depends on how much quality matters vs. cost constraints."
        )
    else:
        report.append(
            f"**Result**: Enhanced baseline achieves comparable or better quality at lower cost. "
        )
        report.append(
            "The structured dialectic may not provide sufficient benefit for these query types."
        )
    report.append("")

    # Methodology
    report.append("## Methodology")
    report.append("")
    report.append("- **Model**: Claude Sonnet 4.5 for response generation")
    report.append("- **Judge**: Claude Opus 4.5 (blind evaluation, randomized order)")
    report.append(
        "- **Criteria**: Nuance, Counterargument Handling, Epistemic Calibration, Synthesis Quality, Insight Density"
    )
    report.append("- **Scale**: 1-5 per criterion, 5-25 total")
    report.append("")

    # Footer
    report.append("---")
    report.append("")
    report.append("*Generated by Hegelion MVB Benchmark*")

    return "\n".join(report)


def main():
    """Generate the benchmark report."""
    print("=" * 60)
    print("MVB Report Generation")
    print("=" * 60)

    # Load data
    print("\nLoading evaluations...")
    evaluations = load_evaluations()
    print(f"Found {len(evaluations)} evaluation results")

    print("\nLoading response stats...")
    response_stats = load_response_stats()
    for method, stats in response_stats.items():
        print(f"  {method}: {len(stats)} responses")

    # Generate report
    print("\nGenerating report...")
    report = generate_report(evaluations, response_stats)

    # Save report
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, "w") as f:
        f.write(report)

    print(f"\nReport saved to: {REPORT_FILE}")
    print("\n" + "=" * 60)
    print("REPORT PREVIEW")
    print("=" * 60)
    # Print first 50 lines
    for line in report.split("\n")[:50]:
        print(line)
    print("...")


if __name__ == "__main__":
    main()

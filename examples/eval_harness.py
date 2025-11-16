import json
import sys
from collections import Counter
from pathlib import Path


def load_results(path: Path):
    """Yield parsed JSON objects from a JSONL results file."""
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def main(path_str: str):
    """Compute simple aggregate stats over Hegelion JSONL results."""
    path = Path(path_str)
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    total = 0
    total_contradictions = 0
    conflict_scores = []
    by_model = Counter()

    for obj in load_results(path):
        total += 1
        total_contradictions += len(obj.get("contradictions", []))

        meta = obj.get("metadata", {}) or {}
        model = meta.get("backend_model") or "unknown"
        by_model[model] += 1

        debug = meta.get("debug") or {}
        if isinstance(debug, dict) and "internal_conflict_score" in debug:
            conflict_scores.append(float(debug["internal_conflict_score"]))

    print(f"Total queries: {total}")
    print(f"Total contradictions: {total_contradictions}")
    if total:
        print(f"Avg contradictions per query: {total_contradictions / total:.2f}")

    if conflict_scores:
        avg_conflict = sum(conflict_scores) / len(conflict_scores)
        print(f"Avg internal_conflict_score: {avg_conflict:.3f}")

    print("\nQueries per model:")
    for model, count in by_model.most_common():
        print(f"  {model}: {count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python eval_harness.py results.jsonl", file=sys.stderr)
        raise SystemExit(1)
    main(sys.argv[1])


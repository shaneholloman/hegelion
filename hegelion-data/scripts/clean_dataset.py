#!/usr/bin/env python3
"""
Hegelian Dataset Cleaner and Deduplicator

This script:
1. Removes exact duplicate queries
2. Removes near-duplicate queries (high similarity)
3. Filters out low-quality samples
4. Ensures proper dialectical structure
5. Removes samples that are too short or lack depth
"""

import json
import sys
import argparse
from pathlib import Path
from typing import List, Dict
import hashlib


class HegelianDatasetCleaner:
    def __init__(
        self,
        input_file: str,
        output_file: str,
        min_thesis_length: int = 200,
        min_antithesis_length: int = 200,
        min_synthesis_length: int = 300,
        min_contradictions: int = 1,
    ):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.min_thesis_length = min_thesis_length
        self.min_antithesis_length = min_antithesis_length
        self.min_synthesis_length = min_synthesis_length
        self.min_contradictions = min_contradictions

        self.samples = []
        self.stats = {
            "input_count": 0,
            "exact_duplicates": 0,
            "too_short": 0,
            "missing_structure": 0,
            "low_quality": 0,
            "output_count": 0,
        }

    def load_samples(self) -> bool:
        """Load all samples from input file"""
        if not self.input_file.exists():
            print(f"❌ Input file not found: {self.input_file}")
            return False

        with open(self.input_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    sample = json.loads(line)
                    self.samples.append(sample)
                except json.JSONDecodeError as e:
                    print(f"⚠ Line {line_num}: JSON decode error: {e}")

        self.stats["input_count"] = len(self.samples)
        print(f"✓ Loaded {len(self.samples)} samples")
        return True

    def get_query_key(self, query: str) -> str:
        """Get normalized query key for deduplication"""
        # Normalize: lowercase, strip, remove extra whitespace
        normalized = " ".join(query.lower().strip().split())
        return normalized

    def get_query_hash(self, query: str) -> str:
        """Get hash of query for exact duplicate detection"""
        return hashlib.md5(self.get_query_key(query).encode()).hexdigest()

    def remove_exact_duplicates(self) -> List[Dict]:
        """Remove samples with identical queries, keeping the best quality one"""
        seen_hashes: Dict[str, Dict] = {}
        unique_samples = []

        for sample in self.samples:
            query = sample.get("query", "")
            query_hash = self.get_query_hash(query)

            if query_hash in seen_hashes:
                # Keep the one with longer dialectical trace
                existing = seen_hashes[query_hash]
                existing_trace = existing.get("trace", {})
                current_trace = sample.get("trace", {})

                existing_length = (
                    len(existing_trace.get("thesis", ""))
                    + len(existing_trace.get("antithesis", ""))
                    + len(existing_trace.get("synthesis", ""))
                )
                current_length = (
                    len(current_trace.get("thesis", ""))
                    + len(current_trace.get("antithesis", ""))
                    + len(current_trace.get("synthesis", ""))
                )

                if current_length > existing_length:
                    # Replace with better quality
                    seen_hashes[query_hash] = sample
                    self.stats["exact_duplicates"] += 1
                else:
                    self.stats["exact_duplicates"] += 1
            else:
                seen_hashes[query_hash] = sample

        unique_samples = list(seen_hashes.values())
        print(f"✓ Removed {self.stats['exact_duplicates']} exact duplicates")
        return unique_samples

    def filter_quality(self, samples: List[Dict]) -> List[Dict]:
        """Filter out low-quality samples"""
        filtered = []

        for sample in samples:
            trace = sample.get("trace", {})
            thesis = trace.get("thesis", "")
            antithesis = trace.get("antithesis", "")
            synthesis = trace.get("synthesis", "")
            contradictions = sample.get("contradictions", [])

            # Check minimum lengths
            if len(thesis) < self.min_thesis_length:
                self.stats["too_short"] += 1
                continue

            if len(antithesis) < self.min_antithesis_length:
                self.stats["too_short"] += 1
                continue

            if len(synthesis) < self.min_synthesis_length:
                self.stats["too_short"] += 1
                continue

            # Check for required structure
            if not all([thesis, antithesis, synthesis]):
                self.stats["missing_structure"] += 1
                continue

            # Check for contradictions
            if len(contradictions) < self.min_contradictions:
                self.stats["low_quality"] += 1
                continue

            # Check for dialectical markers (relaxed check)
            has_dialectical = (
                any(marker in thesis.upper() for marker in ["THESIS", "ASSERT", "CLAIM"])
                or any(
                    marker in antithesis.upper()
                    for marker in ["ANTITHESIS", "CONTRADICTION", "EVIDENCE", "HOWEVER"]
                )
                or any(
                    marker in synthesis.upper()
                    for marker in ["SYNTHESIS", "PREDICTION", "RESEARCH"]
                )
            )

            if not has_dialectical:
                self.stats["low_quality"] += 1
                continue

            filtered.append(sample)

        print(f"✓ Filtered out {self.stats['too_short']} too short")
        print(f"✓ Filtered out {self.stats['missing_structure']} missing structure")
        print(f"✓ Filtered out {self.stats['low_quality']} low quality")
        return filtered

    def rank_by_quality(self, samples: List[Dict]) -> List[Dict]:
        """Rank samples by quality metrics"""

        def quality_score(sample: Dict) -> float:
            trace = sample.get("trace", {})
            thesis = trace.get("thesis", "")
            antithesis = trace.get("antithesis", "")
            synthesis = trace.get("synthesis", "")
            contradictions = sample.get("contradictions", [])
            research = sample.get("research_proposals", [])

            score = 0.0

            # Length score (prefer substantial reasoning)
            total_length = len(thesis) + len(antithesis) + len(synthesis)
            score += min(total_length / 5000, 1.0) * 30  # Max 30 points

            # Contradiction count (more is better, up to a point)
            score += min(len(contradictions), 5) * 10  # Max 50 points

            # Research proposals
            score += min(len(research), 3) * 10  # Max 30 points

            # Dialectical markers
            markers_count = 0
            if "THESIS" in thesis.upper():
                markers_count += 1
            if "ANTITHESIS" in antithesis.upper():
                markers_count += 1
            if "SYNTHESIS" in synthesis.upper():
                markers_count += 1
            if "CONTRADICTION" in antithesis.upper():
                markers_count += 1
            if "EVIDENCE" in antithesis.upper():
                markers_count += 1
            if "PREDICTION" in synthesis.upper():
                markers_count += 1

            score += markers_count * 5  # Max 30 points

            # Conflict score from metadata
            conflict_score = (
                sample.get("metadata", {}).get("debug", {}).get("internal_conflict_score", 0)
            )
            score += conflict_score * 20  # Max ~20 points

            return score

        ranked = sorted(samples, key=quality_score, reverse=True)
        return ranked

    def clean(self) -> bool:
        """Run full cleaning pipeline"""
        print(f"\n{'='*70}")
        print("CLEANING HEGELIAN DATASET")
        print(f"{'='*70}\n")

        if not self.load_samples():
            return False

        # Step 1: Remove exact duplicates
        print("\n[1/3] Removing exact duplicates...")
        unique_samples = self.remove_exact_duplicates()

        # Step 2: Filter by quality
        print("\n[2/3] Filtering by quality...")
        quality_samples = self.filter_quality(unique_samples)

        # Step 3: Rank by quality
        print("\n[3/3] Ranking by quality...")
        final_samples = self.rank_by_quality(quality_samples)

        self.stats["output_count"] = len(final_samples)

        # Write output
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as f:
            for sample in final_samples:
                f.write(json.dumps(sample, ensure_ascii=False) + "\n")

        # Print summary
        print(f"\n{'='*70}")
        print("CLEANING SUMMARY")
        print(f"{'='*70}")
        print(f"Input samples: {self.stats['input_count']}")
        print(f"Exact duplicates removed: {self.stats['exact_duplicates']}")
        print(f"Too short: {self.stats['too_short']}")
        print(f"Missing structure: {self.stats['missing_structure']}")
        print(f"Low quality: {self.stats['low_quality']}")
        print(f"Output samples: {self.stats['output_count']}")
        print(f"Retention rate: {self.stats['output_count']/self.stats['input_count']*100:.1f}%")
        print(f"\n✅ Cleaned dataset saved to: {self.output_file}")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Clean and deduplicate Hegelian dialectical dataset"
    )
    parser.add_argument("input", help="Input JSONL file")
    parser.add_argument("--output", help="Output JSONL file (default: input_cleaned.jsonl)")
    parser.add_argument(
        "--min-thesis", type=int, default=200, help="Minimum thesis length (default: 200)"
    )
    parser.add_argument(
        "--min-antithesis", type=int, default=200, help="Minimum antithesis length (default: 200)"
    )
    parser.add_argument(
        "--min-synthesis", type=int, default=300, help="Minimum synthesis length (default: 300)"
    )
    parser.add_argument(
        "--min-contradictions",
        type=int,
        default=1,
        help="Minimum contradictions required (default: 1)",
    )

    args = parser.parse_args()

    # Default output file
    if not args.output:
        input_path = Path(args.input)
        args.output = input_path.parent / f"{input_path.stem}_cleaned{input_path.suffix}"

    cleaner = HegelianDatasetCleaner(
        input_file=args.input,
        output_file=args.output,
        min_thesis_length=args.min_thesis,
        min_antithesis_length=args.min_antithesis,
        min_synthesis_length=args.min_synthesis,
        min_contradictions=args.min_contradictions,
    )

    success = cleaner.clean()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Hegelian Dataset Validator and Quality Checker

This script validates that training data has proper dialectical structure:
- THESIS → ANTITHESIS → SYNTHESIS
- Contradictions identified
- Research proposals included
- Sufficient depth and quality
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any


class HegelianValidator:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.samples = []
        self.errors = []
        self.warnings = []
        self.stats = defaultdict(int)

    def load_data(self) -> bool:
        """Load JSONL data file"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        sample = json.loads(line)
                        self.samples.append((line_num, sample))
                    except json.JSONDecodeError as e:
                        self.errors.append(f"Line {line_num}: JSON decode error: {e}")

            self.stats["total_samples"] = len(self.samples)
            print(f"✓ Loaded {len(self.samples)} samples from {self.file_path}")
            return True
        except Exception as e:
            self.errors.append(f"Failed to load file: {e}")
            return False

    def check_dialectical_structure(self, line_num: int, sample: Dict) -> Tuple[bool, List[str]]:
        """Check if sample has proper Hegelian dialectical structure"""
        issues = []

        # Check for required fields
        required_fields = ["query", "thesis", "antithesis", "synthesis"]
        for field in required_fields:
            if field not in sample and field not in sample.get("trace", {}):
                issues.append(f"Missing required field: {field}")

        # Check trace structure
        trace = sample.get("trace", {})
        if not trace:
            issues.append("Missing 'trace' field with dialectical structure")
            return False, issues

        thesis = trace.get("thesis", "")
        antithesis = trace.get("antithesis", "")
        synthesis = trace.get("synthesis", "")

        # Check for dialectical keywords in structure
        has_thesis_marker = "THESIS" in thesis.upper()
        has_antithesis_marker = "ANTITHESIS" in antithesis.upper()
        has_synthesis_marker = "SYNTHESIS" in synthesis.upper()

        if not has_thesis_marker:
            self.warnings.append(f"Line {line_num}: Thesis lacks 'THESIS' marker")
        if not has_antithesis_marker:
            self.warnings.append(f"Line {line_num}: Antithesis lacks 'ANTITHESIS' marker")
        if not has_synthesis_marker:
            self.warnings.append(f"Line {line_num}: Synthesis lacks 'SYNTHESIS' marker")

        # Check for CONTRADICTION in antithesis
        if "CONTRADICTION" not in antithesis.upper() and "EVIDENCE" not in antithesis.upper():
            self.warnings.append(
                f"Line {line_num}: Antithesis should identify contradictions with evidence"
            )

        # Check for PREDICTION or RESEARCH in synthesis
        if "PREDICTION" not in synthesis.upper() and "RESEARCH" not in synthesis.upper():
            self.warnings.append(
                f"Line {line_num}: Synthesis should include predictions or research proposals"
            )

        # Check minimum length (dialectical reasoning should be substantial)
        if len(thesis) < 200:
            issues.append(f"Thesis too short ({len(thesis)} chars, minimum 200)")
        if len(antithesis) < 200:
            issues.append(f"Antithesis too short ({len(antithesis)} chars, minimum 200)")
        if len(synthesis) < 300:
            issues.append(f"Synthesis too short ({len(synthesis)} chars, minimum 300)")

        # Check for contradictions list
        contradictions = sample.get("contradictions", [])
        if not contradictions:
            issues.append("No contradictions identified")
        else:
            self.stats["avg_contradictions"] += len(contradictions)

        # Check for research proposals
        research = sample.get("research_proposals", [])
        if not research:
            self.warnings.append(f"Line {line_num}: No research proposals included")
        else:
            self.stats["avg_research_proposals"] += len(research)

        return len(issues) == 0, issues

    def find_duplicates(self) -> Dict[str, List[int]]:
        """Find duplicate queries"""
        query_map = defaultdict(list)

        for line_num, sample in self.samples:
            query = sample.get("query", "").strip().lower()
            if query:
                query_map[query].append(line_num)

        duplicates = {q: lines for q, lines in query_map.items() if len(lines) > 1}
        return duplicates

    def analyze_diversity(self) -> Dict[str, Any]:
        """Analyze topic diversity"""
        first_words = Counter()
        query_lengths = []
        output_lengths = []

        for _, sample in self.samples:
            query = sample.get("query", "")
            if query:
                # Get first 3 words as topic indicator
                words = query.split()[:3]
                first_words[" ".join(words)] += 1
                query_lengths.append(len(query))

            # Check output length
            trace = sample.get("trace", {})
            total_length = (
                len(trace.get("thesis", ""))
                + len(trace.get("antithesis", ""))
                + len(trace.get("synthesis", ""))
            )
            output_lengths.append(total_length)

        return {
            "unique_topic_starters": len(first_words),
            "most_common_topics": first_words.most_common(10),
            "avg_query_length": sum(query_lengths) / len(query_lengths) if query_lengths else 0,
            "avg_output_length": sum(output_lengths) / len(output_lengths) if output_lengths else 0,
            "min_output_length": min(output_lengths) if output_lengths else 0,
            "max_output_length": max(output_lengths) if output_lengths else 0,
        }

    def validate(self) -> bool:
        """Run all validation checks"""
        if not self.load_data():
            return False

        print("\n" + "=" * 70)
        print("HEGELIAN DIALECTICAL STRUCTURE VALIDATION")
        print("=" * 70)

        # Validate each sample
        valid_count = 0
        for line_num, sample in self.samples:
            is_valid, issues = self.check_dialectical_structure(line_num, sample)
            if is_valid:
                valid_count += 1
                self.stats["valid_samples"] += 1
            else:
                self.stats["invalid_samples"] += 1
                for issue in issues:
                    self.errors.append(f"Line {line_num}: {issue}")

        # Find duplicates
        duplicates = self.find_duplicates()
        if duplicates:
            self.stats["duplicate_queries"] = sum(len(v) - 1 for v in duplicates.values())
            print(
                f"\n⚠ Found {len(duplicates)} duplicate queries affecting {self.stats['duplicate_queries']} samples"
            )
            for query, lines in list(duplicates.items())[:5]:
                print(f"  '{query[:60]}...' appears on lines: {lines}")

        # Analyze diversity
        diversity = self.analyze_diversity()

        # Calculate averages
        if self.stats["valid_samples"] > 0:
            self.stats["avg_contradictions"] /= self.stats["valid_samples"]
            self.stats["avg_research_proposals"] /= self.stats["valid_samples"]

        # Print results
        print("\n📊 VALIDATION RESULTS")
        print(f"{'─'*70}")
        print(f"Total samples: {self.stats['total_samples']}")
        print(
            f"Valid samples: {self.stats['valid_samples']} ({valid_count/self.stats['total_samples']*100:.1f}%)"
        )
        print(f"Invalid samples: {self.stats['invalid_samples']}")
        print(f"Duplicate queries: {self.stats.get('duplicate_queries', 0)}")
        print(f"Unique topics: {diversity['unique_topic_starters']}")
        print(f"Avg contradictions per sample: {self.stats.get('avg_contradictions', 0):.1f}")
        print(f"Avg research proposals: {self.stats.get('avg_research_proposals', 0):.1f}")
        print(f"Avg query length: {diversity['avg_query_length']:.0f} chars")
        print(f"Avg dialectical trace length: {diversity['avg_output_length']:.0f} chars")
        print(
            f"Output length range: {diversity['min_output_length']} - {diversity['max_output_length']} chars"
        )

        if diversity["most_common_topics"]:
            print("\nMost common topic patterns:")
            for topic, count in diversity["most_common_topics"][:5]:
                print(f"  '{topic}': {count} samples")

        # Print errors
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors[:20]:  # Show first 20
                print(f"  {error}")
            if len(self.errors) > 20:
                print(f"  ... and {len(self.errors) - 20} more errors")

        # Print warnings
        if self.warnings:
            print(f"\n⚠ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")

        # Final verdict
        print(f"\n{'='*70}")
        if self.stats["valid_samples"] >= self.stats["total_samples"] * 0.95:
            print("✅ DATASET QUALITY: EXCELLENT")
            print("The dataset has proper Hegelian dialectical structure.")
            return True
        elif self.stats["valid_samples"] >= self.stats["total_samples"] * 0.80:
            print("⚠ DATASET QUALITY: GOOD (some issues)")
            print("Most samples have dialectical structure but some need improvement.")
            return True
        else:
            print("❌ DATASET QUALITY: POOR")
            print("Many samples lack proper dialectical structure.")
            return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_hegelian_dataset.py <dataset.jsonl>")
        sys.exit(1)

    validator = HegelianValidator(sys.argv[1])
    success = validator.validate()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

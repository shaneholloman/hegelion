#!/usr/bin/env python3
"""
Direct Kimi API Generator for Hegelian Dialectical Samples

Uses Kimi's OpenAI-compatible API to generate dialectical reasoning traces.
"""

import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, List
import sys

# Try to import OpenAI
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("⚠ OpenAI package not found. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "openai", "-q"], check=True)
    from openai import OpenAI
    HAS_OPENAI = True

# Hegelian Dialectical System Prompt
HEGELIAN_SYSTEM_PROMPT = """You are a master of Hegelian dialectical reasoning. For every question, you MUST follow this exact structure:

**THESIS**: Present the strongest initial position or answer. Be comprehensive and well-reasoned.

**ANTITHESIS**: Critically challenge the thesis. Identify contradictions, flaws, edge cases, and opposing evidence. Format each contradiction as:
CONTRADICTION: [Name of the contradiction]
EVIDENCE: [Specific evidence showing why this is problematic]

**SYNTHESIS**: Resolve the tension between thesis and antithesis. Create a transcendent view that incorporates valid insights from both. Include:
- How the contradiction is resolved
- PREDICTION [N]: Specific testable predictions that follow from this synthesis
- RESEARCH_PROPOSAL: Concrete research that would test this synthesis

Your goal is to demonstrate deep, rigorous reasoning that moves beyond simple pro/con arguments to genuine philosophical synthesis."""

HEGELIAN_USER_TEMPLATE = """Apply rigorous Hegelian dialectical analysis to this question:

{query}

Structure your response with clear THESIS, ANTITHESIS, and SYNTHESIS sections. In the antithesis, identify specific contradictions with evidence. In the synthesis, propose testable predictions and research directions."""


class KimiDialecticalGenerator:
    def __init__(self, api_key: str, base_url: str = "https://api.kimi.com/coding/v1", model: str = "kimi-for-coding"):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
        self.stats = {
            'total': 0,
            'success': 0,
            'errors': 0,
            'total_tokens': 0,
        }

    def generate_dialectic(self, query: str, max_retries: int = 3) -> Optional[Dict]:
        """Generate a single dialectical trace"""
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": HEGELIAN_SYSTEM_PROMPT},
                        {"role": "user", "content": HEGELIAN_USER_TEMPLATE.format(query=query)}
                    ],
                    temperature=0.8,
                    max_tokens=6000,
                )

                content = response.choices[0].message.content

                # Track usage
                if hasattr(response, 'usage'):
                    self.stats['total_tokens'] += response.usage.total_tokens

                # Parse the response
                result = self.parse_dialectic(query, content)

                if result:
                    self.stats['success'] += 1
                    return result
                else:
                    print(f"  ⚠ Failed to parse response (attempt {attempt + 1}/{max_retries})")

            except Exception as e:
                print(f"  ❌ Error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff

        self.stats['errors'] += 1
        return None

    def parse_dialectic(self, query: str, content: str) -> Optional[Dict]:
        """Parse the dialectical response into structured format"""
        # Extract sections
        thesis = ""
        antithesis = ""
        synthesis = ""

        content_upper = content.upper()

        # Find THESIS
        if "THESIS" in content_upper:
            thesis_start = content_upper.find("THESIS")
            antithesis_start = content_upper.find("ANTITHESIS", thesis_start)
            if antithesis_start > thesis_start:
                thesis = content[thesis_start:antithesis_start].strip()
            else:
                # No antithesis found, take everything after THESIS
                thesis = content[thesis_start:].strip()

        # Find ANTITHESIS
        if "ANTITHESIS" in content_upper:
            antithesis_start = content_upper.find("ANTITHESIS")
            synthesis_start = content_upper.find("SYNTHESIS", antithesis_start)
            if synthesis_start > antithesis_start:
                antithesis = content[antithesis_start:synthesis_start].strip()
            else:
                # No synthesis found, take rest
                antithesis = content[antithesis_start:].strip()

        # Find SYNTHESIS
        if "SYNTHESIS" in content_upper:
            synthesis_start = content_upper.find("SYNTHESIS")
            synthesis = content[synthesis_start:].strip()

        # If we couldn't find sections, use the whole content as synthesis
        if not thesis and not antithesis and not synthesis:
            synthesis = content

        # Extract contradictions
        contradictions = []
        if "CONTRADICTION:" in antithesis.upper():
            lines = antithesis.split('\n')
            current_contradiction = None
            current_evidence = None

            for line in lines:
                line_upper = line.upper()
                if "CONTRADICTION:" in line_upper:
                    if current_contradiction:
                        contradictions.append({
                            "description": current_contradiction,
                            "evidence": current_evidence or ""
                        })
                    current_contradiction = line.split(":", 1)[1].strip() if ":" in line else line
                    current_evidence = None
                elif "EVIDENCE:" in line_upper:
                    current_evidence = line.split(":", 1)[1].strip() if ":" in line else line

            # Add last one
            if current_contradiction:
                contradictions.append({
                    "description": current_contradiction,
                    "evidence": current_evidence or ""
                })

        # Extract research proposals
        research_proposals = []
        if "RESEARCH_PROPOSAL:" in synthesis.upper() or "RESEARCH PROPOSAL:" in synthesis.upper():
            lines = synthesis.split('\n')
            for i, line in enumerate(lines):
                line_upper = line.upper()
                if "RESEARCH" in line_upper and "PROPOSAL" in line_upper:
                    proposal_text = line.split(":", 1)[1].strip() if ":" in line else line
                    # Look for prediction in nearby lines
                    prediction = ""
                    for j in range(max(0, i-3), min(len(lines), i+3)):
                        if "PREDICTION" in lines[j].upper():
                            prediction = lines[j].split(":", 1)[1].strip() if ":" in lines[j] else lines[j]
                            break

                    research_proposals.append({
                        "description": proposal_text,
                        "testable_prediction": prediction
                    })

        # If no contradictions found, create at least one
        if not contradictions:
            contradictions.append({
                "description": "Dialectical tension requiring synthesis",
                "evidence": "Thesis and antithesis present opposing viewpoints"
            })

        # If no research proposals, create one
        if not research_proposals:
            research_proposals.append({
                "description": "Empirical validation of synthesis",
                "testable_prediction": "The synthesis can be tested through systematic investigation"
            })

        # Create structured result
        result = {
            "query": query,
            "mode": "synthesis",
            "thesis": thesis,
            "antithesis": antithesis,
            "synthesis": synthesis,
            "contradictions": contradictions,
            "research_proposals": research_proposals,
            "metadata": {
                "source": "kimi-for-coding",
                "backend_provider": "kimi",
                "backend_model": "kimi-for-coding"
            },
            "trace": {
                "thesis": thesis,
                "antithesis": antithesis,
                "synthesis": synthesis,
                "contradictions_found": len(contradictions),
                "research_proposals": [
                    f"{rp['description']} | Prediction: {rp['testable_prediction']}"
                    for rp in research_proposals
                ]
            }
        }

        # Validate minimum quality
        if len(thesis) < 50 or len(antithesis) < 50 or len(synthesis) < 50:
            print(f"  ⚠ Response too short: T={len(thesis)}, A={len(antithesis)}, S={len(synthesis)}")
            return None

        return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate Hegelian dialectical samples using Kimi API")
    parser.add_argument("--prompts", default="hegelion_prompts_500.txt", help="Prompt file")
    parser.add_argument("--output", default="data/hegelion_kimi_500.jsonl", help="Output file")
    parser.add_argument("--limit", type=int, default=500, help="Number of samples to generate")
    parser.add_argument("--resume", action="store_true", default=True, help="Resume from existing")
    parser.add_argument("--api-key", help="Kimi API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--base-url", default="https://api.kimi.com/coding/v1", help="API base URL")
    parser.add_argument("--model", default="kimi-for-coding", help="Model name")

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY") or os.getenv("KIMI_API_KEY")
    if not api_key:
        print("❌ No API key found. Set OPENAI_API_KEY environment variable or use --api-key")
        sys.exit(1)

    print(f"🚀 Kimi Hegelian Dialectical Generator")
    print(f"{'='*70}")
    print(f"API: {args.base_url}")
    print(f"Model: {args.model}")
    print(f"Target: {args.limit} samples")
    print(f"{'='*70}\n")

    # Load prompts
    prompt_file = Path(args.prompts)
    if not prompt_file.exists():
        print(f"❌ Prompt file not found: {prompt_file}")
        sys.exit(1)

    with open(prompt_file, 'r') as f:
        prompts = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith('#')
        ]

    print(f"✓ Loaded {len(prompts)} prompts\n")

    # Check for existing output
    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    processed = 0
    if args.resume and output_file.exists():
        with open(output_file, 'r') as f:
            processed = sum(1 for line in f if line.strip())
        print(f"📍 Resuming from {processed} existing samples\n")

    # Initialize generator
    generator = KimiDialecticalGenerator(api_key, args.base_url, args.model)

    # Generate
    mode = 'a' if args.resume and output_file.exists() else 'w'
    with open(output_file, mode, encoding='utf-8') as f:
        for i in range(processed, min(args.limit, len(prompts))):
            query = prompts[i]

            print(f"\n[{i+1}/{args.limit}] {query[:60]}...")

            result = generator.generate_dialectic(query)

            if result:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
                f.flush()
                print(f"  ✓ Success ({len(result['thesis'])} + {len(result['antithesis'])} + {len(result['synthesis'])} chars)")
            else:
                print(f"  ✗ Failed to generate")

            generator.stats['total'] += 1

            # Progress
            if (i + 1) % 10 == 0:
                print(f"\n📊 Progress: {generator.stats['success']}/{generator.stats['total']} successful")
                print(f"   Total tokens: {generator.stats['total_tokens']:,}")

            # Rate limiting
            time.sleep(1)

    print(f"\n{'='*70}")
    print(f"✅ GENERATION COMPLETE")
    print(f"{'='*70}")
    print(f"Success: {generator.stats['success']}")
    print(f"Errors: {generator.stats['errors']}")
    print(f"Total tokens: {generator.stats['total_tokens']:,}")
    print(f"Output: {output_file}")
    print(f"\nNext: python scripts/validate_hegelian_dataset.py {output_file}")


if __name__ == "__main__":
    main()

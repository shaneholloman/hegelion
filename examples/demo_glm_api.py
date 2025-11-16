#!/usr/bin/env python3
"""Demo script showing Hegelion Python API usage with GLM backend."""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path to allow importing hegelion
sys.path.insert(0, str(Path(__file__).parent.parent))

from hegelion import run_dialectic


def print_section(title: str, width: int = 80) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * width)
    print(f" {title} ".center(width, "="))
    print("=" * width + "\n")


def print_subsection(title: str) -> None:
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---\n")


def format_time(ms: float) -> str:
    """Format milliseconds as human-readable time."""
    if ms < 1000:
        return f"{ms:.2f} ms"
    return f"{ms / 1000:.2f} s"


async def main() -> None:
    """Run the GLM API demo."""
    query = "Can AI be genuinely creative?"
    
    print_section("Hegelion GLM API Demo")
    print(f"Query: {query}\n")
    
    # Check environment variables
    provider = os.getenv("HEGELION_PROVIDER", "openai")
    model = os.getenv("HEGELION_MODEL", "GLM-4.6")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.z.ai/api/coding/paas/v4")
    
    print(f"Backend: {provider}")
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not set in environment!")
        print("Please set it before running this demo.\n")
        sys.exit(1)
    
    print("\n🔄 Running dialectical reasoning...\n")
    
    # Run the dialectic
    result = await run_dialectic(query=query, debug=True)
    
    # Display results
    print_section("Results")
    
    print_subsection("THESIS")
    print(result.thesis)
    
    print_subsection("ANTITHESIS")
    print(result.antithesis)
    
    print_subsection("SYNTHESIS")
    print(result.synthesis)
    
    if result.contradictions:
        print_subsection(f"CONTRADICTIONS ({len(result.contradictions)})")
        for i, contr in enumerate(result.contradictions, 1):
            print(f"\n{i}. {contr.get('description', 'N/A')}")
            if contr.get('evidence'):
                print(f"   Evidence: {contr['evidence']}")
    
    if result.research_proposals:
        print_subsection(f"RESEARCH PROPOSALS ({len(result.research_proposals)})")
        for i, prop in enumerate(result.research_proposals, 1):
            print(f"\n{i}. {prop.get('description', 'N/A')}")
            if prop.get('testable_prediction'):
                print(f"   Testable Prediction: {prop['testable_prediction']}")
    
    # Display metadata
    print_section("Metadata")
    metadata = result.metadata
    print(f"Backend Provider: {metadata.get('backend_provider', 'Unknown')}")
    print(f"Backend Model: {metadata.get('backend_model', 'Unknown')}")
    print(f"Total Time: {format_time(metadata.get('total_time_ms', 0))}")
    
    if metadata.get('debug'):
        debug = metadata['debug']
        if 'internal_conflict_score' in debug:
            print(f"Internal Conflict Score: {debug['internal_conflict_score']:.2f}")
    
    print("\n" + "=" * 80 + "\n")
    print("✅ Demo complete!\n")


if __name__ == "__main__":
    asyncio.run(main())


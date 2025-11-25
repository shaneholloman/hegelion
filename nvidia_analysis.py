#!/usr/bin/env python3
"""
Analyze NVIDIA tweet using Hegelion dialectical reasoning with council support.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/Volumes/VIXinSSD/hegelion')

from hegelion.core.prompt_dialectic import create_single_shot_dialectic_prompt

def main():
    # The NVIDIA tweet to analyze
    nvidia_tweet = """The tweet from @nvidianewsroom on 11/25/25:
"We're delighted by Google's success — they've made great advances in AI and we continue to supply to Google.

NVIDIA is a generation ahead of the industry — it's the only platform that runs every AI model and does it everywhere computing is done.

NVIDIA offers greater performance, versatility, and fungibility than ASICs, which are designed for specific AI frameworks or functions."
"""

    # Create the analysis query with focus areas
    query = f"""Analyze this NVIDIA tweet from a business and legal strategy standpoint:

{nvidia_tweet}

Please consider:
1. Regulatory/antitrust implications
2. Competitive positioning
3. Supply chain leverage
4. Market signaling
5. Legal defensibility of claims

Focus on what strategic pressures or opportunities would prompt such a tweet TODAY (11/25/25 specifically). Pay special attention to the timing - why this message on this particular date?"""

    # Generate the dialectical prompt with council enabled
    prompt = create_single_shot_dialectic_prompt(
        query=query,
        use_search=True,  # Enable search for current context
        use_council=True,  # Enable multi-perspective council critiques
        response_style="sections"  # Get full structured output
    )

    print("=" * 80)
    print("HEGELION DIALECTICAL ANALYSIS PROMPT")
    print("=" * 80)
    print()
    print(prompt)
    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
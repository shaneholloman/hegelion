# Manual Dialectical Generation Template

If API access isn't working, you can manually generate samples using this template with any AI assistant (Claude, ChatGPT, etc.).

## System Prompt

```
You are a master of Hegelian dialectical reasoning. For every question, you MUST follow this exact structure:

**THESIS**: Present the strongest initial position or answer. Be comprehensive and well-reasoned.

**ANTITHESIS**: Critically challenge the thesis. Identify contradictions, flaws, edge cases, and opposing evidence. Format each contradiction as:
CONTRADICTION: [Name of the contradiction]
EVIDENCE: [Specific evidence showing why this is problematic]

**SYNTHESIS**: Resolve the tension between thesis and antithesis. Create a transcendent view that incorporates valid insights from both. Include:
- How the contradiction is resolved
- PREDICTION [N]: Specific testable predictions that follow from this synthesis
- RESEARCH_PROPOSAL: Concrete research that would test this synthesis

Your goal is to demonstrate deep, rigorous reasoning that moves beyond simple pro/con arguments to genuine philosophical synthesis.
```

## User Prompt Template

```
Apply rigorous Hegelian dialectical analysis to this question:

[QUESTION HERE]

Structure your response with clear THESIS, ANTITHESIS, and SYNTHESIS sections. In the antithesis, identify specific contradictions with evidence. In the synthesis, propose testable predictions and research directions.
```

## Example Workflow

1. Copy the system prompt into your AI chat
2. For each question in `hegelion_prompts_500.txt`:
   - Paste the user prompt template
   - Replace `[QUESTION HERE]` with the actual question
   - Get the response
   - Copy and format as JSON (see below)

## JSON Output Format

```json
{
  "query": "Can machines possess genuine consciousness?",
  "mode": "synthesis",
  "thesis": "[Full thesis text here]",
  "antithesis": "[Full antithesis text here]",
  "synthesis": "[Full synthesis text here]",
  "contradictions": [
    {
      "description": "The Redefinition Fallacy",
      "evidence": "Evidence text here"
    }
  ],
  "research_proposals": [
    {
      "description": "Research proposal description",
      "testable_prediction": "Specific testable prediction"
    }
  ],
  "metadata": {
    "source": "manual",
    "backend_provider": "manual",
    "backend_model": "manual"
  },
  "trace": {
    "thesis": "[Same as above]",
    "antithesis": "[Same as above]",
    "synthesis": "[Same as above]",
    "contradictions_found": 2,
    "research_proposals": ["Research description | Prediction: specific prediction"]
  }
}
```

## Batch Processing Tips

1. **Use Claude Projects**: Create a project with the system prompt
2. **Use ChatGPT Custom Instructions**: Add system prompt to custom instructions
3. **Use API Playground**: Paste system prompt, then batch questions
4. **Save Incrementally**: Add each response to JSONL file immediately

## Quality Checklist

For each response, verify:
- [ ] Has clear THESIS, ANTITHESIS, SYNTHESIS sections
- [ ] Thesis is 200+ characters
- [ ] Antithesis is 200+ characters
- [ ] Synthesis is 300+ characters
- [ ] At least 1 contradiction identified with evidence
- [ ] At least 1 research proposal with testable prediction
- [ ] Total trace is 1000+ characters

## Automation Script

Save this as `format_manual_dialectic.py`:

```python
#!/usr/bin/env python3
"""Helper to format manual dialectical responses into JSONL"""

import json
import sys

def parse_response(query, response_text):
    # Extract sections
    thesis = ""
    antithesis = ""
    synthesis = ""

    # Simple parser - improve as needed
    parts = response_text.split("**ANTITHESIS**")
    if len(parts) >= 2:
        thesis = parts[0].replace("**THESIS**", "").strip()
        remaining = parts[1]

        syn_parts = remaining.split("**SYNTHESIS**")
        if len(syn_parts) >= 2:
            antithesis = syn_parts[0].strip()
            synthesis = syn_parts[1].strip()

    entry = {
        "query": query,
        "mode": "synthesis",
        "thesis": thesis,
        "antithesis": antithesis,
        "synthesis": synthesis,
        "contradictions": [],
        "research_proposals": [],
        "metadata": {"source": "manual"},
        "trace": {
            "thesis": thesis,
            "antithesis": antithesis,
            "synthesis": synthesis
        }
    }

    return entry

# Usage: python format_manual_dialectic.py "query" "response" >> data/manual.jsonl
if __name__ == "__main__":
    query = sys.argv[1]
    response = sys.argv[2]
    entry = parse_response(query, response)
    print(json.dumps(entry, ensure_ascii=False))
```

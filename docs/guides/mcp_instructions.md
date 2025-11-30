# Hegelion MCP Instructions for Agents

If you are an AI agent (like Claude, Gemini, or a Cursor agent) connected to the Hegelion MCP server, follow these instructions to use the tools effectively.

## Core Capability
Hegelion is a **Dialectical Reasoning Engine**. It does not just "answer" questions; it forces a structured conflict between ideas to produce a higher-order truth.

## When to Use Hegelion
Use the `run_dialectic` tool when the user asks:
- High-stakes philosophical or strategic questions.
- Questions involving "truth", "bias", or "nuance".
- "Analyze this dialectically."
- "What are the contradictions in X?"
- Any query where a simple summary is insufficient and deep reasoning is required.

## Tool Usage: `run_dialectic`

**Do not** attempt to manually simulate Thesis/Antithesis/Synthesis steps. The tool handles the entire loop internally to ensure strict separation of reasoning states.

1.  **Call the tool:**
    ```json
    {
      "query": "Is open source software sustainable?"
    }
    ```

2.  **Interpret the Output:**
    The tool returns a structured JSON object. You should parse it and present it as follows:
    
    *   **The Synthesis:** This is the primary answer. Present this first or most prominently.
    *   **The Conflict:** Briefly explain *why* the Thesis and Antithesis disagreed (using the `contradictions` field).
    *   **The "Why":** If the user asks for details, show the `thesis` (initial view) and `antithesis` (critique).
    *   **Next Steps:** Present the `research_proposals` as actionable follow-ups.

## Example Response Style

> **Synthesis:** [Insert Synthesis Text]
>
> **The Core Tension:** The initial view (Thesis) argued X, but the critique (Antithesis) identified that Y. The synthesis resolves this by Z.
>
> **Key Contradictions:**
> *   [Contradiction 1]
> *   [Contradiction 2]

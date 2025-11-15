# Hegelion Example: The Printing Press

## Query
"What year was the printing press invented?"

## Sample Result (`HegelionResult`)

**Note:** This example output was generated using Claude Code connected to an Anthropic-compatible endpoint running `glm-4.6`. The default setup instructions in this repo use Anthropic's official API (`claude-4.5-sonnet-latest`), but Hegelion is backend-agnostic.

```json
{
  "query": "What year was the printing press invented?",
  "mode": "synthesis",
  "thesis": "Johannes Gutenberg's metal movable-type press emerged around 1440 in Mainz, rapidly accelerating literacy and the spread of ideas across Europe.",
  "antithesis": "Framing the printing press as a single 1440 breakthrough ignores centuries of Asian innovation, the financial collapse of Gutenberg's shop, and how social demand—not technology alone—made printing transformative.",
  "synthesis": "Gutenberg's press marks a convergence rather than an origin. Asian woodblock and movable-type traditions, Renaissance humanism, and merchant-capital networks combined to create an information ecosystem that shifted power from royal courts to transnational publics.",
  "contradictions": [
    {
      "description": "Treating the press as a single European invention erases Chinese and Korean precedents",
      "evidence": "Movable type existed in Korea by the 1200s and produced state documents at scale"
    },
    {
      "description": "Thesis implies instant success",
      "evidence": "Gutenberg's venture failed financially and adoption took decades"
    },
    {
      "description": "Technological determinism ignores the Renaissance demand-side story",
      "evidence": "Merchant literacy and humanist curricula created the market that made printing durable"
    }
  ],
  "research_proposals": [
    {
      "description": "Compare adoption speed in cities with different merchant densities",
      "testable_prediction": "Ports with pre-existing merchant guilds achieved breakeven printing businesses within 15 years"
    },
    {
      "description": "Map global knowledge flows between East Asian printing centers and Mainz",
      "testable_prediction": "Loanwords and tooling evidence will show Korean influence on early European presses"
    }
  ],
  "metadata": {
    "thesis_time_ms": 1200.0,
    "antithesis_time_ms": 1850.0,
    "synthesis_time_ms": 2100.0,
    "total_time_ms": 5150.0,
    "backend_provider": "AnthropicLLMBackend",
    "backend_model": "glm-4.6"
  }
}
```

The CLI `hegelion "What year was the printing press invented?" --format summary` renders the same content as a readable report while keeping the JSON contract intact.

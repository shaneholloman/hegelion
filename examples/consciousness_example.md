# Hegelion Example: The Nature of Consciousness

## Query
"What is consciousness?"

## Sample Result (`HegelionResult`)

**Note:** This example output demonstrates Hegelion's dialectical approach to philosophical questions. The default setup uses Anthropic's API, but this backend-agnostic system works with any LLM provider.

```json
{
  "query": "What is consciousness?",
  "mode": "synthesis",
  "thesis": "Consciousness is the subjective experience of being aware—what philosophers call qualia. It emerges from complex information processing in the brain's neural networks, creating a unified sense of self that perceives, feels, and reflects upon reality. This emergent property transforms pure computation into lived experience.",
  "antithesis": "Consciousness is not a special property but a user illusion—a narrative the brain constructs after the fact to explain its decisions. What we call 'subjective experience' is merely epiphenomenal to unconscious neural processes. The brain generates behavior, and consciousness is just the story it tells itself.",
  "synthesis": "Consciousness is neither a mystical emergent property nor an irrelevant illusion—it is a **self-modeling process** that the biological system uses for recursive self-regulation. The system doesn't just generate behavior; it maintains a running simulation of itself navigating possibility spaces. This simulation is not merely explanatory baggage but a functional control layer that enables metacognition, long-term planning, and social coordination. The 'hard problem' dissolves when we recognize that consciousness is not something the brain *produces* but something the organism *does* as an integrated system embedded in environment and culture.",
  "contradictions": [
    {
      "description": "Thesis treats consciousness as emergent from neural complexity alone",
      "evidence": "Consciousness varies dramatically with cultural practices, language structures, and environmental embedding, not just neural wiring"
    },
    {
      "description": "Antithesis reduces consciousness to post-hoc confabulation",
      "evidence": "Patients with specific brain lesions lose aspects of self-modeling that directly impair real-time decision-making, not just retrospective explanation"
    },
    {
      "description": "Both treat consciousness as isolated brain property",
      "evidence": "Extended cognition research shows conscious states depend on external scaffolding—tools, language, social coordination"
    }
  ],
  "research_proposals": [
    {
      "description": "Cross-cultural fMRI studies of self-referential processing",
      "testable_prediction": "Individualistic vs. collectivist cultures will show different patterns of default mode network activation during self-reflection tasks"
    },
    {
      "description": "Investigate consciousness as predictive processing loop",
      "testable_prediction": "Conscious awareness should correlate with brain regions generating top-down predictions that minimize surprise across sensory and proprioceptive modalities"
    },
    {
      "description": "Study tool-use integration in conscious awareness",
      "testable_prediction": "Subjects using external memory systems should show extended neural patterns treating the tool as part of the self-model"
    }
  ],
  "metadata": {
    "thesis_time_ms": 1450.0,
    "antithesis_time_ms": 1890.0,
    "synthesis_time_ms": 2350.0,
    "total_time_ms": 5690.0,
    "backend_provider": "AnthropicLLMBackend",
    "backend_model": "claude-4.5-sonnet-latest"
  }
}
```

The CLI `hegelion "What is consciousness?" --format summary` renders this as a readable philosophical report while maintaining the structured JSON contract.
# Hegelion Examples

This directory contains example outputs showcasing Hegelion's dialectical synthesis approach across different domains:

## Example Files

- **[consciousness_example.md](./consciousness_example.md)** - Philosophical inquiry into the nature of consciousness
- **[gravity_example.md](./gravity_example.md)** - Scientific frontier question about the fundamental nature of gravity
- **[ai_creativity_example.md](./ai_creativity_example.md)** - Analysis of AI creativity and co-creative systems
- **[printing_press_example.md](./printing_press_example.md)** - Historical question about technological innovation

## What These Examples Demonstrate

Each example illustrates Hegelion's unique capabilities:

1. **Thesis-Antithesis-Synthesis Structure** - Presents three distinct perspectives that build upon each other
2. **Contradiction Identification** - Explicitly surfaces hidden assumptions and logical tensions
3. **Research Proposals** - Generates testable hypotheses for empirical investigation
4. **Metadata Tracking** - Provides timing and provenance information for reproducibility

## Running These Examples

You can generate similar outputs using the CLI:

```bash
# Basic query
hegelion "What is consciousness?"

# With debug information
hegelion "Is gravity a force or geometry?" --debug

# Summary format for readability
hegelion "Can AI be genuinely creative?" --format summary
```

## Backend Notes

- Examples are backend-agnostic and will work with any configured provider
- Metadata shows actual backend used for each example
- Default configuration uses Anthropic's Claude models
- See `.env.example` for configuration options
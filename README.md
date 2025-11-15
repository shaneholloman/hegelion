# Hegelion

```
/==============================================================\
|   HEGELION: A PERMANENT OPPOSITION CO-PROCESSOR FOR YOUR LLM |
\==============================================================/
```

> **A dialectical reasoning harness for LLMs**
> Thesis → Antithesis → Synthesis, with structured contradictions and research proposals.

Hegelion is a Python package and MCP server that adds **structured Hegelian dialectics** to any LLM stack.

Instead of a single model answer, Hegelion runs a **three-phase loop**:

1. **Thesis** – generate a comprehensive answer
2. **Antithesis** – identify contradictions and challenge assumptions
3. **Synthesis** – construct a higher-level resolution with novel insights

The package provides both Python APIs and MCP tools, returning structured results with contradictions, research proposals, and full dialectical traces.

---

## Why Hegelion?

LLMs today are often:

- **Confident even when they're wrong**
- **Under-opposed** – "self-reflection" is usually just another pass of the same model
- **Opaque** – you rarely see where internal disagreement lives

Hegelion turns dialectic into a **first-class, inspectable protocol**:

- **Named phases**: `THESIS → ANTITHESIS → SYNTHESIS`
- **Always synthesizes** – no arbitrary conflict gating
- **Transparent**: full trace with structured contradictions and research proposals
- **Backend-agnostic**: works with OpenAI, Anthropic, z.ai, or local models
- **Research-focused**: encourages falsifiable predictions and testable proposals

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/hegelion.git
cd hegelion

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### Configuration

Copy the environment template and configure your backend:

```bash
cp .env.example .env
# Edit .env with your API keys
```

Supported backends:

**Anthropic/z.ai:**
```bash
HEGELION_PROVIDER=anthropic
HEGELION_MODEL=glm-4.6
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic  # for z.ai
```

**OpenAI:**
```bash
HEGELION_PROVIDER=openai
HEGELION_MODEL=gpt-4.1-mini
OPENAI_API_KEY=your-key-here
```

**Ollama (local):**
```bash
HEGELION_PROVIDER=ollama
HEGELION_MODEL=llama3.1
```

### Usage

**Python API:**
```python
import asyncio
from hegelion import run_dialectic

async def main():
    result = await run_dialectic("Can AI be genuinely creative?")
    print(f"Mode: {result.mode}")
    print(f"Contradictions: {len(result.contradictions)}")
    print(f"Research proposals: {len(result.research_proposals)}")
    print(f"\nSynthesis:\n{result.synthesis}")

asyncio.run(main())
```

**Command Line:**
```bash
# Single query
hegelion/scripts/hegelion_cli.py "What year was the printing press invented?" --format summary

# Benchmark suite
hegelion/scripts/hegelion_bench.py hegelion/benchmarks/examples_basic.jsonl --summary
```

**MCP Server:**
```bash
# Run MCP server for Claude Desktop, Cursor, etc.
python -m hegelion.mcp_server
```

---

## What Hegelion Does

### 1. Generates a Thesis

A comprehensive, multi-perspective answer to the original question.

### 2. Generates an Antithesis

A critique that:
- Finds contradictions and logical gaps
- Surfaces unexamined assumptions
- Proposes alternative framings
- Extracts structured contradictions with evidence

### 3. Always Generates a Synthesis

**Design change:** Unlike the previous version, Hegelion now always performs synthesis to encourage full dialectical reasoning, rather than gating based on conflict scores.

The synthesis:
- Must *transcend* both thesis and antithesis
- Cannot simply "pick a side" or say "both are partly right"
- Is encouraged to output **research proposals** with falsifiable predictions

### 4. Returns Structured Results

```json
{
  "query": "Can AI be genuinely creative?",
  "mode": "synthesis",
  "thesis": "AI can be considered creative because it generates novel combinations...",
  "antithesis": "AI lacks subjective experience and intrinsic intention...",
  "synthesis": "Both sides treat creativity as all-or-nothing. A more useful view is...",
  "contradictions": [
    {
      "description": "Thesis assumes creativity requires only novel outputs",
      "evidence": "Overlooks the role of intent and subjective experience"
    }
  ],
  "research_proposals": [
    {
      "description": "Compare human and AI-generated works under blind evaluation",
      "testable_prediction": "Expert judges cannot reliably distinguish AI from human creative works"
    }
  ],
  "metadata": {
    "thesis_time_ms": 340,
    "antithesis_time_ms": 510,
    "synthesis_time_ms": 620,
    "total_time_ms": 1470,
    "backend_provider": "AnthropicLLMBackend",
    "backend_model": "glm-4.6"
  }
}
```

**Note:** Internal conflict scoring is still computed for research purposes but is not exposed in the main API to avoid fetishizing scalar precision. Use `debug=True` to access internal metrics.

---

## Package Structure

```
hegelion/
├── hegelion/                     # Main package
│   ├── __init__.py              # Public API exports
│   ├── core.py                  # High-level API (run_dialectic, run_benchmark)
│   ├── engine.py                # Core dialectical engine
│   ├── backends.py              # LLM backend abstractions
│   ├── parsing.py               # Contradiction & research proposal parsing
│   ├── models.py                # Pydantic models & dataclasses
│   ├── prompts.py               # Prompt templates for each phase
│   ├── config.py                # Environment-driven configuration
│   └── mcp_server.py            # MCP server implementation
├── scripts/
│   ├── hegelion_cli.py          # Single query CLI
│   └── hegelion_bench.py        # Benchmark CLI
├── benchmarks/
│   └── examples_basic.jsonl     # Sample prompts for testing
├── examples/
│   └── printing_press_example.md # Example output
├── tests/                       # Test suite
├── .env.example                 # Environment variables template
├── README.md                    # This file
├── HEGELION_SPEC.md             # Detailed specification
└── LICENSE                      # MIT License
```

---

## MCP Integration

### Claude Desktop Configuration

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "hegelion": {
      "command": "python",
      "args": [
        "-m", "hegelion.mcp_server"
      ],
      "cwd": "/path/to/hegelion",
      "env": {
        "HEGELION_PROVIDER": "anthropic",
        "HEGELION_MODEL": "glm-4.6",
        "ANTHROPIC_API_KEY": "your-anthropic-api-key-here",
        "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic"
      }
    }
  }
}
```

**Available MCP Tools:**

1. **`run_dialectic`** - Process a single query with full dialectical analysis
2. **`run_benchmark`** - Run multiple prompts from a JSONL file

---

## When to Use Hegelion

Hegelion is most valuable for:

**High-stakes, contested questions:**
- Ethics, law, policy decisions
- Research direction planning
- Strategic business decisions
- Philosophical and scientific debates

**When you want:**
- Genuine tension between viewpoints
- Explicit contradictions and edge cases
- Research proposals with testable predictions
- Structured analysis of complex topics

**Use cases:**
- **AI alignment research** - Explore tensions in safety proposals
- **Academic research** - Generate novel hypotheses and research directions
- **Strategic planning** - Challenge assumptions and explore alternatives
- **Education** - Teach dialectical reasoning and critical thinking

It's overkill for:
- Simple factual queries
- Basic transformations (summarization, formatting)
- Tasks with clear, uncontroversial answers

---

## Development

### Running Tests

```bash
# Install development dependencies
uv sync --dev

# Run tests
pytest

# Run with coverage
pytest --cov=hegelion
```

### Development Workflow

```bash
# Install pre-commit hooks for secret scanning and code quality
pre-commit install

# Run single query for testing
hegelion/scripts/hegelion_cli.py "What is consciousness?" --debug

# Run benchmark examples
hegelion/scripts/hegelion_bench.py hegelion/benchmarks/examples_basic.jsonl --summary
```

---

## Research Applications

Hegelion is designed for **AI reasoning and ethics research**:

- **Contradiction analysis** - Study how models handle internal conflicts
- **Synthesis quality** - Evaluate the sophistication of dialectical resolution
- **Research proposal generation** - Assess novelty and testability of AI-generated ideas
- **Cross-model comparison** - Compare reasoning patterns across different LLMs
- **Prompt engineering** - Study how different prompts affect dialectical reasoning

The package includes benchmark suites for factual, scientific, historical, philosophical, and ethical questions to enable systematic research evaluation.

---

## Design Philosophy

**Always Synthesize:** Unlike systems that only synthesize when conflict is high, Hegelion always performs synthesis. This encourages comprehensive reasoning and avoids arbitrary thresholds.

**Human Judgment Over Scores:** Internal conflict scoring is kept for research but de-emphasized in the public API to encourage human evaluation of reasoning quality.

**Structured Output:** Focus on machine-readable contradictions and research proposals rather than free-form text alone.

**Backend Agnostic:** Work with any LLM provider through a unified interface.

**Research-Ready:** Designed from the ground up for systematic research on AI reasoning and ethics.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

**Areas for contribution:**
- Additional LLM backend implementations
- New prompt templates for specialized domains
- Benchmark suites for specific fields
- Analysis tools for dialectical outputs
- Documentation and examples

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Status

**Production-ready for research and development.**
Used in AI reasoning research and actively maintained.

For questions, issues, or research collaborations, please open an issue on GitHub.
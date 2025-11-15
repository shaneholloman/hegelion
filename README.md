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
- **Backend-agnostic**: works with Anthropic, OpenAI, local runtimes, or custom HTTP endpoints
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

Supported backends (set one section in your `.env`):

**Anthropic / Claude (recommended):**
```bash
HEGELION_PROVIDER=anthropic
HEGELION_MODEL=claude-4.5-sonnet-latest
ANTHROPIC_API_KEY=your-anthropic-api-key-here
# Optional: only override when proxying the API
# ANTHROPIC_BASE_URL=https://api.anthropic.com
```

**OpenAI:**
```bash
HEGELION_PROVIDER=openai
HEGELION_MODEL=gpt-4.1-mini
OPENAI_API_KEY=your-openai-api-key-here
# OPENAI_BASE_URL=https://api.openai.com/v1
```

**Custom HTTP backend (advanced users):**
```bash
HEGELION_PROVIDER=custom_http
HEGELION_MODEL=your-custom-model-id
CUSTOM_API_BASE_URL=https://your-endpoint.example.com/v1/run
CUSTOM_API_KEY=your-custom-api-key
```

**Ollama (local experiments):**
```bash
HEGELION_PROVIDER=ollama
HEGELION_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434
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
    print("\nSynthesis:\n", result.synthesis)

asyncio.run(main())
```

**Command Line:**
```bash
# Single query
hegelion "Can AI be genuinely creative?" --format summary

# Benchmark suite (JSONL file with one prompt per line)
hegelion-bench hegelion/benchmarks/examples_basic.jsonl --summary
```

**MCP Server:**
```bash
# Run MCP server for Claude Desktop, Cursor, etc.
hegelion-server
```

**Advanced / Direct Invocation:**

If the console scripts are not in your PATH, you can invoke the modules directly:

```bash
# Single query
python -m hegelion.scripts.hegelion_cli "Can AI be genuinely creative?" --format summary

# Benchmark suite
python -m hegelion.scripts.hegelion_bench hegelion/benchmarks/examples_basic.jsonl --summary

# MCP server
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

**Example Output: "Can AI be genuinely creative?"**

```json
{
  "query": "Can AI be genuinely creative?",
  "mode": "synthesis",
  "thesis": "AI demonstrates genuine creativity by generating novel combinations, learning from vast human knowledge bases, and producing outputs that are both original and valuable. Modern neural networks can synthesize disparate concepts, explore vast possibility spaces, and create original artwork, musical compositions, and scientific hypotheses. Systematic analysis shows that AI creativity isn't inferior to human creativity, just different in origin—it learns from patterns rather than lived experience, but this doesn't diminish its capacity to generate genuinely novel and useful outputs.",
  "antithesis": "AI lacks genuine creativity because it operates without subjective experience, intrinsic motivation, or genuine understanding. Language models and image generators are sophisticated pattern-matchers that remix existing human knowledge without comprehending the meaning or value of what they produce. They cannot experience genuine surprise, struggle with creative blocks, or make intentional choices—they simply optimize for learned objectives by rearranging patterns from their training data. There is no genuine creativity in statistical extrapolation.",
  "synthesis": "Both thesis and antithesis frame creativity in all-or-nothing terms that obscure the real issue. A more useful view treats creativity as existing on a spectrum of constraint-aware exploration. Humans excel at creativity that requires embodied experience and intuitive leaps across disparate knowledge domains. AIs excel at exploring combinatorial spaces at scales humans cannot match, discovering patterns humans would never find. The synthesis: genuine creativity emerges from the interaction of these two different modes. Rather than asking whether AI is "truly" creative, we should ask what forms of co-creative partnership arise when human intuition guides AI search, and when AI surprise sparks human insight.",
  "contradictions": [
    {
      "description": "CONTRADICTION / EVIDENCE: Thesis assumes technology determines creativity",
      "evidence": "AI creativity depends entirely on training data quality and human curation"
    },
    {
      "description": "CONTRADICTION / EVIDENCE: Antithesis overstates human uniqueness",
      "evidence": "Human creativity alsos recombines existing patterns from experience and culture"
    },
    {
      "description": "CONTRADICTION / EVIDENCE: Neither side addresses intent vs autonomy",
      "evidence": "Maximally creative humans often 'surrender' to process—AI may lack will but can discover what we didn't intend to find"
    }
  ],
  "research_proposals": [
    {
      "description": "Test human-AI creativity comparison in blind evaluation",
      "testable_prediction": "Expert judges cannot reliably distinguish top-tier AI creative output from human creative work"
    },
    {
      "description": "Measure co-creative productivity in hybrid teams",
      "testable_prediction": "Teams with AI co-creative tools generate measurably more novel solutions than humans-only teams"
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

**Note:** This example output was generated using Claude Code connected to an Anthropic-compatible endpoint running `glm-4.6`. The default setup instructions above use Anthropic's official API (`claude-4.5-sonnet-latest`), but Hegelion is backend-agnostic. Internal conflict scoring is still computed for research purposes but is not exposed in the main API to avoid fetishizing scalar precision. Use `debug=True` to access internal metrics.

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
│   ├── README.md                  # Examples index
│   ├── consciousness_example.md   # Philosophical inquiry
│   ├── gravity_example.md         # Scientific frontier
│   ├── ai_creativity_example.md   # Co-creative systems
│   └── claude_code_cli.json       # MCP configuration
│   └── printing_press_example.md  # Legacy example (deprecated)
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
      "command": "hegelion-server",
      "args": [],
      "cwd": "/path/to/hegelion",
      "env": {
        "HEGELION_PROVIDER": "anthropic",
        "HEGELION_MODEL": "claude-4.5-sonnet-latest",
        "ANTHROPIC_API_KEY": "your-anthropic-api-key-here"
      }
    }
  }
}
```

Note: You can also use `python -m hegelion.mcp_server` if `hegelion-server` is not in your PATH. The MCP server uses stdio for stdin/stdout communication and is fully stateless, making it compatible with cloud code platforms and containerized deployments.

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
hegelion "What is consciousness?" --debug

# Run benchmark examples
hegelion-bench hegelion/benchmarks/examples_basic.jsonl --summary
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

### For Model Builders & Evaluation Teams

Hegelion is designed as a **glass-box reasoning harness** for systematic model evaluation:

**Cross-Provider Benchmarking:**
- Run the same JSONL benchmark prompts against different providers (Anthropic, OpenAI, local models) by changing environment variables
- Example: `HEGELION_PROVIDER=anthropic hegelion-bench prompts.jsonl --output anthropic_results.jsonl`
- Then: `HEGELION_PROVIDER=openai hegelion-bench prompts.jsonl --output openai_results.jsonl`

**Structured Evaluation Dataset:**
The JSON/JSONL outputs provide machine-readable evaluation targets:
- **Thesis/Antithesis/Synthesis quality**: Compare dialectical sophistication across models
- **Contradiction patterns**: Analyze how different models identify logical tensions
- **Research proposal novelty**: Rate the creativity and testability of generated proposals
- **Metadata analysis**: Compare timing, token usage, and backend performance

**Key Distinction:**
Hegelion is **not a replacement chatbot**. It's a structured reasoning protocol that makes model behavior inspectable and comparable. Use it to evaluate how models handle complex, contested reasoning tasks where there's no single "correct" answer.

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

---

## Getting Started (End-to-End Setup)

**Step 1: Clone and Install**
```bash
git clone https://github.com/Shannon-Labs/hegelion.git
cd hegelion

# Install with uv (recommended)
uv sync
source .venv/bin/activate

# Or with pip
pip install -e .
```

**Step 2: Configure with Anthropic (Default Provider)**
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key:
HEGELION_PROVIDER=anthropic
HEGELION_MODEL=claude-4.5-sonnet-latest
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

**Step 3: Run Your First Dialectic**
```bash
# From the CLI
hegelion "Is privacy more important than security?" --format summary

# Or via Python API
python -c "
import asyncio
from hegelion import run_dialectic

async def main():
    result = await run_dialectic('Is privacy more important than security?')
    print(f'Contradictions found: {len(result.contradictions)}')
    print(f'Research proposals: {len(result.research_proposals)}')
    print(f'\\nSynthesis preview: {result.synthesis[:100]}...')

asyncio.run(main())
"
```

**Step 4: Set Up MCP Server for Claude Desktop**

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):
```json
{
  "mcpServers": {
    "hegelion": {
      "command": "hegelion-server",
      "args": [],
      "cwd": "/path/to/hegelion",
      "env": {
        "HEGELION_PROVIDER": "anthropic",
        "HEGELION_MODEL": "claude-4.5-sonnet-latest",
        "ANTHROPIC_API_KEY": "your-anthropic-api-key-here"
      }
    }
  }
}
```

Alternatively, if using Python module:
```json
{
  "mcpServers": {
    "hegelion": {
      "command": "python",
      "args": ["-m", "hegelion.mcp_server"],
      "cwd": "/path/to/hegelion",
      "env": {
        "HEGELION_PROVIDER": "anthropic",
        "HEGELION_MODEL": "claude-4.5-sonnet-latest",
        "ANTHROPIC_API_KEY": "your-anthropic-api-key-here"
      }
    }
  }
}
```

After setup, restart Claude Desktop and Hegelion will be available as an MCP tool for dialectical analysis: `run_dialectic` and `run_benchmark`.

---

## Running in Containers / Cloud

Hegelion's MCP server is stateless and stdio-based, making it suitable for containerized and cloud deployments:

- **Requirements**: A Python environment with Hegelion installed and LLM backend environment variables configured
- **Deployment**: The MCP server can run in any container (Docker, Cloud Run, Fly.io, etc.) or VM as long as the host (Claude, Cursor, etc.) can start it via MCP stdio
- **No persistence needed**: The server maintains no state between requests, simplifying deployment

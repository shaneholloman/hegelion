# Architecture

How Hegelion works under the hood.

## Two Modes

### MCP Mode (Prompt Server)

When used as an MCP server, Hegelion generates structured prompts. Your editor's model executes them.

```
Your Editor (Cursor, Claude Desktop)
    │
    ▼
Hegelion MCP Server
    │  Returns: structured prompts
    ▼
Your LLM (executes the prompts)
```

**Key point:** Hegelion never makes API calls in MCP mode. It's a prompt generator. This means:

- No extra API keys needed
- Works with any model your editor has
- Zero additional cost beyond your existing LLM usage

### Python API Mode

When used via the Python API, Hegelion orchestrates the LLM calls directly.

```
Your Code
    │
    ▼
Hegelion Engine
    │
    ├─► [Call 1] Thesis prompt → LLM → thesis
    ├─► [Call 2] Antithesis prompt → LLM → critique
    └─► [Call 3] Synthesis prompt → LLM → resolution
    │
    ▼
HegelionResult
```

## Core Components

```
hegelion/
├── core/
│   ├── engine.py      # Three-phase orchestration
│   ├── backends.py    # LLM provider abstractions
│   ├── prompts.py     # Phase templates
│   ├── parsing.py     # Contradiction extraction
│   └── models.py      # Result schemas
│
├── mcp/
│   └── server.py      # MCP stdio server
│
└── scripts/
    └── cli.py         # Command-line interface
```

## The Dialectical Loop

### Basic Flow

```python
# Phase 1: Thesis
thesis = await backend.generate(thesis_prompt(query))

# Phase 2: Antithesis
antithesis = await backend.generate(
    antithesis_prompt(query, thesis)
)

# Phase 3: Synthesis
synthesis = await backend.generate(
    synthesis_prompt(query, thesis, antithesis)
)
```

### With Council

When `use_council=True`, the antithesis phase spawns three concurrent critics:

```python
# Phase 2: Council Antithesis
critiques = await asyncio.gather(
    backend.generate(logician_prompt(query, thesis)),
    backend.generate(empiricist_prompt(query, thesis)),
    backend.generate(ethicist_prompt(query, thesis))
)
antithesis = merge_critiques(critiques)
```

### With Judge

When `use_judge=True`, a final evaluation phase scores the synthesis:

```python
# Phase 4: Judge
evaluation = await backend.generate(judge_prompt(synthesis))
if evaluation.score < threshold:
    # Retry synthesis with feedback
    synthesis = await backend.generate(
        synthesis_prompt(query, thesis, antithesis, feedback=evaluation)
    )
```

## Backend Abstraction

Hegelion supports multiple LLM providers through a common interface:

```python
class LLMBackend:
    async def generate(self, prompt: str) -> str: ...
```

Implementations exist for:

- **Anthropic** (Claude)
- **OpenAI** (GPT)
- **Google** (Gemini)
- **Ollama** (local models)
- **Custom HTTP** (any endpoint)

## Structured Output

Hegelion extracts structured data from LLM outputs:

### Contradictions

```
CONTRADICTION: [description]
EVIDENCE: [supporting evidence]
```

Parsed into:

```python
{
    "description": "...",
    "evidence": "..."
}
```

### Research Proposals

```
RESEARCH_PROPOSAL: [description]
TESTABLE_PREDICTION: [falsifiable claim]
```

Parsed into:

```python
{
    "description": "...",
    "testable_prediction": "..."
}
```

## Caching

Hegelion includes result caching with TTL, keyed by query hash. This avoids redundant API calls for repeated queries.

## Streaming

The engine supports callback-based streaming during generation:

```python
async def on_token(token: str):
    print(token, end="", flush=True)

result = await run_dialectic(query, stream_callback=on_token)
```

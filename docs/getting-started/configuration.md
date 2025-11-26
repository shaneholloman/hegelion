# Configuration

Hegelion supports multiple LLM backends via environment variables.

## Backend Configuration

Create a `.env` file in your project root:

### Anthropic (Default)

```bash
HEGELION_PROVIDER=anthropic
HEGELION_MODEL=claude-4.5-sonnet-latest
ANTHROPIC_API_KEY=your-key
```

### OpenAI

```bash
HEGELION_PROVIDER=openai
HEGELION_MODEL=gpt-4.1-mini
OPENAI_API_KEY=your-key
```

### Google Gemini

```bash
HEGELION_PROVIDER=google
HEGELION_MODEL=gemini-2.5-pro
GOOGLE_API_KEY=your-key
```

### Ollama (Local)

```bash
HEGELION_PROVIDER=ollama
HEGELION_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434
```

### Custom HTTP Backend

```bash
HEGELION_PROVIDER=custom_http
HEGELION_MODEL=your-model-id
CUSTOM_API_BASE_URL=https://your-endpoint.example.com/v1/run
CUSTOM_API_KEY=your-key
```

## Engine Settings

```bash
# Max tokens per phase (default: 10000)
HEGELION_MAX_TOKENS_PER_PHASE=10000
```

## Feature Toggles

These can be set at runtime via API or CLI:

| Option | Default | Description |
|--------|---------|-------------|
| `use_council` | `false` | Activates three critics: Logician, Empiricist, Ethicist |
| `use_judge` | `false` | Adds final quality evaluation step |
| `use_search` | `false` | Grounds arguments with web search |
| `response_style` | `sections` | Output format: `json`, `sections`, or `synthesis_only` |

### Python API

```python
result = await run_dialectic(
    "Your question",
    use_council=True,
    use_judge=True,
    use_search=True,
    response_style="json"
)
```

### CLI

```bash
hegelion "Your question" --council --judge --search --format json
```

### MCP

```
Use Hegelion dialectical_single_shot on "Your question" with use_council=true
```

## Verified Backends

The project maintainers regularly test:

- **Anthropic Claude** (default)
- **OpenAI GPT-4**
- **GLM 4.6** via OpenAI-compatible endpoint

We welcome reports for other providers.

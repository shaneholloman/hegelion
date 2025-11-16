# GLM API Demo with GIF Recording

This directory contains a demonstration of using Hegelion's Python API directly with the GLM backend, and a script to record the terminal session as a GIF.

## Demo GIF

![GLM API Demo](./demo_glm_api.gif)

The GIF above was generated with `record_demo.sh` against the deterministic `mock_glm_server.py`, so documentation stays consistent even when you are offline. Swap the base URL and API key back to the real GLM endpoint when you want to hit the live service.

## Files

- `demo_glm_api.py` - Python script demonstrating the Hegelion API with GLM backend
- `record_demo.sh` - Shell script to record the demo as a GIF
- `README_DEMO.md` - This file

## Prerequisites

1. **GLM API Key**: You need a GLM API key from [Z.AI devpack](https://docs.z.ai/devpack/tool/others)
2. **GIF Recording Tool**: Install one of the following:
   - **vhs** (recommended): `brew install vhs` or visit [charmbracelet/vhs](https://github.com/charmbracelet/vhs)
   - **asciinema + agg**: `brew install asciinema agg` or visit [asciinema/asciinema](https://github.com/asciinema/asciinema) and [asciinema/agg](https://github.com/asciinema/agg)
3. **Python 3.10+** with Hegelion installed (from source or PyPI)

## Quick Start

### 1. Set up environment variables

```bash
export OPENAI_API_KEY='your-glm-api-key-here'
export HEGELION_PROVIDER=openai
export HEGELION_MODEL=GLM-4.6
export OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4
```

### 2. Run the demo script directly

```bash
cd examples
python3 demo_glm_api.py
```

This will run the dialectical reasoning on "Can AI be genuinely creative?" and display the results.

### 3. Record as GIF

```bash
cd examples
./record_demo.sh
```

The script will:
- Check for required tools (vhs or asciinema+agg)
- Set up GLM environment variables
- Record the demo execution
- Output `demo_glm_api.gif` in the `examples/` directory

## What the Demo Shows

The demo script (`demo_glm_api.py`) demonstrates:

1. **Direct API Usage**: Using `run_dialectic()` from `hegelion.core` instead of the CLI
2. **GLM Backend Configuration**: Setting up GLM via environment variables
3. **Structured Output**: Displaying:
   - Thesis
   - Antithesis
   - Synthesis
   - Contradictions (with evidence)
   - Research proposals (with testable predictions)
   - Metadata (backend info, timing, debug scores)

## Example Output

The demo will show formatted output like:

```
================================================================================
                          Hegelion GLM API Demo
================================================================================

Query: Can AI be genuinely creative?

Backend: openai
Model: GLM-4.6
Base URL: https://api.z.ai/api/coding/paas/v4

🔄 Running dialectical reasoning...

================================================================================
                                  Results
================================================================================

--- THESIS ---
[Thesis content here...]

--- ANTITHESIS ---
[Antithesis content here...]

--- SYNTHESIS ---
[Synthesis content here...]

--- CONTRADICTIONS (3) ---
1. [Contradiction description]
   Evidence: [Evidence text]

--- RESEARCH PROPOSALS (2) ---
1. [Proposal description]
   Testable Prediction: [Prediction]

================================================================================
                                 Metadata
================================================================================
Backend Provider: OpenAILLMBackend
Backend Model: GLM-4.6
Total Time: 37.56 s
Internal Conflict Score: 0.95

================================================================================

✅ Demo complete!
```

## Troubleshooting

### API Key Issues

If you see:
```
⚠️  Warning: OPENAI_API_KEY not set in environment!
```

Make sure you've exported the `OPENAI_API_KEY` environment variable:
```bash
export OPENAI_API_KEY='your-key-here'
```

### Recording Tool Not Found

The `record_demo.sh` script will check for available tools and provide installation instructions if none are found.

### Import Errors

If you get import errors when running `demo_glm_api.py`, make sure:
1. You're running from the `examples/` directory
2. Hegelion is installed (`pip install hegelion` or `uv sync`)
3. You're using Python 3.10+

### Offline Mock Server (optional)

Need a deterministic run for docs or CI? Launch the mock server and point the OpenAI-compatible client at it:

```bash
# Terminal 1
cd examples
python3 mock_glm_server.py

# Terminal 2
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
export OPENAI_API_KEY=dummy-key
./record_demo.sh
```

The mock server replies with pre-baked thesis/antithesis/synthesis text, so recordings stay stable. Remove the overrides to exercise the real GLM backend.

## Customization

You can modify `demo_glm_api.py` to:
- Change the query (edit the `query` variable)
- Adjust output formatting
- Add more metadata display
- Use a different backend (modify environment variables)

## Notes

- The demo uses `debug=True` to show internal conflict scores
- Recording times may vary based on API response times
- The GIF recording script includes delays to ensure readable output
- Make sure your terminal has good contrast for GIF recording


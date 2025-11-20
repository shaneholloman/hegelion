# Google Gemini Extension for Hegelion

This directory packages everything you need to expose Hegelion’s dialectical agent as a Google Gemini extension (and any other marketplace that accepts OpenAPI specs).

## Architecture Overview

1. **FastAPI service (`server/app.py`)** – imports `HegelionAgent` and exposes `/agent_act`.
2. **Railway deployment (free tier friendly)** – builds from `requirements.txt`, runs `uvicorn`.
3. **OpenAPI Spec (`openapi.yaml`)** – points Gemini / other marketplaces at the Railway URL.

## Quick Start (Railway)

```bash
cd extensions/gemini/server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp env.sample .env   # fill in provider + API keys
uvicorn extensions.gemini.server.app:app --reload
```

Ready to deploy?

```bash
railway init
railway variables set HEGELION_PROVIDER=anthropic
railway variables set HEGELION_MODEL=claude-3-5-sonnet-20241022
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway up --service hegelion-agent \
  --build-cmd "pip install -r requirements.txt" \
  --start-cmd "uvicorn extensions.gemini.server.app:app --host 0.0.0.0 --port \$PORT"
```

## Register with Google Gemini

1. Open [Google AI Studio Extensions](https://aistudio.google.com/app/extensions).
2. Create a new extension “From OpenAPI”, pointing to `extensions/gemini/openapi.yaml` (host the raw file or paste the contents).
3. Set auth = “API key” (Railway lets you enforce this by checking headers before running the agent).
4. Enable the extension inside your Gemini chat/app. Gemini will call your Railway URL whenever it needs adversarial planning.

## Applying the Same Package Elsewhere

- **Cursor MCP Gallery / Claude Tool Hub** – submit the OpenAPI spec plus short description and point them at the Railway URL.
- **Hugging Face Agents / LangChain ToolHub** – wrap `agent_act` as a tool definition that forwards to the Railway endpoint.

See `extensions/gemini/server/README.md` for deployment details and `docs/marketplaces.md` for other listing requirements.


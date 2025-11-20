# Google Gemini Extension for Hegelion

This directory packages everything you need to expose Hegelion’s dialectical agent as a Google Gemini extension (and any other marketplace that accepts OpenAPI specs).

## Architecture Overview

1. **FastAPI service (`server/app.py`)** – imports `HegelionAgent` and exposes `/agent_act`.
2. **Containerized deployment (Dockerfile)** – runs anywhere that supports Python containers (Cloud Run, Render, Fly.io, Railway, etc.).
3. **OpenAPI Spec (`openapi.yaml`)** – wire the HTTPS URL into Google Gemini or other marketplaces.

## Local Development

```bash
cd extensions/gemini/server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp env.sample .env   # fill in provider + API keys
uvicorn extensions.gemini.server.app:app --reload
```

## Deploy to Cloud Run

```bash
# Build container
gcloud config set project HEGELION_PROJECT
gcloud builds submit --tag gcr.io/HEGELION_PROJECT/hegelion-agent extensions/gemini/server

# Deploy (allow unauth so Gemini can call it)
gcloud run deploy hegelion-agent \
  --image gcr.io/HEGELION_PROJECT/hegelion-agent \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars HEGELION_PROVIDER=anthropic,HEGELION_MODEL=claude-3-5-sonnet-20241022

# Add API keys if you want the backend to call Anthropic/OpenAI directly:
gcloud run services update hegelion-agent \
  --region us-central1 \
  --update-env-vars ANTHROPIC_API_KEY=sk-ant-...
```

Cloud Run will emit a URL like `https://hegelion-agent-abc123-uc.a.run.app`. Use that in the OpenAPI spec and Gemini extension registration.

## Register with Google Gemini

1. Open [Google AI Studio Extensions](https://aistudio.google.com/app/extensions).
2. Create a new extension “From OpenAPI”, pointing to `extensions/gemini/openapi.yaml` (host the raw file or paste the contents).
3. Set auth = “API key” (Cloud Run can enforce this via a header check or IAM; leave blank if you want anyone to call it).
4. Enable the extension inside your Gemini chat/app. Gemini will call your HTTPS URL whenever it needs adversarial planning.

## Applying the Same Package Elsewhere

- **Cursor MCP Gallery / Claude Tool Hub** – submit the OpenAPI spec plus short description and point them at the Cloud Run (or other) URL.
- **Hugging Face Agents / LangChain ToolHub** – wrap `agent_act` as a tool definition that forwards to your hosted endpoint.

See `extensions/gemini/server/README.md` for deployment details and `docs/marketplaces.md` for other listing requirements.


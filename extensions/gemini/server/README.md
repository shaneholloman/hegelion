# Railway Deployment (FastAPI)

This folder packages a FastAPI server that exposes the `/agent_act` endpoint for Gemini extensions or any other marketplace that accepts an HTTP tool.

## Local test

```bash
cd extensions/gemini/server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp env.sample .env   # fill in provider + API keys
uvicorn extensions.gemini.server.app:app --reload
```

Call it:

```bash
curl -X POST http://127.0.0.1:8000/agent_act \
  -H "Content-Type: application/json" \
  -d '{"observation":"CI fails on Python 3.12","goal":"Fix CI","coding":true}'
```

## Deploy to Cloud Run

```bash
PROJECT=hegelion-agent
REGION=us-central1

gcloud config set project $PROJECT
gcloud builds submit --tag gcr.io/$PROJECT/hegelion-agent extensions/gemini/server
gcloud run deploy hegelion-agent \
  --image gcr.io/$PROJECT/hegelion-agent \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars HEGELION_PROVIDER=anthropic,HEGELION_MODEL=claude-3-5-sonnet-20241022
# add API keys if desired:
gcloud run services update hegelion-agent \
  --region $REGION \
  --update-env-vars ANTHROPIC_API_KEY=sk-ant-...
```

Cloud Run returns a URL like `https://hegelion-agent-abc123-uc.a.run.app`. Update the OpenAPI spec (or Gemini config) to use that URL.


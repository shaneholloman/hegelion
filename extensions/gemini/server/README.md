# Prompt-Driven FastAPI Service

This service wraps Hegelion’s **prompt MCP tools** (dialectical workflow, single-shot prompt, thesis/antithesis/synthesis). It never calls an LLM itself, so no API keys or paid plans are required.

## Local test

```bash
cd extensions/gemini/server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn extensions.gemini.server.app:app --reload
```

Call it:

```bash
curl -X POST http://127.0.0.1:8000/dialectical_workflow \
  -H "Content-Type: application/json" \
  -d '{"query":"Is AI conscious?","use_council":true}'
```

### Render (recommended free option)

In the Render dashboard → “Create Web Service”:

- **Repository root:** this repo
- **Build Command:** `pip install -r extensions/gemini/server/requirements.txt`
- **Start Command:** `uvicorn extensions.gemini.server.app:app --host 0.0.0.0 --port $PORT`
- **Environment:** leave empty (no secrets needed)

Render will give you a URL like `https://hegelion-prompt.onrender.com`.

### Cloud Run (optional)

```bash
PROJECT=hegelion-prompt
REGION=us-central1

gcloud config set project $PROJECT
gcloud builds submit --tag gcr.io/$PROJECT/hegelion-prompt extensions/gemini/server
gcloud run deploy hegelion-prompt \
  --image gcr.io/$PROJECT/hegelion-prompt \
  --region $REGION \
  --allow-unauthenticated
```

Cloud Run returns a URL like `https://hegelion-prompt-abc123-uc.a.run.app`.

Use whichever URL you deploy in `extensions/gemini/openapi.yaml` (or host the spec elsewhere) when registering the Google Gemini extension.


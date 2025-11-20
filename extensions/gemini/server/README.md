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

## Railway deployment

```bash
cd extensions/gemini/server
railway init                             # or: railway link <project-id>
railway variables set HEGELION_PROVIDER=anthropic
railway variables set HEGELION_MODEL=claude-3-5-sonnet-20241022
railway variables set ANTHROPIC_API_KEY=sk-ant-...
# add OPENAI_API_KEY, GOOGLE_API_KEY, etc. if needed
railway up --service hegelion-agent \
  --build-cmd "pip install -r requirements.txt" \
  --start-cmd "uvicorn extensions.gemini.server.app:app --host 0.0.0.0 --port \$PORT"
```

Railway will print a URL like `https://hegelion-agent.up.railway.app`. Use that in `extensions/gemini/openapi.yaml` or when registering the Gemini extension inside Google AI Studio.


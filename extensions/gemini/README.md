# Google Gemini Extension for Hegelion

> **Note:** This is a backend API service for HTTP/OpenAPI integrations. It is not a web UI—for that, use the MCP server directly in Claude Desktop, Cursor, or VS Code.

This directory packages everything you need to expose Hegelion's dialectical agent as a Google Gemini extension (and any other marketplace that accepts OpenAPI specs).

## Architecture Overview

1. **FastAPI service (`server/app.py`)** – calls the prompt-driven MCP logic (`dialectical_workflow`, `dialectical_single_shot`, `thesis/antithesis/synthesis`) and returns prompts/JSON.  
   No API keys are needed because *the caller’s LLM* executes the prompts.
2. **Containerized deployment (Dockerfile)** – run it on any platform with Python containers (Render free tier, Cloud Run, Fly.io, etc.).
3. **OpenAPI Spec (`openapi.yaml`)** – register the HTTP tools with Google Gemini or other marketplaces.

## Local Development

```bash
cd extensions/gemini/server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp env.sample .env   # fill in provider + API keys
uvicorn extensions.gemini.server.app:app --reload
```

### HTTP Endpoints

| Route | Description | Returns |
|-------|-------------|---------|
| `POST /dialectical_workflow` | Structured JSON workflow (thesis → antithesis → synthesis, optional council/judge) | `{ "workflow": {...} }` |
| `POST /dialectical_single_shot` | One massive prompt for end-to-end reasoning | `PromptResponse` |
| `POST /thesis_prompt` / `antithesis_prompt` / `synthesis_prompt` | Phase-specific prompts with instructions and expected format | `PromptResponse` (council antithesis returns a list) |

## Deploy to Render (free tier example)

```bash
# From repo root
cd extensions/gemini/server
render login               # if needed

# Render Web Service settings
Build Command: pip install -r extensions/gemini/server/requirements.txt
Start Command: uvicorn extensions.gemini.server.app:app --host 0.0.0.0 --port $PORT
Root Directory: .
```

No environment variables are required—the service never calls external LLM APIs. Render will give you a URL like `https://hegelion-prompt.onrender.com`. Update `extensions/gemini/openapi.yaml` (or host the spec elsewhere) to point at that URL.

## Deploy to Cloud Run (optional)

If you prefer Google Cloud:

```bash
gcloud config set project HEGELION_PROJECT
gcloud builds submit --tag gcr.io/HEGELION_PROJECT/hegelion-prompt extensions/gemini/server
gcloud run deploy hegelion-prompt \
  --image gcr.io/HEGELION_PROJECT/hegelion-prompt \
  --region us-central1 \
  --allow-unauthenticated
```

Cloud Run returns a URL (`https://hegelion-prompt-abc123-uc.a.run.app`)—use that in the OpenAPI spec.

## Register with Google Gemini

1. Open [Google AI Studio Extensions](https://aistudio.google.com/app/extensions).
2. Create a new extension “From OpenAPI”, pointing to `extensions/gemini/openapi.yaml` (host the raw file or paste the contents).
3. Authentication is optional; you can add a simple header check in FastAPI if needed, but by default the endpoint is public.
4. Enable the extension inside Gemini/Claude/etc. The model will call your URL whenever it needs a prompt workflow.

## Cursor & Claude MCP Quick Add

Use the same repository when you want MCP-native clients (Cursor, Claude Desktop, VS Code) to call Hegelion locally—no HTTP hosting required.

1. Install the package: `pip install hegelion`.
2. **Claude Desktop (macOS):** Run `hegelion-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"`.
3. **Cursor:** Run `hegelion-setup-mcp`, then go to Settings → MCP Servers → *Import JSON*.
4. **Restart required:** Quit and reopen Claude Desktop (or restart Cursor) after modifying the config.
5. Launch the client; both detect the server automatically and expose the `dialectical_*` tools.

See [`docs/MCP.md`](../../docs/MCP.md) for screenshots and additional options (custom paths, multiple servers).

## Applying the Same Package Elsewhere

- **Cursor MCP Gallery / Claude Tool Hub** – submit the OpenAPI spec plus a short description and point them at your hosted prompt API.
- **Hugging Face Agents / LangChain ToolHub** – wrap the dialetical workflow endpoint as a tool definition so any orchestrator can fetch prompts on demand.

See `extensions/gemini/server/README.md` for deployment details and `docs/marketplaces.md` for other listing requirements.


# Google Gemini Extension for Hegelion

This directory packages everything you need to expose Hegelion’s dialectical agent as a Google Gemini extension (and any other marketplace that accepts OpenAPI specs).

## Architecture Overview

1. **Firebase Cloud Function (Python 3.11)** – wraps `HegelionAgent` in an HTTPS endpoint (`POST /agent_act`).
2. **OpenAPI Spec (`openapi.yaml`)** – describes the endpoint for Google AI Studio or other registries.
3. **Deployment Scripts** – Firebase configuration plus instructions for local testing and secret management.

## Quick Start

```bash
cd extensions/gemini/firebase
cp .firebaserc.example .firebaserc   # set your Firebase project ID
python3 -m venv .venv && source .venv/bin/activate
pip install -r functions/requirements.txt
firebase emulators:start --only functions   # optional local test
firebase deploy --only functions:agent_act
```

### Configure Secrets

The function relies on the same environment variables as the CLI (`HEGELION_PROVIDER`, `HEGELION_MODEL`, `ANTHROPIC_API_KEY`, etc). Use Firebase’s secret manager:

```bash
firebase functions:secrets:set ANTHROPIC_API_KEY
firebase deploy --only functions:agent_act
```

## Register with Google Gemini

1. Open [Google AI Studio Extensions](https://aistudio.google.com/app/extensions).
2. Create a new extension “From OpenAPI”, pointing to `extensions/gemini/openapi.yaml` (host it on GitHub raw or Cloud Storage).
3. Set auth = “API key” (Gemini will prompt for the key—use a short token you verify in Firebase, or leave open if you already gate access).
4. Enable the extension inside your Gemini app / chat. Gemini will now call `agent_act` when it needs adversarial planning.

## Applying the Same Package Elsewhere

- **Cursor MCP Gallery / Claude Tool Hub** – submit the OpenAPI spec plus short description and point them at the Firebase HTTPS endpoint.
- **Hugging Face Agents / LangChain ToolHub** – wrap `agent_act` as a tool definition that forwards to the Firebase URL.

See `extensions/gemini/firebase/README.md` for detailed Firebase deployment notes and `docs/marketplaces.md` for other listings.


# Firebase Deployment (Gemini Extension Backend)

This folder contains a ready-to-deploy Cloud Functions for Firebase project that exposes Hegelion’s agent via `POST /agent_act`.

## Prerequisites

- Firebase CLI (`npm install -g firebase-tools`)
- Python 3.11
- A Firebase project with billing enabled (required for outbound API calls)

## Setup

```bash
cd extensions/gemini/firebase
cp .firebaserc.example .firebaserc   # replace with your project ID
python3 -m venv .venv && source .venv/bin/activate
pip install -r functions/requirements.txt
```

## Local Testing

```bash
firebase emulators:start --only functions
# Send a request:
curl -X POST http://127.0.0.1:5001/PROJECT/REGION/agent_act \
  -H "Content-Type: application/json" \
  -d '{"observation":"CI fails on Python 3.12","coding":true,"goal":"Fix CI"}'
```

## Secrets / Environment Variables

Set LLM keys the same way you would for the CLI:

```bash
firebase functions:secrets:set ANTHROPIC_API_KEY
firebase functions:secrets:set OPENAI_API_KEY
firebase functions:secrets:set HEGELION_PROVIDER   # e.g. anthropic
firebase functions:secrets:set HEGELION_MODEL      # e.g. claude-3-5-sonnet
```

Redeploy after updating secrets; Firebase automatically injects them as environment variables.

## Deploy

```bash
firebase deploy --only functions:agent_act
```

The HTTPS endpoint will be printed on success (format: `https://REGION-PROJECT_ID.cloudfunctions.net/agent_act`).

## Wiring into Google Gemini

Use the OpenAPI file at `extensions/gemini/openapi.yaml` (host it somewhere accessible, e.g., GitHub raw URL). In Google AI Studio → Extensions → “Import from OpenAPI”, paste the URL, provide an auth token if desired, and enable the extension inside your Gemini chat/app.


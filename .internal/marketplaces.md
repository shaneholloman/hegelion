# Agent & MCP Marketplaces

Use this checklist to publish Hegelion beyond MCP-aware IDEs.

## Google Gemini Extensions (AI Studio)

**Goal:** register the hosted FastAPI prompt server so Gemini models can fetch dialectical workflows on demand.

> **Note:** This is optional and separate from the main MCP server. Gemini Extensions require an HTTP API, so we provide a FastAPI wrapper in `extensions/gemini/server`.

1. Deploy `extensions/gemini/server` to any Python hosting (Cloud Run, Railway, Fly.io, etc.). Example:
   ```bash
   cd extensions/gemini/server
   pip install -r requirements.txt
   uvicorn app:app --host 0.0.0.0 --port $PORT
   ```
   Confirm it responds via `curl https://<host>/health`.
2. Host `extensions/gemini/openapi.yaml` (GitHub raw link or any static bucket) and update the `servers` URL to your deployment.
3. AI Studio → Extensions → **Import from OpenAPI**, paste the hosted spec URL, and click **Validate**.
4. Fill the listing metadata (logo, category, description). Auth is optional; leave public for smooth review.
5. Test inside Gemini by enabling the extension and running `use tool hegelion_workflow`.

✅ **Submission packet:** hosted URL, OpenAPI, screenshots of the FastAPI health check.

## Cursor MCP Gallery

**Goal:** make Cursor users add Hegelion in two clicks via the MCP gallery.

1. Ensure `pip install hegelion` works (CI already publishes wheels).
2. Generate the MCP config snippet locally: `hegelion-setup-mcp --write ./cursor-mcp.json`.
3. Submit to <https://cursor.directory> with: name **Hegelion**, category **Reasoning**, install command `pip install hegelion && hegelion-setup-mcp`.
4. Include the JSON snippet so their reviewers can copy/paste into Settings → MCP Servers.
5. Optional but encouraged: attach a 20s Loom/GIF showing `dialectical_workflow` running in Cursor.

✅ **Submission packet:** repo link, config snippet, screenshot/video.

## Anthropic Claude MCP Hub (Beta)

**Goal:** provide Claude Desktop users with the same MCP server via Anthropic’s directory.

1. Run `hegelion-setup-mcp --write ~/.claude_desktop_config.json` and verify Claude launches with `hegelion` listed under Tools.
2. Prepare collateral: 512×512 PNG logo, one-line pitch (“Adversarial dialectic prompt server”), GitHub link, contact email.
3. Fill <https://www.anthropic.com/mcp-tools> with the above plus a short demo clip (optional).
4. In the notes, mention compatibility with Gemini extensions + Cursor gallery to highlight multi-platform coverage.
5. After approval, add their listing URL back into this doc for tracking.

✅ **Submission packet:** config snippet, logo, repo/docs links, contact email, (optional) demo video.

## Hugging Face Tools / Agents

- Option 1: Publish as a “Tool” on https://huggingface.co/tools
  - Wrap your hosted endpoint using their Python SDK
  - Provide README snippet + license
- Option 2: Create a Space demonstrating the agent and link to PyPI package.

## LangChain / LlamaIndex Tool Registries

- Package a simple tool definition referencing your hosted endpoint (or directly instantiate `HegelionAgent`)
- Submit to:
  - https://smith.langchain.com/hub (LangChain Hub)
  - https://docs.llamaindex.ai/en/stable/tool/index.html#tool-gallery (email form)

## Tracking

- [ ] Google Gemini extension live
- [ ] Cursor listing approved
- [ ] Anthropic hub submission sent
- [ ] Hugging Face tool card published
- [ ] LangChain / LlamaIndex tool entry merged

Update this file as each marketplace is completed.


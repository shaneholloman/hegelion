# Agent & MCP Marketplaces

Use this checklist to publish Hegelion beyond MCP-aware IDEs.

## Google Gemini Extensions (AI Studio)

- Endpoint: Cloud Run (or any HTTPS host) FastAPI service (`extensions/gemini/server`)
- Spec: `extensions/gemini/openapi.yaml`
- Submission: AI Studio → Extensions → “Import from OpenAPI”
- Auth: Optional API key header validated in FastAPI (or use IAM)

## Cursor MCP Gallery

- Listing: https://cursor.directory (submit GitHub repo + short description)
- Requirements:
  - Public repo with README screenshots/gifs
  - MCP config snippet (already in `README.md`)
  - Optional short demo video
- Action: open PR/issue on their directory with:
  - Server name: `hegelion`
  - Install command: `pip install hegelion && hegelion-setup-mcp`

## Anthropic Claude MCP Hub (Beta)

- Submission form: https://www.anthropic.com/mcp-tools (requires short survey)
- Provide:
  - Tool name + logo (PNG 512×512)
  - One-liner value prop (“Adversarial dialectic agent”)
  - GitHub repo link + docs (link to `docs/MCP.md`)
  - Contact email for verification
- Optional: include the Railway-hosted OpenAPI endpoint to showcase Gemini compatibility.

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


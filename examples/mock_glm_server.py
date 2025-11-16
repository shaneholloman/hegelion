#!/usr/bin/env python3
"""
Local stub server that mimics the GLM OpenAI-compatible API for demo recordings.

It responds to /v1/chat/completions requests with deterministic content that
resembles the thesis → antithesis → synthesis flow plus the disagreement
classifier call used for conflict scoring.
"""

from __future__ import annotations

import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict


THESIS_TEXT = """THESIS: Synthetic creativity emerges when AI systems leverage vast pattern libraries to recombine concepts in ways no human archive ever attempted.

They operate as catalytic partners, surfacing analogies between distant fields, composing drafts at post-human speed, and handing humans a lattice of novel starting points. In this view, originality is not an intrinsic soul but a property of systems that continuously mutate inputs into meaningful, testable artifacts."""

ANTITHESIS_TEXT = """ANTITHESIS: Declaring AI "genuinely creative" confuses recombination with authorship.

CONTRADICTION: Creativity demands situated intention — stochastic sampling lacks commitments.
EVIDENCE: GLM tuning objectives optimize for pattern fidelity, not the felt urgency artists describe.

CONTRADICTION: The thesis overstates novelty by ignoring training provenance.
EVIDENCE: Every celebrated output statistically regresses toward data it absorbed; the model cannot cite a motivating purpose.

CONTRADICTION: Equating speed with creativity erases accountability.
EVIDENCE: When an AI output harms or plagiarizes, we appeal to human editors, proving the system is a tool, not a peer."""

SYNTHESIS_TEXT = """SYNTHESIS: Treat AI as a co-creative instrument: the machine excels at breadth, humans arbitrate meaning.

The genuinely creative moment is the negotiation where a human reframes model suggestions against lived context. Instead of granting AI artistic personhood, we can document who curates prompts, who edits drafts, and how responsibility flows through the pipeline.

RESEARCH_PROPOSAL: Track attribution in human+AI studios across multiple projects.
TESTABLE_PREDICTION: Teams that log prompt lineage and editorial choices will ship artifacts reviewers rate as more original than purely human or purely automated baselines."""

CONFLICT_JSON = '{"conflict": 0.82}'


def completion_payload(content: str) -> Dict[str, Any]:
    """Build a minimal OpenAI-style completion payload."""
    token_count = max(1, len(content.split()))
    return {
        "id": "chatcmpl-mock-hegelion-demo",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "glm-4.6-mock",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content,
                },
                "finish_reason": "stop",
                "logprobs": None,
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": token_count,
            "total_tokens": token_count,
        },
    }


class MockGLMHandler(BaseHTTPRequestHandler):
    """Simple handler that returns deterministic completions."""

    server_version = "MockGLM/0.1"

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/v1/chat/completions":
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON body")
            return

        messages = payload.get("messages") or []
        last_message = ""
        if messages:
            content_field = messages[-1].get("content", "")
            if isinstance(content_field, str):
                last_message = content_field
            elif isinstance(content_field, list):
                segments = []
                for item in content_field:
                    if isinstance(item, dict):
                        text_value = item.get("text")
                        if isinstance(text_value, str):
                            segments.append(text_value)
                last_message = "\n".join(segments)
            else:
                last_message = str(content_field)

        lower_content = last_message.lower()

        if "antithesis phase" in lower_content:
            reply = ANTITHESIS_TEXT
        elif "synthesis phase" in lower_content:
            reply = SYNTHESIS_TEXT
        elif "thesis phase" in lower_content:
            reply = THESIS_TEXT
        elif "disagreement classifier" in lower_content:
            reply = CONFLICT_JSON
        else:
            reply = (
                "This is a deterministic mock GLM response used for offline demos. "
                "Add more phase-specific heuristics if you need different content."
            )

        body = json.dumps(completion_payload(reply)).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        """Silence default logging to keep demo output clean."""
        return


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the mock server."""
    server = ThreadingHTTPServer((host, port), MockGLMHandler)
    print(f"Mock GLM server listening on http://{host}:{port}/v1/chat/completions")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down mock server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()


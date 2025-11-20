"""Firebase HTTP function that exposes the Hegelion agent."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Tuple

from hegelion.agent import HegelionAgent

JSON_HEADERS = {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}

DEFAULT_ITERATIONS = int(os.getenv("HEGELION_DEFAULT_ITERATIONS", "1"))


def _error(message: str, status: int) -> Tuple[str, int, Dict[str, str]]:
    payload = json.dumps({"error": message}, ensure_ascii=False)
    return payload, status, JSON_HEADERS


def _build_agent(payload: Dict[str, Any]) -> HegelionAgent:
    base_kwargs = {
        "goal": payload.get("goal"),
        "personas": payload.get("personas"),
        "iterations": int(payload.get("iterations") or DEFAULT_ITERATIONS),
        "use_search": bool(payload.get("use_search", False)),
        "debug": bool(payload.get("debug", False)),
    }

    if payload.get("coding"):
        return HegelionAgent.for_coding(**base_kwargs)
    return HegelionAgent(**base_kwargs)


def agent_act(request):
    """Cloud Function entrypoint."""

    if request.method == "OPTIONS":
        return ("", 204, JSON_HEADERS)

    try:
        payload = request.get_json(force=True, silent=False)
    except Exception:  # pragma: no cover - firebase handles logging
        return _error("Invalid JSON payload.", 400)

    if not isinstance(payload, dict):
        return _error("Payload must be a JSON object.", 400)

    observation = payload.get("observation")
    if not observation:
        return _error("'observation' is required.", 400)

    try:
        agent = _build_agent(payload)
        step = agent.act_sync(observation)
    except Exception as exc:  # pragma: no cover - surfaced to client
        return _error(f"Agent failure: {exc}", 500)

    response = {"action": step.action, "result": step.result.to_dict()}
    return json.dumps(response, ensure_ascii=False), 200, JSON_HEADERS

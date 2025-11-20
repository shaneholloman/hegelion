"""FastAPI wrapper to expose the Hegelion agent over HTTP."""

from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from hegelion.agent import HegelionAgent

DEFAULT_ITERATIONS = int(os.getenv("HEGELION_DEFAULT_ITERATIONS", "1"))


class AgentActRequest(BaseModel):
    """Request payload for /agent_act."""

    observation: str = Field(..., description="Current state that needs the next action.")
    goal: Optional[str] = Field(None, description="Optional high-level mission.")
    personas: Optional[str] = Field(None, description="Critic preset, e.g., council.")
    iterations: Optional[int] = Field(
        None, ge=1, description="Refinement loops (Synthesis → new Thesis)."
    )
    use_search: bool = Field(False, description="Encourage critics to call tools / search.")
    coding: bool = Field(False, description="Use the coding-specific agent wrapper.")
    debug: bool = Field(False, description="Include debug traces in the dialectic.")


class AgentActResponse(BaseModel):
    """Response payload returned by /agent_act."""

    action: str
    result: dict


app = FastAPI(
    title="Hegelion Agent API",
    description="Dialects-first agent: Thesis → Antithesis → Synthesis before acting.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_agent(payload: AgentActRequest) -> HegelionAgent:
    base_kwargs = {
        "goal": payload.goal,
        "personas": payload.personas,
        "iterations": payload.iterations or DEFAULT_ITERATIONS,
        "use_search": payload.use_search,
        "debug": payload.debug,
    }
    if payload.coding:
        return HegelionAgent.for_coding(**base_kwargs)
    return HegelionAgent(**base_kwargs)


@app.get("/health")
async def health() -> dict:
    """Simple readiness probe."""

    return {"status": "ok"}


@app.post("/agent_act", response_model=AgentActResponse)
async def agent_act(request: AgentActRequest) -> AgentActResponse:
    """Run a full dialectical step and return the survived action."""

    try:
        agent = build_agent(request)
        step = await agent.act(request.observation)
    except Exception as exc:  # pragma: no cover - surfaced to client
        raise HTTPException(status_code=500, detail=f"Agent failure: {exc}") from exc

    return AgentActResponse(action=step.action, result=step.result.to_dict())

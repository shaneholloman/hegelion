"""FastAPI wrapper that exposes prompt-driven dialectical tools."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from hegelion.prompt_dialectic import (
    PromptDrivenDialectic,
    create_dialectical_workflow,
    create_single_shot_dialectic_prompt,
)


app = FastAPI(
    title="Hegelion Prompt API",
    description="Returns prompt scaffolds for Hegelion's Thesis → Antithesis → Synthesis workflow.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WorkflowRequest(BaseModel):
    query: str = Field(..., description="Question or topic to analyze.")
    use_search: bool = False
    use_council: bool = False
    use_judge: bool = False


class WorkflowResponse(BaseModel):
    workflow: dict


class SingleShotRequest(BaseModel):
    query: str
    use_search: bool = False
    use_council: bool = False


class PromptResponse(BaseModel):
    phase: str | None = None
    prompt: str
    instructions: str | None = None
    expected_format: str | None = None


class CouncilPromptResponse(BaseModel):
    prompts: list[PromptResponse]


class ThesisRequest(BaseModel):
    query: str


class AntithesisRequest(BaseModel):
    query: str
    thesis: str
    use_search: bool = False
    use_council: bool = False


class SynthesisRequest(BaseModel):
    query: str
    thesis: str
    antithesis: str


@app.get("/health")
async def health() -> dict:
    """Simple readiness probe."""

    return {"status": "ok"}


@app.post("/dialectical_workflow", response_model=WorkflowResponse)
async def dialectical_workflow(request: WorkflowRequest) -> WorkflowResponse:
    """Return a structured workflow that any LLM can execute."""

    workflow = create_dialectical_workflow(
        query=request.query,
        use_search=request.use_search,
        use_council=request.use_council,
        use_judge=request.use_judge,
    )
    return WorkflowResponse(workflow=workflow)


@app.post("/dialectical_single_shot", response_model=PromptResponse)
async def single_shot(request: SingleShotRequest) -> PromptResponse:
    """Return one massive prompt for models that can handle the full loop."""

    prompt = create_single_shot_dialectic_prompt(
        query=request.query,
        use_search=request.use_search,
        use_council=request.use_council,
    )
    return PromptResponse(prompt=prompt)


@app.post("/thesis_prompt", response_model=PromptResponse)
async def thesis_prompt(request: ThesisRequest) -> PromptResponse:
    dialectic = PromptDrivenDialectic()
    prompt_obj = dialectic.generate_thesis_prompt(request.query)
    return PromptResponse(prompt=prompt_obj.prompt)


@app.post("/antithesis_prompt", response_model=PromptResponse)
async def antithesis_prompt(request: AntithesisRequest) -> PromptResponse:
    dialectic = PromptDrivenDialectic()
    try:
        if request.use_council:
            council = dialectic.generate_council_prompts(request.query, request.thesis)
            rendered = "\n\n".join(f"## {prompt.phase}\n{prompt.prompt}" for prompt in council)
            return PromptResponse(prompt=rendered)
        prompt_obj = dialectic.generate_antithesis_prompt(
            request.query, request.thesis, use_search_context=request.use_search
        )
        return PromptResponse(prompt=prompt_obj.prompt)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/synthesis_prompt", response_model=PromptResponse)
async def synthesis_prompt(request: SynthesisRequest) -> PromptResponse:
    dialectic = PromptDrivenDialectic()
    prompt_obj = dialectic.generate_synthesis_prompt(
        request.query, request.thesis, request.antithesis
    )
    return PromptResponse(prompt=prompt_obj.prompt)

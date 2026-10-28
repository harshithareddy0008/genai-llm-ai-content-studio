"""AI Content Studio REST API: http://127.0.0.1:8000/docs"""
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from backend.dependencies import get_gemini_service, verify_app_token
from backend.schemas import (
    ChatRequest,
    ChatResponse,
    GenerateRequest,
    GenerateResponse,
)
from backend.services.llm_service import (
    GeminiService,
    LLMProviderError,
    MissingAPIKeyError,
)

app = FastAPI(
    title="AI Content Studio API",
    description="A plain LLM application powered by Google Gemini (no RAG or agents).",
    version="1.0.0",
)


@app.exception_handler(MissingAPIKeyError)
async def missing_key_handler(_request, _exc: MissingAPIKeyError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Gemini API key is not configured on the server."},
    )


@app.get("/", tags=["health"])
def root():
    return {"service": "AI Content Studio API", "docs": "/docs", "status": "ok"}


@app.get("/health", tags=["health"])
def health():
    # Health reflects process availability only, not Gemini account readiness.
    return {"status": "ok"}


@app.post(
    "/generate",
    response_model=GenerateResponse,
    tags=["generation"],
    dependencies=[Depends(verify_app_token)],
)
def generate_content(
    request: GenerateRequest,
    llm: GeminiService = Depends(get_gemini_service),
):
    try:
        generated = llm.generate(request)
    except LLMProviderError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return GenerateResponse(task=request.task, generated_text=generated, model=llm.model)


@app.post(
    "/chat",
    response_model=ChatResponse,
    tags=["chat"],
    dependencies=[Depends(verify_app_token)],
)
def chat(
    request: ChatRequest,
    llm: GeminiService = Depends(get_gemini_service),
):
    try:
        reply = llm.chat(request)
    except LLMProviderError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return ChatResponse(reply=reply, model=llm.model)

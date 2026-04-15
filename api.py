"""
FastAPI wrapper around the LangGraph agent pipeline.

Exposes a single POST /api/chat endpoint that the React frontend calls.
Runs graph.invoke() in a threadpool so the event loop stays responsive.

Start with:  uvicorn api:app --reload --port 8000
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.graph import run_agent

logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)

# React agent id → LangGraph forced_intent.  "master" means no forced intent —
# let the intent_detector route it.
AGENT_TO_INTENT: dict[str, str] = {
    "hr": "hr_general",
    "qa": "qa_technical",
    "security": "sensitive_info",
    "master": "",
}

app = FastAPI(title="ICE QAgent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    agent: Literal["hr", "qa", "security", "master"] = "master"
    chat_history: list[ChatHistoryItem] = Field(default_factory=list)


class SourceItem(BaseModel):
    name: str = ""
    score: float = 0.0
    content: str = ""


class ReasoningStep(BaseModel):
    step: str = ""
    detail: str = ""


class ChatResponse(BaseModel):
    response: str
    agent: str = ""
    intent: str = ""
    confidence: float = 0.0
    sources: list[SourceItem] = Field(default_factory=list)
    reasoning_trace: list[ReasoningStep] = Field(default_factory=list)
    used_web_search: bool = False
    guardrail_blocked: bool = False
    threat_level: str = "NONE"


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "ice-qagent-api"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    forced_intent = AGENT_TO_INTENT[req.agent]
    history_payload = [item.model_dump() for item in req.chat_history[-6:]]

    logger.info(
        "[chat] agent=%s forced_intent=%r history_len=%d query=%r",
        req.agent,
        forced_intent,
        len(history_payload),
        req.query[:120],
    )

    try:
        result = await asyncio.to_thread(
            run_agent,
            query=req.query,
            chat_history=history_payload,
            forced_intent=forced_intent or None,
        )
    except Exception as exc:
        logger.exception("[chat] run_agent failed")
        raise HTTPException(status_code=500, detail=f"Agent pipeline failed: {exc}") from exc

    sources_raw = result.get("sources") or []
    sources: list[SourceItem] = []
    for s in sources_raw:
        if isinstance(s, dict):
            sources.append(
                SourceItem(
                    name=str(s.get("name", s.get("source", ""))),
                    score=float(s.get("score", 0.0) or 0.0),
                    content=str(s.get("content", s.get("snippet", "")))[:600],
                )
            )

    trace_raw = result.get("reasoning_trace") or []
    trace: list[ReasoningStep] = []
    for t in trace_raw:
        if isinstance(t, dict):
            trace.append(
                ReasoningStep(
                    step=str(t.get("step", "")),
                    detail=str(t.get("detail", "")),
                )
            )

    return ChatResponse(
        response=str(result.get("response", "")),
        agent=str(result.get("agent", "")),
        intent=str(result.get("intent", "")),
        confidence=float(result.get("confidence", 0.0) or 0.0),
        sources=sources,
        reasoning_trace=trace,
        used_web_search=bool(result.get("used_web_search", False)),
        guardrail_blocked=bool(result.get("guardrail_blocked", False)),
        threat_level=str(result.get("threat_level", "NONE")),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=int(os.environ.get("API_PORT", "8000")),
        reload=True,
    )

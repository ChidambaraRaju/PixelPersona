"""FastAPI routes for persona chat."""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional
import asyncio
import logging

from pixelpersona.models.persona import AVAILABLE_PERSONAS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PixelPersona API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CORS headers added to all responses via middleware
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

# In-memory agent store (per V1 scope - no multi-user)
agents: Dict[str, any] = {}

class ChatRequest(BaseModel):
    query: str
    thread_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    persona_name: str
    response: str

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/personas")
async def list_personas():
    """List all available personas. Frontend calls this to populate persona selection."""
    return {"personas": AVAILABLE_PERSONAS}

@app.post("/chat", response_model=ChatResponse)
async def chat(
    persona_name: str = Query(..., description="Name of the persona to chat with"),
    request: ChatRequest = None
):
    """Non-streaming chat endpoint (for simple requests)."""
    from pixelpersona.agents.persona_agent import PersonaAgent

    # Validate persona exists
    if persona_name not in AVAILABLE_PERSONAS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown persona: '{persona_name}'. Available: {list(AVAILABLE_PERSONAS.keys())}"
        )

    # Get or create agent for persona (lazy load)
    if persona_name not in agents:
        agents[persona_name] = PersonaAgent(
            persona_name=persona_name,
            persona_description=AVAILABLE_PERSONAS[persona_name]
        )

    agent = agents[persona_name]

    try:
        response = await agent.chat(
            query=request.query,
            thread_id=request.thread_id
        )
    except Exception as e:
        logger.error(f"[CHAT ERROR] {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(
        persona_name=persona_name,
        response=response
    )

@app.post("/chat/stream")
async def chat_stream(
    persona_name: str = Query(..., description="Name of the persona to chat with"),
    request: ChatRequest = None
):
    """Streaming chat endpoint using SSE.

    Frontend passes persona_name as query parameter.
    Example: POST /chat/stream?persona_name=Albert%20Einstein
    """
    from fastapi.responses import StreamingResponse
    from pixelpersona.agents.persona_agent import PersonaAgent

    # Validate persona exists
    if persona_name not in AVAILABLE_PERSONAS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown persona: '{persona_name}'. Available: {list(AVAILABLE_PERSONAS.keys())}"
        )

    # Get or create agent for persona (lazy load)
    if persona_name not in agents:
        agents[persona_name] = PersonaAgent(
            persona_name=persona_name,
            persona_description=AVAILABLE_PERSONAS[persona_name]
        )

    agent = agents[persona_name]

    async def generate():
        try:
            response = await agent.chat(
                query=request.query,
                thread_id=request.thread_id
            )
            # Yield full response (chunked for SSE)
            for i in range(0, len(response), 50):
                chunk = response[i:i+50]
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"[STREAM ERROR] {type(e).__name__}: {e}")
            yield f"data: [ERROR] {str(e)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )

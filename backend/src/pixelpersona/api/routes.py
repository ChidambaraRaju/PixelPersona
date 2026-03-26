"""FastAPI routes for persona chat."""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import asyncio

from pixelpersona.models.persona import AVAILABLE_PERSONAS

app = FastAPI(title="PixelPersona API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    response = await agent.chat(
        query=request.query,
        thread_id=request.thread_id
    )

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
        # Yield persona name first
        yield f"data: {persona_name}\n\n"

        # Stream response chunks
        try:
            response = await agent.chat(
                query=request.query,
                thread_id=request.thread_id
            )
            # Yield full response (chunked for SSE)
            for i in range(0, len(response), 50):
                chunk = response[i:i+50]
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.01)
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
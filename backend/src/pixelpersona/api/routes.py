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

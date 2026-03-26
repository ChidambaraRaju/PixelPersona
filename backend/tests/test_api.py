"""Tests for FastAPI routes."""
import pytest
from fastapi.testclient import TestClient
from pixelpersona.api.routes import app
from pixelpersona.models.persona import AVAILABLE_PERSONAS

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_list_personas():
    response = client.get("/personas")
    assert response.status_code == 200
    personas = response.json()["personas"]
    assert "Albert Einstein" in personas
    assert len(personas) == 4  # V1 has 4 personas

def test_chat_requires_persona_name():
    """Chat endpoint should reject requests without persona_name query param."""
    response = client.post("/chat", json={"query": "Hello"})
    assert response.status_code == 422  # Missing required parameter

def test_chat_with_unknown_persona():
    """Chat endpoint should reject unknown personas."""
    response = client.post(
        "/chat?persona_name=Unknown%20Persona",
        json={"query": "Hello"}
    )
    assert response.status_code == 400
    assert "Unknown persona" in response.json()["detail"]

def test_chat_stream_requires_persona_name():
    """Stream endpoint should reject requests without persona_name query param."""
    response = client.post("/chat/stream", json={"query": "Hello"})
    assert response.status_code == 422  # Missing required parameter
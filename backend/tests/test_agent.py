"""Tests for persona agent."""
import pytest
import os
from pixelpersona.agents.persona_agent import PersonaAgent

# Skip tests if no GROQ_API_KEY is set
requires_groq = pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set"
)

@pytest.fixture
def agent():
    if not os.getenv("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY not set", allow_module_level=True)
    return PersonaAgent(persona_name="Albert Einstein")

@pytest.mark.asyncio
async def test_agent_create_with_config(agent):
    assert agent.persona_name == "Albert Einstein"
    assert agent.agent is not None
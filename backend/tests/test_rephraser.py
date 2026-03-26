"""Tests for query rephraser."""
import pytest
import os
from pixelpersona.retrieval.rephraser import QueryRephraser

@pytest.fixture
def rephraser():
    if not os.getenv("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY not set", allow_module_level=True)
    return QueryRephraser()

@pytest.mark.asyncio
async def test_rephrase_returns_string(rephraser):
    """Test that rephrase returns a string."""
    result = await rephraser.rephrase("Test query")
    assert isinstance(result, str)

@pytest.mark.asyncio
async def test_rephrase_improves_query(rephraser):
    """Test that rephrase returns a different query."""
    original = "What did Einstein think about war?"
    rephrased = await rephraser.rephrase(original)
    assert len(rephrased) > 5
    assert rephrased != original
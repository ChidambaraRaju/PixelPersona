"""Tests for persona retriever."""
import pytest
import os
from pixelpersona.retrieval.retriever import PersonaRetriever

# Skip tests if no GROQ_API_KEY is set
requires_groq = pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set"
)

@pytest.fixture
def retriever():
    return PersonaRetriever()

@pytest.mark.asyncio
@requires_groq
async def test_retrieve_returns_list(retriever):
    """Test that retrieve returns a list of results."""
    chunks = await retriever.retrieve(
        persona_name="Albert Einstein",
        query="What were Einstein's views on physics?",
        top_k=3
    )
    assert isinstance(chunks, list)

@pytest.mark.asyncio
@requires_groq
async def test_retrieve_with_chroma_data(retriever):
    """Test retrieve with data in Chroma (from ingestion)."""
    # First ingest some test data if not present
    chunks = await retriever.retrieve(
        persona_name="Albert Einstein",
        query="Einstein physics",
        top_k=2
    )
    assert isinstance(chunks, list)
    # If data exists, should return content
    for chunk in chunks:
        assert "content" in chunk
        assert "metadata" in chunk
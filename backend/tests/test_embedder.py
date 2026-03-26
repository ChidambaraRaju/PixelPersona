"""Tests for embedder."""
import pytest
from pixelpersona.processing.embedder import LocalEmbedder

@pytest.fixture
def embedder():
    return LocalEmbedder()

def test_embed_query(embedder):
    """Test single query embedding (embed_query interface)."""
    result = embedder.embed_query("Hello world")
    assert isinstance(result, list)
    assert len(result) == 384  # bge-small dimension

def test_embed_documents(embedder):
    """Test batch document embedding (embed_documents interface)."""
    texts = ["Hello", "World", "Test"]
    results = embedder.embed_documents(texts)
    assert len(results) == 3
    assert all(len(r) == 384 for r in results)

def test_dimension_property(embedder):
    assert embedder.dimension == 384

def test_embed_query_returns_list_of_floats(embedder):
    """Test that embeddings are floats."""
    result = embedder.embed_query("Test")
    assert all(isinstance(x, float) for x in result)
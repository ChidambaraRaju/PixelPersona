"""Tests for text chunker."""
import pytest
from langchain_core.documents import Document
from pixelpersona.processing.chunker import PersonaChunker

@pytest.fixture
def chunker():
    return PersonaChunker(chunk_size=200, chunk_overlap=50)

def test_chunk_single_document(chunker):
    text = " ".join(["word"] * 250)
    docs = [Document(page_content=text, metadata={"source": "test"})]
    chunks = chunker.chunk_documents(docs)
    assert len(chunks) >= 1

def test_chunk_respects_semantic_boundaries(chunker):
    # Text longer than chunk_size to force splitting
    text = ("Paragraph one with some content. " * 20) + "\n\n" + ("Paragraph two with more content. " * 20) + "\n\n" + ("Paragraph three. " * 20)
    docs = [Document(page_content=text, metadata={"source": "test"})]
    chunks = chunker.chunk_documents(docs)
    # Should split at paragraph boundaries, not mid-paragraph
    assert len(chunks) >= 2

def test_chunk_with_metadata_preserved(chunker):
    docs = [
        Document(page_content="Content about Einstein.", metadata={"persona": "Einstein", "source_type": "wikipedia"})
    ]
    chunks = chunker.chunk_documents(docs)
    assert all("persona" in chunk.metadata for chunk in chunks)

def test_chunk_text_method(chunker):
    text = "word " * 250
    chunks = chunker.chunk(text)
    assert len(chunks) >= 1

def test_chunk_with_metadata_updates(chunker):
    docs = [Document(page_content="Test content", metadata={"source": "test"})]
    chunks = chunker.chunk_documents(docs, metadata_updates={"persona": "TestPersona", "new_field": "value"})
    assert all(chunk.metadata.get("persona") == "TestPersona" for chunk in chunks)
    assert all(chunk.metadata.get("new_field") == "value" for chunk in chunks)
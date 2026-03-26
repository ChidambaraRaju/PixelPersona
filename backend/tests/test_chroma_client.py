"""Tests for Chroma client."""
import pytest
from langchain_core.documents import Document
from pixelpersona.processing.embedder import LocalEmbedder
from pixelpersona.storage.chroma_client import PersonaVectorStore, ChromaCollectionManager

@pytest.fixture
def embedder():
    return LocalEmbedder()

@pytest.fixture
def vector_store(temp_data_dir, embedder):
    return PersonaVectorStore(
        persona_name="Albert_Einstein",
        persist_dir=str(temp_data_dir),
        embedding_function=embedder
    )

def test_create_persona_vector_store(vector_store):
    assert vector_store.persona_name == "Albert_Einstein"
    assert vector_store.collection_name == "Albert_Einstein"

def test_add_documents_to_vector_store(vector_store):
    docs = [
        Document(page_content="Test content 1", metadata={"source": "test"}),
        Document(page_content="Test content 2", metadata={"source": "test"})
    ]
    vector_store.add_documents(docs)
    count = vector_store.count()
    assert count == 2

def test_similarity_search(vector_store):
    docs = [
        Document(page_content="Albert Einstein was a physicist.", metadata={"source": "wiki"}),
        Document(page_content="Einstein developed the theory of relativity.", metadata={"source": "wiki"})
    ]
    vector_store.add_documents(docs)

    results = vector_store.similarity_search("Einstein physics", k=2)
    assert len(results) <= 2

def test_chroma_collection_manager(temp_data_dir, embedder):
    manager = ChromaCollectionManager(
        embedding_function=embedder,
        persist_dir=str(temp_data_dir)
    )

    # Add documents
    docs = [Document(page_content="Tesla invented AC power.", metadata={"source": "test"})]
    manager.add_documents("Nikola_Tesla", docs)

    # Verify count
    count = manager.count("Nikola_Tesla")
    assert count == 1

    # Retrieve
    results = manager.similarity_search("Nikola_Tesla", "AC power", k=1)
    assert len(results) <= 1
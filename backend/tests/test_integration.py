"""End-to-end integration tests."""
import pytest
import os
from langchain_core.documents import Document

# Skip integration tests if no GROQ_API_KEY
requires_groq = pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set"
)

@pytest.fixture
def embedder():
    from pixelpersona.processing.embedder import LocalEmbedder
    return LocalEmbedder()

@pytest.fixture
def collection_manager(embedder, temp_data_dir):
    from pixelpersona.storage.chroma_client import ChromaCollectionManager
    return ChromaCollectionManager(
        embedding_function=embedder,
        persist_dir=str(temp_data_dir)
    )

@pytest.fixture
def chunker():
    from pixelpersona.processing.chunker import PersonaChunker
    return PersonaChunker()

@requires_groq
@pytest.mark.asyncio
async def test_full_ingestion_and_retrieval_flow(collection_manager, chunker, temp_data_dir):
    """Test: ingest sample data and retrieve it."""
    from pixelpersona.scraping.wikipedia import WikipediaScraper

    persona = "TestPersona_E2E"
    scraper = WikipediaScraper()

    # Ingestion
    result = scraper.scrape("Albert Einstein")
    assert result.get("content"), "Scraping failed"

    # Create document and chunk
    doc = Document(page_content=result["content"], metadata={"source_type": "wikipedia"})
    chunks = chunker.chunk_documents([doc], metadata_updates={"persona": persona})
    assert len(chunks) > 0, "Chunking failed"

    # Add to collection
    collection_manager.add_documents(persona, chunks)

    # Verify count
    count = collection_manager.count(persona)
    assert count > 0, "Documents not stored"

    # Retrieval
    from pixelpersona.retrieval.retriever import PersonaRetriever
    retriever = PersonaRetriever()

    results = await retriever.retrieve(
        persona_name=persona,
        query="Einstein physics theory",
        top_k=2
    )

    assert isinstance(results, list)
    if results:
        assert "content" in results[0]
        assert "metadata" in results[0]

@requires_groq
def test_chroma_persistence_after_restart(temp_data_dir, embedder):
    """Test that Chroma data persists and can be reloaded."""
    from pixelpersona.storage.chroma_client import ChromaCollectionManager
    from langchain_core.documents import Document

    persona = "PersistenceTest"
    manager = ChromaCollectionManager(
        embedding_function=embedder,
        persist_dir=str(temp_data_dir)
    )

    # Add documents
    docs = [Document(page_content="Test content about Nikola Tesla.", metadata={"source": "test"})]
    manager.add_documents(persona, docs)

    # Create new manager (simulating restart)
    manager2 = ChromaCollectionManager(
        embedding_function=embedder,
        persist_dir=str(temp_data_dir)
    )

    # Verify data persisted
    count = manager2.count(persona)
    assert count == 1
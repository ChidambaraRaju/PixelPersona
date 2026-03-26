"""Retrieval pipeline: rephrase -> embed -> query Chroma."""
from typing import List, Dict, Any
from langchain_core.documents import Document
from pixelpersona.retrieval.rephraser import QueryRephraser
from pixelpersona.processing.embedder import LocalEmbedder
from pixelpersona.storage.chroma_client import ChromaCollectionManager
from pixelpersona.config import TOP_K_CHUNKS

class PersonaRetriever:
    """Retrieves relevant context for a persona query."""

    def __init__(
        self,
        rephraser: QueryRephraser = None,
        embedder: Any = None,
        collection_manager: ChromaCollectionManager = None
    ):
        self.rephraser = rephraser or QueryRephraser()
        self.embedder = embedder or LocalEmbedder()
        # ChromaCollectionManager requires embedding_function
        self.collection_manager = collection_manager or ChromaCollectionManager(
            embedding_function=self.embedder
        )

    async def retrieve(
        self,
        persona_name: str,
        query: str,
        top_k: int = TOP_K_CHUNKS
    ) -> List[Dict[str, Any]]:
        """Retrieve top-k relevant chunks for a persona query."""
        # Step 1: Rephrase query
        rephrased_query = await self.rephraser.rephrase(query)

        # Step 2: Query Chroma using similarity_search
        # The ChromaCollectionManager handles embedding internally
        docs = self.collection_manager.similarity_search(
            persona_name=persona_name,
            query=rephrased_query,
            k=top_k
        )

        # Convert LangChain Documents to dicts for compatibility
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in docs
        ]
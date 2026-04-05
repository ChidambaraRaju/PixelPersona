"""Retrieval pipeline: rephrase -> embed -> query Chroma."""
import logging
from typing import List, Dict, Any
from langchain_core.documents import Document
from pixelpersona.retrieval.rephraser import QueryRephraser
from pixelpersona.processing.embedder import LocalEmbedder
from pixelpersona.storage.chroma_client import ChromaCollectionManager
from pixelpersona.config import TOP_K_CHUNKS

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

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
        logger.info("\n" + "-"*60)
        logger.info("[RETRIEVER] Starting retrieval pipeline")
        logger.info(f"  Original query: {query}")

        # Step 1: Rephrase query to improve retrieval quality
        rephrased_query = await self.rephraser.rephrase(query)
        logger.info(f"  Rephrased query: {rephrased_query}")

        # Step 2: Query Chroma using similarity_search
        # The ChromaCollectionManager handles embedding internally
        docs = self.collection_manager.similarity_search(
            persona_name=persona_name,
            query=rephrased_query,
            k=top_k
        )

        logger.info(f"  Chroma returned: {len(docs)} documents")

        # Convert LangChain Documents to dicts for compatibility
        results = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in docs
        ]

        logger.info("[RETRIEVER] Retrieval complete")
        logger.info("-"*60 + "\n")

        return results
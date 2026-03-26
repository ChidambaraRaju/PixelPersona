"""Local embedding generation using sentence-transformers with LangChain Embeddings interface."""
from typing import List
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from pixelpersona.config import EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE

class LocalEmbedder(Embeddings):
    """Generates embeddings using BAAI/bge-small-en-v1.5.

    Implements LangChain's Embeddings interface for compatibility with
    langchain vector stores like langchain_chroma.Chroma.
    """

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)
        self.batch_size = EMBEDDING_BATCH_SIZE

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query text.

        Part of LangChain's Embeddings interface.
        """
        return self.model.encode(text, normalize_embeddings=True).tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches.

        Part of LangChain's Embeddings interface.
        Optimized batch processing for ingestion efficiency.
        """
        return self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=True,
            show_progress_bar=False
        ).tolist()

    @property
    def dimension(self) -> int:
        """Embedding dimension."""
        return self.model.get_sentence_embedding_dimension()
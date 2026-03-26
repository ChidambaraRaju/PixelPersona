"""Persona vector store using langchain_chroma.Chroma."""
from typing import List, Optional, Any
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
from uuid import uuid4
from pixelpersona.config import CHROMA_PERSIST_DIR

class PersonaVectorStore:
    """LangChain Chroma vector store for a specific persona.

    Wraps langchain_chroma.Chroma with persona-specific collection management.
    Each persona gets their own Chroma collection for cleaner filtering.
    """

    def __init__(
        self,
        persona_name: str,
        embedding_function: Embeddings,
        persist_dir: str = CHROMA_PERSIST_DIR
    ):
        self.persona_name = persona_name
        self.collection_name = persona_name.replace(" ", "_")
        self._embedding_function = embedding_function
        self._persist_dir = persist_dir

        # Initialize langchain_chroma.Chroma for this persona's collection
        self._vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=embedding_function,
            persist_directory=f"{persist_dir}/{self.collection_name}"
        )

    def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None
    ) -> None:
        """Add documents to the persona's collection.

        Embeddings are generated using the provided embedding_function.
        """
        if ids is None:
            ids = [str(uuid4()) for _ in range(len(documents))]

        self._vector_store.add_documents(documents=documents, ids=ids)

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None,
        **kwargs
    ) -> List[Document]:
        """Perform similarity search on the persona's collection."""
        return self._vector_store.similarity_search(
            query=query,
            k=k,
            filter=filter,
            **kwargs
        )

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None,
        **kwargs
    ) -> List[tuple[Document, float]]:
        """Perform similarity search with relevance scores."""
        return self._vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter,
            **kwargs
        )

    def count(self) -> int:
        """Return the number of documents in the collection."""
        return self._vector_store._collection.count()

    def delete(self, ids: Optional[List[str]] = None, **kwargs) -> None:
        """Delete documents from the collection by IDs."""
        if ids:
            self._vector_store.delete(ids=ids, **kwargs)
        else:
            self._vector_store.delete(**kwargs)


class ChromaCollectionManager:
    """Manages multiple PersonaVectorStore instances (one per persona)."""

    def __init__(
        self,
        embedding_function: Embeddings,
        persist_dir: str = CHROMA_PERSIST_DIR
    ):
        self._embedding_function = embedding_function
        self._persist_dir = persist_dir
        self._stores: dict[str, PersonaVectorStore] = {}

    def get_store(self, persona_name: str) -> PersonaVectorStore:
        """Get or create a PersonaVectorStore for the given persona."""
        if persona_name not in self._stores:
            self._stores[persona_name] = PersonaVectorStore(
                persona_name=persona_name,
                embedding_function=self._embedding_function,
                persist_dir=self._persist_dir
            )
        return self._stores[persona_name]

    def add_documents(
        self,
        persona_name: str,
        documents: List[Document],
        ids: Optional[List[str]] = None
    ) -> None:
        """Add documents to a persona's collection."""
        store = self.get_store(persona_name)
        store.add_documents(documents, ids)

    def similarity_search(
        self,
        persona_name: str,
        query: str,
        k: int = 5,
        **kwargs
    ) -> List[Document]:
        """Search documents for a specific persona."""
        store = self.get_store(persona_name)
        return store.similarity_search(query=query, k=k, **kwargs)

    def count(self, persona_name: str) -> int:
        """Get document count for a persona."""
        store = self.get_store(persona_name)
        return store.count()
"""Text chunking using LangChain's RecursiveCharacterTextSplitter."""
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pixelpersona.config import CHUNK_SIZE, CHUNK_OVERLAP

class PersonaChunker:
    """Splits text into overlapping chunks using LangChain's RecursiveCharacterTextSplitter.

    Uses recursive splitting with separators: ["\\n\\n", "\\n", ". ", " ", ""]
    This respects semantic boundaries (paragraphs, sentences) before arbitrary splits.
    """

    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
        separators: List[str] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\\n\\n", "\\n", ". ", " ", ""]
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            add_start_index=True,
            length_function=len  # character-based for better control
        )

    def chunk(self, text: str) -> List[str]:
        """Split a single text string into chunks."""
        if not text.strip():
            return []
        return self._splitter.split_text(text)

    def chunk_documents(
        self,
        documents: List[Document],
        metadata_updates: dict = None
    ) -> List[Document]:
        """Split documents into chunks, preserving and updating metadata.

        Args:
            documents: List of LangChain Document objects
            metadata_updates: Optional dict of metadata to add to all chunks

        Returns:
            List of chunked Document objects with updated metadata
        """
        if not documents:
            return []

        chunks = self._splitter.split_documents(documents)

        # Update metadata on each chunk
        if metadata_updates:
            for chunk in chunks:
                chunk.metadata.update(metadata_updates)

        return chunks

    @property
    def splitter(self) -> RecursiveCharacterTextSplitter:
        """Expose the underlying splitter for advanced use cases."""
        return self._splitter
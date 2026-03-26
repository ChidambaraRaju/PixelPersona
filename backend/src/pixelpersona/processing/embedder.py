"""Local embedding generation using LangChain's HuggingFaceEmbeddings wrapper."""
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from pixelpersona.config import EMBEDDING_MODEL

def LocalEmbedder() -> HuggingFaceEmbeddings:
    """Creates a HuggingFaceEmbeddings instance for BAAI/bge-small-en-v1.5.

    Returns a LangChain HuggingFaceEmbeddings object which implements the
    Embeddings interface and is compatible with langchain vector stores
    like langchain_chroma.Chroma.

    The from_documents method handles embedding automatically.
    """
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True}
    )
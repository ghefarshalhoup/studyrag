"""Vector store setup and management for document retrieval."""

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

from src.config import settings


class VectorStoreManager:
    """Manages the in-memory vector store for document retrieval."""

    def __init__(self, embeddings: Embeddings | None = None):
        """Initialize the vector store. `embeddings` defaults to the configured OpenAI model."""
        self.embeddings = embeddings or OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            openai_api_key=settings.openai_api_key,
        )
        self.vector_store = InMemoryVectorStore(embedding=self.embeddings)
        self._document_count = 0

    def add_documents(self, documents: list[Document]) -> int:
        """Add documents to the vector store and return count added."""
        if not documents:
            return 0

        self.vector_store.add_documents(documents)
        self._document_count += len(documents)
        return len(documents)

    def clear(self) -> None:
        """Clear all documents from the vector store."""
        # Reinitialize the vector store to clear it
        self.vector_store = InMemoryVectorStore(embedding=self.embeddings)
        self._document_count = 0

    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        """Search for similar documents."""
        if self._document_count == 0:
            return []
        return self.vector_store.similarity_search(query, k=k)

    def similarity_search_with_score(
        self, query: str, k: int = 4
    ) -> list[tuple[Document, float]]:
        """Search for similar documents with relevance scores."""
        if self._document_count == 0:
            return []
        return self.vector_store.similarity_search_with_score(query, k=k)

    def as_retriever(self, k: int = 4):
        """Return the vector store as a retriever."""
        return self.vector_store.as_retriever(search_kwargs={"k": k})

    @property
    def document_count(self) -> int:
        """Return the number of documents in the store."""
        return self._document_count

    @property
    def is_empty(self) -> bool:
        """Check if the vector store is empty."""
        return self._document_count == 0

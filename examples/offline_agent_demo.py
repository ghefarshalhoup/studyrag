"""Exercise the real graph with scripted answers and fake embeddings, without API calls.

This is a behavior demonstration, not a retrieval-quality benchmark.
Run from the repository root: python examples/offline_agent_demo.py
"""
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models import FakeListChatModel

from src.memory import ConversationMemory
from src.rag_agent import RAGAgent
from src.vector_store import VectorStoreManager


async def main():
    store = VectorStoreManager(embeddings=DeterministicFakeEmbedding(size=32))
    store.add_documents([Document(
        page_content="Use collections.deque for a FIFO queue; it supports fast appends and pops at both ends.",
        metadata={"source": "demo-notes.pdf", "page": 1},
    )])
    model = FakeListChatModel(responses=[
        "Which data structure supports a FIFO queue?",
        "yes",
        "Use collections.deque for fast appends and pops at both ends [demo-notes.pdf, Page 1].",
        "How do I configure a Qdrant collection?",
        "no",
    ])
    agent = RAGAgent(store, ConversationMemory(), llm=model)
    print("OFFLINE DEMO: scripted model + fake embeddings; not measured answer quality.\n")
    for question in ["What should I use for a FIFO queue?", "How do I configure a Qdrant collection?"]:
        result = await agent.ainvoke(question)
        print("Question:", question)
        print("Answer:", result["generation"])
        print("Accepted sources:", len(result["sources"]))
        print()
    assert agent.memory.message_count == 4
    print("Both completed turns are saved in conversation memory.")


if __name__ == "__main__":
    asyncio.run(main())

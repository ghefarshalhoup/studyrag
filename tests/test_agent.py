"""Run the whole LangGraph pipeline with a scripted model and fake embeddings (no API calls)."""

import asyncio

from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models import FakeListChatModel

from src.memory import ConversationMemory
from src.rag_agent import RAGAgent
from src.vector_store import VectorStoreManager


def make_agent(responses: list[str], documents: list[Document]) -> RAGAgent:
    store = VectorStoreManager(embeddings=DeterministicFakeEmbedding(size=32))
    store.add_documents(documents)
    return RAGAgent(store, ConversationMemory(trim_n=4), llm=FakeListChatModel(responses=responses))


def collect(agent: RAGAgent, question: str) -> list[dict]:
    async def run():
        return [event async for event in agent.astream(question)]

    return asyncio.run(run())


def test_pipeline_rewrites_retrieves_grades_and_answers():
    documents = [
        Document(page_content="Hypothesis testing is a reason to collect data.", metadata={"source": "notes.pdf", "page": 2}),
        Document(page_content="Gothic cathedrals use flying buttresses.", metadata={"source": "noise.pdf", "page": 1}),
    ]
    # Model calls in order: query rewrite, one grade per retrieved document, the answer.
    agent = make_agent(["Why do people collect data?", "yes", "no", "To test hypotheses [notes.pdf, Page 2]."], documents)

    events = collect(agent, "why collect data?")

    steps = [e["thought"].step for e in events if "thought" in e]
    assert steps == ["Query Analysis", "Retrieval", "Document Grading", "Generation"]
    answer = "".join(e["token"] for e in events if "token" in e).strip()
    assert answer == "To test hypotheses [notes.pdf, Page 2]."
    sources = events[-1]["sources"]
    assert len(sources) == 1  # only the document graded "yes"
    assert [m.content for m in agent.memory.get_messages()] == ["why collect data?", answer]


def test_history_with_braces_does_not_break_the_prompt():
    agent = make_agent(["q", "yes", "answer"], [Document(page_content="text", metadata={"source": "a.pdf", "page": 1})])
    agent.memory.add_user_message("What does {x} mean in set notation?")
    agent.memory.add_ai_message("It is a set containing x.")

    events = collect(agent, "and {y}?")

    assert events[-1]["done"] is True


def test_empty_store_still_answers_without_sources():
    agent = make_agent(["q", "I couldn't find relevant information in the uploaded documents."], [])

    events = collect(agent, "anything?")

    assert events[-1]["sources"] == []

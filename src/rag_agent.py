"""Agentic RAG implementation using LangGraph."""

from typing import AsyncIterator, TypedDict
from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from src.config import settings
from src.vector_store import VectorStoreManager
from src.memory import ConversationMemory


@dataclass
class AgentThought:
    """Represents a thought/step from the agent."""

    step: str
    content: str
    metadata: dict | None = None


class AgentState(TypedDict):
    """State for the RAG agent graph."""

    question: str
    rewritten_question: str
    documents: list[Document]
    graded_documents: list[Document]
    generation: str
    thoughts: list[AgentThought]


class RAGAgent:
    """Agentic RAG pipeline: query rewriting -> retrieval -> relevance grading -> generation."""

    def __init__(
        self,
        vector_store: VectorStoreManager,
        memory: ConversationMemory,
        llm: BaseChatModel | None = None,
    ):
        """Initialize the RAG agent. `llm` defaults to the configured OpenAI chat model."""
        self.vector_store = vector_store
        self.memory = memory

        self.llm = llm or ChatOpenAI(
            model=settings.openai_chat_model,
            openai_api_key=settings.openai_api_key,
            temperature=0,
            streaming=True,
        )

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("grade_documents", self._grade_documents)
        workflow.add_node("generate", self._generate)

        # Set entry point
        workflow.set_entry_point("analyze_query")

        # Simple linear flow - no loops, for predictable response times
        workflow.add_edge("analyze_query", "retrieve")
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_edge("grade_documents", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()

    def _history(self) -> list:
        """Conversation turns so far, without the system message."""
        return [m for m in self.memory.get_messages() if not isinstance(m, SystemMessage)]

    async def _analyze_query(self, state: AgentState) -> dict:
        """Analyze and potentially rewrite the query for better retrieval."""
        question = state["question"]
        thoughts = state.get("thoughts", [])

        # Query rewriting prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a query analyzer for a RAG system. Your job is to rewrite user questions
to be more effective for document retrieval.

Guidelines:
- Make the query more specific and searchable
- Expand abbreviations if clear from context
- Keep the core intent of the question
- If the question is already clear, return it as-is

Conversation context:
{context}

Return ONLY the rewritten query, nothing else."""),
            ("human", "Original question: {question}"),
        ])

        # Get conversation context
        context = "\n".join([
            f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
            for m in self._history()[-4:]  # Last 4 messages for context
        ])

        chain = prompt | self.llm | StrOutputParser()
        rewritten = await chain.ainvoke({
            "question": question,
            "context": context or "No previous context",
        })

        thoughts.append(AgentThought(
            step="Query Analysis",
            content=f"Original: {question}\nRewritten: {rewritten}",
        ))

        return {
            "rewritten_question": rewritten.strip(),
            "thoughts": thoughts,
        }

    async def _retrieve(self, state: AgentState) -> dict:
        """Retrieve relevant documents from the vector store."""
        query = state.get("rewritten_question") or state["question"]
        thoughts = state.get("thoughts", [])

        documents = self.vector_store.similarity_search(query, k=4)

        thoughts.append(AgentThought(
            step="Retrieval",
            content=f"Retrieved {len(documents)} documents for query: {query}",
            metadata={"document_count": len(documents)},
        ))

        return {
            "documents": documents,
            "thoughts": thoughts,
        }

    async def _grade_documents(self, state: AgentState) -> dict:
        """Grade retrieved documents for relevance."""
        documents = state["documents"]
        question = state.get("rewritten_question") or state["question"]
        thoughts = state.get("thoughts", [])

        if not documents:
            thoughts.append(AgentThought(
                step="Document Grading",
                content="No documents to grade",
            ))
            return {
                "graded_documents": [],
                "thoughts": thoughts,
            }

        # Grading prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a document relevance grader. Grade whether a document is relevant
to answering the user's question.

Return ONLY 'yes' or 'no'."""),
            ("human", """Question: {question}

Document content:
{document}

Is this document relevant to answering the question?"""),
        ])

        chain = prompt | self.llm | StrOutputParser()

        graded_docs = []
        grading_results = []

        for i, doc in enumerate(documents):
            result = await chain.ainvoke({
                "question": question,
                "document": doc.page_content[:1000],  # Limit content for grading
            })

            is_relevant = result.strip().lower() == "yes"
            grading_results.append(f"Doc {i+1}: {'Relevant' if is_relevant else 'Not relevant'}")

            if is_relevant:
                graded_docs.append(doc)

        thoughts.append(AgentThought(
            step="Document Grading",
            content=f"Graded {len(documents)} documents, {len(graded_docs)} relevant\n" +
                   "\n".join(grading_results),
            metadata={"relevant_count": len(graded_docs)},
        ))

        return {
            "graded_documents": graded_docs,
            "thoughts": thoughts,
        }

    async def _generate(self, state: AgentState) -> dict:
        """Generate answer based on retrieved documents."""
        question = state["question"]
        # Prefer graded documents, fall back to all retrieved documents
        graded_docs = state.get("graded_documents", [])
        all_docs = state.get("documents", [])
        documents = graded_docs if graded_docs else all_docs
        thoughts = state.get("thoughts", [])

        # Format documents for context
        if documents:
            doc_context = "\n\n---\n\n".join([
                f"[Source: {doc.metadata.get('source', 'Unknown')}, Page {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}"
                for doc in documents
            ])
            system_note = ""
        else:
            doc_context = "No documents were found relevant to your question."
            system_note = "\nNote: No relevant documents were found. Please let the user know and suggest they rephrase or upload relevant documents."

        # Generation prompt. History goes through a placeholder so braces in
        # earlier messages are not read as template variables.
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful study assistant called StudyRAG. Answer the user's question based on the
provided document context.

Guidelines:
- Base your answer on the provided documents
- If the documents don't contain enough information, say so clearly
- Be concise but thorough
- Cite sources when possible using [Source, Page X] format{system_note}

Document Context:
{context}"""),
            MessagesPlaceholder("history"),
            ("human", "{question}"),
        ])

        chain = prompt | self.llm | StrOutputParser()

        generation = await chain.ainvoke({
            "context": doc_context,
            "question": question,
            "system_note": system_note,
            "history": self._history()[-6:],  # Include recent conversation
        })

        thoughts.append(AgentThought(
            step="Generation",
            content=f"Generated response based on {len(documents)} document(s)" +
                   (" (no relevant docs found)" if not documents else ""),
        ))

        return {
            "generation": generation,
            "thoughts": thoughts,
        }

    async def astream(
        self,
        question: str,
    ) -> AsyncIterator[dict]:
        """Stream the agent's response with thoughts.

        Yields dicts with keys:
        - 'thought': AgentThought object
        - 'token': str token from generation
        - 'sources': list of source documents
        - 'done': bool indicating completion
        """
        initial_state: AgentState = {
            "question": question,
            "rewritten_question": "",
            "documents": [],
            "graded_documents": [],
            "generation": "",
            "thoughts": [],
        }

        previous_thoughts = []

        config = {"recursion_limit": 10}  # Safety limit
        async for event in self.graph.astream(initial_state, config=config, stream_mode="values"):
            # Yield new thoughts
            current_thoughts = event.get("thoughts", [])
            for thought in current_thoughts[len(previous_thoughts):]:
                yield {"thought": thought}
            previous_thoughts = current_thoughts.copy()

        # Get final state
        final_state = event

        # Yield the final generation word by word for a streaming effect
        generation = final_state.get("generation", "")
        for token in generation.split():
            yield {"token": token + " "}

        # Yield sources
        documents = final_state.get("graded_documents", []) or final_state.get("documents", [])
        sources = [
            {
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", "N/A"),
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
            }
            for doc in documents
        ]

        yield {"sources": sources, "done": True}

        # Update memory
        self.memory.add_user_message(question)
        self.memory.add_ai_message(generation)

    async def ainvoke(self, question: str) -> dict:
        """Invoke the agent and return the complete response."""
        sources = []
        thoughts = []

        async for event in self.astream(question):
            if "thought" in event:
                thoughts.append(event["thought"])
            if "sources" in event:
                sources = event["sources"]
            if event.get("done"):
                break

        # Get the complete generation from memory
        messages = self.memory.get_messages()
        generation = messages[-1].content if messages else ""

        return {
            "generation": generation,
            "sources": sources,
            "thoughts": thoughts,
        }

"""Chat UI component with streaming and agent thoughts."""

import asyncio
import streamlit as st
from src.rag_agent import RAGAgent, AgentThought


def render_thought(thought: AgentThought) -> None:
    """Render an agent thought in the UI."""
    with st.expander(f"Agent: {thought.step}", expanded=False):
        st.markdown(thought.content)
        if thought.metadata:
            st.json(thought.metadata)


def render_message(role: str, content: str, is_dark_mode: bool = False) -> None:
    """Render a chat message."""
    if role == "user":
        st.chat_message("user").markdown(content)
    else:
        st.chat_message("assistant").markdown(content)


def render_chat_history(messages: list[dict]) -> None:
    """Render the chat history."""
    for msg in messages:
        render_message(msg["role"], msg["content"])


async def stream_response(
    agent: RAGAgent,
    question: str,
    thought_container,
    response_container,
) -> dict:
    """Stream the agent response with thoughts.

    Args:
        agent: The RAG agent
        question: User question
        thought_container: Streamlit container for thoughts
        response_container: Streamlit container for response

    Returns:
        Dict with 'response' and 'sources'
    """
    thoughts = []
    response_text = ""
    sources = []

    async for event in agent.astream(question):
        if "thought" in event:
            thought = event["thought"]
            thoughts.append(thought)
            with thought_container:
                render_thought(thought)

        if "token" in event:
            response_text += event["token"]
            response_container.markdown(response_text + " ")

        if "sources" in event:
            sources = event["sources"]

    return {
        "response": response_text.strip(),
        "sources": sources,
        "thoughts": thoughts,
    }


def run_stream_response(
    agent: RAGAgent,
    question: str,
    thought_container,
    response_container,
) -> dict:
    """Synchronous wrapper for stream_response."""
    return asyncio.run(stream_response(
        agent, question, thought_container, response_container
    ))


def chat_input_handler(
    agent: RAGAgent,
    chat_container,
    sources_callback,
) -> None:
    """Handle chat input and streaming response.

    Args:
        agent: The RAG agent
        chat_container: Container for chat messages
        sources_callback: Callback to update sources display
    """
    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Render existing chat history
    with chat_container:
        render_chat_history(st.session_state.chat_history)

    # Chat input
    if question := st.chat_input("Ask a question about your documents..."):
        # Check if documents are loaded
        if agent.vector_store.is_empty:
            st.warning("Please upload documents first!")
            return

        # Add user message to history and display
        st.session_state.chat_history.append({
            "role": "user",
            "content": question,
        })

        with chat_container:
            st.chat_message("user").markdown(question)

            # Create containers for streaming
            thought_container = st.container()
            with st.chat_message("assistant"):
                response_container = st.empty()

                # Stream the response
                result = run_stream_response(
                    agent,
                    question,
                    thought_container,
                    response_container,
                )

        # Add assistant message to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["response"],
        })

        # Update sources
        sources_callback(result["sources"])

        # Store thoughts for reference
        if "agent_thoughts" not in st.session_state:
            st.session_state.agent_thoughts = []
        st.session_state.agent_thoughts.extend(result["thoughts"])


def clear_chat_history() -> None:
    """Clear the chat history."""
    st.session_state.chat_history = []
    st.session_state.agent_thoughts = []
    if "current_sources" in st.session_state:
        st.session_state.current_sources = []

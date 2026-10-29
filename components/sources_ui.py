"""Sources display component with collapsible retrieval info."""

import streamlit as st


def render_source(source: dict, index: int) -> None:
    """Render a single source with collapsible content.

    Args:
        source: Dict with 'source', 'page', and 'content' keys
        index: Index of the source for display
    """
    source_name = source.get("source", "Unknown")
    page = source.get("page", "N/A")
    content = source.get("content", "No content available")

    with st.expander(f"Source {index + 1}: {source_name} (Page {page})", expanded=False):
        st.markdown(f"**File:** {source_name}")
        st.markdown(f"**Page:** {page}")
        st.markdown("---")
        st.markdown(content)


def render_sources_panel(sources: list[dict] | None = None) -> None:
    """Render the sources panel.

    Args:
        sources: List of source dicts, or None to use session state
    """
    st.subheader("Retrieved Sources")

    # Use provided sources or get from session state
    if sources is None:
        sources = st.session_state.get("current_sources", [])

    if not sources:
        st.info("Sources will appear here when you ask questions.")
        return

    st.markdown(f"**{len(sources)} sources found**")
    st.markdown("---")

    for i, source in enumerate(sources):
        render_source(source, i)


def update_sources(sources: list[dict]) -> None:
    """Update the current sources in session state.

    Args:
        sources: List of source dicts
    """
    st.session_state.current_sources = sources


def render_document_info(uploaded_files: list, chunk_count: int) -> None:
    """Render information about uploaded documents.

    Args:
        uploaded_files: List of uploaded file names
        chunk_count: Total number of chunks created
    """
    if not uploaded_files:
        st.info("No documents uploaded yet.")
        return

    st.subheader("Loaded Documents")

    for file_name in uploaded_files:
        st.markdown(f"- {file_name}")

    st.markdown(f"**Total chunks:** {chunk_count}")


def render_agent_thoughts() -> None:
    """Render the agent's thinking process from session state."""
    thoughts = st.session_state.get("agent_thoughts", [])

    if not thoughts:
        return

    st.subheader("Agent Thinking")

    # Show only last few thoughts to avoid clutter
    recent_thoughts = thoughts[-5:]

    for thought in recent_thoughts:
        with st.expander(thought.step, expanded=False):
            st.markdown(thought.content)
            if thought.metadata:
                st.json(thought.metadata)

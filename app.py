"""StudyRAG - Main Streamlit Application."""

import streamlit as st

from src.config import settings
from src.document_loader import process_uploaded_files
from src.vector_store import VectorStoreManager
from src.memory import ConversationMemory
from src.rag_agent import RAGAgent
from components.chat_ui import chat_input_handler, clear_chat_history
from components.sources_ui import (
    render_sources_panel,
    update_sources,
    render_document_info,
    render_agent_thoughts,
)


# Page configuration
st.set_page_config(
    page_title="StudyRAG",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_theme_css(is_dark_mode: bool) -> str:
    """Get CSS for light or dark mode."""
    if is_dark_mode:
        return """
        <style>
            :root {
                --bg-color: #1a1a2e;
                --secondary-bg: #16213e;
                --text-color: #e8e8e8;
                --accent-color: #4a9eff;
                --border-color: #2d3748;
            }
            .stApp {
                background-color: var(--bg-color);
            }
            .stChatMessage {
                background-color: var(--secondary-bg);
            }
            .stExpander {
                background-color: var(--secondary-bg);
                border-color: var(--border-color);
            }
            .source-card {
                background-color: var(--secondary-bg);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 0.5rem;
            }
            .thought-bubble {
                background-color: #2d3748;
                border-left: 3px solid var(--accent-color);
                padding: 0.5rem 1rem;
                margin: 0.5rem 0;
                font-size: 0.9rem;
                color: #a0aec0;
            }
        </style>
        """
    else:
        return """
        <style>
            :root {
                --bg-color: #ffffff;
                --secondary-bg: #f7fafc;
                --text-color: #1a202c;
                --accent-color: #3182ce;
                --border-color: #e2e8f0;
            }
            .source-card {
                background-color: var(--secondary-bg);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 0.5rem;
            }
            .thought-bubble {
                background-color: #edf2f7;
                border-left: 3px solid var(--accent-color);
                padding: 0.5rem 1rem;
                margin: 0.5rem 0;
                font-size: 0.9rem;
                color: #4a5568;
            }
        </style>
        """


def initialize_session_state():
    """Initialize all session state variables."""
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = VectorStoreManager()

    if "memory" not in st.session_state:
        st.session_state.memory = ConversationMemory()
        st.session_state.memory.set_system_message(
            "You are StudyRAG, a helpful study assistant. Help users understand "
            "their uploaded documents by answering questions accurately and citing sources."
        )

    if "agent" not in st.session_state:
        st.session_state.agent = RAGAgent(
            vector_store=st.session_state.vector_store,
            memory=st.session_state.memory,
        )

    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "current_sources" not in st.session_state:
        st.session_state.current_sources = []

    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False


def validate_settings() -> list[str]:
    """Validate application settings."""
    return settings.validate()


def handle_file_upload(uploaded_files):
    """Process uploaded files and add to vector store."""
    if not uploaded_files:
        return

    new_files = []
    for file in uploaded_files:
        if file.name not in st.session_state.uploaded_files:
            new_files.append((file, file.name))
            st.session_state.uploaded_files.append(file.name)

    if new_files:
        with st.spinner(f"Processing {len(new_files)} file(s)..."):
            # Process and chunk documents
            documents = process_uploaded_files(new_files)

            # Add to vector store
            count = st.session_state.vector_store.add_documents(documents)

            st.success(f"Added {count} chunks from {len(new_files)} file(s)")


def render_sidebar():
    """Render the sidebar with controls and settings."""
    with st.sidebar:
        st.title("StudyRAG")
        st.markdown("---")

        # Theme toggle
        st.session_state.dark_mode = st.toggle(
            "Dark Mode",
            value=st.session_state.dark_mode,
            help="Toggle between light and dark themes",
        )

        st.markdown("---")

        # File upload
        st.subheader("Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose PDF or DOCX files",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            help=f"Maximum file size: {settings.max_file_size_mb}MB",
        )

        handle_file_upload(uploaded_files)

        st.markdown("---")

        # Document info
        render_document_info(
            st.session_state.uploaded_files,
            st.session_state.vector_store.document_count,
        )

        st.markdown("---")

        # Actions
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Clear Chat", use_container_width=True):
                clear_chat_history()
                st.session_state.memory.clear()
                st.rerun()

        with col2:
            if st.button("Clear All", use_container_width=True):
                clear_chat_history()
                st.session_state.memory.clear_all()
                st.session_state.vector_store.clear()
                st.session_state.uploaded_files = []
                st.session_state.current_sources = []
                st.rerun()

        st.markdown("---")

        # Settings info
        with st.expander("Settings", expanded=False):
            st.markdown(f"**Model:** {settings.openai_chat_model}")
            st.markdown(f"**Embedding:** {settings.openai_embedding_model}")
            st.markdown(f"**Chunk Size:** {settings.chunk_size}")
            st.markdown(f"**Memory Trim:** {settings.memory_trim_n}")


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()

    # Validate settings
    errors = validate_settings()
    if errors:
        st.error("Configuration errors:")
        for error in errors:
            st.error(f"- {error}")
        st.info("Please check your .env file and restart the application.")
        return

    # Apply theme
    st.markdown(get_theme_css(st.session_state.dark_mode), unsafe_allow_html=True)

    # Render sidebar
    render_sidebar()

    # Main content - side by side layout
    chat_col, sources_col = st.columns([2, 1])

    with chat_col:
        st.header("Chat")

        # Chat container
        chat_container = st.container()

        # Handle chat input
        chat_input_handler(
            agent=st.session_state.agent,
            chat_container=chat_container,
            sources_callback=update_sources,
        )

    with sources_col:
        st.header("Sources")

        # Sources panel
        render_sources_panel()

        st.markdown("---")

        # Agent thoughts
        render_agent_thoughts()


if __name__ == "__main__":
    main()

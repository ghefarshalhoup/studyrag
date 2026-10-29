"""Conversation memory management with trim-first-N pattern."""

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from src.config import settings


class ConversationMemory:
    """Manages conversation history with trim-first-N pattern."""

    def __init__(self, trim_n: int | None = None):
        """Initialize conversation memory.

        Args:
            trim_n: Number of oldest messages to trim when limit is reached.
                   If None, uses the value from settings.
        """
        self.trim_n = trim_n if trim_n is not None else settings.memory_trim_n
        self.messages: list[BaseMessage] = []
        self._system_message: SystemMessage | None = None

    def set_system_message(self, content: str) -> None:
        """Set the system message (preserved during trimming)."""
        self._system_message = SystemMessage(content=content)

    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation."""
        self.messages.append(HumanMessage(content=content))
        self._trim_if_needed()

    def add_ai_message(self, content: str) -> None:
        """Add an AI message to the conversation."""
        self.messages.append(AIMessage(content=content))
        self._trim_if_needed()

    def add_message(self, message: BaseMessage) -> None:
        """Add any message type to the conversation."""
        if isinstance(message, SystemMessage):
            self._system_message = message
        else:
            self.messages.append(message)
            self._trim_if_needed()

    def _trim_if_needed(self) -> None:
        """Trim the oldest N messages if conversation is getting too long.

        The trim-first-N pattern removes the oldest messages while preserving
        the system message and most recent context.
        """
        # Trim when we have more than 4x trim_n messages
        # This keeps a reasonable amount of context
        max_messages = self.trim_n * 4 if self.trim_n > 0 else 50

        if len(self.messages) > max_messages and self.trim_n > 0:
            # Remove the oldest N messages (after system message)
            self.messages = self.messages[self.trim_n:]

    def get_messages(self) -> list[BaseMessage]:
        """Get all messages including system message."""
        messages = []

        if self._system_message:
            messages.append(self._system_message)

        messages.extend(self.messages)
        return messages

    def get_messages_for_context(self) -> list[BaseMessage]:
        """Get messages formatted for LLM context."""
        return self.get_messages()

    def clear(self) -> None:
        """Clear all messages except system message."""
        self.messages = []

    def clear_all(self) -> None:
        """Clear all messages including system message."""
        self.messages = []
        self._system_message = None

    @property
    def message_count(self) -> int:
        """Return the number of messages (excluding system)."""
        return len(self.messages)

    @property
    def is_empty(self) -> bool:
        """Check if conversation is empty."""
        return len(self.messages) == 0

    def get_last_n_messages(self, n: int) -> list[BaseMessage]:
        """Get the last N messages."""
        return self.messages[-n:] if n > 0 else []

    def to_dict(self) -> dict:
        """Convert memory to dictionary for serialization."""
        return {
            "messages": [
                {"type": type(m).__name__, "content": m.content}
                for m in self.messages
            ],
            "system_message": self._system_message.content if self._system_message else None,
            "trim_n": self.trim_n,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConversationMemory":
        """Create memory from dictionary."""
        memory = cls(trim_n=data.get("trim_n", settings.memory_trim_n))

        if data.get("system_message"):
            memory.set_system_message(data["system_message"])

        for msg_data in data.get("messages", []):
            msg_type = msg_data["type"]
            content = msg_data["content"]

            if msg_type == "HumanMessage":
                memory.messages.append(HumanMessage(content=content))
            elif msg_type == "AIMessage":
                memory.messages.append(AIMessage(content=content))

        return memory

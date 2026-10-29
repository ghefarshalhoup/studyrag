from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.memory import ConversationMemory


def test_trims_oldest_messages_past_the_limit():
    memory = ConversationMemory(trim_n=2)  # limit: 4 x trim_n = 8 messages
    for i in range(9):
        memory.add_user_message(f"message {i}")

    contents = [m.content for m in memory.messages]
    assert contents == [f"message {i}" for i in range(2, 9)]


def test_system_message_survives_trimming_and_clear():
    memory = ConversationMemory(trim_n=1)
    memory.set_system_message("You are StudyRAG.")
    for i in range(10):
        memory.add_ai_message(f"answer {i}")
    memory.clear()

    messages = memory.get_messages()
    assert len(messages) == 1
    assert isinstance(messages[0], SystemMessage)


def test_round_trip_through_dict():
    memory = ConversationMemory(trim_n=4)
    memory.set_system_message("system")
    memory.add_user_message("question")
    memory.add_ai_message("answer")

    restored = ConversationMemory.from_dict(memory.to_dict())
    assert [type(m) for m in restored.get_messages()] == [SystemMessage, HumanMessage, AIMessage]
    assert restored.get_messages()[-1].content == "answer"

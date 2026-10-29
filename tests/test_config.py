from src.config import Settings


def make_settings(**overrides) -> Settings:
    values = dict(
        openai_api_key="sk-test",
        openai_chat_model="gpt-4o",
        openai_embedding_model="text-embedding-3-small",
        memory_trim_n=4,
        chunk_size=1000,
        chunk_overlap=200,
        max_file_size_mb=100,
    )
    values.update(overrides)
    return Settings(**values)


def test_valid_settings_have_no_errors():
    assert make_settings().validate() == []


def test_invalid_settings_are_reported():
    errors = make_settings(openai_api_key="", chunk_overlap=1000, max_file_size_mb=0).validate()

    assert "OPENAI_API_KEY is required" in errors
    assert "CHUNK_OVERLAP must be less than CHUNK_SIZE" in errors
    assert "MAX_FILE_SIZE_MB must be positive" in errors

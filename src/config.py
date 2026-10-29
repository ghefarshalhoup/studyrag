"""Configuration loader for StudyRAG application."""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str
    openai_chat_model: str
    openai_embedding_model: str

    # Memory Configuration
    memory_trim_n: int

    # Document Chunking Configuration
    chunk_size: int
    chunk_overlap: int

    # File Upload Configuration
    max_file_size_mb: int

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables."""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o"),
            openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            memory_trim_n=int(os.getenv("MEMORY_TRIM_N", "4")),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "100")),
        )

    def validate(self) -> list[str]:
        """Validate settings and return list of errors."""
        errors = []

        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required")

        if self.chunk_overlap >= self.chunk_size:
            errors.append("CHUNK_OVERLAP must be less than CHUNK_SIZE")

        if self.memory_trim_n < 0:
            errors.append("MEMORY_TRIM_N must be non-negative")

        if self.max_file_size_mb <= 0:
            errors.append("MAX_FILE_SIZE_MB must be positive")

        return errors


# Global settings instance
settings = Settings.from_env()

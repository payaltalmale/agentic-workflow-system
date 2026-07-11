"""
Central configuration. Everything downstream (agents, memory, orchestrator)
reads from a single `settings` object so there's one source of truth.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_url: str = "http://127.0.0.1:11434/api/chat"
    
    model_name: str = "llama3.2:3b"

    quality_threshold: int = 60
    max_rewrite_retries: int = 3

    sqlite_db_path: str = "data/memory.db"
    audit_log_path: str = "data/audit.log"

    class Config:
        env_file = ".env"


settings = Settings()


print("=" * 40)
print("QUALITY_THRESHOLD =", settings.quality_threshold)
print("=" * 40)

import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base directory of the project
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    
    # Supabase configurations
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_STORAGE_QUESTIONS_BUCKET: str = os.getenv("SUPABASE_STORAGE_QUESTIONS_BUCKET", "questions")
    
    # AI Tutor specific configurations
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_CHAT_MODEL: str = os.getenv("OLLAMA_CHAT_MODEL", "ai-tutor")
    
    # Operational modes
    USE_MOCK_QUESTIONS: bool = os.getenv("USE_MOCK_QUESTIONS", "false").lower() in ("1", "true", "yes")

    class Config:
        case_sensitive = True

settings = Settings()

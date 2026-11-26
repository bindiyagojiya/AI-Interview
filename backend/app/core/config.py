from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "InterviewIQ AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "interviewiq_dev_secret_key_change_in_production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ALGORITHM: str = "HS256"

    # Database Configuration: SQLite default for zero-config dev/testing;
    # Override with PostgreSQL URL in .env for production database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./interviewiq_dev.db"
    )

    # AI Configuration (Optional Gemini Key)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://10.0.2.2:8081",
        "*"
    ]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="allow")

settings = Settings()

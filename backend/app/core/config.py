from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import os


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://127.0.0.1:3000"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./recoverai.db"
    SYNC_DATABASE_URL: str = "sqlite:///./recoverai.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Razorpay Test Mode Credentials (NEVER USE LIVE KEYS)
    RAZORPAY_KEY_ID: str = "rzp_test_mockkey12345"
    RAZORPAY_KEY_SECRET: str = "mocksecret12345"
    RAZORPAY_WEBHOOK_SECRET: str = "mockwebhooksecret12345"
    RAZORPAY_API_BASE_URL: str = "https://api.razorpay.com/v1"

    # AI / LLM Provider Configuration
    LLM_PROVIDER: str = "mock"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.0-flash"

    # Fintech Policy Engine Defaults
    HIGH_VALUE_THRESHOLD: float = 10000.00
    MAX_RETRY_ATTEMPTS: int = 2
    MIN_AI_CONFIDENCE: float = 0.70
    MIN_RECOVERY_SCORE: float = 15.00
    CONTACT_COOLDOWN_MINUTES: int = 60
    DEMO_MODE: bool = True

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

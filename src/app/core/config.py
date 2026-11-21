import logging

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Raglicious: AI Chatbot API with RAG"
    app_version: str = "0.1.0"
    environment: Literal["development", "testing", "production"] = "development"
    log_level: str = "INFO"

    openai_api_key: str
    openai_model: str = "gpt-5-mini"
    openai_timeout_seconds: float = Field(default=30.0, gt=0)

    database_url: str
    cors_origins: list[str] = ["http://localhost:3000"]

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        if value.upper() not in logging.getLevelNamesMapping():
            raise ValueError(f"Invalid log level: {value}")

        return value.upper()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

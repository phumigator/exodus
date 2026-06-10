"""
Конфигурация API: адреса удалённого сервера с Ollama/Whisper и БД Postgres.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Удалённый сервер с Ollama и Whisper
    remote_api_base_url: str = "http://remote-host:11434"
    whisper_api_base_url: str = "http://remote-host:9000"

    # Postgres на том же удалённом сервере
    database_url: str = "postgresql://user:password@remote-host:5432/analytics"

    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_prefix = "EXODUS_"


settings = Settings()

"""
Конфигурация API: Whisper на удалённом сервере, OpenRouter для суммаризации,
БД Postgres.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Удалённый сервер с Whisper
    whisper_api_base_url: str = "http://remote-host:9000"

    # OpenRouter — суммаризация текста через внешний LLM API
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    # Заголовки, которые OpenRouter использует для рейтинга приложений на openrouter.ai/rankings
    openrouter_site_url: str = "https://github.com/phumigator/exodus"
    openrouter_app_name: str = "Exodus"
    # Прямые запросы к openrouter.ai с этой сети блокируются ("Access denied by
    # security policy"); нужен туннель через локальный прокси-клиент. None — без прокси.
    openrouter_proxy_url: str | None = None

    # Postgres на том же удалённом сервере
    database_url: str = "postgresql://user:password@remote-host:5432/analytics"

    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_prefix = "EXODUS_"


settings = Settings()

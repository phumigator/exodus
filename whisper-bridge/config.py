"""
Конфигурация моста: приватный Whisper-контейнер во внутренней docker-сети,
OpenRouter для коррекции распознанного текста, общий секрет для авторизации
запросов от VPS.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Общий секрет, который VPS присылает в заголовке X-Internal-Token
    # (env_prefix ниже уже добавляет BRIDGE_, поле не должно повторять его)
    shared_secret: str = ""

    # Уже работающий с VPS контейнер whisper-test (проект docker-stack),
    # доступен по имени в общей сети ai-network, наружу не опубликован
    whisper_internal_url: str = "http://whisper-test:9000"

    # OpenRouter — коррекция грамматики/смысла распознанного текста
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free"

    class Config:
        env_file = ".env"
        env_prefix = "BRIDGE_"


settings = Settings()

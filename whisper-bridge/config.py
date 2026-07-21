"""
Конфигурация моста: приватный Whisper-контейнер во внутренней docker-сети,
общий секрет для авторизации запросов от VPS.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Общий секрет, который VPS присылает в заголовке X-Internal-Token
    # (env_prefix ниже уже добавляет BRIDGE_, поле не должно повторять его)
    shared_secret: str = ""

    # Уже работающий с VPS контейнер whisper-service (проект docker-stack),
    # доступен по имени в общей сети ai-network, наружу не опубликован
    whisper_internal_url: str = "http://whisper-service:9000"

    class Config:
        env_file = ".env"
        env_prefix = "BRIDGE_"


settings = Settings()

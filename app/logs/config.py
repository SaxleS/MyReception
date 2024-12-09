from pydantic_settings import BaseSettings
from pydantic import Field


class LogConfig(BaseSettings):
    MONGO_URI: str = Field(..., env="MONGO_URI", description="URI для подключения к MongoDB")
    DATABASE_NAME: str = Field(..., env="DATABASE_NAME", description="Имя базы данных для логов")
    COLLECTION_NAME: str = Field(..., env="COLLECTION_NAME", description="Имя коллекции для логов")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Игнор лишних переменных
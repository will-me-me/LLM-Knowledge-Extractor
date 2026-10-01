from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str 
    DATABASE_URL: str
    FRONTEND_URL: str 

    model_config = SettingsConfigDict(env_file=".env", title="Settings", env_file_encoding="utf-8")


@lru_cache
def get_settings():
    return Settings()
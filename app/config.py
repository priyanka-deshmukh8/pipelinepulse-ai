from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "PipelinePulse AI"
    database_url: str = "sqlite:///./pipelinepulse.db"
    jwt_secret_key: str = "local-development-only-change-me"
    access_token_expire_minutes: int = 30
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_deployment: str | None = None
    azure_openai_embedding_deployment: str | None = None
    vector_connection: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # watsonx.ai
    watsonx_api_key: str = "MOCK"
    watsonx_project_id: str = "MOCK"
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"

    granite_chat_model: str = "ibm/granite-3-3-8b-instruct"
    granite_ttm_model: str = "ibm/granite-ttm-512-96-r2"
    granite_embed_model: str = "ibm/granite-embedding-278m-multilingual"

    # Database
    database_url: str = "sqlite:///./foodwise.db"

    # App
    jwt_secret: str = "dev-secret-change-in-prod"
    allowed_origins: str = "http://localhost:5173"

    # Vector store
    vector_store_backend: str = "chroma"
    chroma_persist_dir: str = "./rag/vector_store"

    # Feature flag: set to "real" to use actual watsonx.ai calls
    ai_mode: str = "mock"  # "mock" | "real"


@lru_cache
def get_settings() -> Settings:
    return Settings()

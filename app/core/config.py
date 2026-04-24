from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Research Intelligence Platform", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    auto_create_tables: bool = Field(default=False, alias="AUTO_CREATE_TABLES")

    postgres_db: str = Field(default="research_platform", alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="db", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@db:5432/research_platform",
        alias="DATABASE_URL",
    )

    jwt_secret_key: str = Field(default="replace-with-a-strong-random-secret", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=60,
        alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    openalex_base_url: str = Field(default="https://api.openalex.org", alias="OPENALEX_BASE_URL")
    openalex_api_key: str = Field(default="", alias="OPENALEX_API_KEY")
    openalex_mailto: str = Field(default="", alias="OPENALEX_MAILTO")
    openalex_default_per_page: int = Field(default=25, alias="OPENALEX_DEFAULT_PER_PAGE")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

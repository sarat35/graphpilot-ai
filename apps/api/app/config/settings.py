from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    app_name: str = "buyseconds"
    app_env: str = "development"
    log_level: str = "INFO"

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    intelligence_model_name: str = "gpt-5-mini"
    product_search_mode: str = "mock"
    google_serper_api_key: str = ""
    google_serper_base_url: str = "https://google.serper.dev/search"

    aws_profile: str = "default"
    aws_region: str = "us-east-1"

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""

    database_url: str = ""
    supabase_url: str = ""
    supabase_publishable_key: str = ""
    supabase_jwt_issuer: str = ""
    supabase_jwt_audience: str = "authenticated"
    supabase_jwks_url: str = ""
    supabase_service_role_key: str = ""
    supabase_secret_key: str = ""
    cors_origins: str = "http://localhost:3000"
    redis_url: str = ""

    model_config = SettingsConfigDict(
        env_file=REPOSITORY_ROOT / ".env",
        extra="ignore",
    )


settings = Settings()
